import cv2
import os
import time

# Directory to save frames
save_dir = os.path.join(os.path.dirname(__file__), 'source_video_feed')
os.makedirs(save_dir, exist_ok=True)

# Open the default camera
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit(1)

frame_count = 0
print("Press 'q' to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        # Save the frame
        frame_path = os.path.join(save_dir, f'frame_{frame_count:04d}.jpg')
        cv2.imwrite(frame_path, frame)
        print(f"Saved {frame_path}")
        frame_count += 1
        # Wait for 1 second or until 'q' is pressed
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows() 