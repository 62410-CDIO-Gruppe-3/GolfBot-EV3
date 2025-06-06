import cv2
import numpy as np

def detect_arrows(image, arrow_template):
    result = cv2.matchTemplate(image, arrow_template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    loc = np.where(result >= threshold)
    arrow_points = list(zip(*loc[::-1]))
    return arrow_points

def detect_arrow_tip(image, arrow_template):
    """
    Detects arrows in the image using template matching and returns the tip position of the first detected arrow.
    Args:
        image (np.ndarray): Input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
    Returns:
        tuple: (x, y) coordinates of the arrow tip in the image, or None if not found.
    """
    # Convert image to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Template matching
    result = cv2.matchTemplate(gray, arrow_template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None  # No arrow found

    # The top-left corner of the matched region
    top_left = max_loc
    h, w = arrow_template.shape

    # Assume the tip is at the "front" of the template (e.g., rightmost point)
    # You may need to adjust this depending on your template orientation
    tip_offset = (w - 1, h // 2)
    tip_x = top_left[0] + tip_offset[0]
    tip_y = top_left[1] + tip_offset[1]

    return (tip_x, tip_y)