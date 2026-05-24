from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


PAYMENT_CHOICES = [
    ("crdb", "CRDB Bank"),
    ("nmb", "NMB Bank"),
    ("nbc", "NBC Bank"),
    ("equity", "Equity Bank"),
    ("absa", "Absa Bank"),
    ("stanbic", "Stanbic Bank"),
    ("exim", "Exim Bank"),
    ("boa", "BOA Bank"),
    ("mpesa", "M-Pesa"),
    ("airtel", "Airtel Money"),
    ("tigo", "Tigo Pesa"),
    ("halopesa", "HaloPesa"),
    ("cash", "Cash"),
]


class Purchase(models.Model):
    usdt_amount = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    rate_tzs = models.DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    amount_paid_tzs = models.DecimalField(max_digits=30, decimal_places=2, editable=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    supplier_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="purchases",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchases"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["supplier_name"]),
        ]

    def save(self, *args, **kwargs):
        self.amount_paid_tzs = self.usdt_amount * self.rate_tzs
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            InventoryLot.objects.create(
                purchase=self,
                usdt_amount=self.usdt_amount,
                remaining=self.usdt_amount,
                rate_tzs=self.rate_tzs,
            )

    def __str__(self):
        return f"Purchase #{self.pk} — {self.usdt_amount} USDT @ {self.rate_tzs}"

    @property
    def remaining_inventory(self):
        try:
            return self.inventory_lot.remaining
        except InventoryLot.DoesNotExist:
            return Decimal("0")


class InventoryLot(models.Model):
    """Tracks remaining USDT per purchase for FIFO accounting."""

    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name="inventory_lot")
    usdt_amount = models.DecimalField(max_digits=20, decimal_places=2)
    remaining = models.DecimalField(max_digits=20, decimal_places=2)
    rate_tzs = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_lots"
        ordering = ["created_at"]

    @property
    def is_fully_consumed(self):
        return self.remaining <= 0

    def __str__(self):
        return f"Lot #{self.pk} — {self.remaining}/{self.usdt_amount} USDT remaining"
