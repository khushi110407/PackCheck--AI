from django.shortcuts import render

from scanner.models import ProductScan


def violations(request):

    scan = ProductScan.objects.order_by(
        '-scanned_at'
    ).first()

    compliance_result = {}

    if scan:
        compliance_result = request.session.get(
            f'compliance_{scan.id}',
            {}
        )

    violations_list = compliance_result.get(
        'violations',
        []
    )

    score = compliance_result.get(
        'score',
        0
    )

    status = compliance_result.get(
        'status',
        'Analysis Pending'
    )

    context = {
        'scan': scan,
        'violations': violations_list,
        'total_violations': len(violations_list),
        'score': score,
        'status': status,
    }

    return render(
        request,
        'compliance/violations.html',
        context
    )