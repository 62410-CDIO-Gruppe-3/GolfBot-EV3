import cv2
import numpy as np
import json
import os

from math import atan2, degrees, hypot

# --- CONFIGURATION ---
CALIB_FILE = os.path.join(os.path.dirname(__file__), "marker_hsv.json")
VIDEO_SRC = 1  # Change to 1 if your camera is on index 1

# --- MARKER FILTERS ---
MIN_AREA = 40
MAX_AREA = 3000
MIN_CIRC = 0.40

def load_hsv_ranges():
    """Return ((pink_lo, pink_hi),), ((purple_lo, purple_hi),) tuples."""
    if os.path.isfile(CALIB_FILE):
        try:
            with open(CALIB_FILE, "r", encoding="utf8") as f:
                data = json.load(f)
            pink_lo = np.asarray(data["pink"]["lo"], dtype=np.uint8)
            pink_hi = np.asarray(data["pink"]["hi"], dtype=np.uint8)
            purp_lo = np.asarray(data["purple"]["lo"], dtype=np.uint8)
            purp_hi = np.asarray(data["purple"]["hi"], dtype=np.uint8)
            return ((pink_lo, pink_hi),), ((purp_lo, purp_hi),)
        except Exception as e:
            print("[debug_marker_detection] WARNING: could not load HSV calibration:", e)
    # fallback values
    _DEFAULT_PINK_HSV = ((np.array([155, 60, 60]), np.array([179, 255, 255])),)
    _DEFAULT_PURPLE_HSV = ((np.array([110, 40, 40]), np.array([140, 255, 255])),)
    return _DEFAULT_PINK_HSV, _DEFAULT_PURPLE_HSV

PINK_HSV, PURPLE_HSV = load_hsv_ranges()

def colour_mask(hsv: np.ndarray, ranges):
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in ranges:
        mask |= cv2.inRange(hsv, lo, hi)
    return mask

def find_markers_with_reasons(mask: np.ndarray):
    """Return (passed, failed) where:
       - passed: list of (x, y, area)
       - failed: list of dicts with keys: reason, area, circ, (x, y)
    """
    passed = []
    failed = []
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        area = cv2.contourArea(c)
        if area < MIN_AREA:
            failed.append({"reason": "area too small", "area": area})
            continue
        if area > MAX_AREA:
            failed.append({"reason": "area too large", "area": area})
            continue
        peri = cv2.arcLength(c, True)
        circ = 4 * np.pi * area / (peri * peri) if peri else 0
        if circ < MIN_CIRC:
            failed.append({"reason": "not circular", "area": area, "circ": circ})
            continue
        m = cv2.moments(c)
        if m["m00"] == 0:
            failed.append({"reason": "zero moment", "area": area})
            continue
        x = int(m["m10"] / m["m00"])
        y = int(m["m01"] / m["m00"])
        passed.append((x, y, area))
    return passed, failed

def main():
    cap = cv2.VideoCapture(VIDEO_SRC)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():
        print("Could not open video source", VIDEO_SRC)
        return

    print("Press Q to quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame.")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        pink_mask = cv2.morphologyEx(colour_mask(hsv, PINK_HSV), cv2.MORPH_OPEN, kernel)
        purple_mask = cv2.morphologyEx(colour_mask(hsv, PURPLE_HSV), cv2.MORPH_OPEN, kernel)

        pinks, pinks_failed = find_markers_with_reasons(pink_mask)
        purples, purples_failed = find_markers_with_reasons(purple_mask)

        print("\n--- Frame ---")
        print(f"Pink markers found: {len(pinks)}")
        for i, (x, y, area) in enumerate(pinks):
            print(f"  Pink {i}: (x={x}, y={y}), area={area:.1f}")
        if pinks_failed:
            print("  Pink candidates failed:")
            for fail in pinks_failed:
                print("   ", fail)

        print(f"Purple markers found: {len(purples)}")
        for i, (x, y, area) in enumerate(purples):
            print(f"  Purple {i}: (x={x}, y={y}), area={area:.1f}")
        if purples_failed:
            print("  Purple candidates failed:")
            for fail in purples_failed:
                print("   ", fail)

        # Draw for visualization
        vis = frame.copy()
        for (x, y, area) in pinks:
            cv2.circle(vis, (x, y), 8, (0, 0, 255), 2)
        for (x, y, area) in purples:
            cv2.circle(vis, (x, y), 8, (255, 0, 0), 2)
        cv2.imshow("Markers", vis)

        if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q')):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()