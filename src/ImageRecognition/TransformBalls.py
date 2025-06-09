import cv2
import numpy as np
from typing import Sequence

def transform_balls(balls: Sequence[tuple[tuple[float, float], float]],
                    H: np.ndarray,
                    with_radius: bool = True
                    ) -> list[tuple[tuple[float, float], float] | tuple[float, float]]:
    """
    Warp ball centres (and radii) through a homography.

    Parameters
    ----------
    balls : list of ((cx, cy), r)
        Output of your detector in image pixel coords.
    H     : (3,3) ndarray
        Homography matrix mapping image → world space (the one you
        obtained with create_homography).
    with_radius : bool, default=True
        If True, each item in the returned list contains the transformed
        radius as well; otherwise only the centre.

    Returns
    -------
    warped : list
        Same length as balls.  Each item is either
            ((x', y'), r')   or   (x', y')
        depending on with_radius.
    """
    if H.shape != (3, 3):
        raise ValueError("H must be a 3×3 matrix")

    warped = []
    for (cx, cy), r in balls:
        # centre → homogeneous → warp
        src_pt   = np.array([[[cx, cy]]], dtype=np.float32)
        dst_pt   = cv2.perspectiveTransform(src_pt, H)[0][0]   # (x', y')

        if with_radius:
            # quickly estimate how the radius scales by warping a point
            # one radius unit to the +x direction
            edge_pt = np.array([[[cx + r, cy]]], dtype=np.float32)
            dst_ed  = cv2.perspectiveTransform(edge_pt, H)[0][0]
            r_new   = float(np.hypot(*(dst_ed - dst_pt)))
            warped.append(((float(dst_pt[0]), float(dst_pt[1])), r_new))
        else:
            warped.append((float(dst_pt[0]), float(dst_pt[1])))

    return warped