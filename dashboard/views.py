from django.shortcuts import render

from scanner.models import ProductScan


def dashboard(request):

    # Get all scans
    scans = ProductScan.objects.all().order_by("-scanned_at")

    total_scans = scans.count()

    compliant = 0
    review_required = 0
    violations = 0

    recent_scans = []

    for scan in scans:

        compliance_result = request.session.get(
            f"compliance_{scan.id}",
            {}
        )

        status = compliance_result.get(
            "status",
            "Analysis Pending"
        )

        score = compliance_result.get(
            "score",
            0
        )

        violation_count = compliance_result.get(
            "violation_count",
            0
        )

        # Count compliant products
        if status == "Compliant":
            compliant += 1

        # Count products requiring review
        elif status == "Partially Compliant":
            review_required += 1

        # Total violations
        violations += violation_count

        # Recent scans
        recent_scans.append({
            "id": scan.id,
            "product_name": scan.product_name or "Unnamed Product",
            "category": scan.category or "Not Specified",
            "scanned_at": scan.scanned_at,
            "score": score,
            "status": status,
            "violation_count": violation_count,
        })

    # Compliance percentage
    if total_scans > 0:
        compliance_percentage = round(
            (compliant / total_scans) * 100
        )
    else:
        compliance_percentage = 0

    context = {
        "total_scans": total_scans,
        "compliant": compliant,
        "review_required": review_required,
        "violations": violations,
        "compliance_percentage": compliance_percentage,
        "recent_scans": recent_scans[:5],
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )
