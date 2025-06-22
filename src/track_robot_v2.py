from __future__ import annotations

import cv2
import numpy as np
import json
import os
from math import atan2, degrees, hypot
from typing import Optional, Tuple, Dict, List

# ---------------------------------------------------------------------------
# --- CALIBRATION FILE ------------------------------------------------------
CALIB_FILE = os.path.join(os.path.dirname(__file__), "marker_hsv.json")

# fallback values (will be overridden if JSON exists)
_DEFAULT_PINK_HSV = ((np.array([155, 60, 60]), np.array([179, 255, 255])),)
_DEFAULT_PURPLE_HSV = ((np.array([110, 40, 40]), np.array([140, 255, 255])),)


def _load_hsv_ranges():
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
            print("[robot_tracker] WARNING: could not load HSV calibration:", e)
    return _DEFAULT_PINK_HSV, _DEFAULT_PURPLE_HSV


# will be replaced by reload_calibration() if the user recalibrates
PINK_HSV, PURPLE_HSV = _load_hsv_ranges()

# ---------------------------------------------------------------------------
# --- GEOMETRIC FILTERS (unchanged) ----------------------------------------
MIN_AREA = 40           # ignore speckles < this many px²
MAX_AREA = 3000         # ignore blobs bigger than a marker (e.g. arena rail)
MIN_CIRC = 0.40         # 4πA / P², 1.0 is a perfect circle
ROI_RADIUS = 100        # search window half-size once we have a track
RESET_AFTER_MISSES = 15 # frames without a hit → full-frame search again


# ---------------------------------------------------------------------------
# --- INTERNAL STATEFUL TRACKER --------------------------------------------
class _RobotTracker:
    """Tracks the two discs and estimates robot pose frame-by-frame."""

    def __init__(self):
        self._expected_d: Optional[float] = None   # learnt disc distance (px)
        self._centroid:   Optional[Tuple[int, int]] = None  # last robot centre
        self._missed: int = 0                      # frames since last hit

    # ------------------------------- utilities -----------------------------
    @staticmethod
    def _colour_mask(hsv: np.ndarray, ranges):
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lo, hi in ranges:
            mask |= cv2.inRange(hsv, lo, hi)
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

    # ------------------------------ main update ---------------------------
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

        # ---------- choose the best magenta–purple pair -------------------
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

        # --- promote ROI coords to full-frame -----------------------------
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
# --- PUBLIC CONVENIENCE WRAPPER ------------------------------------------
_tracker = _RobotTracker()


def get_robot_pose(frame_bgr: np.ndarray, debug: bool = False):
    """Stateless façade around the internal tracker (see module docstring)."""
    return _tracker.update(frame_bgr, debug)


def reset_tracker():
    """Forget any previously remembered state (ROI, learned disc distance)."""
    global _tracker
    _tracker = _RobotTracker()


# ---------------------------------------------------------------------------
# --- HSV PICKER / CALIBRATION ROUTINE -------------------------------------

class _PickerState:
    def __init__(self):
        self.label: str = "pink"                # current disc being sampled
        self.samples: Dict[str, List[Tuple[int,int,int]]] = {"pink": [], "purple": []}
        self.marks: List[Tuple[int,int,str]] = []  # list of (x, y, label)

    def add_sample(self, hsv: Tuple[int,int,int], x: int, y: int):
        self.samples[self.label].append(hsv)
        self.marks.append((x, y, self.label))

    def enough(self):
        return all(len(self.samples[l]) >= 3 for l in ("pink", "purple"))


def _mouse_cb(event, x, y, _flags, state: _PickerState):
    if event == cv2.EVENT_LBUTTONDOWN:
        state._latest_xy = (x, y)
        state._clicked = True


