import cv2
import pyautogui
from ultralytics import YOLO

# Load your trained YOLOv11 pose model
model = YOLO("runs/pose/train/weights/best.pt")  # Replace with your model path

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

dragging = False

# Define landmark IDs (as per your dataset structure)
INDEX_TIP = 8
MIDDLE_TIP = 12
THUMB_TIP = 4

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    results = model.predict(frame, conf=0.5, verbose=False)

    if results and results[0].keypoints is not None:
        keypoints = results[0].keypoints.xy[0]  # Keypoints for first detected hand

        if len(keypoints) >= max(INDEX_TIP, MIDDLE_TIP, THUMB_TIP):
            index_x, index_y = keypoints[INDEX_TIP]

            # Convert to screen coordinates
            screen_x = int(index_x / frame.shape[1] * screen_w)
            screen_y = int(index_y / frame.shape[0] * screen_h)

            # Clamp coordinates to prevent fail-safe trigger
            screen_x = max(1, min(screen_w - 1, screen_x))
            screen_y = max(1, min(screen_h - 1, screen_y))

            pyautogui.moveTo(screen_x, screen_y)

            # Build a dict of keypoints
            keypoint_ids = {i: (int(x), int(y)) for i, (x, y) in enumerate(keypoints)}

            # Gesture logic
            if INDEX_TIP in keypoint_ids and MIDDLE_TIP not in keypoint_ids:
                # Only index finger → move
                dragging = False

            elif INDEX_TIP in keypoint_ids and MIDDLE_TIP in keypoint_ids and THUMB_TIP not in keypoint_ids:
                # Index + Middle → click
                pyautogui.click()
                dragging = False

            elif INDEX_TIP in keypoint_ids and MIDDLE_TIP in keypoint_ids and THUMB_TIP in keypoint_ids:
                # Index + Middle + Thumb → drag
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

            # Optional: draw index fingertip
            cv2.circle(frame, (int(index_x), int(index_y)), 10, (0, 255, 0), -1)

    cv2.imshow("YOLOv11 Mouse Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
