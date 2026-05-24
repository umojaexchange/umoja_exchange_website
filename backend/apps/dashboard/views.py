from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.purchases.models import Purchase, InventoryLot
from apps.sales.models import Sale
from apps.settings_app.models import SystemSettings


def _zero(val):
    return val if val is not None else Decimal("0")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    settings = SystemSettings.get()

    total_purchases_tzs = _zero(Purchase.objects.aggregate(t=Sum("amount_paid_tzs"))["t"])
    total_sales_tzs = _zero(Sale.objects.aggregate(t=Sum("paid_amount_tzs"))["t"])
    total_profit = _zero(Sale.objects.aggregate(t=Sum("profit_tzs"))["t"])

    daily_profit = _zero(Sale.objects.filter(created_at__gte=today_start).aggregate(t=Sum("profit_tzs"))["t"])
    weekly_profit = _zero(Sale.objects.filter(created_at__gte=week_start).aggregate(t=Sum("profit_tzs"))["t"])
    monthly_profit = _zero(Sale.objects.filter(created_at__gte=month_start).aggregate(t=Sum("profit_tzs"))["t"])
    annual_profit = _zero(Sale.objects.filter(created_at__gte=year_start).aggregate(t=Sum("profit_tzs"))["t"])

    remaining_inventory = _zero(InventoryLot.objects.filter(remaining__gt=0).aggregate(t=Sum("remaining"))["t"])
    total_customers = Sale.objects.values("customer_name").distinct().count()
    total_sales_count = Sale.objects.count()
    total_purchases_count = Purchase.objects.count()

    capital = settings.company_capital
    capital_warning = capital > 0 and capital <= settings.min_threshold

    return Response({
        "total_capital": capital,
        "capital_warning": capital_warning,
        "min_threshold": settings.min_threshold,
        "total_purchases_tzs": total_purchases_tzs,
        "total_sales_tzs": total_sales_tzs,
        "total_profit": total_profit,
        "daily_profit": daily_profit,
        "weekly_profit": weekly_profit,
        "monthly_profit": monthly_profit,
        "annual_profit": annual_profit,
        "remaining_inventory": remaining_inventory,
        "total_customers": total_customers,
        "total_sales_count": total_sales_count,
        "total_purchases_count": total_purchases_count,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_charts(request):
    now = timezone.now()

    # Daily profit — last 30 days
    thirty_days_ago = now - timedelta(days=30)
    daily_profit_qs = (
        Sale.objects.filter(created_at__gte=thirty_days_ago)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(profit=Sum("profit_tzs"), sales=Sum("paid_amount_tzs"), count=Count("id"))
        .order_by("day")
    )
    daily_profit_chart = [
        {
            "date": item["day"].strftime("%Y-%m-%d"),
            "profit": float(item["profit"] or 0),
            "sales": float(item["sales"] or 0),
            "count": item["count"],
        }
        for item in daily_profit_qs
    ]

    # Monthly profit — last 12 months
    twelve_months_ago = now - timedelta(days=365)
    monthly_qs = (
        Sale.objects.filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(profit=Sum("profit_tzs"), sales=Sum("paid_amount_tzs"), count=Count("id"))
        .order_by("month")
    )
    monthly_chart = [
        {
            "month": item["month"].strftime("%b %Y"),
            "profit": float(item["profit"] or 0),
            "sales": float(item["sales"] or 0),
            "count": item["count"],
        }
        for item in monthly_qs
    ]

    # Monthly purchases — last 12 months
    monthly_purchases_qs = (
        Purchase.objects.filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount_paid_tzs"), count=Count("id"))
        .order_by("month")
    )
    monthly_purchases = {
        item["month"].strftime("%b %Y"): float(item["total"] or 0)
        for item in monthly_purchases_qs
    }

    # Payment method distribution
    payment_dist_qs = (
        Sale.objects.values("payment_method")
        .annotate(count=Count("id"), total=Sum("paid_amount_tzs"))
        .order_by("-count")
    )
    payment_dist = [
        {"method": item["payment_method"], "count": item["count"], "total": float(item["total"] or 0)}
        for item in payment_dist_qs
    ]

    return Response({
        "daily_profit": daily_profit_chart,
        "monthly": monthly_chart,
        "monthly_purchases": monthly_purchases,
        "payment_distribution": payment_dist,
    })
