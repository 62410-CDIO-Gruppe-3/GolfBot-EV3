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
#_DEFAULT_PINK_HSV = ((np.array([155, 60, 60]), np.array([179, 255, 255])),)
#_DEFAULT_PURPLE_HSV = ((np.array([110, 40, 40]), np.array([140, 255, 255])),)

# ---------------------------------------------------------------------------
# --- CAMERA UTILITIES ------------------------------------------------------
# ---------------------------------------------------------------------------
# --- LIGHTING NORMALISATION -------------------------------------------------

def preprocess_lighting(img_bgr: np.ndarray) -> np.ndarray:
    """
    1. Gray-World colour constancy -> removes colour casts and tracks slow
       brightness drift.
    2. CLAHE on the lightness channel only -> makes 'dark' frames resemble
       'bright' ones without shifting hue.
    """
    # --- Gray-World ---------------------------------------------------------
    img = img_bgr.astype(np.float32)
    avg_b, avg_g, avg_r = [c.mean() + 1e-6 for c in cv2.split(img)]
    avg = (avg_b + avg_g + avg_r) / 3.0
    scale = avg / np.array([avg_b, avg_g, avg_r])
    img *= scale
    img = np.clip(img, 0, 255).astype(np.uint8)

    # --- CLAHE on L channel -------------------------------------------------
    lab  = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_eq  = clahe.apply(l)
    img_eq = cv2.merge((l_eq, a, b))
    return cv2.cvtColor(img_eq, cv2.COLOR_LAB2BGR)

def init_camera(src: int | str = 0,
                exposure: float = -6.0,     # typical webcam units (≈1/60 s)
                gain: float = 0.0,
                wb_blue: float = 4600,      # Kelvin → webcam units vary
                wb_red: float = 4600):
    """
    Open a cv2.VideoCapture, then put *all* automatic controls in manual mode
    so the colour statistics become repeatable frame-to-frame.

    Returns
    -------
    cv2.VideoCapture
    """
    cap = cv2.VideoCapture(src)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source {src}")

    # ------------ turn OFF every auto feature the driver exposes ------------
    # NOTE: driver constants differ between platforms, so we catch failures.
    # Windows + DirectShow
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)          # 1 = manual, 3 = auto
    cap.set(cv2.CAP_PROP_AUTO_WB,       0)          # 0 = manual
    # Linux + UVC (values are floats; -1 = auto)
    cap.set(cv2.CAP_PROP_EXPOSURE,      exposure)
    cap.set(cv2.CAP_PROP_GAIN,          gain)
    cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, wb_blue)
    cap.set(cv2.CAP_PROP_WHITE_BALANCE_RED_V,  wb_red)

    return cap

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
    def update(
        self,
        frame_bgr: np.ndarray,
        debug: bool = False,
        homography: Optional[np.ndarray] = None,
    ) -> Optional[
        Tuple[Tuple[int, int], float] | Tuple[Tuple[int, int], float, np.ndarray]
    ]:
        """Return pose or None; with *debug=True* also returns an overlay img.

        If *homography* (3×3) is supplied, the returned centroid and heading
        are reported **in the transformed coordinate space**, i.e. after
        applying the projective transform to both the front (pink) and back
        (purple) marker positions.
        """
        roi = self._roi_slices(frame_bgr.shape)
        crop = frame_bgr[roi] if roi else frame_bgr

        # --- NEW STEP -------------------------------------------------------------
        crop = preprocess_lighting(crop)

        hsv  = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        pink_m   = cv2.morphologyEx(self._colour_mask(hsv, PINK_HSV),   cv2.MORPH_OPEN, kernel)
        purple_m = cv2.morphologyEx(self._colour_mask(hsv, PURPLE_HSV), cv2.MORPH_OPEN, kernel)

        pinks  = self._find_markers(pink_m)
        purps  = self._find_markers(purple_m)
        print(f"[DEBUG] Pink markers: {len(pinks)}, Purple markers: {len(purps)}")
        if not pinks or not purps:
            self._register_miss()
            return None

        # ---------- choose the best magenta–purple pair -------------------
        exp = self._expected_d or (0.125 * frame_bgr.shape[1])  # 1/8 of width
        best, best_score = None, 1e9
        for (px, py, _), (ux, uy, _) in [(p, u) for p in pinks for u in purps]:
            d = hypot(px - ux, py - uy)
            print(f"[DEBUG] Pair: pink=({px},{py}), purple=({ux},{uy}), distance={d:.2f}, expected={exp:.2f}")
            if not (0.5 * exp <= d <= 1.5 * exp):
                print(f"[DEBUG] Pair rejected: distance {d:.2f} not in [{0.6*exp:.2f}, {1.4*exp:.2f}]")
                continue
            score = abs(d - exp)
            if score < best_score:
                best_score, best = score, ((px, py), (ux, uy), d)

        if best is None:
            self._register_miss()
            return None

        (fx, fy), (bx, by), d = best
        cx, cy = (fx + bx) // 2, (fy + by) // 2
        heading = degrees(atan2(fy - by, fx - bx)) + 3  # +ve = clockwise, adjusted 5 deg left
        print(f"[DEBUG] Chosen pair: front=({fx},{fy}), back=({bx},{by}), centroid=({cx},{cy}), heading={heading:.2f}°")

        # --- promote ROI coords to full-frame -----------------------------
        offx = roi[1].start if roi else 0
        offy = roi[0].start if roi else 0
        fx_full, fy_full = fx + offx, fy + offy
        bx_full, by_full = bx + offx, by + offy

        # --- apply homography if provided ---------------------------------
        if homography is not None:
            try:
                pts = np.array([[fx_full, fy_full], [bx_full, by_full]], dtype=np.float32).reshape(-1, 1, 2)
                pts_t = cv2.perspectiveTransform(pts, homography).reshape(-1, 2)
                (fx_t, fy_t), (bx_t, by_t) = pts_t
                cx_t, cy_t = (fx_t + bx_t) * 0.5, (fy_t + by_t) * 0.5
                cx_out, cy_out = int(round(cx_t)), int(round(cy_t))
                heading = degrees(atan2(fy_t - by_t, fx_t - bx_t)) - 5  # adjusted 5 deg left
            except cv2.error as e:
                print("[robot_tracker] WARNING: homography transform failed:", e)
                # fall back to pixel coords
                cx_out, cy_out = cx + offx, cy + offy
        else:
            # no homography
            cx_out, cy_out = cx + offx, cy + offy

        self._centroid = (cx + offx, cy + offy)  # still use image coords for ROI
        self._missed   = 0
        self._expected_d = 0.8 * self._expected_d + 0.2 * d if self._expected_d else d

        if not debug:
            return ((cx_out, cy_out), heading)

        dbg = frame_bgr.copy()
        cv2.circle(dbg, (fx_full, fy_full), 8, (  0,   0, 255), -1)  # red front
        cv2.circle(dbg, (bx_full, by_full), 8, (255,   0,   0), -1)  # blue back
        cv2.line  (dbg, (bx_full, by_full), (fx_full, fy_full), (  0, 255,   0), 2)
        cv2.circle(dbg,  self._centroid,          6, (  0, 255, 255), -1)  # yellow centre
        return ((cx_out, cy_out), heading, dbg)


