import re


def clean_value(value):
    """
    Clean OCR extracted value.
    """
    if not value:
        return None

    value = str(value).strip()

    # Remove unwanted characters from beginning/end
    value = re.sub(r"^[\s:;,\-]+", "", value)
    value = re.sub(r"[\s:;,\-]+$", "", value)

    # Remove multiple spaces
    value = re.sub(r"\s+", " ", value)

    if len(value) < 2:
        return None

    return value


def normalize_ocr_text(text):
    """
    Normalize common OCR mistakes.
    """
    if not text:
        return ""

    text = str(text)

    # Common OCR substitutions
    replacements = {
        "M.R.P": "MRP",
        "M.R.P.": "MRP",
        "m.r.p": "MRP",
        "m.r.p.": "MRP",

        "N.E.T": "NET",
        "W.T.": "WT",

        "P.K.D": "PKD",
        "P.K.D.": "PKD",

        "U.S.E": "USE",
        "U.S.E.": "USE",

        "L.O.T": "LOT",
        "L.O.T.": "LOT",

        "C.O.D.E": "CODE",
        "C.O.D.E.": "CODE",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def extract_manufacturer(text):
    """
    Detect Manufacturer / Packer / Importer.
    """

    patterns = [
        r"manufactured\s*(?:by|&\s*packed\s*by)\s*[:\-]?\s*(.+)",
        r"manufactured\s*(?:and\s*packed\s*by)\s*[:\-]?\s*(.+)",
        r"manufactured\s*&\s*packed\s*by\s*[:\-]?\s*(.+)",
        r"mfd\.?\s*by\s*[:\-]?\s*(.+)",
        r"mfg\.?\s*by\s*[:\-]?\s*(.+)",
        r"manufacturer\s*[:\-]?\s*(.+)",
        r"packed\s*by\s*[:\-]?\s*(.+)",
        r"packer\s*[:\-]?\s*(.+)",
        r"importer\s*[:\-]?\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            # Stop at next common declaration
            value = re.split(
                r"\b(?:mrp|net\s*(?:weight|quantity)|pkd|mfg|mfd|use\s*by|consumer\s*care|helpline)\b",
                value,
                flags=re.IGNORECASE
            )[0]

            value = clean_value(value)

            if value:
                return value

    return None


def extract_net_quantity(text):
    """
    Detect Net Quantity / Net Weight.
    """

    patterns = [

        # NET WEIGHT 600 g
        r"net\s*(?:weight|wt)\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|kgs|g|gm|gms|mg|l|ltr|litre|liter|ml)",

        # NET QUANTITY 600 g
        r"net\s*(?:quantity|qty)\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|kgs|g|gm|gms|mg|l|ltr|litre|liter|ml)",

        # NET WT 600g
        r"net\s*wt\.?\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|kgs|g|gm|gms|mg|l|ltr|litre|liter|ml)",

        # quantity 600 g
        r"(?:quantity|qty)\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|kgs|g|gm|gms|mg|l|ltr|litre|liter|ml)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            number = match.group(1)
            unit = match.group(2)

            # Standardize units
            unit_map = {
                "kgs": "kg",
                "gm": "g",
                "gms": "g",
                "ltr": "l",
                "litre": "l",
                "liter": "l",
            }

            unit = unit_map.get(
                unit.lower(),
                unit.lower()
            )

            return f"{number} {unit}"

    return None


def extract_mrp(text):
    """
    Detect Maximum Retail Price / MRP.
    """

    patterns = [

        # MRP ₹10
        r"\bmrp\b\s*[:\-]?\s*"
        r"(?:rs\.?|₹|inr)?\s*"
        r"(\d+(?:\.\d+)?)",

        # MRP Rs 10
        r"\bmrp\b\s*[:\-]?\s*"
        r"(?:rs\.?|inr)\s*"
        r"(\d+(?:\.\d+)?)",

        # Maximum Retail Price ₹10
        r"maximum\s*retail\s*price\s*[:\-]?\s*"
        r"(?:rs\.?|₹|inr)?\s*"
        r"(\d+(?:\.\d+)?)",

        # ₹10
        r"₹\s*(\d+(?:\.\d+)?)",

        # Rs. 10
        r"\brs\.?\s*(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            price = match.group(1)

            return f"₹{price}"

    return None


def extract_date(text):
    """
    Detect manufacturing / packing date.

    Handles:
    MFG 07/2026
    MFD 07/2026
    PKD 13/07/26
    PKD 07/2026
    Manufacturing Date 07/2026
    """

    patterns = [

        # MFG / MFD / PKD DD/MM/YYYY
        r"\b(?:mfg|mfd|pkd|packed)\b"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",

        # MFG / MFD / PKD MM/YYYY
        r"\b(?:mfg|mfd|pkd|packed)\b"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{4})",

        # Manufacturing Date
        r"manufacturing\s*date\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",

        # Manufacturing Date MM/YYYY
        r"manufacturing\s*date\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{4})",

        # Month Year
        r"(?:mfg|mfd|manufacturing)\s*[:\-]?\s*"
        r"([A-Za-z]{3,9}\s+\d{4})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return clean_value(
                match.group(1)
            )

    return None


def extract_consumer_care(text):
    """
    Detect Consumer Care / Customer Care / Helpline.
    """

    patterns = [

        r"consumer\s*care\s*[:\-]?\s*(.+)",

        r"customer\s*care\s*[:\-]?\s*(.+)",

        r"consumer\s*complaint\s*[:\-]?\s*(.+)",

        r"helpline\s*[:\-]?\s*(.+)",

        r"toll\s*free\s*[:\-]?\s*(.+)",

        r"contact\s*us\s*[:\-]?\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            # Stop at next declaration
            value = re.split(
                r"\b(?:mrp|net\s*(?:weight|quantity)|pkd|mfg|mfd|manufactured)\b",
                value,
                flags=re.IGNORECASE
            )[0]

            value = clean_value(value)

            if value:
                return value

    return None


def extract_declarations(text):
    """
    Main declaration extraction function.

    Returns:
        manufacturer
        net_quantity
        mrp
        manufacturing_date
        consumer_care
    """

    result = {
        "manufacturer": None,
        "net_quantity": None,
        "mrp": None,
        "manufacturing_date": None,
        "consumer_care": None,
    }

    if not text:
        return result

    # Normalize OCR text
    text = normalize_ocr_text(text)

    # Extract fields
    result["manufacturer"] = extract_manufacturer(
        text
    )

    result["net_quantity"] = extract_net_quantity(
        text
    )

    result["mrp"] = extract_mrp(
        text
    )

    result["manufacturing_date"] = extract_date(
        text
    )

    result["consumer_care"] = extract_consumer_care(
        text
    )

    return result