import cv2
import os
from pathlib import Path
from ImageRecognition.Homography import create_homography, save_homography

# Constants (matching main.py)
TRANSFORM_W, TRANSFORM_H = 1800, 1200
HOMOGRAPHY_FILE = str((Path(__file__).parent / "homography.npy").resolve())

def main():
    # Initialize video capture (using camera 1 to match main.py). Use iriun.com to get the camera working.
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    # Read first frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        cap.release()
        return

    # Save the frame temporarily
    temp_frame_path = "temp_frame.jpg"
    cv2.imwrite(temp_frame_path, frame)

    try:
        print("Select 4 points clockwise (BL → BR → TR → TL)")
        print("Press 'q' to abort")
        
        # Create homography matrix
        H = create_homography(temp_frame_path, dst_size=(TRANSFORM_W, TRANSFORM_H))
        
        # Save the homography matrix
        save_homography(H, HOMOGRAPHY_FILE)
        print(f"Successfully created and saved homography to {HOMOGRAPHY_FILE}")
        
    except Exception as e:
        print(f"Error creating homography: {e}")
    finally:
        # Clean up
        if os.path.exists(temp_frame_path):
            os.remove(temp_frame_path)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 