# ---------------------------------------------------------------------------
# --- PUBLIC CONVENIENCE WRAPPER ------------------------------------------
_tracker = _RobotTracker()


def get_robot_pose(
    frame_bgr: np.ndarray,
    homography: Optional[np.ndarray] = None,
    debug: bool = False,
) -> Optional[
    Tuple[Tuple[int, int], float] | Tuple[Tuple[int, int], float, np.ndarray]
]:
    """
    Detect the robot's position and heading in *frame_bgr*.

    The result can optionally be expressed in a different coordinate space by
    supplying a 3×3 *homography* matrix. If provided, both the returned centre
    point and heading angle are calculated **after** projecting the front and
    back disc positions through *homography*.

    Parameters
    ----------
    frame_bgr : np.ndarray
        Input image in BGR order (OpenCV style).
    homography : Optional[np.ndarray], default ``None``
        3×3 projective transform matrix mapping image pixels to the target
        coordinate space. If *None* the raw image coordinates are returned.
    debug : bool, default ``False``
        When *True*, an additional BGR debug image is returned.

    Returns
    -------
    (centre, heading) or (centre, heading, debug_img) or ``None``
        Exactly like before, except that *centre* and *heading* are mapped
        through *homography* when one is supplied.
    """
    result = _tracker.update(frame_bgr, debug=debug, homography=homography)

    # Retain verbose detection diagnostics for external logging
    frame_bgr_norm = preprocess_lighting(frame_bgr)
    hsv = cv2.cvtColor(frame_bgr_norm, cv2.COLOR_BGR2HSV)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    pink_mask = cv2.morphologyEx(_tracker._colour_mask(hsv, PINK_HSV), cv2.MORPH_OPEN, kernel)
    purple_mask = cv2.morphologyEx(_tracker._colour_mask(hsv, PURPLE_HSV), cv2.MORPH_OPEN, kernel)
    pinks = _tracker._find_markers(pink_mask)
    purples = _tracker._find_markers(purple_mask)
    print(f"[DEBUG] Pink markers: {len(pinks)}, Purple markers: {len(purples)}")

    return result


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
        state._latest_xy_resized = (x, y)
        state._clicked = True


def calibrate_markers(video_src=1, h_margin=20, sv_margin=80):
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
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():
        raise RuntimeError("Could not open video source " + str(video_src))

    state = _PickerState()
    cv2.namedWindow("calibrate", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("calibrate", 640, 360)
    cv2.setMouseCallback("calibrate", _mouse_cb, state)

    print("\n=== HSV CALIBRATION ===")
    print("Click on the **pink** sticker (front). Press 1/2 to switch colours.")

    saved = False
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # Resize frame first
        display = cv2.resize(frame.copy(), (640, 360))
        scale_x = 640 / frame.shape[1]
        scale_y = 360 / frame.shape[0]

        # draw stored marks at their clicked (resized) positions
        for mx, my, lbl in state.marks:
            colour = (0, 0, 255) if lbl == "pink" else (255, 0, 0)
            cv2.drawMarker(display, (mx, my), colour,
                           markerType=cv2.MARKER_TILTED_CROSS,
                           markerSize=12, thickness=2)

        # mouse click? read pixel
        if getattr(state, "_clicked", False):
            px_r, py_r = state._latest_xy_resized
            # Map back to original frame coordinates
            px = int(px_r / scale_x)
            py = int(py_r / scale_y)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[py, px]
            state.add_sample(tuple(int(v) for v in hsv), px_r, py_r)  # store resized coords for drawing
            state._clicked = False
            print(f"{state.label:6s} @ ({px:3d},{py:3d}) [resized=({px_r},{py_r})] -> HSV {hsv}")

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
                flash = cv2.resize(frame.copy(), (640, 360))
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