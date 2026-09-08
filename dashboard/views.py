from django.shortcuts import render

from scanner.models import ProductScan


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):

    # ---------------------------------------------------------
    # Get all product scans
    # ---------------------------------------------------------

    scans = ProductScan.objects.all().order_by(
        "-scanned_at"
    )

    # ---------------------------------------------------------
    # Basic Statistics
    # ---------------------------------------------------------

    total_scans = scans.count()

    compliant = 0
    partially_compliant = 0
    non_compliant = 0
    review_required = 0

    total_violations = 0

    # ---------------------------------------------------------
    # ML Statistics
    # ---------------------------------------------------------

    packaged_products = 0
    possible_packaged_products = 0
    unknown_products = 0

    ml_confidence_total = 0
    ml_confidence_count = 0

    # ---------------------------------------------------------
    # Recent Scans
    # ---------------------------------------------------------

    recent_scans = []

    # =========================================================
    # PROCESS SCANS
    # =========================================================

    for scan in scans:

        # -----------------------------------------------------
        # Compliance Result
        # -----------------------------------------------------

        compliance_result = request.session.get(
            f"compliance_{scan.id}",
            {}
        )

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

        # -----------------------------------------------------
        # Count Compliance Status
        # -----------------------------------------------------

        if status == "Compliant":

            compliant += 1

        elif status == "Partially Compliant":

            partially_compliant += 1
            review_required += 1

        elif status == "Non-Compliant":

            non_compliant += 1

        else:

            review_required += 1

        # -----------------------------------------------------
        # Total Violations
        # -----------------------------------------------------

        total_violations += violation_count

        # =====================================================
        # ML CLASSIFICATION
        # =====================================================

        ml_classification = request.session.get(
            f"ml_classification_{scan.id}",
            {}
        )

        ml_label = ml_classification.get(
            "label",
            "UNKNOWN"
        )

        ml_confidence = ml_classification.get(
            "confidence",
            0
        )

        # -----------------------------------------------------
        # ML Label Statistics
        # -----------------------------------------------------

        if ml_label == "PACKAGED_COMMODITY":

            packaged_products += 1

        elif ml_label == "POSSIBLE_PACKAGED_COMMODITY":

            possible_packaged_products += 1

        else:

            unknown_products += 1

        # -----------------------------------------------------
        # ML Confidence
        # -----------------------------------------------------

        try:

            ml_confidence = float(
                ml_confidence
            )

            ml_confidence_total += (
                ml_confidence
            )

            ml_confidence_count += 1

        except (
            TypeError,
            ValueError
        ):

            pass

        # =====================================================
        # RECENT SCAN DATA
        # =====================================================

        recent_scans.append({

            "id": scan.id,

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

            "ml_label":
                ml_label,

            "ml_confidence":
                ml_confidence,

        })

    # =========================================================
    # COMPLIANCE PERCENTAGE
    # =========================================================

    if total_scans > 0:

        compliance_percentage = round(
            (compliant / total_scans) * 100
        )

    else:

        compliance_percentage = 0

    # =========================================================
    # AVERAGE ML CONFIDENCE
    # =========================================================

    if ml_confidence_count > 0:

        average_ml_confidence = round(
            (
                ml_confidence_total
                / ml_confidence_count
            ) * 100
        )

    else:

        average_ml_confidence = 0

    # =========================================================
    # ML DETECTION PERCENTAGE
    # =========================================================

    if total_scans > 0:

        packaged_detection_percentage = round(
            (
                packaged_products
                / total_scans
            ) * 100
        )

    else:

        packaged_detection_percentage = 0

    # =========================================================
    # DASHBOARD CONTEXT
    # =========================================================

    context = {

        # -----------------------------------------------------
        # Basic Dashboard Statistics
        # -----------------------------------------------------

        "total_scans":
            total_scans,

        "compliant":
            compliant,

        "partially_compliant":
            partially_compliant,

        "non_compliant":
            non_compliant,

        "review_required":
            review_required,

        "violations":
            total_violations,

        "compliance_percentage":
            compliance_percentage,

        # -----------------------------------------------------
        # ML Statistics
        # -----------------------------------------------------

        "packaged_products":
            packaged_products,

        "possible_packaged_products":
            possible_packaged_products,

        "unknown_products":
            unknown_products,

        "average_ml_confidence":
            average_ml_confidence,

        "packaged_detection_percentage":
            packaged_detection_percentage,

        # -----------------------------------------------------
        # Recent Scans
        # -----------------------------------------------------

        "recent_scans":
            recent_scans[:5],

    }

    # =========================================================
    # RENDER DASHBOARD
    # =========================================================

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )
