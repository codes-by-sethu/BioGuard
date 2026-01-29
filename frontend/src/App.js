import React, { useRef, useState, useEffect } from 'react';
import Webcam from "react-webcam";
import axios from 'axios';
import './App.css';

function App() {
  const webcamRef = useRef(null);
  const [identity, setIdentity] = useState("SCANNING...");
  const [isMatch, setIsMatch] = useState(false);

  // Logic to capture frame and send to FastAPI
  const verifyIdentity = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        // 1. Prepare the image as a "file" for Python
        const blob = await fetch(imageSrc).then(res => res.blob());
        const formData = new FormData();
        formData.append("file", blob, "frame.jpg");

        try {
          // 2. Call your FastAPI Backend
          const res = await axios.post("http://localhost:8000/verify", formData);
          
          if (res.data.status === "success") {
            setIdentity(res.data.user);
            setIsMatch(true);
          } else {
            setIdentity("UNKNOWN");
            setIsMatch(false);
          }
        } catch (err) {
          setIdentity("OFFLINE (Check Backend)");
          setIsMatch(false);
        }
      }
    }
  };

  // Run the verification every 2 seconds
  useEffect(() => {
    const interval = setInterval(verifyIdentity, 2000); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <h1 className="title">BIOMETRIC ACCESS CONTROL</h1>
      
      <div className={`webcam-box ${isMatch ? 'match' : ''}`}>
        <div className="scan-line"></div>
        <Webcam 
          ref={webcamRef} 
          screenshotFormat="image/jpeg" 
          mirrored={true} 
        />
      </div>

      <div className="info-display">
        <h3>SUBJECT IDENTIFIED:</h3>
        <div className="status-text" style={{ color: isMatch ? '#238636' : '#f85149' }}>
          {identity}
        </div>
      </div>
    </div>
  );
}

export default App;