from django.urls import path

from .views import SaleCreateView, SaleDetailView, SaleListView

urlpatterns = [
    path("", SaleListView.as_view(), name="sale-list"),
    path("create/", SaleCreateView.as_view(), name="sale-create"),
    path("<int:pk>/", SaleDetailView.as_view(), name="sale-detail"),
]
