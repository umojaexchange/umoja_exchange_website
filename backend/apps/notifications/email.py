"""Resend email integration for automated reports."""
import resend
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

from apps.purchases.models import Purchase
from apps.sales.models import Sale
from apps.purchases.models import InventoryLot
from apps.settings_app.models import SystemSettings


def _fmt(val):
    return f"{val:,.2f}" if val is not None else "0.00"


def build_daily_report_html(date=None):
    if date is None:
        date = timezone.localdate()

    purchases_today = Purchase.objects.filter(created_at__date=date)
    sales_today = Sale.objects.filter(created_at__date=date)

    from django.db.models import Sum, Count
    p_agg = purchases_today.aggregate(total_usdt=Sum("usdt_amount"), total_tzs=Sum("amount_paid_tzs"), count=Count("id"))
    s_agg = sales_today.aggregate(total_usdt=Sum("usdt_amount"), total_tzs=Sum("paid_amount_tzs"), total_profit=Sum("profit_tzs"), count=Count("id"))

    settings_obj = SystemSettings.get()
    remaining = InventoryLot.objects.filter(remaining__gt=0).aggregate(t=Sum("remaining"))["t"] or 0

    capital = settings_obj.company_capital
    capital_warning = capital > 0 and capital <= settings_obj.min_threshold
    warning_html = f'<tr><td colspan="2" style="background:#FEF9C3;color:#92400E;padding:12px;font-weight:bold;text-align:center;">⚠️ Capital is at or below minimum threshold ({_fmt(settings_obj.min_threshold)} TZS)</td></tr>' if capital_warning else ""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Daily Report</title></head>
<body style="margin:0;padding:0;font-family:Calibri,Arial,sans-serif;background:#F3F4F6;">
  <div style="max-width:640px;margin:24px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.1);">
    <div style="background:#0F0F0F;padding:28px 32px;display:flex;align-items:center;">
      <div>
        <div style="color:#FACC15;font-size:22px;font-weight:bold;letter-spacing:1px;">UMOJA EXCHANGE</div>
        <div style="color:#9CA3AF;font-size:13px;margin-top:4px;">Daily Financial Report — {date.strftime('%d %B %Y')}</div>
      </div>
    </div>
    <div style="padding:28px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-radius:8px;overflow:hidden;border:1px solid #E5E7EB;">
        <tr style="background:#0F0F0F;"><td colspan="2" style="padding:10px 16px;color:#FACC15;font-weight:bold;font-size:14px;">📦 Purchases Today</td></tr>
        <tr style="background:#F9FAFB;"><td style="padding:10px 16px;color:#4B5563;">Transactions</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">{p_agg['count'] or 0}</td></tr>
        <tr><td style="padding:10px 16px;color:#4B5563;">Total USDT Purchased</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">{_fmt(p_agg['total_usdt'])} USDT</td></tr>
        <tr style="background:#F9FAFB;"><td style="padding:10px 16px;color:#4B5563;">Total Paid</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">TZS {_fmt(p_agg['total_tzs'])}</td></tr>

        <tr style="background:#0F0F0F;"><td colspan="2" style="padding:10px 16px;color:#FACC15;font-weight:bold;font-size:14px;">💸 Sales Today</td></tr>
        <tr style="background:#F9FAFB;"><td style="padding:10px 16px;color:#4B5563;">Transactions</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">{s_agg['count'] or 0}</td></tr>
        <tr><td style="padding:10px 16px;color:#4B5563;">Total USDT Sold</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">{_fmt(s_agg['total_usdt'])} USDT</td></tr>
        <tr style="background:#F9FAFB;"><td style="padding:10px 16px;color:#4B5563;">Total Revenue</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">TZS {_fmt(s_agg['total_tzs'])}</td></tr>
        <tr><td style="padding:10px 16px;color:#4B5563;">Today's Profit</td><td style="padding:10px 16px;font-weight:bold;color:#16A34A;text-align:right;">TZS {_fmt(s_agg['total_profit'])}</td></tr>

        <tr style="background:#0F0F0F;"><td colspan="2" style="padding:10px 16px;color:#FACC15;font-weight:bold;font-size:14px;">📊 Status</td></tr>
        <tr style="background:#F9FAFB;"><td style="padding:10px 16px;color:#4B5563;">Company Capital</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">TZS {_fmt(capital)}</td></tr>
        <tr><td style="padding:10px 16px;color:#4B5563;">Remaining Inventory</td><td style="padding:10px 16px;font-weight:bold;text-align:right;">{_fmt(remaining)} USDT</td></tr>
        {warning_html}
      </table>
    </div>
    <div style="background:#F9FAFB;padding:16px 32px;text-align:center;color:#9CA3AF;font-size:12px;border-top:1px solid #E5E7EB;">
      Umoja Exchange · Automated Daily Report · {date.strftime('%d %B %Y')}
    </div>
  </div>
</body>
</html>
"""


def send_daily_report(date=None):
    sys = SystemSettings.get()
    if not sys.report_email or not settings.RESEND_API_KEY:
        return False
    resend.api_key = settings.RESEND_API_KEY
    date = date or timezone.localdate()
    html = build_daily_report_html(date)
    try:
        resend.Emails.send({
            "from": settings.FROM_EMAIL,
            "to": [sys.report_email],
            "subject": f"Umoja Exchange Daily Report — {date.strftime('%d %B %Y')}",
            "html": html,
        })
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False


def send_monthly_report():
    from django.utils import timezone
    now = timezone.now()
    # Send report for previous month
    return send_daily_report()
