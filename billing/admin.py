from django.contrib import admin
from billing.models import Product, SalesBill, SalesBillItem
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'available_stocks','price_per_unit','tax_percent','is_active']
    readonly_fields = ['created_at']
    search_fields = ['name']
admin.site.register(Product,ProductAdmin)

class SalesBillAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_email','purchase_date','purchase_no', 'rounded_net_price','cash_received','is_active']
    readonly_fields = ['created_at']
    search_fields = ['customer_email']
admin.site.register(SalesBill,SalesBillAdmin)

class SalesBillItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity','net_price','is_active']
    readonly_fields = ['created_at']
    raw_id_fields = ['product']
admin.site.register(SalesBillItem,SalesBillItemAdmin)
