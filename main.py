import cv2
import mediapipe as mp
import os
import pandas as pd
import threading
from deepface import DeepFace
from datetime import datetime

# --- CONFIG ---
DB_PATH = "images"
LOG_FILE = "attendance.csv"
THRESHOLD = 0.35

# --- Liveness State ---
blink_count = 0
face_verified = False
current_user = "Scanning..."
is_processing = False

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

def log_attendance(name):
    today = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_csv(LOG_FILE)
    if df[(df['Name'] == name) & (df['Date'] == today)].empty:
        new_entry = pd.DataFrame([[name, today, datetime.now().strftime("%H:%M:%S")]], columns=["Name", "Date", "Time"])
        new_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
        return True
    return False

def check_face(frame):
    global current_user, face_verified, is_processing
    try:
        results = DeepFace.find(img_path=frame, db_path=DB_PATH, enforce_detection=False, silent=True)
        if len(results) > 0 and not results[0].empty:
            dist = results[0]['distance'][0]
            if dist < THRESHOLD:
                path = results[0]['identity'][0]
                current_user = os.path.basename(path).split('.')[0].upper()
                face_verified = True
            else:
                current_user = "Unknown"
                face_verified = False
        else:
            face_verified = False
    except: pass
    is_processing = False

# --- Start System ---
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    # 1. Blink Detection Logic
    if results.multi_face_landmarks:
        mesh_coords = results.multi_face_landmarks[0].landmark
        # Eye landmarks (Upper and Lower lids)
        left_eye_top = mesh_coords[159].y
        left_eye_bottom = mesh_coords[145].y
        
        eye_distance = left_eye_bottom - left_eye_top
        
        # If distance is very small, it's a blink
        if eye_distance < 0.012: # Threshold for a closed eye
            blink_count += 1
            cv2.putText(frame, "BLINK DETECTED!", (w-200, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 2. Run Face Recognition in Background
    if not is_processing:
        is_processing = True
        threading.Thread(target=check_face, args=(frame.copy(),), daemon=True).start()

    # 3. Final Verification Logic
    # Must have matched a face AND blinked at least once
    if face_verified and blink_count > 0:
        log_attendance(current_user)
        status_text = f"VERIFIED: {current_user}"
        color = (0, 255, 0)
    else:
        status_text = f"Liveness Check: Blink Needed" if face_verified else f"Status: {current_user}"
        color = (0, 165, 255)

    # UI Rendering
    cv2.rectangle(frame, (0, 0), (w, 50), (30, 30, 30), -1)
    cv2.putText(frame, status_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    cv2.imshow("Anti-Spoofing Attendance System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()