def calibrate_markers(video_src=1, h_margin=10, sv_margin=40):
    """Interactively create/update *marker_hsv.json*.

    Controls
    --------
    1 – sample **pink / front** disc
    2 – sample **purple / back** disc
    Left click  – add a sample for the current disc
    S – save JSON (enabled once ≥3 samples per disc)
    C – clear all samples
    Q / Esc – quit without saving
    """
    cap = cv2.VideoCapture(video_src)
    if not cap.isOpened():
        raise RuntimeError("Could not open video source " + str(video_src))

    state = _PickerState()
    cv2.namedWindow("calibrate")
    cv2.setMouseCallback("calibrate", _mouse_cb, state)

    print("\n=== HSV CALIBRATION ===")
    print("Click on the **pink** sticker (front). Press 1/2 to switch colours.")

    saved = False
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        display = frame.copy()

        # draw stored marks
        for mx, my, lbl in state.marks:
            colour = (0, 0, 255) if lbl == "pink" else (255, 0, 0)
            cv2.drawMarker(display, (mx, my), colour,
                           markerType=cv2.MARKER_TILTED_CROSS,
                           markerSize=12, thickness=2)

        # mouse click? read pixel
        if getattr(state, "_clicked", False):
            px, py = state._latest_xy
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[py, px]
            state.add_sample(tuple(int(v) for v in hsv), px, py)
            state._clicked = False
            print(f"{state.label:6s} @ ({px:3d},{py:3d}) -> HSV {hsv}")

        # overlay current mode and instructions
        txt = ("Sampling: " + state.label.upper() +
               "   (1/2 to switch)   S=save  C=clear  Q=quit")
        cv2.putText(display, txt, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("calibrate", display)
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):           # Esc or Q: quit
            break
        elif key == ord('1'):
            state.label = "pink"
        elif key == ord('2'):
            state.label = "purple"
        elif key == ord('c'):
            state = _PickerState()
            print("Cleared all samples.")
        elif key == ord('s') and state.enough():
            # ----------------- save & give visual confirmation -------------
            _write_calibration(state.samples, h_margin, sv_margin)

            # flash a green ✓ for ~1 second (≈30 frames)
            for _ in range(30):
                flash = frame.copy()
                cv2.putText(flash, "✓ Saved", (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                            (0, 255, 0), 3, cv2.LINE_AA)
                cv2.imshow("calibrate", flash)
                cv2.waitKey(30)

            saved = True
            break

    cap.release()
    cv2.destroyWindow("calibrate")
    if saved:
        reload_calibration()
        print("Saved calibration ➜", CALIB_FILE)
    else:
        print("Calibration aborted.")


def _write_calibration(samples: Dict[str, List[Tuple[int,int,int]]], h_m: int, sv_m: int):
    def rangex(arr, margin, vmax):
        lo = max(0, min(arr) - margin)
        hi = min(vmax, max(arr) + margin)
        return [int(lo), int(hi)]

    pink_h = [h for h,_,_ in samples["pink"]]
    pink_s = [s for _,s,_ in samples["pink"]]
    pink_v = [v for _,_,v in samples["pink"]]

    purp_h = [h for h,_,_ in samples["purple"]]
    purp_s = [s for _,s,_ in samples["purple"]]
    purp_v = [v for _,_,v in samples["purple"]]

    data = {
        "pink":   {"lo": [rangex(pink_h,h_m,179)[0], rangex(pink_s,sv_m,255)[0], rangex(pink_v,sv_m,255)[0]],
                    "hi": [rangex(pink_h,h_m,179)[1], rangex(pink_s,sv_m,255)[1], rangex(pink_v,sv_m,255)[1]]},
        "purple": {"lo": [rangex(purp_h,h_m,179)[0], rangex(purp_s,sv_m,255)[0], rangex(purp_v,sv_m,255)[0]],
                    "hi": [rangex(purp_h,h_m,179)[1], rangex(purp_s,sv_m,255)[1], rangex(purp_v,sv_m,255)[1]]},
    }

    with open(CALIB_FILE, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)


def reload_calibration():
    """Reload HSV limits from *marker_hsv.json* and reset the tracker."""
    global PINK_HSV, PURPLE_HSV
    PINK_HSV, PURPLE_HSV = _load_hsv_ranges()
    reset_tracker()


# ---------------------------------------------------------------------------
# --- COMMAND-LINE ENTRY POINT ---------------------------------------------
if __name__ == "__main__":
    calibrate_markers()