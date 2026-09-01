from django.shortcuts import render


def report_history(request):
    return render(
        request,
        'reports/history.html'
    )