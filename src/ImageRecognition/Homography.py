import cv2
import numpy as np
from pathlib import Path


# ───────────────────────────────────────── create ──
def create_homography(img_path: str | Path,
                      dst_size: tuple[int, int] = (1000, 700),
                      window_max: int = 900) -> np.ndarray:
    """
    Pick four corners in 'img_path' → homography H s.t.
        (clicked pts)  →  (0,0), (w,0), (w,h), (0,h)  with w,h = dst_size.

    A scaled preview window (max side <= window_max) is opened.
    Click order must be:  TL, TR, BR, BL  (clockwise).

    Returns
    -------
    H : np.ndarray, shape (3,3) – perspective-transform matrix.
    """

    img = cv2.imread(str(img_path))
    if img is None:
        raise FileNotFoundError(img_path)

    h0, w0 = img.shape[:2]
    scale = min(1.0, window_max / max(h0, w0))
    small = cv2.resize(img, None, fx=scale, fy=scale,
                       interpolation=cv2.INTER_AREA)

    print("Select 4 points clockwise (TL ➜ TR ➜ BR ➜ BL). "
          "Hit <Esc>/<q> to abort.")

    clicked: list[tuple[int, int]] = []

    def _mouse(evt, x, y, *_):
        if evt == cv2.EVENT_LBUTTONDOWN and len(clicked) < 4:
            cv2.circle(small, (x, y), 6, (0, 255, 0), -1)
            cv2.imshow(win, small)
            # scale back to full-res coords
            clicked.append((int(x/scale), int(y/scale)))

    win = "Pick 4 corners"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, _mouse)
    cv2.imshow(win, small)

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key in (27, ord('q')):      # Esc or 'q'
            cv2.destroyAllWindows()
            raise RuntimeError("User aborted.")
        if len(clicked) == 4:
            break

    cv2.destroyAllWindows()

    dst_w, dst_h = dst_size
    dst = np.array([[0, 0],
                    [dst_w, 0],
                    [dst_w, dst_h],
                    [0, dst_h]], dtype=np.float32)

    H, _ = cv2.findHomography(np.array(clicked, np.float32), dst)
    if H is None:
        raise RuntimeError("cv2.findHomography failed – bad click order?")
    return H


# ───────────────────────────────────────── save ──
def save_homography(H: np.ndarray, filename: str | Path) -> None:
    """
    Save a 3×3 homography.  Extension decides the format:

    • *.npy*  – NumPy np.save / np.load  (default, loss-less)
    • *.txt*  – plain text via np.savetxt   (human-readable)
    """
    filename = Path(filename)
    if filename.suffix.lower() == ".txt":
        np.savetxt(filename, H, fmt="%.8f")
    else:                      # fall back to NumPy binary
        np.save(filename, H)
    print(f"Saved H → {filename}")


# ───────────────────────────────────────── load ──
def load_homography(filename: str | Path) -> np.ndarray:
    """
    Load a homography previously saved with *save_homography*.
    """
    filename = Path(filename)
    if not filename.exists():
        raise FileNotFoundError(filename)
    if filename.suffix.lower() == ".txt":
        H = np.loadtxt(filename, dtype=np.float64).reshape(3, 3)
    else:
        H = np.load(filename)
    if H.shape != (3, 3):
        raise ValueError("File does not contain a 3×3 homography.")
    return H