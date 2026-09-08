from scanner.services.ocr_engine import extract_text

def run_ocr(image_path):
    text = extract_text(image_path)

    return {
        "text": text,
        "success": bool(
            text and not text.startswith("OCR Error")
        )
    }