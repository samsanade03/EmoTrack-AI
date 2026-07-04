import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from deepface import DeepFace
from collections import deque
import os
import pyttsx3
import time


# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ----- TEXT TO SPEECH ENGINE -----
engine = pyttsx3.init()
engine.setProperty('rate', 165)  # Voice speed
engine.setProperty('volume', 1.0)

# ----- CAMERA SETUP -----
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print("Camera not detected")
    exit()

engine.say("Camera opened successfully")
engine.runAndWait()

# ----- HAND DETECTOR -----
hand_detector = HandDetector(detectionCon=0.3, maxHands=2)

# ----- FACE DETECTOR -----
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ----- EMOTION HISTORY -----
emotion_history = deque(maxlen=12)
last_spoken_emotion = None
last_speak_time = 0

# ----- SMOOTH EMOTION FUNCTION -----
def smooth_emotion(new_emotion):
    emotion_history.append(new_emotion)
    return max(set(emotion_history), key=emotion_history.count)

# ----- EMOTION VOICE AI -----
def speak_emotion(emotion):
    responses = {
        "happy": "You look happy today!",
        "sad": "Everything will be okay. Stay strong.",
        "angry": "Take a deep breath and relax.",
        "surprise": "Oh! You look surprised!",
        "neutral": "You seem calm and relaxed.",
        "fear": "Try not to worry.",
        "disgust": "Hmm, something seems unpleasant."
    }

    if emotion in responses:
        engine.say(responses[emotion])
        engine.runAndWait()


# ----- MAIN LOOP -----
while True:
    ret, img = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Flip camera for mirror effect
    

    # ----- HAND DETECTION -----
    hands, img = hand_detector.findHands(img, draw=True)

    if hands:
        for hand in hands:
            hand_type = hand["type"]   # Correct way to get Left or Right

            if hand_type == "Left":
                cv2.putText(img, "Left Hand Detected", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            elif hand_type == "Right":
                cv2.putText(img, "Right Hand Detected", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    hands_up = bool(hands)

    # ----- FACE & EMOTION DETECTION (ONLY IF NO HANDS) -----
    if not hands_up:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            face_roi = img[y:y+h, x:x+w]

            try:
                result = DeepFace.analyze(
                    face_roi,
                    actions=['emotion'],
                    enforce_detection=False
                )

                emotion = result[0]['dominant_emotion']
                sm_emotion = smooth_emotion(emotion)

                # ----- SPEAK ONLY IF EMOTION CHANGED -----
                current_time = time.time()
                if sm_emotion != last_spoken_emotion and current_time - last_speak_time > 3:
                    speak_emotion(sm_emotion)
                    last_spoken_emotion = sm_emotion
                    last_speak_time = current_time

                # ----- DRAW FACE BOX -----
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 100, 255), 2)

                # Emotion Label
                cv2.putText(img, sm_emotion.upper(), (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 255), 2)

            except Exception as e:
                print("DeepFace error:", e)

    # ----- WINDOW TITLE -----
    cv2.putText(img, "Human Emotion Monitoring System - By Shalom Sanade", (20, 680),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Human Emotion Monitoring System", img)

    if cv2.waitKey(1) & 0xFF == ord('e'):
        break


# ----- CLEANUP -----
print("Closing camera...")

cap.release()
cv2.destroyAllWindows()

time.sleep(0.5)  # Let OpenCV fully close

print("Camera closed successfully")

# ----- SAFE VOICE EXIT -----
try:
    exit_engine = pyttsx3.init()
    exit_engine.setProperty('rate', 165)
    exit_engine.setProperty('volume', 1.0)

    exit_engine.say("Camera closed. Thanks for using this system. Goodbye!")
    exit_engine.runAndWait()
    exit_engine.stop()

    print("Exit voice played successfully")

except Exception as e:
    print("Voice error:", e)

# ----- SAFE MESSAGE BOX -----
try:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "Thank You",
        "This system is developed by Shalom Sanade.\nThank you for using it!"
    )

    root.destroy()
    print("Message box shown")

except Exception as e:
    print("Tkinter error:", e)