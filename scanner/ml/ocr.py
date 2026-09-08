from scanner.services.ocr_engine import extract_text

from ml.preprocessing import preprocess_for_ocr
from ml.text_classifier import classify_text


# =========================================================
# ML + OCR PIPELINE
# =========================================================

def run_ml_ocr(image_path):
    """
    AI-assisted OCR pipeline.

    Image
        ↓
    Image Preprocessing
        ↓
    OCR Engine
        ↓
    Text Classification
        ↓
    Final Result
    """

    try:

        # =====================================================
        # STEP 1: IMAGE PREPROCESSING
        # =====================================================

        processed_image = preprocess_for_ocr(
            image_path
        )

        preprocessing_success = (
            processed_image is not None
        )

        # =====================================================
        # STEP 2: OCR
        # =====================================================

        text = extract_text(
            image_path
        )

        # Make sure text is always a string
        if text is None:
            text = ""

        text = str(text).strip()

        # =====================================================
        # OCR FAILED
        # =====================================================

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

                "preprocessing_success":
                    preprocessing_success,
            }

        # =====================================================
        # STEP 3: TEXT CLASSIFICATION
        # =====================================================

        classification = classify_text(
            text
        )

        # Safety fallback
        if not classification:

            classification = {
                "label": "UNKNOWN",
                "confidence": 0.0,
                "detected_keywords": [],
                "detected_categories": [],
            }

        # =====================================================
        # STEP 4: FINAL RESULT
        # =====================================================

        return {

            "success": True,

            "text": text,

            "classification": classification,

            "preprocessing_success":
                preprocessing_success,

        }

    # =========================================================
    # ERROR HANDLING
    # =========================================================

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