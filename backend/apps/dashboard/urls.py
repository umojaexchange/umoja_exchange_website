from django.urls import path

from .views import dashboard_charts, dashboard_summary

urlpatterns = [
    path("summary/", dashboard_summary, name="dashboard-summary"),
    path("charts/", dashboard_charts, name="dashboard-charts"),
]
