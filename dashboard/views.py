from django.shortcuts import render


def dashboard(request):
    context = {
        "total_scans": 0,
        "compliant": 0,
        "review_required": 0,
        "violations": 0,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )
