from django.shortcuts import render, redirect

from .forms import ProductScanForm
from .models import ProductScan

from .ml.ocr import run_ocr
from .services.declaration_extractor import extract_declarations

from compliance.rule_engine import run_rule_engine


# =========================================================
# UPLOAD PRODUCT
# =========================================================

def upload_product(request):

    if request.method == 'POST':

        form = ProductScanForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product_name = request.POST.get(
                'product_name',
                ''
            )

            category = request.POST.get(
                'category',
                ''
            )

            product_image = form.cleaned_data[
                'product_image'
            ]

            # Save product scan
            scan = ProductScan.objects.create(
                product_name=product_name,
                category=category,
                product_image=product_image
            )

            # Image path
            image_path = scan.product_image.path

            # =================================================
            # OCR
            # =================================================

            ocr_result = run_ocr(image_path)

            ocr_text = ocr_result["text"]

            ocr_success = ocr_result["success"]


            # =================================================
            # DECLARATION EXTRACTION
            # =================================================

            declarations = extract_declarations(
                ocr_text
            )


            # =================================================
            # COMPLIANCE RULE ENGINE
            # =================================================

            compliance_result = run_rule_engine(
                declarations
            )


            # =================================================
            # SAVE RESULT IN SESSION
            # =================================================

            request.session[
                f'ocr_text_{scan.id}'
            ] = ocr_text

            request.session[
                f'ocr_success_{scan.id}'
            ] = ocr_success

            request.session[
                f'declarations_{scan.id}'
            ] = declarations

            request.session[
                f'compliance_{scan.id}'
            ] = compliance_result


            # Go to result page
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
            'scanner:upload'
        )


    # Get OCR result
    ocr_text = request.session.get(
        f'ocr_text_{scan.id}',
        ''
    )


    ocr_success = request.session.get(
        f'ocr_success_{scan.id}',
        False
    )


    # Get declarations
    declarations = request.session.get(
        f'declarations_{scan.id}',
        {}
    )


    # Get compliance result
    compliance_result = request.session.get(
        f'compliance_{scan.id}',
        {}
    )


    context = {

        'scan': scan,

        'ocr_text': ocr_text,

        'ocr_success': ocr_success,

        'declarations': declarations,

        'compliance_result': compliance_result,

    }


    return render(
        request,
        'scanner/result.html',
        context
    )


# =========================================================
# SCAN HISTORY
# =========================================================

def scan_history(request):

    # Get all scans
    scans = ProductScan.objects.all().order_by(
        '-scanned_at'
    )


    history_data = []


    for scan in scans:

        # Get compliance result from session
        compliance_result = request.session.get(
            f'compliance_{scan.id}',
            {}
        )


        # Score
        score = compliance_result.get(
            'score',
            0
        )


        # Status
        status = compliance_result.get(
            'status',
            'Analysis Pending'
        )


        # Violation count
        violation_count = compliance_result.get(
            'violation_count',
            0
        )


        history_data.append({

            'id': scan.id,

            'product_name':
                scan.product_name
                or 'Unnamed Product',

            'category':
                scan.category
                or 'Not Specified',

            'scanned_at':
                scan.scanned_at,

            'score':
                score,

            'status':
                status,

            'violation_count':
                violation_count,

        })


    # Send data to reports/history.html
    return render(
        request,
        'reports/history.html',
        {
            'scans': history_data
        }
    )