from django.urls import path
from .views import SaleListView, SaleCreateView, SaleDetailView
urlpatterns = [
    path("", SaleListView.as_view(), name="sale-list"),
    path("create/", SaleCreateView.as_view(), name="sale-create"),
    path("<int:pk>/", SaleDetailView.as_view(), name="sale-detail"),
]
