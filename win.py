import os
import cv2
import numpy as np
import math
import time
import pyautogui
from cvzone.HandTrackingModule import HandDetector
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from pynput.keyboard import Key, Controller
import webbrowser
import subprocess

# Camera settings
width, height = 600, 440
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Variables
hs, ws = int(120 * 2.5), int(213 * 2.5)
buttonPressed = False
buttonCounter = 0
buttonDelay = 25
annotations = [[]]
annotationNumber = -1
annotationStart = False
pointerX, pointerY = 0, 0
keyboard = Controller()
paint_open = False
drawing = False

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img)

    if hands and not buttonPressed:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        # Gesture 1 - Previous Slide
        if fingers == [0, 0, 0, 0, 1]:
            print('Right')
            keyboard.press(Key.page_down)
            keyboard.release(Key.page_down)

        # Gesture 2 - Next Slide
        elif fingers == [1, 0, 0, 0, 0]:
            print('Left')
            keyboard.press(Key.page_up)
            keyboard.release(Key.page_up)

        # Gesture 3 - Volume Control
        elif fingers == [1, 1, 0, 0, 0]:
            print("Volume Control")
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volRange = volume.GetVolumeRange()
            minVol, maxVol = volRange[0], volRange[1]

            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]

            length = math.hypot(x2 - x1, y2 - y1)
            vol = np.interp(length, [50, 220], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)

        # Gesture 4 - Drawing in Paint
        elif fingers == [0, 1, 0, 0, 0] and paint_open:
            print('Drawing in Paint')
            x, y = lmList[8][0], lmList[8][1]
            screen_x = int(np.interp(x, [0, width], [0, 1920]))
            screen_y = int(np.interp(y, [0, height], [0, 1080]))
            pyautogui.moveTo(screen_x, screen_y)
            if not drawing:
                pyautogui.mouseDown()
                drawing = True
        else:
            if drawing:
                pyautogui.mouseUp()
                drawing = False

        # Gesture 5 - Erasing
            elif fingers == [0, 1, 1, 1, 0]:
                print('Erasing')
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

        # Gesture 6 - Open Browser
            elif fingers == [0, 1, 1, 1, 1]:
                print("Open Google")
                webbrowser.open('https://www.google.com')
                time.sleep(5)  # wait for Google to load

                # Move to Google search bar and click
                search_bar_pos = (600, 400)  # <-- Adjust coordinates if needed
                pyautogui.moveTo(search_bar_pos[0], search_bar_pos[1], duration=1)
                pyautogui.click()


        # Gesture 7 - Open Calculator
            elif fingers == [0, 0, 1, 1, 1]:
                print("Open Calculator")
                subprocess.Popen(["calc.exe"])
                search_bar_pos = (600, 400)  # <-- Adjust coordinates if needed
                pyautogui.moveTo(search_bar_pos[0], search_bar_pos[1], duration=1)
                pyautogui.click()

        # Gesture 8 - Open YouTube
            elif fingers == [0, 0, 0, 1, 1]:
                    print("Open Google")
                    webbrowser.open('https://www.youtube.com')
                    time.sleep(5)  # wait for Google to load

                    # Move to Google search bar and click
                    search_bar_pos = (600, 400)  # <-- Adjust coordinates if needed
                    pyautogui.moveTo(search_bar_pos[0], search_bar_pos[1], duration=1)
                    pyautogui.click()
            

        # # Gesture 8 - Open Paint
        #     elif fingers == [0, 1, 0, 0, 1] and not paint_open:
        #         print("Open Paint")
        #         subprocess.Popen(["mspaint.exe"])
        #         paint_open = True
        #         cv2.waitKey(2000)  # Wait for Paint to open

        # Gesture 9 - Open PDF
            elif fingers == [0, 1, 0, 0, 0]:
                print("Open PDF")
                pdf_path = r"C:\Users\janug\OneDrive\Desktop\tejuu\majorreport.docx"  # Replace this with your actual path
                os.startfile(pdf_path)
                buttonPressed = True


    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    # Display webcam
    cv2.imshow("Webcam Feed", img)

    # Quit condition
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
