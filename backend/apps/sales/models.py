from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal, ROUND_HALF_UP
from apps.purchases.models import PAYMENT_CHOICES


class Sale(models.Model):
    usdt_amount = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    sale_rate_tzs = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    paid_amount_tzs = models.DecimalField(max_digits=30, decimal_places=2)
    avg_buy_rate = models.DecimalField(max_digits=20, decimal_places=2)
    profit_margin = models.DecimalField(max_digits=20, decimal_places=2)
    profit_tzs = models.DecimalField(max_digits=30, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    customer_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sales",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer_name"]),
        ]

    def __str__(self):
        return f"Sale #{self.pk} — {self.usdt_amount} USDT @ {self.sale_rate_tzs} → Profit: {self.profit_tzs} TZS"


class SaleLot(models.Model):
    """Records which inventory lots were consumed by a sale (FIFO audit trail)."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="sale_lots")
    inventory_lot = models.ForeignKey(
        "purchases.InventoryLot", on_delete=models.PROTECT, related_name="sale_lots"
    )
    usdt_consumed = models.DecimalField(max_digits=20, decimal_places=2)
    buy_rate = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        db_table = "sale_lots"

    def __str__(self):
        return f"SaleLot: {self.usdt_consumed} USDT from Lot #{self.inventory_lot_id}"
