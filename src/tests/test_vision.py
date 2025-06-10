"""
tests/test_vision.py – Test af boldgenkendelse med vision.py
"""

from vision import BallDetector

def test_detect_balls_and_vip(image_path):
    import cv2
    detector = BallDetector()
    frame = cv2.imread(image_path)
    balls = detector.detect_balls(frame)
    vip = detector.detect_vip(frame)
    print(f"Fundne bolde: {balls}")
    if vip:
        print(f"VIP-bold fundet ved: {vip}")
    else:
        print("VIP-bold ikke fundet.")

if __name__ == "__main__":
    # Udskift med sti til testbillede
    test_image = "test_images/banebillede.jpg"
    test_detect_balls_and_vip(test_image)