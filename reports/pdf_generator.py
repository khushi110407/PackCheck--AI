from io import BytesIO

from django.template.loader import render_to_string

from xhtml2pdf import pisa


def generate_compliance_report(context):
    """
    Generate a PDF compliance report from Django template.
    """

    html = render_to_string(
        "reports/report_pdf.html",
        context
    )

    result = BytesIO()

    pdf = pisa.CreatePDF(
        html,
        dest=result
    )

    if pdf.err:
        return None

    return result.getvalue()