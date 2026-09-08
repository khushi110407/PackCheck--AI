from django.shortcuts import render, redirect

from .forms import ProductScanForm
from .models import ProductScan

from ml.ocr import run_ml_ocr

from .services.declaration_extractor import extract_declarations

from compliance.rule_engine import run_rule_engine

from reports.models import ComplianceReport


# =========================================================
# UPLOAD PRODUCT
# =========================================================

def upload_product(request):

    if request.method == "POST":

        form = ProductScanForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product_name = request.POST.get(
                "product_name",
                ""
            ).strip()

            category = request.POST.get(
                "category",
                ""
            ).strip()

            product_image = form.cleaned_data[
                "product_image"
            ]

            # -------------------------------------------------
            # SAVE PRODUCT SCAN
            # -------------------------------------------------

            scan = ProductScan.objects.create(
                product_name=product_name,
                category=category,
                product_image=product_image
            )

            image_path = scan.product_image.path

            # -------------------------------------------------
            # ML + OCR
            # -------------------------------------------------

            ml_result = run_ml_ocr(
                image_path
            )

            ocr_text = ml_result.get(
                "text",
                ""
            )

            ocr_success = ml_result.get(
                "success",
                False
            )

            classification = ml_result.get(
                "classification",
                {
                    "label": "UNKNOWN",
                    "confidence": 0.0,
                    "detected_keywords": [],
                    "detected_categories": []
                }
            )

            # -------------------------------------------------
            # DECLARATION EXTRACTION
            # -------------------------------------------------

            declarations = extract_declarations(
                ocr_text
            )

            # Make sure all expected keys exist
            declarations = {
                "manufacturer": declarations.get(
                    "manufacturer"
                ) or "",

                "net_quantity": declarations.get(
                    "net_quantity"
                ) or "",

                "mrp": declarations.get(
                    "mrp"
                ) or "",

                "manufacturing_date": declarations.get(
                    "manufacturing_date"
                ) or "",

                "consumer_care": declarations.get(
                    "consumer_care"
                ) or "",
            }

            # -------------------------------------------------
            # COMPLIANCE RULE ENGINE
            # -------------------------------------------------

            compliance_result = run_rule_engine(
                declarations
            )

            compliance_result["classification"] = (
                classification
            )

            # -------------------------------------------------
            # COMPLIANCE DATA
            # -------------------------------------------------

            score = compliance_result.get(
                "score",
                0
            )

            status = compliance_result.get(
                "status",
                "Analysis Pending"
            )

            violation_count = compliance_result.get(
                "violation_count",
                0
            )

            violations = compliance_result.get(
                "violations",
                []
            )

            # -------------------------------------------------
            # ML DATA
            # -------------------------------------------------

            ml_label = classification.get(
                "label",
                "UNKNOWN"
            )

            ml_confidence = classification.get(
                "confidence",
                0.0
            )

            detected_keywords = classification.get(
                "detected_keywords",
                []
            )

            detected_categories = classification.get(
                "detected_categories",
                []
            )

            # -------------------------------------------------
            # SAVE COMPLETE REPORT
            # -------------------------------------------------

            ComplianceReport.objects.create(

                product_name=product_name,

                category=category,

                ocr_text=ocr_text,

                ocr_success=ocr_success,

                # Declarations
                manufacturer=declarations.get(
                    "manufacturer",
                    ""
                ),

                net_quantity=declarations.get(
                    "net_quantity",
                    ""
                ),

                mrp=declarations.get(
                    "mrp",
                    ""
                ),

                manufacturing_date=declarations.get(
                    "manufacturing_date",
                    ""
                ),

                consumer_care=declarations.get(
                    "consumer_care",
                    ""
                ),

                # AI / ML
                ml_label=ml_label,

                ml_confidence=ml_confidence,

                detected_keywords=detected_keywords,

                detected_categories=detected_categories,

                # Compliance
                score=score,

                status=status,

                violation_count=violation_count,

                violations=violations,
            )

            # -------------------------------------------------
            # SAVE SESSION DATA
            # -------------------------------------------------

            request.session[
                f"ocr_text_{scan.id}"
            ] = ocr_text

            request.session[
                f"ocr_success_{scan.id}"
            ] = ocr_success

            request.session[
                f"declarations_{scan.id}"
            ] = declarations

            request.session[
                f"compliance_{scan.id}"
            ] = compliance_result

            request.session[
                f"ml_classification_{scan.id}"
            ] = classification

            # Make sure session is saved
            request.session.modified = True

            # -------------------------------------------------
            # REDIRECT TO RESULT
            # -------------------------------------------------

            return redirect(
                "scanner:result",
                scan_id=scan.id
            )

    else:

        form = ProductScanForm()

    return render(
        request,
        "scanner/upload.html",
        {
            "form": form
        }
    )


# =========================================================
# SCAN RESULT
# =========================================================

