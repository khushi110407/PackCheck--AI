from django.shortcuts import render, redirect

from .forms import ProductScanForm
from .models import ProductScan
from .ml.ocr import run_ocr


def upload_product(request):
    if request.method == 'POST':
        form = ProductScanForm(request.POST, request.FILES)

        if form.is_valid():
            product_name = request.POST.get('product_name', '')
            category = request.POST.get('category', '')
            product_image = form.cleaned_data['product_image']

            # Save product scan
            scan = ProductScan.objects.create(
                product_name=product_name,
                category=category,
                product_image=product_image
            )

            # Run OCR on uploaded image
            image_path = scan.product_image.path
            ocr_result = run_ocr(image_path)

            # Store OCR text temporarily in session
            request.session[f'ocr_text_{scan.id}'] = ocr_result['text']
            request.session[f'ocr_success_{scan.id}'] = ocr_result['success']

            return redirect('scanner:result', scan_id=scan.id)

    else:
        form = ProductScanForm()

    return render(
        request,
        'scanner/upload.html',
        {'form': form}
    )


def scan_result(request, scan_id):
    try:
        scan = ProductScan.objects.get(id=scan_id)
    except ProductScan.DoesNotExist:
        return redirect('scanner:upload')

    ocr_text = request.session.get(
        f'ocr_text_{scan.id}',
        ''
    )

    ocr_success = request.session.get(
        f'ocr_success_{scan.id}',
        False
    )

    context = {
        'scan': scan,
        'ocr_text': ocr_text,
        'ocr_success': ocr_success,
    }

    return render(
        request,
        'scanner/result.html',
        context
    )


def scan_history(request):
    scans = ProductScan.objects.all().order_by('-scanned_at')

    return render(
        request,
        'scanner/history.html',
        {'scans': scans}
    )