# 🛡️ BioGuard: AI-Powered Biometric Attendance System

A full-stack facial recognition system that automates attendance logging using a **React** frontend and a **FastAPI** neural engine.



## 🚀 Features
* **Real-time Recognition:** Sub-second facial identification using the VGG-Face model.
* **Cybersecurity UI:** High-tech "Scanning HUD" built with React and CSS animations.
* **Automated Logging:** Persistence layer managed via Pandas to record timestamps in CSV.
* **Decoupled Architecture:** Scalable REST API design for separate frontend/backend management.

## 🛠️ Tech Stack
* **Frontend:** React.js, Axios, React-Webcam
* **Backend:** Python, FastAPI, Uvicorn
* **AI Engine:** DeepFace (TensorFlow/Keras)
* **Data:** Pandas, OpenCV

## 📂 Project Structure
```text
attendance_system/
├── backend/
│   ├── app.py           # FastAPI Neural Engine
│   ├── images/          # Face database (Identity folders)
│   └── attendance.csv   # Attendance logbook
└── frontend/
    ├── src/             # React logic & UI
    └── package.json     # JS dependencies

⚙️ Setup & Installation
1. Backend Setup

```
cd backend
pip install fastapi uvicorn deepface tf-keras opencv-python pandas
python app.py
```

2. Frontend Setup
```
cd frontend
npm install
npm start
```

📊 How it Works
Capture: The React frontend captures a frame from the webcam every 2 seconds.

Transfer: The frame is sent as a Blob via an Axios POST request to the /verify endpoint.

Analysis: The Backend uses DeepFace to calculate the "Euclidean Distance" between the live frame and the images/ database.

Action: If the distance is below the threshold (0.50), the system logs the entry and triggers a success state in the UI.

Created by Sethu