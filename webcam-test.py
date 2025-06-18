import cv2
import math
import mediapipe as mp
from cntrler import Master_control
# Initialize MediaPipe
mc  = Master_control()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, 
                      min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def recognize_gesture(hand_landmarks, image_width, image_height):
    landmarks = []
    for landmark in hand_landmarks.landmark:
        landmarks.append((int(landmark.x * image_width), 
                         int(landmark.y * image_height),
                         landmark.z))
    
    # Key points
    wrist = landmarks[0]
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Helper functions
    def distance(p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    
    def is_finger_extended(tip, pip, mcp, threshold=0.8):
        # Check if finger is extended by comparing distances
        tip_pip_dist = distance(tip, pip)
        tip_mcp_dist = distance(tip, mcp)
        return tip_mcp_dist > threshold * tip_pip_dist
    
   
        # finger placement calculator
    index_folded = not is_finger_extended(landmarks[8], landmarks[6], landmarks[5])
    middle_folded = not is_finger_extended(landmarks[12], landmarks[10], landmarks[9])
    ring_folded = not is_finger_extended(landmarks[16], landmarks[14], landmarks[13])
    pinky_folded = not is_finger_extended(landmarks[20], landmarks[18], landmarks[17])
    thumb_folded = distance(thumb_tip, landmarks[2]) < distance(thumb_tip, wrist)
    folded =  [thumb_folded,index_folded,middle_folded,ring_folded,pinky_folded]
    
    
        # finger placement calculator
    index_extended = is_finger_extended(landmarks[8], landmarks[6], landmarks[5])
    middle_extended = is_finger_extended(landmarks[12], landmarks[10], landmarks[9])
    ring_extended =  is_finger_extended(landmarks[16], landmarks[14], landmarks[13])
    pinky_extended = is_finger_extended(landmarks[20], landmarks[18], landmarks[17])
    thumb_extended = not distance(thumb_tip, landmarks[2]) < distance(thumb_tip, wrist)
    extended = [thumb_extended,index_extended,middle_extended,ring_extended,pinky_extended]

    print("Closed:",folded)
    print("Extended:",extended)

    if(distance(thumb_tip,index_tip)>20 and folded[2] and folded[3] and folded[4] ):
        # Usage
        mc.zoom_in() 
        return "Zoom Out"
    elif(distance(thumb_tip,index_tip)<50 and folded[2] and folded[3] and folded[4]):
        mc.zoom_out()
        return "Zoom In"
    elif(folded[0] and extended[1] and folded[2] and folded[3] and folded[4]):
        mc.click_on_application("Gesture Recognition", 100, 100, click_delay=1.5)
        #mc.switch_app()
        return "Click"
    elif(extended[0] and folded[1] and extended[2] and folded[3] and folded[4]):
        x,y = 100,100 
        mc.move_an_application("Gesture Recognition",x,y)
        x +=50
        y +=501
        return "Drag"
# elif(extended[0] and folded[1] and folded[2] and folded[3] and folded[4]):
 #       return "Thums Up"
    
    
    

# Main loop
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue
    
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get gesture result
            h, w = image.shape[:2]
            gesture = recognize_gesture(hand_landmarks, w, h)
            
            # Display gesture
            text_position = (int(hand_landmarks.landmark[0].x * w), 
                           int(hand_landmarks.landmark[0].y * h - 30))
            cv2.putText(image, gesture, text_position, 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Gesture Recognition', cv2.resize(image,(400,400)))
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()