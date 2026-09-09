import os
import shutil
import cv2
import pytesseract
import re
from difflib import SequenceMatcher


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

def configure_tesseract():
    """
    Configure Tesseract OCR for both Windows and Linux/Render.

    Priority:
    1. TESSERACT_CMD environment variable
    2. System-installed Tesseract
    3. Windows default installation path
    """

    # -----------------------------------------------------
    # 1. Environment variable
    # -----------------------------------------------------

    env_path = os.getenv("TESSERACT_CMD")

    if env_path and os.path.exists(env_path):
        pytesseract.pytesseract.tesseract_cmd = env_path
        return env_path

    # -----------------------------------------------------
    # 2. System PATH
    # -----------------------------------------------------

    system_tesseract = shutil.which("tesseract")

    if system_tesseract:
        pytesseract.pytesseract.tesseract_cmd = system_tesseract
        return system_tesseract

    # -----------------------------------------------------
    # 3. Windows default path
    # -----------------------------------------------------

    windows_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in windows_paths:

        if os.path.exists(path):

            pytesseract.pytesseract.tesseract_cmd = path
            return path

    # -----------------------------------------------------
    # No Tesseract found
    # -----------------------------------------------------

    return None


TESSERACT_PATH = configure_tesseract()


# =========================================================
# DECLARATION KEYWORDS
# =========================================================

TARGET_KEYWORDS = [
    "mrp",
    "maximum retail price",
    "net",
    "weight",
    "quantity",
    "pkd",
    "mfg",
    "mfd",
    "manufactured",
    "packed",
    "use by",
    "best before",
    "lot",
    "consumer",
    "customer",
    "care",
    "helpline",
    "toll free",
    "machine code",
]


# =========================================================
# IMAGE RESIZE
# =========================================================

def resize_for_ocr(image):
    """
    Resize image to a suitable OCR size.
    """

    height, width = image.shape[:2]

    target_width = 1800

    if width == 0:
        return image

    if width != target_width:

        scale = target_width / width

        new_width = target_width
        new_height = int(height * scale)

        image = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=(
                cv2.INTER_CUBIC
                if width < target_width
                else cv2.INTER_AREA
            )
        )

    return image


# =========================================================
# PREPROCESS IMAGE
# =========================================================

def preprocess_image(image):
    """
    Mild preprocessing.

    Aggressive thresholding is avoided because it was
    producing garbage OCR in the product image.
    """

    image = resize_for_ocr(image)

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    return gray


# =========================================================
# CLEAN OCR
# =========================================================

