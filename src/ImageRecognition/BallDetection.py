import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_balls(image_path, show=True):
    """
    Detect orange & white balls (< = 11 per frame).

    Returns
    -------
    balls : list of dict
        [{ "center": (x, y), "radius": r, "color": "white|orange" }, …]
    """
    img  = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # ---- Hough-circle search ---------------------------------------------
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=gray.shape[0] / 18,
        param1=80,
        param2=20,
        minRadius=10,
        maxRadius=40,
    )

    balls, hsv = [], cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    if circles is not None:
        for x, y, r in np.uint16(np.around(circles[0])):
            # mask a small disc inside the circle & sample its colour
            mask = np.zeros(gray.shape, np.uint8)
            cv2.circle(mask, (x, y), int(r * 0.6), 255, -1)
            h, s, v, _ = cv2.mean(hsv, mask=mask)

            colour = None
            if 10 <= h <= 35 and s > 100 and v > 100:
                colour = "orange"
            elif s < 40 and v > 180:
                colour = "white"
            if colour:
                balls.append({"center": (int(x), int(y)), "radius": int(r), "color": colour})

    # ---- scene rule: ≤ 11 balls ------------------------------------------
    if len(balls) > 11:
        raise RuntimeError(f"Detected {len(balls)} balls – exceeds the expected maximum of 11!")

    # ---- optional preview -------------------------------------------------
    if show:
        vis = img.copy()
        for b in balls:
            x, y = b["center"]
            col  = (0,165,255) if b["color"] == "orange" else (255,255,255)
            cv2.circle(vis, (x, y), b["radius"], col, 3)
            cv2.putText(vis, b["color"], (x - b["radius"], y - b["radius"] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
        plt.figure(figsize=(6, 8))
        plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
        plt.title("Detected balls (white & orange)")
        plt.axis("off")
        plt.show()

    return balls
