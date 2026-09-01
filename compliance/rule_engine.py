from .rules import get_all_rules


def check_compliance(extracted_text):
    """
    Check mandatory declarations in extracted OCR text.
    """

    text = extracted_text.lower()

    results = []

    found_count = 0

    for rule in get_all_rules():

        code = rule['code']

        found = False

        if code == 'MANUFACTURER_DETAILS':

            keywords = [
                'manufactured by',
                'manufactured',
                'packed by',
                'imported by',
                'manufacturer',
                'packer',
                'importer',
            ]

            found = any(
                keyword in text
                for keyword in keywords
            )

        elif code == 'NET_QUANTITY':

            keywords = [
                'net quantity',
                'net wt',
                'net weight',
                'quantity',
            ]

            found = any(
                keyword in text
                for keyword in keywords
            )

        elif code == 'MRP':

            keywords = [
                'mrp',
                'maximum retail price',
                'retail price',
            ]

            found = any(
                keyword in text
                for keyword in keywords
            )

        elif code == 'PACKING_DATE':

            keywords = [
                'month',
                'year',
                'mfg',
                'mfd',
                'manufacturing date',
                'packed on',
                'date of packing',
            ]

            found = any(
                keyword in text
                for keyword in keywords
            )

        elif code == 'CONSUMER_CARE':

            keywords = [
                'consumer care',
                'customer care',
                'helpline',
                'toll free',
                'contact us',
            ]

            found = any(
                keyword in text
                for keyword in keywords
            )

        if found:
            found_count += 1

        results.append({
            'code': code,
            'name': rule['name'],
            'description': rule['description'],
            'found': found,
            'status': 'PASS' if found else 'FAIL',
        })

    total_rules = len(get_all_rules())

    score = (
        (found_count / total_rules) * 100
        if total_rules
        else 0
    )

    return {
        'results': results,
        'score': round(score, 2),
        'found_count': found_count,
        'total_rules': total_rules,
        'compliant': found_count == total_rules,
    }