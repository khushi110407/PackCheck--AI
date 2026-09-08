from django.urls import path

from . import views


app_name = "reports"


urlpatterns = [

    # Latest report
    path(
        "report/",
        views.report,
        name="report"
    ),

    # Specific report
    path(
        "report/<int:report_id>/",
        views.report_detail,
        name="report_detail"
    ),

    # Latest PDF
    path(
        "download-pdf/",
        views.download_pdf,
        name="download_pdf"
    ),

    # Specific PDF
    path(
        "download-pdf/<int:report_id>/",
        views.download_pdf,
        name="download_pdf_specific"
    ),

    # Inspection History
    path(
        "history/",
        views.history,
        name="history"
    ),

]