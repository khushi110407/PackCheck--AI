from django.contrib import admin

from .models import ComplianceCheck


@admin.register(ComplianceCheck)
class ComplianceCheckAdmin(admin.ModelAdmin):

    list_display = (
        'product_name',
        'status',
        'compliance_score',
        'violations_count',
        'checked_at',
    )

    list_filter = (
        'status',
        'checked_at',
    )

    search_fields = (
        'product_name',
        'product_id',
    )

    readonly_fields = (
        'checked_at',
    )