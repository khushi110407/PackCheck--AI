import re


# =========================================================
# TEXT CLASSIFIER
# =========================================================

def classify_text(text):
    """
    Classify OCR extracted text.

    This lightweight classifier checks for packaged
    commodity related declarations and returns:
    - label
    - confidence
    - detected keywords
    """

    if not text:
        return {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "detected_keywords": [],
        }

    text = str(text).lower()

    # -----------------------------------------------------
    # Important packaged commodity keywords
    # -----------------------------------------------------

    keyword_patterns = {
        "mrp": [
            r"\bmrp\b",
            r"maximum\s+retail\s+price",
        ],

        "net_quantity": [
            r"\bnet\s+weight\b",
            r"\bnet\s+quantity\b",
            r"\bnet\s+wt\b",
            r"\bnet\b",
        ],

        "manufacturer": [
            r"\bmanufactured\s+by\b",
            r"\bmanufactured\s+and\s+packed\s+by\b",
            r"\bmfd\.?\s+by\b",
            r"\bmfg\.?\s+by\b",
            r"\bmanufacturer\b",
            r"\bpacked\s+by\b",
            r"\bpacker\b",
            r"\bimporter\b",
        ],

        "date": [
            r"\bpkd\b",
            r"\bmfg\b",
            r"\bmfd\b",
            r"\bmanufacturing\s+date\b",
            r"\buse\s+by\b",
            r"\bbest\s+before\b",
        ],

        "consumer_care": [
            r"\bconsumer\s+care\b",
            r"\bcustomer\s+care\b",
            r"\bhelpline\b",
            r"\btoll\s+free\b",
            r"\bcontact\s+us\b",
        ],

        "lot": [
            r"\blot\b",
            r"\blot\s+no\b",
            r"\bbatch\b",
            r"\bbatch\s+no\b",
        ],
    }


    # -----------------------------------------------------
    # Detect keywords
    # -----------------------------------------------------

    detected_keywords = []

    detected_categories = []

    for category, patterns in keyword_patterns.items():

        found = False

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                found = True
                break

        if found:

            detected_categories.append(
                category
            )

            detected_keywords.append(
                category
            )


    # -----------------------------------------------------
    # Additional signals
    # -----------------------------------------------------

    has_price = bool(
        re.search(
            r"(₹|rs\.?|inr)\s*\d+(?:\.\d+)?",
            text,
            re.IGNORECASE
        )
    )

    has_quantity = bool(
        re.search(
            r"\d+(?:\.\d+)?\s*"
            r"(kg|kgs|g|gm|gms|mg|l|ltr|"
            r"litre|liter|ml)\b",
            text,
            re.IGNORECASE
        )
    )

    has_date = bool(
        re.search(
            r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
            text
        )
    )


    # -----------------------------------------------------
    # Calculate confidence
    # -----------------------------------------------------

    score = 0

    # Strong indicators
    if "mrp" in detected_categories:
        score += 25

    if "net_quantity" in detected_categories:
        score += 20

    if "manufacturer" in detected_categories:
        score += 20

    if "date" in detected_categories:
        score += 15

    if "consumer_care" in detected_categories:
        score += 10

    if "lot" in detected_categories:
        score += 5

    if has_price:
        score += 3

    if has_quantity:
        score += 1

    if has_date:
        score += 1


    # Maximum confidence
    confidence = min(
        score / 100,
        0.99
    )


    # -----------------------------------------------------
    # Classification
    # -----------------------------------------------------

    if score >= 40:

        label = "PACKAGED_COMMODITY"

    elif score >= 15:

        label = "POSSIBLE_PACKAGED_COMMODITY"

    else:

        label = "UNKNOWN"


    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {

        "label":
            label,

        "confidence":
            round(
                confidence,
                2
            ),

        "detected_keywords":
            detected_keywords,

        "detected_categories":
            detected_categories,

    }