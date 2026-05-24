from django.urls import path
from .views import dashboard_summary, dashboard_charts
urlpatterns = [
    path("summary/", dashboard_summary, name="dashboard-summary"),
    path("charts/", dashboard_charts, name="dashboard-charts"),
]
