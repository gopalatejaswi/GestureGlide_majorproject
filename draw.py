import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import subprocess
import time

class FingerPaintApp:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils

        self.is_drawing = False
        self.is_erasing = False
        self.last_x, self.last_y = 0, 0

        # Open MS Paint (you can adjust this command based on your OS)
        self.open_mspaint()

        self.cap = cv2.VideoCapture(0)

    def open_mspaint(self):
        # Open MS Paint (for Windows)
        subprocess.Popen('mspaint')
        time.sleep(3)  # Wait for MS Paint to load

    def update_video(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)  # Mirror the frame for natural interaction
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to get hand landmarks
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # Get index fingertip position (landmark 8)
                x = int(landmarks.landmark[8].x * frame.shape[1])
                y = int(landmarks.landmark[8].y * frame.shape[0])

                # Draw the fingertip position on the frame
                cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)

                # Simulate mouse movement using the fingertip
                self.move_mouse(x, y)

                # Check if the hand gesture is for drawing or erasing
                self.check_gestures(landmarks)

        # Display the frame in OpenCV
        cv2.imshow("Finger Paint App", frame)

        # Wait for key press to stop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return

    def move_mouse(self, x, y):
        # Map the detected fingertip position to the screen resolution
        screen_width, screen_height = pyautogui.size()
        mapped_x = np.clip(int(x * screen_width / 640), 0, screen_width)
        mapped_y = np.clip(int(y * screen_height / 480), 0, screen_height)

        pyautogui.moveTo(mapped_x, mapped_y)

        # Start drawing if the finger moves
        if self.is_drawing:
            pyautogui.mouseDown()

        if self.is_erasing:
            pyautogui.mouseDown(button='right')

    def check_gestures(self, landmarks):
        # Get the distance between the thumb and index finger to detect a pinch gesture
        thumb_x = int(landmarks.landmark[4].x * 640)
        thumb_y = int(landmarks.landmark[4].y * 480)
        index_x = int(landmarks.landmark[8].x * 640)
        index_y = int(landmarks.landmark[8].y * 480)

        distance = np.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)

        # Add a threshold to avoid false positives for small distances
        pinch_threshold = 50  # Adjust this based on your preferences

        # If the fingers are close enough (pinch gesture), trigger erasing
        if distance < pinch_threshold:
            self.is_erasing = True
            self.is_drawing = False
        else:
            # Default to drawing if no pinch gesture is detected
            self.is_erasing = False
            self.is_drawing = True

    def run(self):
        while True:
            self.update_video()

        # Release the webcam and close OpenCV window
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = FingerPaintApp()
    app.run()
