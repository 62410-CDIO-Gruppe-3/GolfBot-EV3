import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_red_cross(image_path, show=True):
    """
    Detect the red cross in an image.

    Returns
    -------
    bbox : (x, y, w, h)
        Bounding‑box around the detected cross.
    center : (cx, cy)
        Center of the cross.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # --- Step1: threshold the red regions in HSV space --------------------
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 70, 50])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([160, 70, 50])
    upper2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask  = cv2.bitwise_or(mask1, mask2)

    # small clean‑up – remove isolated pixels
    kernel = np.ones((5, 5), np.uint8)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # --- Step2: connected component analysis -----------------------------
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask, connectivity=8
    )
    h, w = mask.shape
    best_idx, best_score = None, 0

    # filter each component
    for i in range(1, num_labels):          # 0 is background
        x, y, bw, bh, area = stats[i]
        cx, cy = centroids[i]

        # Ignore components that touch the border (they are frame edges)
        pad = 5
        if x <= pad or y <= pad or x + bw >= w - pad or y + bh >= h - pad:
            continue

        # Discard components that are much too small or too large
        if not (0.03 * w < bw < 0.4 * w and 0.03 * h < bh < 0.4 * h):
            continue

        # Prefer square-ish bounding boxes (a plus sign looks square overall)
        aspect_score = 1.0 - abs((bw / float(bh)) - 1.0)

        # Prefer components near the image centre
        centre_score = 1.0 / (np.hypot(cx - w / 2, cy - h / 2) + 1)

        score = 2 * aspect_score + centre_score
        if score > best_score:
            best_score, best_idx = score, i

    if best_idx is None:
        raise RuntimeError("Red cross not found")

    x, y, bw, bh, _ = stats[best_idx]
    cx, cy          = centroids[best_idx]

    if show:
        out = img.copy()
        cv2.rectangle(out, (x, y), (x + bw, y + bh), (0, 255, 0), 4)
        cv2.drawMarker(out, (int(cx), int(cy)), (255, 0, 0),
                       cv2.MARKER_CROSS, 30, 3)

        plt.figure(figsize=(6, 8))
        plt.imshow(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        plt.title("Detected red cross")
        plt.axis("off")
        plt.show()

    return (int(x), int(y), int(bw), int(bh)), (int(cx), int(cy))

# --- demo on the provided image -------------------------------------------
bbox, centre = detect_red_cross("/mnt/data/test_image0.jpg")
print("Bounding‐box:", bbox)
print("Center:", centre)