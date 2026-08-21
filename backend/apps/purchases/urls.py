from django.urls import path

from .views import PurchaseDetailView, PurchaseListCreateView, inventory_summary

urlpatterns = [
    path("", PurchaseListCreateView.as_view(), name="purchase-list"),
    path("<int:pk>/", PurchaseDetailView.as_view(), name="purchase-detail"),
    path("inventory/", inventory_summary, name="inventory-summary"),
]
