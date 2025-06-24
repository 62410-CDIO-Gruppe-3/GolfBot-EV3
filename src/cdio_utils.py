from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import cv2  # type: ignore
import numpy as np
import math

try:
    # Only import if the user actually needs inference.
    from inference_sdk import InferenceHTTPClient, InferenceConfiguration  # type: ignore
except ImportError:  # pragma: no cover – makes linting/tests happy when package is absent
    InferenceHTTPClient = None  # type: ignore

__all__ = [
    "InferenceConfig",
    "load_image",
    "select_four_points",
    "compute_homography",
    "run_inference",
    "transform_points",
    "warp_image",
    "draw_points",
    "process_image",
]


# ---------------------------------------------------------------------------
# Dataclasses / typed containers
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class InferenceConfig:
    """Parameters required to hit a Roboflow/Inference endpoint."""

    api_url: str
    api_key: str
    model_id: str

    def client(self) -> "InferenceHTTPClient":
        if InferenceHTTPClient is None:  # pragma: no cover
            raise RuntimeError(
                "inference‑sdk is not installed. Please `pip install inference‑sdk` "
                "or add it to your project dependencies."
            )
        custom_configuration = InferenceConfiguration(confidence_threshold=0.001)
        c = InferenceHTTPClient(api_url=self.api_url, api_key=self.api_key)
        c.use_configuration(custom_configuration)
        c.select_model(self.model_id)
        return c


# ---------------------------------------------------------------------------
# Core utilities
# ---------------------------------------------------------------------------


def load_image(path: str | Path, *, reduced_color: int = 2) -> np.ndarray:
    """Load an image from *path*.

    Parameters
    ----------
    path:
        Path to the image on disk.
    reduced_color:
        If 1,2,4,... OpenCV will downsample by that factor (see `cv2.IMREAD_REDUCED_COLOR_*`).
        Use 0 to disable downsampling.  Downsampling accelerates interactive selection and
        inference on large images.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    if reduced_color not in {0, 2, 4, 8}:  # OpenCV only supports these divisors
        raise ValueError("reduced_color must be one of {0, 2, 4, 8}")

    flag = cv2.IMREAD_COLOR if reduced_color == 0 else getattr(
        cv2, f"IMREAD_REDUCED_COLOR_{reduced_color}")
    img = cv2.imread(str(path), flag)
    if img is None:
        raise RuntimeError(f"OpenCV failed to read image: {path}")
    return img


def select_four_points(
    image: np.ndarray,
    *,
    window_name: str = "Select 4 points",
    resize: tuple[int, int] | None = (800, 600),
) -> List[Tuple[int, int]]:
    """Interactively select exactly four points from *image*.

    This opens an OpenCV window.  Left‑click to mark points; the function returns once four
    points are chosen and the window is closed.  Blocking.
    """

    points: list[tuple[int, int]] = []

    def _click(event: int, x: int, y: int, flags: int, param):  # noqa: D401, N802 – OpenCV API
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow(window_name, image)

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    if resize is not None:
        w, h = resize
        cv2.resizeWindow(window_name, w, h)
    cv2.imshow(window_name, image)
    cv2.setMouseCallback(window_name, _click)

    print("Please left‑click four points …")
    while len(points) < 4:
        if cv2.waitKey(1) == 27:  # Esc key to abort
            cv2.destroyWindow(window_name)
            raise KeyboardInterrupt("Point selection aborted by user (Esc pressed).")
    cv2.destroyWindow(window_name)
    return points

def run_inference(
    image: np.ndarray,
    cfg: InferenceConfig,
    *,
    client: "InferenceHTTPClient" | None = None,
) -> dict:
    """Perform object detection on *image* using the Roboflow inference SDK.

    Parameters
    ----------
    image:
        Numpy BGR array as loaded by OpenCV.
    cfg:
        :class:`InferenceConfig` with endpoint and credentials.
    client:
        Optionally supply a pre‑configured :class:`InferenceHTTPClient` instance (e.g. for
        batching).  If *None*, one is created on‑the‑fly.
    """
    if client is None:
        client = cfg.client()
    return client.infer(image)


def _to_points_array(points: Iterable[Tuple[float, float]]) -> np.ndarray:
    return np.asarray(list(points), dtype=np.float32).reshape(-1, 1, 2)


def transform_points(
    points: Sequence[Tuple[float, float]], H: np.ndarray
) -> np.ndarray:
    """Apply homography *H* to *points* and return an N×2 array of transformed coordinates."""
    if not points:
        return np.empty((0, 2), dtype=np.float32)
    pts = _to_points_array(points)
    transformed = cv2.perspectiveTransform(pts, H)
    return transformed.reshape(-1, 2)


def warp_image(
    image: np.ndarray,
    H: np.ndarray,
    width: int,
    height: int,
    *,
    interpolation: int = cv2.INTER_LINEAR,
) -> np.ndarray:
    """Return the perspective‑warped *image* using homography *H* to size *width × height*."""
    return cv2.warpPerspective(image, H, (width, height), flags=interpolation)


def draw_points(
    image: np.ndarray,
    points: Sequence[Tuple[float, float] | np.ndarray],
    *,
    color: Tuple[int, int, int] = (0, 0, 255),
    radius: int = 10,
    thickness: int = -1,
) -> np.ndarray:
    """Overlay *points* onto *image* and return a copy."""
    out = image.copy()
    for p in points:
        x, y = map(int, p)
        cv2.circle(out, (x, y), radius, color, thickness)
    return out


# ---------------------------------------------------------------------------
# High‑level convenience wrapper
# ---------------------------------------------------------------------------


def process_image(
    image_path: str | Path,
    transform_size: tuple[int, int],
    cfg: InferenceConfig,
    *,
    reduced_color: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    """One‑shot helper that reproduces the entire pipeline of the original script.

    Returns
    -------
    warped_image:
        Perspective‑corrected image.
    transformed_points:
        N×2 array with detection points mapped into the warped coordinate system.
    """
    width, height = transform_size

    # 1. Read image
    img = load_image(image_path, reduced_color=reduced_color)

    # 2. Interactive four‑corner selection
    src_pts = select_four_points(img)

    # 3. Compute homography
    H = compute_homography(src_pts, width, height)

    # 4. Run inference
    result = run_inference(img, cfg)
    raw_points = [(pred["x"], pred["y"]) for pred in result.get("predictions", [])]
    if not raw_points:
        raise RuntimeError("No predictions returned by inference endpoint.")

    # 5. Map points + warp image
    transformed_points = transform_points(raw_points, H)
    warped = warp_image(img, H, width, height)

    return warped, transformed_points