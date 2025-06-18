import os
import cv2
import numpy as np
import math
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

# Load slides
folderPath = r"C:\Users\janug\OneDrive\Documents\Downloads\hands_main\hands_main\runs\pose\output\tests"
pathImages = sorted(os.listdir(folderPath), key=len)

# Variables
imgNumber = 0
hs, ws = int(120 * 2.5), int(213 * 2.5)
buttonPressed = False
buttonCounter = 0
buttonDelay = 25
annotations = [[]]
annotationNumber = -1
annotationStart = False
pointerX, pointerY = 0, 0
keyboard = Controller()

detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    #pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    #imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)
    
    if hands and not buttonPressed:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']
        indexFinger = lmList[8][0], lmList[8][1]

        xVal = int(np.interp(lmList[8][0], [width//2, width], [0, ws]))
        yVal = int(np.interp(lmList[8][1], [150, height-150], [0, hs]))

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


        # Gesture 4 - Drawing on the Slide
        elif fingers == [0, 1, 0, 0, 0]:
            print('Drawing')
            if not annotationStart:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            x, y = lmList[8][0], lmList[8][1]
            pointerX = int(np.interp(x, [0, width], [0, imgCurrent.shape[1]]))
            pointerY = int(np.interp(y, [0, height], [0, imgCurrent.shape[0]]))
            cv2.circle(imgCurrent, (pointerX, pointerY), 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append((pointerX, pointerY))
            

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

        # Gesture 7 - Open Calculator
        elif fingers == [0, 1, 1, 0, 1]:
            print("Open Calculator")
            subprocess.Popen(["calc.exe"])

        # Gesture 8 - Open Paint
        elif fingers == [0, 1, 0, 0, 1]:
            print("Open Paint")
            subprocess.Popen(["mspaint.exe"])

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    # Draw Annotations
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 255), 12)

    # Overlay webcam on slides
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgSmall.shape
    imgSmall[0:hs, w - ws:w] = imgSmall
    imgCurrent = cv2.resize(imgSmall, (300,200))

    cv2.imshow("Slides", imgCurrent)
    
    # Quit condition
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
