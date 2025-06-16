"""
test_vision_and_obstacles.py – Test af bold- og forhindringsgenkendelse
Kører både BallDetector (hvide/orange bolde) og obstacle_detection (f.eks. sort kors).
"""

import cv2
from vision.vision import BallDetector
from vision.obstacle_detection import detect_obstacles

# Indlæs testbillede (tilpas stien)
image_path = "assets/test_image0.jpg"
frame = cv2.imread(image_path)

if frame is None:
    print("Kunne ikke indlæse testbillede:", image_path)
    exit()

# Initier bold-detektor
detector = BallDetector()
balls = detector.detect_balls(frame)
vip = detector.detect_vip(frame)

# Detekter forhindringer
obstacles = detect_obstacles(frame)

# Tegn hvide bolde (grøn)
for (x, y) in balls:
    cv2.circle(frame, (x, y), 20, (0, 255, 0), 2)

# Tegn VIP-bold (orange kontur)
if vip:
    cv2.circle(frame, vip, 25, (0, 140, 255), 3)
    cv2.putText(frame, "VIP", (vip[0]-10, vip[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,140,255), 2)

# Tegn forhindringer (rød)
for obs in obstacles:
    x, y, w, h = obs['x'], obs['y'], obs['width'], obs['height']
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.putText(frame, obs['type'], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

# Vis resultat
cv2.imshow("Test – Vision + Obstacles", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
