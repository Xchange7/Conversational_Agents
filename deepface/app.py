from flask import Flask, jsonify, Response
from threading import Thread
import cv2
import time
from deepface import DeepFace
import numpy as np

app = Flask(__name__)

# Global Variables
current_emotion = "unknown"
running = True
show_display = True  # Set to False for headless environments
latest_frame = None
latest_processed_frame = None

def capture_emotion():
    global current_emotion, running, latest_frame, latest_processed_frame
    # Init Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot Open Camera")
        running = False
        return
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Cannot Read Frame from Camera")
            break
            
        # Store original frame
        latest_frame = frame.copy()
        
        try:
            # Face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw rectangle around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Emotion Analysis
            result = DeepFace.analyze(latest_frame, actions=['emotion'], enforce_detection=False)
            if isinstance(result, list):
                result = result[0]
            current_emotion = result['dominant_emotion']
            
            # Add emotion text to frame
            cv2.putText(frame, f"Emotion: {current_emotion}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Store processed frame
            latest_processed_frame = frame.copy()
            
            # Display if enabled
            if show_display:
                cv2.imshow('Emotion Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print("Exception:", e)
            current_emotion = "error"
            if frame is not None:
                cv2.putText(frame, "No face detected", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                latest_processed_frame = frame.copy()
                
                if show_display:
                    cv2.imshow('Emotion Detection', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        
        # Process at reasonable rate
        time.sleep(0.03)  # ~30 fps
    
    cap.release()
    if show_display:
        cv2.destroyAllWindows()

def generate_frames():
    global latest_processed_frame
    while running:
        if latest_processed_frame is not None:
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', latest_processed_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03)  # ~30 fps

@app.route('/emotion', methods=['GET'])
def get_emotion():
    """return emotion detected"""
    print("emotion detected:", current_emotion)
    return jsonify({"emotion": current_emotion})

@app.route('/video_feed')
def video_feed():
    """Video streaming route for web integration"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Capture emotion by another thread
    t = Thread(target=capture_emotion)
    t.daemon = True
    t.start()
    # Use Flask service，Listen to 0.0.0.0:5005
    app.run(host='0.0.0.0', port=5005)


