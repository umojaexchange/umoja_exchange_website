import django_filters
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit_logs.utils import log_action

from .models import InventoryLot, Purchase
from .serializers import PurchaseSerializer


class PurchaseFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="created_at__date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="created_at__date", lookup_expr="lte")
    payment_method = django_filters.CharFilter(field_name="payment_method", lookup_expr="exact")

    class Meta:
        model = Purchase
        fields = ["payment_method", "date_from", "date_to"]


class PurchaseListCreateView(generics.ListCreateAPIView):
    queryset = Purchase.objects.select_related("created_by", "inventory_lot").all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PurchaseFilter
    search_fields = ["supplier_name", "notes"]
    ordering_fields = ["created_at", "usdt_amount", "rate_tzs", "amount_paid_tzs"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        purchase = serializer.save(created_by=self.request.user)
        log_action(
            self.request.user, "CREATE", "purchases.Purchase", purchase.id,
            f"Purchase of {purchase.usdt_amount} USDT @ {purchase.rate_tzs} TZS from {purchase.supplier_name}",
        )


class PurchaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Purchase.objects.select_related("created_by", "inventory_lot").all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        purchase = serializer.save()
        # Update the linked inventory lot rate if purchase rate changed
        try:
            lot = purchase.inventory_lot
            lot.rate_tzs = purchase.rate_tzs
            lot.save()
        except Exception:
            pass
        log_action(
            self.request.user, "UPDATE", "purchases.Purchase", purchase.id,
            f"Updated purchase #{purchase.id}",
        )

    def perform_destroy(self, instance):
        # Prevent deletion if lots have been partially consumed
        try:
            lot = instance.inventory_lot
            if lot.remaining < lot.usdt_amount:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Cannot delete purchase: some USDT has already been sold (FIFO).")
        except InventoryLot.DoesNotExist:
            pass
        log_action(
            self.request.user, "DELETE", "purchases.Purchase", instance.id,
            f"Deleted purchase #{instance.id} from {instance.supplier_name}",
        )
        instance.delete()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inventory_summary(request):
    """Returns total available USDT inventory."""
    total = InventoryLot.objects.filter(remaining__gt=0).aggregate(
        total_usdt=Sum("remaining"),
        total_lots=Sum("id"),
    )
    return Response({
        "total_available_usdt": total["total_usdt"] or 0,
        "active_lots": InventoryLot.objects.filter(remaining__gt=0).count(),
    })
