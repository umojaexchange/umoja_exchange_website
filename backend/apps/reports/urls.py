from django.urls import path
from .views import export_pdf, export_excel
urlpatterns = [
    path("export/pdf/", export_pdf, name="export-pdf"),
    path("export/excel/", export_excel, name="export-excel"),
]
