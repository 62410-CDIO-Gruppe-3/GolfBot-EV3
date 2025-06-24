import cv2, track_robot_v3 as tr

cap = tr.init_camera(1)                 # or cv2.VideoCapture(...)

while True:
    ok, frame = cap.read()
    if not ok: break
    pose = tr.get_robot_pose(frame, debug=True)
    if pose is not None and len(pose) == 3:
        (_, _), _, dbg = pose
        cv2.imshow('tracker', dbg)
    else:
        cv2.imshow('tracker', frame)
    if cv2.waitKey(1) & 0xFF == 27:     # Esc to quit
        break
