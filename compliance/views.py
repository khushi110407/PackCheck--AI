from django.shortcuts import render, get_object_or_404

from .models import ComplianceCheck


def violations(request):

    checks = ComplianceCheck.objects.filter(
        status='NON_COMPLIANT'
    ).order_by('-checked_at')

    context = {
        'checks': checks,
        'total_violations': checks.count(),
    }

    return render(
        request,
        'compliance/violations.html',
        context
    )


def details(request, pk):

    check = get_object_or_404(
        ComplianceCheck,
        pk=pk
    )

    context = {
        'check': check,
    }

    return render(
        request,
        'compliance/details.html',
        context
    )