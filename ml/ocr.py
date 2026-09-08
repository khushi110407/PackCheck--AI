from scanner.services.ocr_engine import extract_text
from .text_classifier import classify_text


def run_ml_ocr(image_path):

    try:

        # OCR engine ને IMAGE PATH જ આપવાનો
        text = extract_text(image_path)

        if not text:
            return {
                "success": False,
                "text": "",
                "classification": {
                    "label": "UNKNOWN",
                    "confidence": 0.0,
                    "detected_keywords": [],
                    "detected_categories": [],
                },
                "preprocessing_success": False,
                "error": "OCR returned empty text",
            }

        # Text classification
        classification = classify_text(text)

        return {
            "success": True,
            "text": text,
            "classification": classification,
            "preprocessing_success": True,
        }

    except Exception as e:

        return {
            "success": False,
            "text": "",
            "classification": {
                "label": "UNKNOWN",
                "confidence": 0.0,
                "detected_keywords": [],
                "detected_categories": [],
            },
            "preprocessing_success": False,
            "error": str(e),
        }