def clean_text(text):
    """
    Remove obvious empty/noise lines.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"\s+",
            " ",
            line
        )

        if len(line) < 2:
            continue

        if not any(
            char.isalnum()
            for char in line
        ):
            continue

        lines.append(line)

    return "\n".join(lines)


# =========================================================
# NORMALIZE OCR TEXT
# =========================================================

def normalize_text(text):
    """
    Normalize common OCR variations.
    """

    if not text:
        return ""

    replacements = {

        "M.R.P": "MRP",
        "M.R.P.": "MRP",
        "M R P": "MRP",

        "P.K.D": "PKD",
        "P.K.D.": "PKD",

        "M.F.G": "MFG",
        "M.F.G.": "MFG",

        "M.F.D": "MFD",
        "M.F.D.": "MFD",

        "N.E.T": "NET",
        "N.E.T.": "NET",

        "W.T": "WT",
        "W.T.": "WT",

        "L.O.T": "LOT",
        "L.O.T.": "LOT",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    return text


# =========================================================
# KEYWORD MATCH
# =========================================================

def keyword_similarity(word, keyword):
    """
    Fuzzy match useful for OCR errors.
    """

    word = word.lower().strip()
    keyword = keyword.lower().strip()

    if not word or not keyword:
        return 0

    return SequenceMatcher(
        None,
        word,
        keyword
    ).ratio()


# =========================================================
# OCR CONFIDENCE
# =========================================================

def average_confidence(data):
    """
    Calculate average OCR confidence.
    """

    values = []

    for value in data.get(
        "conf",
        []
    ):

        try:

            value = float(value)

        except (
            ValueError,
            TypeError
        ):

            continue

        if value >= 0:
            values.append(value)

    if not values:
        return 0

    return sum(values) / len(values)


# =========================================================
# OCR ONE IMAGE
# =========================================================

def run_basic_ocr(image):
    """
    Run two Tesseract layouts and select the better one.
    """

    processed = preprocess_image(
        image
    )

    configs = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 11",
    ]

    best_text = ""
    best_score = -1

    for config in configs:

        try:

            data = pytesseract.image_to_data(
                processed,
                config=config,
                lang="eng",
                output_type=pytesseract.Output.DICT
            )

            text_parts = []

            for word in data["text"]:

                word = word.strip()

                if word:
                    text_parts.append(word)

            text = " ".join(
                text_parts
            )

            text = clean_text(
                text
            )

            if not text:
                continue

            confidence = average_confidence(
                data
            )

            # Keyword relevance
            lower = text.lower()

            keyword_hits = 0

            for keyword in TARGET_KEYWORDS:

                if keyword in lower:
                    keyword_hits += 1

            digit_count = sum(
                char.isdigit()
                for char in text
            )

            score = (
                confidence * 0.3
                + keyword_hits * 50
                + min(
                    digit_count * 4,
                    40
                )
            )

            if score > best_score:

                best_score = score
                best_text = text

        except Exception:
            continue

    return (
        best_text,
        best_score
    )


# =========================================================
# FIND BEST ORIENTATION
# =========================================================

def find_best_orientation(image):
    """
    Test 4 orientations.

    The orientation with the strongest declaration
    keywords is selected.
    """

    orientations = [

        (
            "original",
            image
        ),

        (
            "clockwise",
            cv2.rotate(
                image,
                cv2.ROTATE_90_CLOCKWISE
            )
        ),

        (
            "counter_clockwise",
            cv2.rotate(
                image,
                cv2.ROTATE_90_COUNTERCLOCKWISE
            )
        ),

        (
            "180",
            cv2.rotate(
                image,
                cv2.ROTATE_180
            )
        ),
    ]

    best_image = image
    best_text = ""
    best_score = -1

    for name, candidate in orientations:

        text, score = run_basic_ocr(
            candidate
        )

        if not text:
            continue

        if score > best_score:

            best_score = score
            best_text = text
            best_image = candidate

    return (
        best_image,
        best_text,
        best_score
    )


# =========================================================
# FIND TARGET REGIONS
# =========================================================

def find_target_regions(image):
    """
    Locate declaration keywords using Tesseract
    bounding boxes.

    Returns crop coordinates around useful keywords.
    """

    processed = preprocess_image(
        image
    )

    try:

        data = pytesseract.image_to_data(
            processed,
            config="--oem 3 --psm 11",
            lang="eng",
            output_type=pytesseract.Output.DICT
        )

    except Exception:
        return []

    height, width = processed.shape[:2]

    regions = []

    for i, word in enumerate(
        data["text"]
    ):

        word = word.strip()

        if not word:
            continue

        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])

        if w <= 0 or h <= 0:
            continue

        # -----------------------------------------
        # Find closest target keyword
        # -----------------------------------------

        matched_keyword = None
        matched_score = 0

        for keyword in TARGET_KEYWORDS:

            similarity = keyword_similarity(
                word,
                keyword
            )

            if similarity > matched_score:

                matched_score = similarity
                matched_keyword = keyword

        # Exact / strong fuzzy match
        if matched_score < 0.70:
            continue

        # -----------------------------------------
        # Large surrounding crop
        # -----------------------------------------

        pad_x = 450

        pad_y = 120

        x1 = max(
            0,
            x - pad_x
        )

        y1 = max(
            0,
            y - pad_y
        )

        x2 = min(
            width,
            x + w + pad_x
        )

        y2 = min(
            height,
            y + h + pad_y
        )

        regions.append(
            (
                matched_keyword,
                x1,
                y1,
                x2,
                y2
            )
        )

    # Remove duplicate/overlapping regions

    unique_regions = []

    for region in regions:

        keyword, x1, y1, x2, y2 = region

        duplicate = False

        for old in unique_regions:

            _, ox1, oy1, ox2, oy2 = old

            overlap_x = max(
                0,
                min(x2, ox2)
                - max(x1, ox1)
            )

            overlap_y = max(
                0,
                min(y2, oy2)
                - max(y1, oy1)
            )

            overlap_area = (
                overlap_x * overlap_y
            )

            current_area = (
                (x2 - x1)
                * (y2 - y1)
            )

            if current_area > 0:

                overlap_ratio = (
                    overlap_area
                    / current_area
                )

                if overlap_ratio > 0.50:

                    duplicate = True
                    break

        if not duplicate:

            unique_regions.append(
                region
            )

    return unique_regions


# =========================================================
# OCR TARGET REGION
# =========================================================

def ocr_region(
    image,
    x1,
    y1,
    x2,
    y2
):
    """
    OCR a targeted declaration region.
    """

    crop = image[
        y1:y2,
        x1:x2
    ]

    if crop.size == 0:
        return ""

    crop = preprocess_image(
        crop
    )

    # Slightly improve local contrast

    crop = cv2.normalize(
        crop,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    results = []

    configs = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 11",
    ]

    for config in configs:

        try:

            text = pytesseract.image_to_string(
                crop,
                config=config,
                lang="eng"
            )

            text = clean_text(
                text
            )

            if text:

                results.append(
                    text
                )

        except Exception:
            continue

    if not results:
        return ""

    # Prefer longest useful result

    return max(
        results,
        key=len
    )


# =========================================================
# TARGETED DECLARATION OCR
# =========================================================

def targeted_declaration_ocr(image):
    """
    Search the image for declaration keywords and
    OCR their surrounding regions.
    """

    regions = find_target_regions(
        image
    )

    if not regions:
        return ""

    results = []

    for (
        keyword,
        x1,
        y1,
        x2,
        y2
    ) in regions:

        try:

            text = ocr_region(
                image,
                x1,
                y1,
                x2,
                y2
            )

            if not text:
                continue

            results.append(
                f"[{keyword.upper()} REGION]\n{text}"
            )

        except Exception:
            continue

    if not results:
        return ""

    return "\n".join(
        results
    )


# =========================================================
# MERGE OCR RESULTS
# =========================================================

def merge_ocr_text(
    full_text,
    targeted_text
):
    """
    Combine full-image OCR and targeted OCR.

    Full OCR preserves general label information.
    Targeted OCR improves declaration extraction.
    """

    full_text = normalize_text(
        full_text
    )

    targeted_text = normalize_text(
        targeted_text
    )

    if not full_text and not targeted_text:
        return ""

    if not targeted_text:
        return full_text

    if not full_text:
        return targeted_text

    # Avoid exact duplicate blocks

    if targeted_text in full_text:
        return full_text

    return (
        full_text
        + "\n\n"
        + "===== TARGETED DECLARATION OCR =====\n"
        + targeted_text
    )


# =========================================================
# MAIN FUNCTION
# =========================================================

def extract_text(image_path):
    """
    Main PackCheck AI OCR pipeline.

    Pipeline:

        Product Image
             ↓
        Orientation Detection
             ↓
        Best Orientation
             ↓
        Full Image OCR
             ↓
        Declaration Keyword Detection
             ↓
        Targeted Region Cropping
             ↓
        Targeted OCR
             ↓
        Combined OCR Text
    """

    try:

        # -----------------------------------------
        # Check Tesseract
        # -----------------------------------------

        if not TESSERACT_PATH:

            raise RuntimeError(
                "Tesseract OCR is not installed or could not be found."
            )

        # -----------------------------------------
        # Read image
        # -----------------------------------------

        original = cv2.imread(
            image_path
        )

        if original is None:

            raise ValueError(
                "Unable to read image"
            )

        # -----------------------------------------
        # Find best orientation
        # -----------------------------------------

        (
            best_image,
            full_text,
            orientation_score
        ) = find_best_orientation(
            original
        )

        # -----------------------------------------
        # Targeted OCR
        # -----------------------------------------

        targeted_text = (
            targeted_declaration_ocr(
                best_image
            )
        )

        # -----------------------------------------
        # Merge
        # -----------------------------------------

        final_text = merge_ocr_text(
            full_text,
            targeted_text
        )

        # -----------------------------------------
        # Final clean
        # -----------------------------------------

        final_text = clean_text(
            final_text
        )

        if not final_text:

            return (
                "No readable text detected."
            )

        return final_text

    except Exception as e:

        return (
            f"OCR Error: {str(e)}"
        )