def scan_result(request, scan_id):

    try:

        scan = ProductScan.objects.get(
            id=scan_id
        )

    except ProductScan.DoesNotExist:

        return redirect(
            "scanner:upload"
        )

    # -------------------------------------------------
    # FIRST TRY SESSION DATA
    # -------------------------------------------------

    ocr_text = request.session.get(
        f"ocr_text_{scan.id}",
        ""
    )

    ocr_success = request.session.get(
        f"ocr_success_{scan.id}",
        False
    )

    declarations = request.session.get(
        f"declarations_{scan.id}",
        {}
    )

    compliance_result = request.session.get(
        f"compliance_{scan.id}",
        {}
    )

    ml_classification = request.session.get(
        f"ml_classification_{scan.id}",
        {}
    )

    # -------------------------------------------------
    # NORMALIZE SESSION DATA
    # -------------------------------------------------

    declarations = {
        "manufacturer": declarations.get(
            "manufacturer",
            ""
        ) or "",

        "net_quantity": declarations.get(
            "net_quantity",
            ""
        ) or "",

        "mrp": declarations.get(
            "mrp",
            ""
        ) or "",

        "manufacturing_date": declarations.get(
            "manufacturing_date",
            ""
        ) or "",

        "consumer_care": declarations.get(
            "consumer_care",
            ""
        ) or "",
    }

    # -------------------------------------------------
    # FALLBACK: GET LATEST DATABASE REPORT
    # -------------------------------------------------

    if not any(declarations.values()):

        report = (
            ComplianceReport.objects
            .filter(
                product_name=scan.product_name,
                category=scan.category
            )
            .order_by("-created_at")
            .first()
        )

        if report:

            ocr_text = report.ocr_text or ""

            ocr_success = report.ocr_success

            declarations = {

                "manufacturer":
                    report.manufacturer or "",

                "net_quantity":
                    report.net_quantity or "",

                "mrp":
                    report.mrp or "",

                "manufacturing_date":
                    report.manufacturing_date or "",

                "consumer_care":
                    report.consumer_care or "",
            }

            compliance_result = {

                "score":
                    report.score,

                "status":
                    report.status,

                "violation_count":
                    report.violation_count,

                "violations":
                    report.violations or [],
            }

            ml_classification = {

                "label":
                    report.ml_label or "UNKNOWN",

                "confidence":
                    report.ml_confidence or 0,

                "detected_keywords":
                    report.detected_keywords or [],

                "detected_categories":
                    report.detected_categories or [],
            }

    # -------------------------------------------------
    # FALLBACK COMPLIANCE VALUES
    # -------------------------------------------------

    if not compliance_result:

        compliance_result = {
            "score": 0,
            "status": "Analysis Pending",
            "violation_count": 0,
            "violations": [],
        }

    # -------------------------------------------------
    # FALLBACK ML VALUES
    # -------------------------------------------------

    if not ml_classification:

        ml_classification = {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "detected_keywords": [],
            "detected_categories": [],
        }

    # -------------------------------------------------
    # FINAL CONTEXT
    # -------------------------------------------------

    context = {

        "scan": scan,

        "ocr_text": ocr_text,

        "ocr_success": ocr_success,

        "declarations": declarations,

        "compliance_result": compliance_result,

        "ml_classification": ml_classification,

        "classification_label":
            ml_classification.get(
                "label",
                "UNKNOWN"
            ),

        "classification_confidence":
            ml_classification.get(
                "confidence",
                0
            ),

        "detected_keywords":
            ml_classification.get(
                "detected_keywords",
                []
            ),

        "detected_categories":
            ml_classification.get(
                "detected_categories",
                []
            ),
    }

    return render(
        request,
        "scanner/result.html",
        context
    )


# =========================================================
# SCAN HISTORY
# =========================================================

def scan_history(request):

    scans = ProductScan.objects.all().order_by(
        "-scanned_at"
    )

    history_data = []

    for scan in scans:

        # -------------------------------------------------
        # GET SESSION DATA
        # -------------------------------------------------

        compliance_result = request.session.get(
            f"compliance_{scan.id}",
            {}
        )

        classification = request.session.get(
            f"ml_classification_{scan.id}",
            {}
        )

        # -------------------------------------------------
        # FALLBACK TO DATABASE REPORT
        # -------------------------------------------------

        if not compliance_result or not classification:

            report = (
                ComplianceReport.objects
                .filter(
                    product_name=scan.product_name,
                    category=scan.category
                )
                .order_by("-created_at")
                .first()
            )

            if report:

                if not compliance_result:

                    compliance_result = {

                        "score":
                            report.score,

                        "status":
                            report.status,

                        "violation_count":
                            report.violation_count,

                        "violations":
                            report.violations or [],
                    }

                if not classification:

                    classification = {

                        "label":
                            report.ml_label or "UNKNOWN",

                        "confidence":
                            report.ml_confidence or 0,

                        "detected_keywords":
                            report.detected_keywords or [],

                        "detected_categories":
                            report.detected_categories or [],
                    }

        # -------------------------------------------------
        # COMPLIANCE DATA
        # -------------------------------------------------

        score = compliance_result.get(
            "score",
            0
        )

        status = compliance_result.get(
            "status",
            "Analysis Pending"
        )

        violation_count = compliance_result.get(
            "violation_count",
            0
        )

        # -------------------------------------------------
        # CLASSIFICATION DATA
        # -------------------------------------------------

        classification_label = classification.get(
            "label",
            "UNKNOWN"
        )

        classification_confidence = classification.get(
            "confidence",
            0
        )

        # -------------------------------------------------
        # HISTORY DATA
        # -------------------------------------------------

        history_data.append({

            "id":
                scan.id,

            "product_name":
                scan.product_name
                or "Unnamed Product",

            "category":
                scan.category
                or "Not Specified",

            "scanned_at":
                scan.scanned_at,

            "score":
                score,

            "status":
                status,

            "violation_count":
                violation_count,

            "classification":
                classification_label,

            "classification_confidence":
                classification_confidence,
        })

    return render(
        request,
        "reports/history.html",
        {
            "scans": history_data
        }
    )