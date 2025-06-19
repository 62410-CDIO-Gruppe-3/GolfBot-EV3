"""
Robust pose‑tracker for the LEGO EV3 robot with magenta & purple discs.
---------------------------------------------------------------------
* Uses HSV segmentation + geometric sanity checks
* Keeps state between frames (ROI search window + learned disc distance)
* Resistant against glare/ shadows/ the red arena rails

API
---
get_robot_pose(frame_bgr, debug=False) -> ((cx, cy), heading_deg)
                                             or
                                         ((cx, cy), heading_deg, overlay_img)

 * heading 0 ° points to the right, positive clockwise (OpenCV image coords).
 * If either disc is not visible, the function returns **None**.

Drop the file into your project and do:

    from robot_tracker import get_robot_pose
    pose = get_robot_pose(frame)

If you want to re‑initialise (e.g. after a long cut in the video), call
`reset_tracker()`.
"""

from __future__ import annotations

import cv2
import numpy as np
from math import atan2, degrees, hypot
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# --- COLOUR MASKS -----------------------------------------------------------
#   Magenta disc: narrow hue window (155–179) – excludes the red arena rails
#   Purple  disc: 110–140, wide S & V so it survives shade and glare
# ---------------------------------------------------------------------------
PINK_HSV = (
    (np.array([155,  60,  60]), np.array([179, 255, 255])),  # magenta only
)
PURPLE_HSV = (
    (np.array([110,  40,  40]), np.array([140, 255, 255])),  # violet / purple
)

# ---------------------------------------------------------------------------
# --- GEOMETRIC FILTERS ------------------------------------------------------
MIN_AREA   = 40           # ignore speckles < this many px²
MAX_AREA   = 3000         # ignore blobs bigger than a marker (e.g. arena rail)
MIN_CIRC   = 0.40         # 4πA / P², 1.0 is a perfect circle
ROI_RADIUS = 100          # search window half‑size once we have a track
RESET_AFTER_MISSES = 15   # frames without a hit → full‑frame search again

# ---------------------------------------------------------------------------
# --- INTERNAL STATEFUL TRACKER ---------------------------------------------
class _RobotTracker:
    """Tracks the two discs and estimates robot pose frame‑by‑frame."""

    def __init__(self):
        self._expected_d: Optional[float] = None   # learnt disc distance (px)
        self._centroid:   Optional[Tuple[int, int]] = None  # last robot centre
        self._missed: int = 0                      # frames since last hit

    # -------------------------------- utility ------------------------------
    @staticmethod
    def _colour_mask(hsv: np.ndarray, ranges) -> np.ndarray:
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lo, hi in ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))
        return mask

    @staticmethod
    def _find_markers(mask: np.ndarray):
        """Return (x, y, area) for blobs that look like our circular stickers."""
        good = []
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            area = cv2.contourArea(c)
            if area < MIN_AREA or area > MAX_AREA:
                continue
            peri = cv2.arcLength(c, True)
            circ = 4 * np.pi * area / (peri * peri) if peri else 0
            if circ < MIN_CIRC:
                continue
            m = cv2.moments(c)
            good.append((int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]), area))
        return good

    def _roi_slices(self, shape):
        if self._centroid is None:
            return None  # whole frame
        x, y = self._centroid
        h, w = shape[:2]
        r = ROI_RADIUS
        return (slice(max(0, y - r), min(h, y + r)),
                slice(max(0, x - r), min(w, x + r)))

    def _register_miss(self):
        self._missed += 1
        if self._missed > RESET_AFTER_MISSES:
            self._centroid = None  # reset ROI search

    # -------------------------------- main update --------------------------
    def update(self, frame_bgr: np.ndarray, debug=False):
        """Return pose or None; with *debug=True* also returns an overlay img."""
        roi = self._roi_slices(frame_bgr.shape)
        crop = frame_bgr[roi] if roi else frame_bgr

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        pink_m   = cv2.morphologyEx(self._colour_mask(hsv, PINK_HSV),   cv2.MORPH_OPEN, kernel)
        purple_m = cv2.morphologyEx(self._colour_mask(hsv, PURPLE_HSV), cv2.MORPH_OPEN, kernel)

        pinks  = self._find_markers(pink_m)
        purps  = self._find_markers(purple_m)
        if not pinks or not purps:
            self._register_miss()
            return None

        # ---------- choose the best magenta–purple pair --------------------
        exp = self._expected_d or (0.125 * frame_bgr.shape[1])  # 1/8 of width
        best, best_score = None, 1e9
        for (px, py, _), (ux, uy, _) in [(p, u) for p in pinks for u in purps]:
            d = hypot(px - ux, py - uy)
            if not (0.6 * exp <= d <= 1.4 * exp):
                continue
            score = abs(d - exp)
            if score < best_score:
                best_score, best = score, ((px, py), (ux, uy), d)

        if best is None:
            self._register_miss()
            return None

        (fx, fy), (bx, by), d = best
        cx, cy = (fx + bx) // 2, (fy + by) // 2
        heading = degrees(atan2(fy - by, fx - bx))  # +ve = clockwise

        # --- promote ROI coords to full‑frame ------------------------------
        offx = roi[1].start if roi else 0
        offy = roi[0].start if roi else 0
        self._centroid = (cx + offx, cy + offy)
        self._missed   = 0
        self._expected_d = 0.8 * self._expected_d + 0.2 * d if self._expected_d else d

        if not debug:
            return (self._centroid, heading)

        dbg = frame_bgr.copy()
        cv2.circle(dbg, (fx + offx, fy + offy), 8, (  0,   0, 255), -1)  # red front
        cv2.circle(dbg, (bx + offx, by + offy), 8, (255,   0,   0), -1)  # blue back
        cv2.line  (dbg, (bx + offx, by + offy), (fx + offx, fy + offy), (  0, 255,   0), 2)
        cv2.circle(dbg,  self._centroid,          6, (  0, 255, 255), -1)  # yellow centre
        return (self._centroid, heading, dbg)

# ---------------------------------------------------------------------------
# --- PUBLIC CONVENIENCE WRAPPER -------------------------------------------
_tracker = _RobotTracker()

def get_robot_pose(frame_bgr: np.ndarray, debug: bool = False):
    """Stateless façade around the internal tracker (see module docstring)."""
    return _tracker.update(frame_bgr, debug)


def reset_tracker():
    """Forget any previously remembered state (ROI, learned disc distance)."""
    global _tracker
    _tracker = _RobotTracker()