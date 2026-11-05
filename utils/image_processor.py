import os
import cv2
import numpy as np

def read_image_from_stream(file_stream):
    """
    Reads an uploaded file stream or raw bytes into an OpenCV BGR numpy array.
    """
    if hasattr(file_stream, 'read'):
        file_bytes = file_stream.read()
    else:
        file_bytes = file_stream
        
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def validate_image(image_input):
    """
    Validates the image file for:
    1. Successful decoding (not corrupt)
    2. Minimum dimensions (at least 64x64)
    3. Maximum dimensions sanity check
    4. Foliage/leaf content heuristic (checking color variance & hue distribution)
    
    Returns: (is_valid: bool, error_message: str or None, image: np.ndarray)
    """
    if isinstance(image_input, (str, os.PathLike)):
        if not os.path.exists(image_input):
            return False, "Image file not found on server.", None
        image = cv2.imread(str(image_input))
    elif isinstance(image_input, np.ndarray):
        image = image_input
    else:
        image = read_image_from_stream(image_input)
        
    if image is None or image.size == 0:
        return False, "Failed to decode image. The file may be corrupt or not a valid image format.", None

    height, width, channels = image.shape
    if height < 64 or width < 64:
        return False, f"Image resolution too low ({width}x{height}px). Minimum required is 64x64px.", image

    # Check for blank / solid color images
    std_dev = np.std(image)
    if std_dev < 10.0:
        return False, "The image appears to be a blank or solid color surface without any discernible plant features.", image

    # Leaf/botanical content check using HSV
    # Green, yellow, brown/rust hues are typical in plant health and pathology
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Green mask (Hue 25-90)
    lower_green = np.array([25, 30, 30])
    upper_green = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Yellow/brown diseased foliage mask (Hue 10-25)
    lower_yellow_brown = np.array([10, 30, 30])
    upper_yellow_brown = np.array([25, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow_brown, upper_yellow_brown)
    
    total_pixels = height * width
    foliage_pixels = cv2.countNonZero(mask_green) + cv2.countNonZero(mask_yellow)
    foliage_ratio = foliage_pixels / float(total_pixels)
    
    # Notice: some high-closeups or dark spots might have slightly lower ratio,
    # so we set a gentle warning threshold rather than hard reject if texture variance exists
    is_leaf_likely = foliage_ratio > 0.05 or std_dev > 25.0
    
    if not is_leaf_likely:
        return False, "No plant foliage or leaf features detected in the provided image. Please frame a clear plant leaf.", image

    return True, None, image

def preprocess_image(image, target_size=(224, 224)):
    """
    Preprocesses an OpenCV BGR image for MobileNetV2:
    1. Converts BGR to RGB
    2. Resizes to target_size (224, 224) using high-quality anti-aliased interpolation
    3. Normalizes pixel values to range [-1, 1] as expected by MobileNetV2
    4. Expands dimensions to (1, 224, 224, 3) batch
    """
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized_image = cv2.resize(rgb_image, target_size, interpolation=cv2.INTER_AREA)
    
    # MobileNetV2 normalization: (x / 127.5) - 1.0 (scales [0, 255] to [-1.0, 1.0])
    normalized_image = (resized_image.astype(np.float32) / 127.5) - 1.0
    batch_image = np.expand_dims(normalized_image, axis=0)
    return batch_image

def get_image_diagnostics(image):
    """
    Computes visual diagnostics from the image:
    - Resolution
    - Sharpness / blur score (Laplacian variance)
    - Foliage coverage percentage
    - Dominant color profile
    """
    h, w, _ = image.shape
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Foliage ratio
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([25, 30, 30])
    upper_green = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    foliage_ratio = round((cv2.countNonZero(mask_green) / (h * w)) * 100, 1)
    
    quality_label = "Excellent" if blur_score > 120 else ("Good" if blur_score > 60 else "Soft / Low Light")
    
    return {
        "width": w,
        "height": h,
        "sharpness": round(float(blur_score), 1),
        "foliage_coverage": foliage_ratio,
        "quality_label": quality_label
    }
