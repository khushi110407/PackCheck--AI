from django.contrib import admin

from .models import ProductScan


@admin.register(ProductScan)
class ProductScanAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product_name',
        'scanned_at',
    )

    search_fields = (
        'product_name',
    )

    list_filter = (
        'scanned_at',
    )