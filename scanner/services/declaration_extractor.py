import re


# =========================================================
# CLEAN VALUE
# =========================================================

def clean_value(value):
    if not value:
        return None

    value = str(value)

    value = value.replace("\n", " ")
    value = value.replace("\r", " ")
    value = value.replace("\t", " ")

    value = re.sub(r"\s+", " ", value)

    value = value.strip(" :-|,.;")

    return value if value else None


# =========================================================
# NORMALIZE OCR TEXT
# =========================================================

def normalize_ocr_text(text):

    if not text:
        return ""

    text = str(text)

    replacements = {
        "M.R.P.": "MRP",
        "M.R.P": "MRP",
        "M R P": "MRP",

        "P.K.D.": "PKD",
        "P.K.D": "PKD",

        "M.F.G.": "MFG",
        "M.F.G": "MFG",

        "M.F.D.": "MFD",
        "M.F.D": "MFD",

        "N.E.T.": "NET",
        "N.E.T": "NET",

        "W.T.": "WT",
        "W.T": "WT",

        "L.O.T.": "LOT",
        "L.O.T": "LOT",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# MANUFACTURER
# =========================================================

def extract_manufacturer(text):

    patterns = [

        r"manufactured\s+(?:for|by)\s*[:\-]?\s*(.{3,120})",

        r"manufactured\s+and\s+packed\s+by\s*[:\-]?\s*(.{3,120})",

        r"manufactured\s+and\s+marketed\s+by\s*[:\-]?\s*(.{3,120})",

        r"mfd\.?\s*(?:by|for)?\s*[:\-]?\s*(.{3,120})",

        r"mfg\.?\s*(?:by|for)?\s*[:\-]?\s*(.{3,120})",

        r"manufacturer\s*[:\-]?\s*(.{3,120})",

        r"packed\s+by\s*[:\-]?\s*(.{3,120})",

        r"packer\s*[:\-]?\s*(.{3,120})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = clean_value(
                match.group(1)
            )

            if value:

                value = re.split(
                    r"\b(?:mrp|net|weight|quantity|pkd|mfd|mfg|use|best|consumer|customer|care|lot|machine|lic)\b",
                    value,
                    flags=re.IGNORECASE
                )[0]

                value = clean_value(value)

                if value:
                    return value

    return None


# =========================================================
# NET QUANTITY
# =========================================================

def extract_net_quantity(text):

    patterns = [

        r"net\s*weight\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(kg|kgs|g|gm|gms|mg|l|ltr|litre|liter|ml)\b",

        r"net\s*quantity\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(kg|kgs|g|gm|gms|mg|l|ltr|litre|liter|ml)\b",

        r"(?:net|wet)\s*(?:weight|wt|quantity)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(kg|kgs|g|gm|gms|mg|l|ltr|litre|liter|ml)\b",

        r"net\s*weight\s*[:\-]?\s*(\d+(?:\.\d+)?)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            groups = match.groups()

            if len(groups) >= 2:

                number = groups[-2]
                unit = groups[-1]

                return f"{number} {unit}"

            if len(groups) == 1:

                return clean_value(
                    groups[0]
                )

    # Fallback:
    # Look around NET WEIGHT

    match = re.search(
        r"net\s+weight.{0,40}?(\d+(?:\.\d+)?)\s*(kg|g|gm|mg|ml|l)\b",
        text,
        re.IGNORECASE
    )

    if match:

        return f"{match.group(1)} {match.group(2)}"

    return None


# =========================================================
# MRP
# =========================================================

def extract_mrp(text):

    patterns = [

        r"\bmrp\b\s*[:\-]?\s*(?:rs\.?|inr)?\s*[₹]?\s*(\d+(?:\.\d+)?)",

        r"maximum\s+retail\s+price\s*[:\-]?\s*(?:rs\.?|inr)?\s*[₹]?\s*(\d+(?:\.\d+)?)",

        r"[₹]\s*(\d+(?:\.\d+)?)",

        r"\brs\.?\s*(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE
        ):

            value = match.group(1)

            try:
                number = float(value)
            except ValueError:
                continue

            start = max(
                0,
                match.start() - 30
            )

            end = min(
                len(text),
                match.end() + 40
            )

            nearby = text[start:end]

            # Ignore nutritional values
            if re.search(
                r"per\s*(?:100\s*g|100g|g|kg|ml|l)",
                nearby,
                re.IGNORECASE
            ):
                continue

            return f"₹{value}"

    # OCR fallback:
    # If "MRP" is nearby, search next number

    match = re.search(
        r"mrp.{0,30}?(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if match:

        return f"₹{match.group(1)}"

    return None


# =========================================================
# MANUFACTURING DATE
# =========================================================

def extract_manufacturing_date(text):

    patterns = [

        r"\bpkd\.?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",

        r"\bpkd\.?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{2,4})",

        r"\bmfg\.?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",

        r"\bmfg\.?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{2,4})",

        r"\bmfd\.?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",

        r"\bmfd\.?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{2,4})",

        r"manufacturing\s+date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",

        r"manufacturing\s+date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{2,4})",
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


# =========================================================
# CONSUMER CARE
# =========================================================

def extract_consumer_care(text):

    patterns = [

        r"consumer\s+care\s*[:\-]?\s*(.{5,100})",

        r"customer\s+care\s*[:\-]?\s*(.{5,100})",

        r"consumer\s+complaint\s*[:\-]?\s*(.{5,100})",

        r"helpline\s*[:\-]?\s*(.{5,100})",

        r"toll\s*free\s*[:\-]?\s*(.{5,100})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = clean_value(
                match.group(1)
            )

            if value:

                value = re.split(
                    r"\b(?:mrp|net|weight|pkd|mfd|mfg|lot|machine|manufactured|packed|lic)\b",
                    value,
                    flags=re.IGNORECASE
                )[0]

                value = clean_value(
                    value
                )

                if value:
                    return value

    # Phone number fallback

    phone_patterns = [

        r"\b1800[\s\-]?\d{3}[\s\-]?\d{4}\b",

        r"\b\d{10}\b",

        r"\b\d{4}[\s\-]\d{3}[\s\-]\d{3}\b",
    ]

    for pattern in phone_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return clean_value(
                match.group(0)
            )

    return None


# =========================================================
# MAIN DECLARATION EXTRACTION
# =========================================================

def extract_declarations(text):

    text = normalize_ocr_text(
        text
    )

    if not text:

        return {
            "manufacturer": None,
            "net_quantity": None,
            "mrp": None,
            "manufacturing_date": None,
            "consumer_care": None,
        }

    manufacturer = extract_manufacturer(
        text
    )

    net_quantity = extract_net_quantity(
        text
    )

    mrp = extract_mrp(
        text
    )

    manufacturing_date = extract_manufacturing_date(
        text
    )

    consumer_care = extract_consumer_care(
        text
    )

    return {

        "manufacturer":
            manufacturer,

        "net_quantity":
            net_quantity,

        "mrp":
            mrp,

        "manufacturing_date":
            manufacturing_date,

        "consumer_care":
            consumer_care,
    }