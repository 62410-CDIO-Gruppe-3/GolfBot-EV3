# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "inference-sdk==0.40.0",
#     "marimo",
#     "numpy==1.26.4",
#     "openai==1.68.2",
#     "opencv-python==4.10.0.84",
#     "owner==0.0.10",
#     "python-lsp-server==1.12.2",
# ]
# ///

import sys
sys.path.append(r"C:\\Users\\hatal\\GolfBot-EV3\\src")

import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    from inference_sdk import InferenceHTTPClient
    import cv2
    import numpy as np
    import sys

    # ----- CONFIGURATION -----
    API_URL = "https://detect.roboflow.com"
    API_KEY = "HgPiWohuYZMpwLGfCExS"
    MODEL_ID = "tabletennis-ball-detection/1"
    IMAGE_PATH = "assets\\test_image.jpg"
    WINDOW_NAME = "Select 4 points"
    TRANSFORM_WIDTH, TRANSFORM_HEIGHT = 1800, 1200

    # ----- LOAD IMAGE -----
    image = cv2.imread(IMAGE_PATH, cv2.IMREAD_REDUCED_COLOR_2)
    if image is None:
        print(f"Failed to load image from {IMAGE_PATH}")
        sys.exit(1)

    height, width = image.shape[:2]
    print(f"Image loaded: {width}x{height}")

    # ----- INFERENCE -----
    print("Running inference...")
    client = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)
    result = client.infer(image, model_id=MODEL_ID)

    # ----- POINT SELECTION -----
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow(WINDOW_NAME, image)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 600)
    cv2.imshow(WINDOW_NAME, image)
    cv2.setMouseCallback(WINDOW_NAME, click_event)

    print("Please select 4 points in the image.")
    while len(points) < 4:
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    return (
        TRANSFORM_HEIGHT,
        TRANSFORM_WIDTH,
        cv2,
        image,
        np,
        points,
        result,
        sys,
    )


@app.cell
def _(TRANSFORM_HEIGHT, TRANSFORM_WIDTH, cv2, np, points, result, sys):
    # ----- COMPUTE HOMOGRAPHY -----
    pts_src = np.array(points, dtype="float32")
    pts_dst = np.array([
        [0, 0],
        [TRANSFORM_WIDTH, 0],
        [TRANSFORM_WIDTH, TRANSFORM_HEIGHT],
        [0, TRANSFORM_HEIGHT]
    ], dtype="float32")

    H, status = cv2.findHomography(pts_src, pts_dst)
    if H is None:
        print("Failed to compute homography matrix.")
        sys.exit(1)

    # ----- TRANSFORM PREDICTED POINTS -----
    detected_points = [(pred["x"], pred["y"]) for pred in result["predictions"]]
    if not detected_points:
        print("No predictions found.")
        sys.exit(0)

    points_array = np.array(detected_points, dtype="float32").reshape(-1, 1, 2)
    transformed_points_array = cv2.perspectiveTransform(points_array, H)
    transformed_points = transformed_points_array.reshape(-1, 2)

    print("Transformed points:")
    for pt in transformed_points:
        print(f"({pt[0]:.2f}, {pt[1]:.2f})")

    return H, transformed_points


@app.cell
def _(H, TRANSFORM_HEIGHT, TRANSFORM_WIDTH, cv2, image, transformed_points):
    # ----- WARP IMAGE -----
    warped_image = cv2.warpPerspective(image, H, (TRANSFORM_WIDTH, TRANSFORM_HEIGHT))

    # ----- DRAW TRANSFORMED PREDICTION POINTS -----
    for _pt in transformed_points:
        x, y = int(_pt[0]), int(_pt[1])
        cv2.circle(warped_image, (x, y), 10, (0, 0, 255), -1)  # Red circles

    # ----- SHOW RESULT -----
    cv2.namedWindow("Transformed Image with Predictions", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Transformed Image with Predictions", 900, 600)
    cv2.imshow("Transformed Image with Predictions", warped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return


if __name__ == "__main__":
    app.run()

def get_transformed_points_from_image():
    """
    Runs the image recognition pipeline and returns only the transformed points.
    Returns:
        np.ndarray: Array of transformed (x, y) points.
    """
    from inference_sdk import InferenceHTTPClient
    import cv2
    import numpy as np
    import sys

    # ----- CONFIGURATION -----
    API_URL = "https://detect.roboflow.com"
    API_KEY = "HgPiWohuYZMpwLGfCExS"
    MODEL_ID = "tabletennis-ball-detection/1"
    IMAGE_PATH = "C:\\Users\\hatal\\GolfBot-EV3\\src\\assets\\test_image.jpg"
    WINDOW_NAME = "Select 4 points"
    TRANSFORM_WIDTH, TRANSFORM_HEIGHT = 1800, 1200

    # ----- LOAD IMAGE -----
    image = cv2.imread(IMAGE_PATH, cv2.IMREAD_REDUCED_COLOR_2)
    if image is None:
        print(f"Failed to load image from {IMAGE_PATH}")
        sys.exit(1)

    # ----- INFERENCE -----
    client = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)
    result = client.infer(image, model_id=MODEL_ID)

    # ----- POINT SELECTION -----
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow(WINDOW_NAME, image)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 600)
    cv2.imshow(WINDOW_NAME, image)
    cv2.setMouseCallback(WINDOW_NAME, click_event)

    print("Please select 4 points in the image.")
    while len(points) < 4:
        cv2.waitKey(1)
    cv2.destroyAllWindows()

    # ----- COMPUTE HOMOGRAPHY -----
    pts_src = np.array(points, dtype="float32")
    pts_dst = np.array([
        [0, 0],
        [TRANSFORM_WIDTH, 0],
        [TRANSFORM_WIDTH, TRANSFORM_HEIGHT],
        [0, TRANSFORM_HEIGHT]
    ], dtype="float32")

    H, status = cv2.findHomography(pts_src, pts_dst)
    if H is None:
        print("Failed to compute homography matrix.")
        sys.exit(1)

    # ----- TRANSFORM PREDICTED POINTS -----
    detected_points = [(pred["x"], pred["y"]) for pred in result["predictions"]]
    if not detected_points:
        print("No predictions found.")
        sys.exit(0)

    points_array = np.array(detected_points, dtype="float32").reshape(-1, 1, 2)
    transformed_points_array = cv2.perspectiveTransform(points_array, H)
    transformed_points = transformed_points_array.reshape(-1, 2)

    return transformed_points