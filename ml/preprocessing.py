import cv2


# =========================================================
# IMAGE RESIZE
# =========================================================

def resize_image(image, target_width=1800):
    """
    Resize image to an OCR-friendly width.
    """

    if image is None:
        return None

    height, width = image.shape[:2]

    if width == 0:
        return image

    if width == target_width:
        return image

    scale = target_width / width

    new_width = target_width
    new_height = int(height * scale)

    interpolation = (
        cv2.INTER_CUBIC
        if width < target_width
        else cv2.INTER_AREA
    )

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=interpolation
    )


# =========================================================
# GRAYSCALE
# =========================================================

def convert_to_grayscale(image):
    """
    Convert BGR image to grayscale.
    """

    if image is None:
        return None

    if len(image.shape) == 2:
        return image

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


# =========================================================
# CONTRAST ENHANCEMENT
# =========================================================

def enhance_contrast(gray_image):
    """
    Improve text visibility using CLAHE.
    """

    if gray_image is None:
        return None

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    return clahe.apply(gray_image)


# =========================================================
# NOISE REMOVAL
# =========================================================

def remove_noise(gray_image):
    """
    Remove small image noise while preserving text.
    """

    if gray_image is None:
        return None

    return cv2.GaussianBlur(
        gray_image,
        (3, 3),
        0
    )


# =========================================================
# SHARPEN IMAGE
# =========================================================

def sharpen_image(gray_image):
    """
    Sharpen text edges for better OCR.
    """

    if gray_image is None:
        return None

    kernel = (
        3
        * cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 3)
        )
    )

    sharpened = cv2.addWeighted(
        gray_image,
        1.5,
        cv2.filter2D(
            gray_image,
            -1,
            kernel
        ),
        -0.5,
        0
    )

    return sharpened


# =========================================================
# ADAPTIVE THRESHOLD
# =========================================================

def apply_threshold(gray_image):
    """
    Convert image into high-contrast black/white form.
    """

    if gray_image is None:
        return None

    thresholded = cv2.adaptiveThreshold(
        gray_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return thresholded


# =========================================================
# MORPHOLOGICAL CLEANING
# =========================================================

def morphological_cleanup(image):
    """
    Clean small gaps/noise around characters.
    """

    if image is None:
        return None

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2, 2)
    )

    return cv2.morphologyEx(
        image,
        cv2.MORPH_CLOSE,
        kernel
    )


# =========================================================
# MAIN OCR PREPROCESSING
# =========================================================

def preprocess_for_ocr(
    image,
    target_width=1800
):
    """
    Complete preprocessing pipeline.

    Image
      ↓
    Resize
      ↓
    Grayscale
      ↓
    Contrast Enhancement
      ↓
    Noise Removal
      ↓
    Sharpening
      ↓
    Threshold
      ↓
    Morphological Cleanup
    """

    if image is None:
        return None

    # 1. Resize
    image = resize_image(
        image,
        target_width
    )

    # 2. Grayscale
    gray = convert_to_grayscale(
        image
    )

    # 3. Contrast enhancement
    enhanced = enhance_contrast(
        gray
    )

    # 4. Noise removal
    denoised = remove_noise(
        enhanced
    )

    # 5. Sharpen
    sharpened = sharpen_image(
        denoised
    )

    # 6. Threshold
    thresholded = apply_threshold(
        sharpened
    )

    # 7. Morphological cleanup
    cleaned = morphological_cleanup(
        thresholded
    )

    return cleaned


# =========================================================
# SIMPLE PREPROCESSING
# =========================================================

def basic_preprocess(image):
    """
    Lightweight preprocessing for faster OCR.
    """

    if image is None:
        return None

    image = resize_image(image)

    gray = convert_to_grayscale(
        image
    )

    gray = enhance_contrast(
        gray
    )

    gray = remove_noise(
        gray
    )

    return gray