
from __future__ import annotations

# -----------------------------------------------------------------------
#  ROBOT TRACKER – v3 (front/back flipped)
#  ---------------------------------------------------------------
#  Purple sticker is now considered the FRONT, pink the BACK.
#
#  Based on track_robot_v3.py (2025‑06‑24)
# -----------------------------------------------------------------------
import cv2
import numpy as np
import json
import os
from math import atan2, degrees, hypot
from typing import Optional, Tuple, List

CALIB_FILE = os.path.join(os.path.dirname(__file__), "marker_hsv.json")

_DEFAULT_PINK_HSV = (
    (np.array([155, 60, 60]), np.array([179, 255, 255])),
    (np.array([  0, 60, 60]), np.array([ 10, 255, 255])),
)
_DEFAULT_PURPLE_HSV = (
    (np.array([110, 40, 40]), np.array([140, 255, 255])),
)

def _load_hsv_ranges():
    if os.path.isfile(CALIB_FILE):
        try:
            with open(CALIB_FILE, "r", encoding="utf8") as f:
                data = json.load(f)

            def parse(col):
                pairs = []
                if "lo" in data[col] and "hi" in data[col]:
                    pairs.append((np.asarray(data[col]["lo"], np.uint8),
                                  np.asarray(data[col]["hi"], np.uint8)))
                if "lo2" in data[col] and "hi2" in data[col]:
                    pairs.append((np.asarray(data[col]["lo2"], np.uint8),
                                  np.asarray(data[col]["hi2"], np.uint8)))
                return tuple(pairs)

            return parse("pink"), parse("purple")
        except Exception as e:
            print("[robot_tracker] WARNING: could not load HSV calibration:", e)
    return _DEFAULT_PINK_HSV, _DEFAULT_PURPLE_HSV

PINK_HSV, PURPLE_HSV = _load_hsv_ranges()

# ------------------- constants -----------------------------------------
MIN_AREA = 40
MAX_AREA = 3000
MIN_CIRC = 0.40
ROI_RADIUS = 100
RESET_AFTER_MISSES = 15

# ------------------- helpers -------------------------------------------
def preprocess_lighting(img_bgr: np.ndarray) -> np.ndarray:
    img = img_bgr.astype(np.float32)
    avg_b, avg_g, avg_r = [c.mean() + 1e-6 for c in cv2.split(img)]
    avg = (avg_b + avg_g + avg_r) / 3.0
    img *= avg / np.array([avg_b, avg_g, avg_r])
    img = np.clip(img, 0, 255).astype(np.uint8)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_eq = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((l_eq, a, b)), cv2.COLOR_LAB2BGR)

# ------------------- tracker class -------------------------------------
class _RobotTracker:
    def __init__(self):
        self._expected_d: Optional[float] = None
        self._centroid: Optional[Tuple[int,int]] = None
        self._missed: int = 0

    @staticmethod
    def _colour_mask(hsv, ranges):
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in ranges:
            mask |= cv2.inRange(hsv, lo, hi)
        return mask

    @staticmethod
    def _find_markers(mask):
        good = []
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            area = cv2.contourArea(c)
            if area < MIN_AREA or area > MAX_AREA:
                continue
            peri = cv2.arcLength(c, True)
            circ = 4*np.pi*area/(peri*peri) if peri else 0
            if circ < MIN_CIRC:
                continue
            m = cv2.moments(c)
            good.append((int(m["m10"]/m["m00"]), int(m["m01"]/m["m00"]), area))
        return good

    def _roi(self, shape):
        if self._centroid is None:
            return None
        x, y = self._centroid
        h, w = shape[:2]
        r = ROI_RADIUS
        return (slice(max(0, y-r), min(h, y+r)),
                slice(max(0, x-r), min(w, x+r)))

    def _miss(self):
        self._missed += 1
        if self._missed > RESET_AFTER_MISSES:
            self._centroid = None

    def update(self, frame_bgr, debug=False, homography=None):
        roi = self._roi(frame_bgr.shape)
        crop = frame_bgr[roi] if roi else frame_bgr

        crop = preprocess_lighting(crop)
        hsv  = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        pink_m   = cv2.morphologyEx(self._colour_mask(hsv, PINK_HSV),   cv2.MORPH_OPEN, kernel)
        purple_m = cv2.morphologyEx(self._colour_mask(hsv, PURPLE_HSV), cv2.MORPH_OPEN, kernel)

        pinks  = self._find_markers(pink_m)
        purps  = self._find_markers(purple_m)
        if not pinks or not purps:
            self._miss()
            return None

        exp = self._expected_d or (0.125 * frame_bgr.shape[1])
        best, best_score = None, 1e9
        for (px,py,_), (ux,uy,_) in ((p,u) for p in pinks for u in purps):
            d = hypot(px-ux, py-uy)
            if not (0.5*exp <= d <= 1.5*exp):
                continue
            score = abs(d-exp)
            if score < best_score:
                best_score, best = score, ((px,py),(ux,uy),d)

        if best is None:
            self._miss()
            return None

        # swap roles: PURPLE is front
        (backx, backy), (frontx, fronty), d = best
        cx, cy = (frontx + backx)//2, (fronty + backy)//2
        heading = degrees(atan2(fronty - backy, frontx - backx))

        offx = roi[1].start if roi else 0
        offy = roi[0].start if roi else 0
        frontx += offx; fronty += offy
        backx  += offx; backy  += offy
        cx += offx; cy += offy

        if homography is not None:
            try:
                pts = np.array([[frontx, fronty], [backx, backy]], np.float32).reshape(-1,1,2)
                pts_t = cv2.perspectiveTransform(pts, homography).reshape(-1,2)
                (frontx, fronty), (backx, backy) = pts_t
                cx, cy = (frontx + backx)*0.5, (fronty + backy)*0.5
                heading = degrees(atan2(fronty - backy, frontx - backx))
            except cv2.error:
                pass

        self._centroid = (int(cx), int(cy))
        self._missed = 0
        self._expected_d = 0.8*self._expected_d + 0.2*d if self._expected_d else d

        if not debug:
            return (self._centroid, heading)

        dbg = frame_bgr.copy()
        cv2.circle(dbg, (int(frontx), int(fronty)), 8, (0,0,255), -1)  # red front (now purple)
        cv2.circle(dbg, (int(backx),  int(backy)),  8, (255,0,0), -1)  # blue back (now pink)
        cv2.line(dbg, (int(backx), int(backy)), (int(frontx), int(fronty)), (0,255,0), 2)
        cv2.circle(dbg, self._centroid, 6, (0,255,255), -1)
        return (self._centroid, heading, dbg)

_tracker = _RobotTracker()

def get_robot_pose(frame_bgr, homography=None, debug=False):
    return _tracker.update(frame_bgr, debug, homography)

def reset_tracker():
    global _tracker
    _tracker = _RobotTracker()
