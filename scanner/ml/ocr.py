from scanner.services.ocr_engine import extract_text


def run_ocr(image_path):
    """
    Run OCR on the uploaded product image.
    """

    text = extract_text(image_path)

    return {
        "text": text,
        "success": bool(
            text and not text.startswith("OCR Error")
        )
    }