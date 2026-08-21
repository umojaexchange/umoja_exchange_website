import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit_logs.utils import log_action

from .models import Sale
from .serializers import SaleCreateSerializer, SaleSerializer, execute_fifo_sale, reverse_fifo_sale


class SaleFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="created_at__date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="created_at__date", lookup_expr="lte")
    payment_method = django_filters.CharFilter(field_name="payment_method", lookup_expr="exact")

    class Meta:
        model = Sale
        fields = ["payment_method", "date_from", "date_to"]


class SaleListView(generics.ListAPIView):
    queryset = Sale.objects.select_related("created_by").prefetch_related("sale_lots__inventory_lot").all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SaleFilter
    search_fields = ["customer_name", "notes"]
    ordering_fields = ["created_at", "usdt_amount", "sale_rate_tzs", "profit_tzs"]
    ordering = ["-created_at"]


class SaleCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SaleCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            sale = execute_fifo_sale(
                usdt_amount=serializer.validated_data["usdt_amount"],
                sale_rate=serializer.validated_data["sale_rate_tzs"],
                payment_method=serializer.validated_data["payment_method"],
                customer_name=serializer.validated_data["customer_name"],
                notes=serializer.validated_data.get("notes", ""),
                user=request.user,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        log_action(
            request.user, "CREATE", "sales.Sale", sale.id,
            f"Sale of {sale.usdt_amount} USDT to {sale.customer_name} — Profit: {sale.profit_tzs} TZS",
        )
        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)


class SaleDetailView(generics.RetrieveDestroyAPIView):
    queryset = Sale.objects.select_related("created_by").prefetch_related("sale_lots__inventory_lot").all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        log_action(
            self.request.user, "DELETE", "sales.Sale", instance.id,
            f"Deleted sale #{instance.id} — {instance.usdt_amount} USDT to {instance.customer_name}",
        )
        reverse_fifo_sale(instance)
