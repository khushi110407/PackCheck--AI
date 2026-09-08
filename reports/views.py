from django.shortcuts import render
from django.http import HttpResponse, Http404

from .models import ComplianceReport
from .pdf_generator import generate_compliance_report


def report(request):
    """
    Open the latest compliance report.
    """
    compliance_report = (
        ComplianceReport.objects
        .order_by("-created_at")
        .first()
    )

    if not compliance_report:
        return render(
            request,
            "reports/report.html",
            {
                "report": None,
                "ocr_text": "",
                "declarations": {},
                "compliance_result": {},
            }
        )

    context = {
        "report": compliance_report,
        "ocr_text": compliance_report.ocr_text,
        "declarations": {
            "manufacturer": compliance_report.manufacturer,
            "net_quantity": compliance_report.net_quantity,
            "mrp": compliance_report.mrp,
            "manufacturing_date": compliance_report.manufacturing_date,
            "consumer_care": compliance_report.consumer_care,
        },
        "compliance_result": {
            "score": compliance_report.score,
            "status": compliance_report.status,
            "violation_count": compliance_report.violation_count,
            "violations": compliance_report.violations,
        },
    }

    return render(
        request,
        "reports/report.html",
        context
    )


def report_detail(request, report_id):
    """
    Open a specific compliance report.
    """

    compliance_report = (
        ComplianceReport.objects
        .filter(id=report_id)
        .first()
    )

    if not compliance_report:
        raise Http404("Compliance report not found.")

    context = {
        "report": compliance_report,
        "ocr_text": compliance_report.ocr_text,
        "declarations": {
            "manufacturer": compliance_report.manufacturer,
            "net_quantity": compliance_report.net_quantity,
            "mrp": compliance_report.mrp,
            "manufacturing_date": compliance_report.manufacturing_date,
            "consumer_care": compliance_report.consumer_care,
        },
        "compliance_result": {
            "score": compliance_report.score,
            "status": compliance_report.status,
            "violation_count": compliance_report.violation_count,
            "violations": compliance_report.violations,
        },
    }

    return render(
        request,
        "reports/report.html",
        context
    )


def download_pdf(request, report_id=None):
    """
    Download PDF for a specific report.
    If report_id is not provided, download latest report.
    """

    if report_id:
        compliance_report = (
            ComplianceReport.objects
            .filter(id=report_id)
            .first()
        )
    else:
        compliance_report = (
            ComplianceReport.objects
            .order_by("-created_at")
            .first()
        )

    if not compliance_report:
        return HttpResponse(
            "No compliance report available.",
            status=404
        )

    context = {
        "report": compliance_report
    }

    pdf = generate_compliance_report(context)

    if not pdf:
        return HttpResponse(
            "PDF generation failed.",
            status=500
        )

    response = HttpResponse(
        pdf,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        "attachment; "
        f"filename=PackCheck_Report_{compliance_report.id}.pdf"
    )

    return response


def history(request):
    """
    Display all compliance reports.
    """

    reports = (
        ComplianceReport.objects
        .all()
        .order_by("-created_at")
    )

    history_data = []

    for compliance_report in reports:

        history_data.append({
            "id": compliance_report.id,
            "product_name": (
                compliance_report.product_name
                or "Unnamed Product"
            ),
            "category": (
                compliance_report.category
                or "Not Specified"
            ),
            "scanned_at": compliance_report.created_at,
            "score": compliance_report.score,
            "status": compliance_report.status,
            "violation_count": (
                compliance_report.violation_count
            ),
            "classification": (
                compliance_report.ml_label
            ),
            "classification_confidence": (
                compliance_report.ml_confidence
            ),
        })

    return render(
        request,
        "reports/history.html",
        {
            "scans": history_data
        }
    )