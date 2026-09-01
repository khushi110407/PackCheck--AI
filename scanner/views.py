from django.shortcuts import render, redirect
from .forms import ProductScanForm
from .models import ProductScan


def upload_product(request):

    if request.method == 'POST':

        form = ProductScanForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            scan = form.save()

            return redirect(
                'scanner:result',
                scan_id=scan.id
            )

    else:

        form = ProductScanForm()

    return render(
        request,
        'scanner/upload.html',
        {
            'form': form
        }
    )


def scan_result(request, scan_id):

    try:
        scan = ProductScan.objects.get(
            id=scan_id
        )

    except ProductScan.DoesNotExist:

        return redirect(
            'scanner:upload'
        )

    return render(
        request,
        'scanner/result.html',
        {
            'scan': scan
        }
    )