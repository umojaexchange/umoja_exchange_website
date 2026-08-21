from django.contrib import admin

from .models import InventoryLot, Purchase


class InventoryLotInline(admin.TabularInline):
    model = InventoryLot
    extra = 0
    readonly_fields = ["usdt_amount","remaining","rate_tzs","created_at"]
    can_delete = False

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ["id","supplier_name","usdt_amount","rate_tzs","amount_paid_tzs","payment_method","created_at"]
    list_filter = ["payment_method","created_at"]
    search_fields = ["supplier_name"]
    readonly_fields = ["amount_paid_tzs","created_at","updated_at"]
    inlines = [InventoryLotInline]

@admin.register(InventoryLot)
class InventoryLotAdmin(admin.ModelAdmin):
    list_display = ["id","purchase","usdt_amount","remaining","rate_tzs","created_at"]
    readonly_fields = ["purchase","usdt_amount","rate_tzs","created_at"]
