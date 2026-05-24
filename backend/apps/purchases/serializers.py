from rest_framework import serializers
from .models import Purchase, InventoryLot, PAYMENT_CHOICES


class InventoryLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLot
        fields = ["id", "usdt_amount", "remaining", "rate_tzs", "is_fully_consumed"]


class PurchaseSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    remaining_inventory = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    class Meta:
        model = Purchase
        fields = [
            "id", "usdt_amount", "rate_tzs", "amount_paid_tzs",
            "payment_method", "payment_method_display",
            "supplier_name", "notes",
            "created_by", "created_by_name",
            "remaining_inventory",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "amount_paid_tzs", "created_by", "created_at", "updated_at"]

    def validate_usdt_amount(self, value):
        from apps.settings_app.models import SystemSettings
        s = SystemSettings.get()
        if value < s.min_asset_value:
            raise serializers.ValidationError(f"Minimum asset value is {s.min_asset_value} USDT.")
        if value > s.max_asset_value:
            raise serializers.ValidationError(f"Maximum asset value is {s.max_asset_value} USDT.")
        return value

    def validate_rate_tzs(self, value):
        from apps.settings_app.models import SystemSettings
        s = SystemSettings.get()
        if value < s.min_rate:
            raise serializers.ValidationError(f"Rate is below minimum allowed ({s.min_rate} TZS).")
        if value > s.max_rate:
            raise serializers.ValidationError(f"Rate exceeds maximum allowed ({s.max_rate} TZS).")
        return value
