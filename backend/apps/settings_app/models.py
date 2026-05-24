from django.db import models


class SystemSettings(models.Model):
    """Singleton model for system-wide configuration."""

    min_rate = models.DecimalField(max_digits=20, decimal_places=2, default=2000)
    max_rate = models.DecimalField(max_digits=20, decimal_places=2, default=5000)
    min_asset_value = models.DecimalField(max_digits=20, decimal_places=2, default=10)
    max_asset_value = models.DecimalField(max_digits=20, decimal_places=2, default=100000)
    company_capital = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    min_threshold = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    report_email = models.EmailField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_settings"
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "System Settings"
