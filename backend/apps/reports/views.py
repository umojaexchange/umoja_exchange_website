from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .generators import generate_pdf_report, generate_excel_report
from apps.purchases.models import Purchase
from apps.sales.models import Sale
from apps.audit_logs.utils import log_action

def _filter_qs(qs, request):
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    return qs, date_from, date_to

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_pdf(request):
    report_type = request.query_params.get("type", "purchases")
    qs = Purchase.objects.all() if report_type == "purchases" else Sale.objects.all()
    qs, date_from, date_to = _filter_qs(qs, request)
    buf = generate_pdf_report(report_type, qs, date_from, date_to)
    log_action(request.user, "EXPORT", f"{report_type}.PDF", None, f"Exported {report_type} PDF report")
    resp = HttpResponse(buf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="umoja_{report_type}_report.pdf"'
    return resp

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_excel(request):
    report_type = request.query_params.get("type", "purchases")
    qs = Purchase.objects.all() if report_type == "purchases" else Sale.objects.all()
    qs, date_from, date_to = _filter_qs(qs, request)
    buf = generate_excel_report(report_type, qs, date_from, date_to)
    log_action(request.user, "EXPORT", f"{report_type}.Excel", None, f"Exported {report_type} Excel report")
    resp = HttpResponse(buf, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="umoja_{report_type}_report.xlsx"'
    return resp
