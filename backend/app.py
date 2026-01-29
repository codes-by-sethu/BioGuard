from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os
import pandas as pd
from deepface import DeepFace
from datetime import datetime
import logging

# --- 1. ROBUST PATH CONFIGURATION ---
# This ensures it finds 'backend/images' even if you start from 'attendance_system'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "images")
LOG_FILE = os.path.join(BASE_DIR, "attendance.csv")
THRESHOLD = 0.50 

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BioGuard")

# --- 2. STARTUP CHECKS ---
# Auto-clean the AI cache so new actress photos are recognized immediately
if os.path.exists(DB_PATH):
    for file in os.listdir(DB_PATH):
        if file.endswith(".pkl"):
            os.remove(os.path.join(DB_PATH, file))
            logger.info("🧹 Cleaned old AI cache.")
else:
    os.makedirs(DB_PATH)
    logger.warning(f"⚠️ Created missing folder: {DB_PATH}")

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Name", "Date", "Time"]).to_csv(LOG_FILE, index=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. HELPER FUNCTIONS ---

def get_user_name(file_path):
    """Extracts 'KATRINA' from 'images/KATRINA/pic.jpg'"""
    path_parts = os.path.normpath(file_path).split(os.sep)
    # The folder name is always the second to last part
    return path_parts[-2].upper() if len(path_parts) >= 2 else "UNKNOWN"

def log_attendance(name):
    """Saves to CSV if the user hasn't been logged today"""
    today = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_csv(LOG_FILE)
    if df[(df['Name'] == name) & (df['Date'] == today)].empty:
        new_entry = pd.DataFrame([[name, today, datetime.now().strftime("%H:%M:%S")]], columns=["Name", "Date", "Time"])
        new_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
        logger.info(f"✅ Attendance logged: {name}")

# --- 4. API ENDPOINTS ---

@app.post("/verify")
async def verify_face(file: UploadFile = File(...)):
    try:
        # Check if DB_PATH is empty
        if not os.listdir(DB_PATH):
            return {"status": "error", "message": "Add photos to backend/images folder!"}

        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # AI Recognition
        results = DeepFace.find(
            img_path=frame, 
            db_path=DB_PATH, 
            enforce_detection=False, 
            model_name="VGG-Face",
            silent=True
        )
        
        if len(results) > 0 and not results[0].empty:
            match = results[0].iloc[0]
            dist = match['distance']
            user_name = get_user_name(match['identity'])

            logger.info(f"🔍 Analyzing: {user_name} | Distance: {dist:.4f}")

            if dist < THRESHOLD:
                log_attendance(user_name)
                return {"status": "success", "user": user_name, "confidence": round(1-dist, 2)}
        
        return {"status": "unknown", "user": "SCANNING..."}
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"status": "error", "message": "Processing..."}

if __name__ == "__main__":
    import uvicorn
    print(f"\n🚀 SYSTEM STARTING...")
    print(f"📂 DATABASE: {DB_PATH}")
    uvicorn.run(app, host="0.0.0.0", port=8000)