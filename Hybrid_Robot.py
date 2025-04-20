import cv2
import mediapipe as mp
import serial
import time
import speech_recognition as sr
import pyttsx3
import os
from openai import OpenAI
from dotenv import load_dotenv

# ========== LOAD ENVIRONMENT VARIABLES ==========
load_dotenv()

com_port = os.getenv("COM_PORT")
baudrate = int(os.getenv("BAUDRATE"))
token = os.getenv("LLM_API_KEY")
endpoint = os.getenv("ENDPOINT")
model = os.getenv("MODEL")

# ========== GPT CLIENT ==========
client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# ========== INITIALIZATION ==========
engine = pyttsx3.init()
try:
    bt = serial.Serial(com_port, baudrate)
    print(f" Connected to {com_port}")
    time.sleep(2)
except serial.SerialException:
    print(f" Failed to connect to {com_port}")
    bt = None

# ========== VOICE UTILITIES ==========
def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_voice_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(" Say a command...")
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        print(" You said:", command)
        return command
    except sr.UnknownValueError:
        print(" Sorry, I didn’t get that.")
        return None

def ask_llm(prompt):
    print(" Asking LG-AI LLM")
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Convert natural language instructions to robot movement commands."},
                {"role": "user", "content": f"{prompt}. Return the result as a list like ['W','A','S']."}
            ],
            temperature=0.8,
            top_p=1
        )
        reply = res.choices[0].message.content
        print(" LLM Response:", reply)
        return eval(reply)
    except Exception as e:
        print(" LLM Error:", e)
        return []

def send_command(cmd):
    if bt:
        bt.write(cmd.encode())
        print(f"📤 Sent: {cmd}")
    else:
        print(f" BT not connected. Would've sent: {cmd}")

# ========== GESTURE DETECTION ==========
def gesture_mode():
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    last_command = None

    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            gesture = "Neutral"

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = hand_landmarks.landmark
                    wrist_y = landmarks[mp_hands.HandLandmark.WRIST].y * h
                    index_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * h
                    pinky_y = landmarks[mp_hands.HandLandmark.PINKY_TIP].y * h
                    thumb_x = landmarks[mp_hands.HandLandmark.THUMB_TIP].x * w
                    index_x = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * w

                    if index_y < wrist_y - 50:
                        gesture = "Hand Up"
                    elif index_y > wrist_y + 50:
                        gesture = "Hand Down"
                    elif index_x < thumb_x - 50:
                        gesture = "Tilt Left"
                    elif index_x > thumb_x + 50:
                        gesture = "Tilt Right"
                    else:
                        gesture = "Neutral"

                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            command_map = {
                "Hand Up": 'W', #forward
                "Hand Down": 'S', #backward
                "Tilt Left": 'A', # left
                "Tilt Right": 'D', # right
                "Neutral": 'X' # stop
            }

            current_command = command_map.get(gesture, 'X')

            if current_command != last_command:
                print(f" Gesture: {gesture} → Sending: {current_command}")
                send_command(current_command)
                last_command = current_command

            cv2.putText(frame, f"Gesture: {gesture}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Gesture Control", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# ========== VOICE MODE ==========
def voice_mode():
    text = get_voice_command()
    if not text:
        speak("Please try again.")
        return

    commands = ask_llm(f"Convert this to robot commands: {text}")
    if not commands:
        speak("I couldn't understand your command.")
        return

    for c in commands:
        send_command(c)
        time.sleep(1)

# ========== MAIN MENU ==========
def main():
    print("🤖 Welcome to Hybrid Gesture + Voice Robot Control")
    while True:
        mode = input("Choose mode (gesture/voice/quit): ").strip().lower()
        if mode == "gesture":
            gesture_mode()
        elif mode == "voice":
            voice_mode()
        elif mode == "quit":
            break
        else:
            print("Invalid option.")

    if bt:
        bt.close()
    print(" Disconnected.")

if __name__ == "__main__":
    main()
