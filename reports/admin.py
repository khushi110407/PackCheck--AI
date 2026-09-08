from django.contrib import admin

from .models import ComplianceReport


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product_name",
        "category",
        "score",
        "status",
        "violation_count",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
        "created_at",
    )

    search_fields = (
        "product_name",
        "category",
        "manufacturer",
        "mrp",
        "net_quantity",
    )

    ordering = (
        "-created_at",
    )