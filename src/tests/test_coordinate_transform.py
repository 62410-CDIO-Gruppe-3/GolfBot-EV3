"""
tests/test_coordinate_transform.py – Test af coordinate_transform.py for GolfBot-EV3
"""

import numpy as np
from Positioning.coordinate_transform import image_to_field_coords

def test_image_to_field_coords():
    # Dummy homografi: identitetsmatrix (bør returnere samme punkt)
    H = np.eye(3)
    img_point = (100, 200)
    field_point = image_to_field_coords(img_point, H)
    print(f"Test identitet: {img_point} -> {field_point}")
    assert np.allclose(field_point, img_point), "Identitets-homografi fejlede"

    # Eksempel på en simpel skalering (2x i x, 0.5x i y)
    H_scale = np.array([
        [2, 0, 0],
        [0, 0.5, 0],
        [0, 0, 1]
    ])
    img_point = (50, 100)
    expected = (100, 50)
    field_point = image_to_field_coords(img_point, H_scale)
    print(f"Test skalering: {img_point} -> {field_point} (forventet {expected})")
    assert np.allclose(field_point, expected), "Skalerings-homografi fejlede"

    print("Alle coordinate_transform-tests bestået.")

if __name__ == "__main__":
    test_image_to_field_coords()