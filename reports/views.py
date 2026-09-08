from django.shortcuts import render

from scanner.models import ProductScan
from .models import ComplianceReport


# =========================================================
# COMPLIANCE REPORT
# =========================================================

def report(request):

    compliance_report = ComplianceReport.objects.order_by(
        '-created_at'
    ).first()

    scan = None
    declarations = {}
    compliance_result = {}
    ocr_text = ''

    if compliance_report:

        scan = ProductScan.objects.filter(
            product_name=compliance_report.product_name,
            category=compliance_report.category
        ).order_by(
            '-scanned_at'
        ).first()

        ocr_text = compliance_report.ocr_text

        declarations = {
            'manufacturer':
                compliance_report.manufacturer,

            'net_quantity':
                compliance_report.net_quantity,

            'mrp':
                compliance_report.mrp,

            'manufacturing_date':
                compliance_report.manufacturing_date,

            'consumer_care':
                compliance_report.consumer_care,
        }

        compliance_result = {
            'score':
                compliance_report.score,

            'status':
                compliance_report.status,

            'violation_count':
                compliance_report.violation_count,

            'violations':
                compliance_report.violations,
        }

    context = {
        'scan': scan,
        'ocr_text': ocr_text,
        'declarations': declarations,
        'compliance_result': compliance_result,
    }

    return render(
        request,
        'reports/report.html',
        context
    )


# =========================================================
# INSPECTION HISTORY
# =========================================================

def history(request):

    reports = ComplianceReport.objects.all().order_by(
        '-created_at'
    )

    history_data = []

    for report in reports:

        history_data.append({
            'id':
                report.id,

            'product_name':
                report.product_name
                or 'Unnamed Product',

            'category':
                report.category
                or 'Not Specified',

            'scanned_at':
                report.created_at,

            'score':
                report.score,

            'status':
                report.status,

            'violation_count':
                report.violation_count,
        })

    context = {
        'scans': history_data,
    }

    return render(
        request,
        'reports/history.html',
        context
    )
