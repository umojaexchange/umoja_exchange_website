"""
Seed demo data for local testing (purchases, inventory, sales, settings).

    python manage.py seed_demo            # add demo data
    python manage.py seed_demo --clear    # wipe purchases/sales/lots first, then seed

Refuses to run when DEBUG=False unless --force, so it can't seed production.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.purchases.models import PAYMENT_CHOICES, InventoryLot, Purchase
from apps.sales.models import Sale, SaleLot
from apps.settings_app.models import SystemSettings

METHODS = [m[0] for m in PAYMENT_CHOICES]
SUPPLIERS = ["Binance P2P", "Kraken OTC", "Local Trader", "Crypto Hub", "Wallet X"]
CUSTOMERS = ["John M.", "Asha K.", "Peter S.", "Grace T.", "David L.", "Neema R.", "Juma B."]


def _backdate(model, pk, when):
    # created_at is auto_now_add; update() bypasses it to set a historical date.
    model.objects.filter(pk=pk).update(created_at=when)


class Command(BaseCommand):
    help = "Seed demo purchases/sales/inventory for local dashboard testing."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete existing purchases/sales/lots first.")
        parser.add_argument("--force", action="store_true", help="Allow running when DEBUG=False.")
        parser.add_argument("--purchases", type=int, default=25, help="Number of purchases (default 25).")
        parser.add_argument("--sales", type=int, default=60, help="Number of sales (default 60).")

    def handle(self, *args, **opts):
        if not dj_settings.DEBUG and not opts["force"]:
            raise CommandError("Refusing to seed with DEBUG=False. Use --force only if you really mean it.")

        random.seed(42)
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()

        if opts["clear"]:
            SaleLot.objects.all().delete()
            Sale.objects.all().delete()
            InventoryLot.objects.all().delete()
            Purchase.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing purchases/sales/lots."))

        # System settings
        s = SystemSettings.get()
        s.company_capital = Decimal("50000000")
        s.min_threshold = Decimal("5000000")
        s.min_rate, s.max_rate = Decimal("2400"), Decimal("2800")
        s.save()

        now = timezone.now()

        # ── Purchases (spread over the last ~90 days) ────────────────────────
        for _ in range(opts["purchases"]):
            usdt = Decimal(random.randint(100, 3000))
            rate = Decimal(random.randint(2450, 2600))
            p = Purchase.objects.create(
                usdt_amount=usdt, rate_tzs=rate,
                payment_method=random.choice(METHODS),
                supplier_name=random.choice(SUPPLIERS),
                created_by=user, notes="demo",
            )
            _backdate(Purchase, p.pk, now - timedelta(days=random.randint(30, 90), hours=random.randint(0, 23)))
            _backdate(InventoryLot, p.inventory_lot.pk, now - timedelta(days=random.randint(30, 90)))

        # ── Sales (spread over the last ~30 days, FIFO-consumed) ─────────────
        made = 0
        for _ in range(opts["sales"]):
            want = Decimal(random.randint(50, 800))
            lots = list(InventoryLot.objects.filter(remaining__gt=0).order_by("created_at"))
            if not lots:
                break
            consumed, need = [], want
            for lot in lots:
                if need <= 0:
                    break
                take = min(lot.remaining, need)
                if take <= 0:
                    continue
                consumed.append((lot, take))
                lot.remaining -= take
                lot.save()
                need -= take
            got = want - need
            if got <= 0:
                continue

            total_cost = sum(t * lot.rate_tzs for lot, t in consumed)
            avg_buy = (total_cost / got).quantize(Decimal("0.01"))
            sale_rate = (avg_buy + Decimal(random.randint(30, 150))).quantize(Decimal("0.01"))
            paid = (got * sale_rate).quantize(Decimal("0.01"))
            margin = (sale_rate - avg_buy).quantize(Decimal("0.01"))
            profit = (got * margin).quantize(Decimal("0.01"))

            sale = Sale.objects.create(
                usdt_amount=got, sale_rate_tzs=sale_rate, paid_amount_tzs=paid,
                avg_buy_rate=avg_buy, profit_margin=margin, profit_tzs=profit,
                payment_method=random.choice(METHODS),
                customer_name=random.choice(CUSTOMERS),
                created_by=user, notes="demo",
            )
            for lot, t in consumed:
                SaleLot.objects.create(sale=sale, inventory_lot=lot, usdt_consumed=t, buy_rate=lot.rate_tzs)
            _backdate(Sale, sale.pk, now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)))
            made += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Purchase.objects.count()} purchases, {made} sales, "
            f"{InventoryLot.objects.filter(remaining__gt=0).count()} lots with stock."
        ))
