import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def preprocess_images(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image")

    # Resize
    image = cv2.resize(
        image,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    # Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Otsu threshold
    _, otsu = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return [
        image,
        gray,
        enhanced,
        otsu,
        adaptive
    ]


def clean_text(text):
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if len(line) >= 2:
            lines.append(line)

    return "\n".join(lines)


def score_text(text):
    if not text:
        return 0

    score = 0

    # More readable characters = better
    score += min(len(text), 500)

    # Reward useful product-related words
    keywords = [
        "MRP",
        "Rs",
        "₹",
        "Net",
        "Quantity",
        "Manufactured",
        "Manufactured by",
        "Mfg",
        "Date",
        "Consumer",
        "Care",
        "Customer",
        "g",
        "kg",
        "ml",
        "L"
    ]

    lower_text = text.lower()

    for keyword in keywords:
        if keyword.lower() in lower_text:
            score += 100

    return score


def extract_text(image_path):

    try:
        images = preprocess_images(image_path)

        results = []

        configs = [
            "--oem 3 --psm 6",
            "--oem 3 --psm 11",
            "--oem 3 --psm 12"
        ]

        for image in images:

            for config in configs:

                text = pytesseract.image_to_string(
                    image,
                    config=config,
                    lang="eng"
                )

                text = clean_text(text)

                if text:
                    results.append(text)

        if not results:
            return "No readable text detected."

        # Select best OCR result
        best_text = max(
            results,
            key=score_text
        )

        return best_text

    except Exception as e:
        return f"OCR Error: {str(e)}"