import numpy as np
import cv2

def image_to_field_coords(point, homography_matrix):
    """
    Omdanner et punkt fra billedkoordinater til bane-koordinater.
    :param point: (x, y) tuple i billedkoordinater
    :param homography_matrix: 3x3 matrix fra cv2.findHomography
    :return: (x, y) tuple i bane-koordinater
    """
    pts = np.array([[point]], dtype='float32')
    transformed = cv2.perspectiveTransform(pts, homography_matrix)
    return tuple(transformed[0][0])

# Eksempel på brug:
if __name__ == "__main__":
    # Dummy homografi og punkt
    H = np.eye(3)
    img_point = (100, 200)
    field_point = image_to_field_coords(img_point, H)
    print(f"Billedpunkt {img_point} -> Banepunkt {field_point}")