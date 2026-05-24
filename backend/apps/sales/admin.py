from django.contrib import admin
from .models import Sale, SaleLot

class SaleLotInline(admin.TabularInline):
    model = SaleLot
    extra = 0
    readonly_fields = ["inventory_lot","usdt_consumed","buy_rate"]
    can_delete = False

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["id","customer_name","usdt_amount","sale_rate_tzs","profit_tzs","payment_method","created_at"]
    list_filter = ["payment_method","created_at"]
    search_fields = ["customer_name"]
    readonly_fields = ["paid_amount_tzs","avg_buy_rate","profit_margin","profit_tzs","created_at","updated_at"]
    inlines = [SaleLotInline]
