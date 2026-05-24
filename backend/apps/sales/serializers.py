from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from rest_framework import serializers

from apps.purchases.models import InventoryLot
from .models import Sale, SaleLot


# ─── FIFO Engine ─────────────────────────────────────────────────────────────
def execute_fifo_sale(usdt_amount, sale_rate, payment_method, customer_name, notes, user):
    """
    Creates a Sale using FIFO inventory depletion.
    Returns the created Sale instance.
    Raises ValueError if insufficient inventory.
    """
    usdt_amount = Decimal(str(usdt_amount))
    sale_rate = Decimal(str(sale_rate))

    with transaction.atomic():
        # Lock available lots in FIFO order
        lots = list(
            InventoryLot.objects.filter(remaining__gt=0)
            .order_by("created_at")
            .select_for_update()
        )

        total_available = sum(lot.remaining for lot in lots)
        if total_available < usdt_amount:
            raise ValueError(
                f"Insufficient inventory. Available: {total_available} USDT, Requested: {usdt_amount} USDT."
            )

        # Consume lots FIFO
        remaining_to_sell = usdt_amount
        consumed = []  # [(lot, amount_consumed)]

        for lot in lots:
            if remaining_to_sell <= 0:
                break
            consume = min(lot.remaining, remaining_to_sell)
            consumed.append((lot, consume))
            lot.remaining -= consume
            lot.save()
            remaining_to_sell -= consume

        # Weighted average buy rate
        total_cost = sum(amt * lot.rate_tzs for lot, amt in consumed)
        avg_buy_rate = (total_cost / usdt_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        profit_margin = (sale_rate - avg_buy_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        profit_tzs = (usdt_amount * profit_margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        paid_amount_tzs = (usdt_amount * sale_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        sale = Sale.objects.create(
            usdt_amount=usdt_amount,
            sale_rate_tzs=sale_rate,
            paid_amount_tzs=paid_amount_tzs,
            avg_buy_rate=avg_buy_rate,
            profit_margin=profit_margin,
            profit_tzs=profit_tzs,
            payment_method=payment_method,
            customer_name=customer_name,
            notes=notes,
            created_by=user,
        )

        SaleLot.objects.bulk_create([
            SaleLot(
                sale=sale,
                inventory_lot=lot,
                usdt_consumed=consumed_amt,
                buy_rate=lot.rate_tzs,
            )
            for lot, consumed_amt in consumed
        ])

    return sale


def reverse_fifo_sale(sale):
    """Restores inventory lots when a sale is deleted."""
    with transaction.atomic():
        for sale_lot in sale.sale_lots.select_related("inventory_lot").all():
            lot = sale_lot.inventory_lot
            lot.remaining += sale_lot.usdt_consumed
            lot.save()
        sale.delete()


# ─── Serializers ─────────────────────────────────────────────────────────────
class SaleLotSerializer(serializers.ModelSerializer):
    purchase_id = serializers.IntegerField(source="inventory_lot.purchase_id", read_only=True)

    class Meta:
        model = SaleLot
        fields = ["id", "inventory_lot", "purchase_id", "usdt_consumed", "buy_rate"]


class SaleSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    sale_lots = SaleLotSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id", "usdt_amount", "sale_rate_tzs",
            "paid_amount_tzs", "avg_buy_rate",
            "profit_margin", "profit_tzs",
            "payment_method", "payment_method_display",
            "customer_name", "notes",
            "created_by", "created_by_name",
            "sale_lots",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "paid_amount_tzs", "avg_buy_rate",
            "profit_margin", "profit_tzs",
            "created_by", "created_at", "updated_at",
        ]

    def validate_usdt_amount(self, value):
        from apps.settings_app.models import SystemSettings
        s = SystemSettings.get()
        if value < s.min_asset_value:
            raise serializers.ValidationError(f"Minimum asset value is {s.min_asset_value} USDT.")
        if value > s.max_asset_value:
            raise serializers.ValidationError(f"Maximum asset value is {s.max_asset_value} USDT.")
        return value

    def validate_sale_rate_tzs(self, value):
        from apps.settings_app.models import SystemSettings
        s = SystemSettings.get()
        if value < s.min_rate:
            raise serializers.ValidationError(f"Rate is below minimum ({s.min_rate} TZS).")
        if value > s.max_rate:
            raise serializers.ValidationError(f"Rate exceeds maximum ({s.max_rate} TZS).")
        return value


class SaleCreateSerializer(serializers.Serializer):
    usdt_amount = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0.01"))
    sale_rate_tzs = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0.01"))
    payment_method = serializers.ChoiceField(choices=[c[0] for c in __import__("apps.purchases.models", fromlist=["PAYMENT_CHOICES"]).PAYMENT_CHOICES])
    customer_name = serializers.CharField(max_length=255)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_usdt_amount(self, value):
        from apps.settings_app.models import SystemSettings
        s = SystemSettings.get()
        if value < s.min_asset_value:
            raise serializers.ValidationError(f"Minimum asset value is {s.min_asset_value} USDT.")
        if value > s.max_asset_value:
            raise serializers.ValidationError(f"Maximum asset value is {s.max_asset_value} USDT.")
        return value
