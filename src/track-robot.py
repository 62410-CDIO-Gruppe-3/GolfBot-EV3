# robot_tracker.py
import cv2
import numpy as np
from math import atan2, degrees

# --- tune only if you change the stickers or the lighting --------------------
# HSV ranges were calibrated on the two photos you sent
PINK_LOWER   = np.array([160,  80, 100], dtype=np.uint8)   # magenta / hot-pink
PINK_UPPER   = np.array([179, 255, 255], dtype=np.uint8)

PURPLE_LOWER = np.array([105,  80,  60], dtype=np.uint8)   # blue-violet
PURPLE_UPPER = np.array([140, 255, 255], dtype=np.uint8)
# -----------------------------------------------------------------------------


def _largest_blob_center(mask: np.ndarray) -> tuple[int, int] | None:
    """Return the centroid (x, y) of the largest contour in *mask*."""
    conts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not conts:
        return None
    c = max(conts, key=cv2.contourArea)
    if cv2.contourArea(c) < 50:         # ignore tiny specks
        return None
    m = cv2.moments(c)
    return (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))


def get_robot_pose(frame_bgr: np.ndarray,
                   debug: bool = False
                   ) -> tuple[tuple[int, int], float] | None:
    """
    Detect the robot in *frame_bgr* and return:

        ((cx, cy), heading_deg)

    * (cx, cy)  – midpoint between the two coloured markers (robot centre)
    * heading   – angle in degrees: 0° = right, 90° = down in image coordinates

    If either disc is missing the function returns **None**.

    Set *debug=True* to get a copy of the frame with the detections drawn on it
    (very handy for live tuning).
    """
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    # build masks and clean them up
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    mask_pink   = cv2.morphologyEx(cv2.inRange(hsv, PINK_LOWER,   PINK_UPPER),
                                   cv2.MORPH_OPEN, kernel)
    mask_purple = cv2.morphologyEx(cv2.inRange(hsv, PURPLE_LOWER, PURPLE_UPPER),
                                   cv2.MORPH_OPEN, kernel)

    front = _largest_blob_center(mask_pink)
    back  = _largest_blob_center(mask_purple)
    if front is None or back is None:
        return None                      # one (or both) markers not found

    # centre of the robot and heading vector
    cx, cy = (front[0] + back[0]) // 2, (front[1] + back[1]) // 2
    dx, dy = front[0] - back[0], front[1] - back[1]
    heading_deg = degrees(atan2(dy, dx))  # positive CW, OpenCV image coords

    if debug:
        dbg = frame_bgr.copy()
        cv2.circle(dbg, front, 8, (0, 0, 255), -1)     # red   – front disc
        cv2.circle(dbg, back,  8, (255, 0, 0), -1)     # blue  – back disc
        cv2.line(dbg, back, front, (0, 255, 0), 2)     # green – heading
        cv2.circle(dbg, (cx, cy), 6, (0, 255, 255), -1)  # yellow – centre
        return ((cx, cy), heading_deg, dbg)

    return ((cx, cy), heading_deg)
