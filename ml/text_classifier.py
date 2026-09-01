def classify_text(text):
    """
    Basic text classification.
    """

    if not text:
        return {
            'label': 'UNKNOWN',
            'confidence': 0
        }

    text = text.lower()

    if 'mrp' in text:
        label = 'PACKAGED_COMMODITY'
        confidence = 0.90
    else:
        label = 'UNKNOWN'
        confidence = 0.50

    return {
        'label': label,
        'confidence': confidence
    }