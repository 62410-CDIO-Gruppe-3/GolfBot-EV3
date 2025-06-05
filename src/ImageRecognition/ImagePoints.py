def get_transformed_points_from_image(image_path=None):
    """
    Runs the image recognition pipeline and returns only the transformed points.
    Args:
        image_path (str): Path to the image file.
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
    if image_path is None:
        image_path = "C:\\Users\\hatal\\GolfBot-EV3\\src\\assets\\test_image.jpg"
    WINDOW_NAME = "Select 4 points"
    TRANSFORM_WIDTH, TRANSFORM_HEIGHT = 1800, 1200

    # ----- LOAD IMAGE -----
    image = cv2.imread(image_path, cv2.IMREAD_REDUCED_COLOR_2)
    if image is None:
        print(f"Failed to load image from {image_path}")
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

    print(f"Please select 4 points in the image: {image_path}")
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