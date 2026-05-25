from flask import Flask, render_template, Response
from picamera2 import Picamera2
from motion import MotionDetector
from ultralytics import YOLO
import cv2
import psutil
import time
import os
import threading

# -------------------
# MODEL + APP INIT
# -------------------
model = YOLO("yolov8n.pt")
app = Flask(__name__)

# -------------------
# CAMERA SETUP
# -------------------
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"size": (320, 240), "format": "RGB888"}))
camera.start()

# -------------------
# MOTION
# -------------------
motion_detector = MotionDetector()
motion_state = {
    "Active": False,
    "last_trigger": 0,
    "event_count": 0
}

# -------------------
# AI STATE
# -------------------
ai_state = {
    "person_detected": False,
    "boxes": []
}

# -------------------
# EVENT STATE (CONVERSATION ENGINE)
# -------------------
event_state = {
    "person_present": False,
    "last_seen": 0,
    "last_announced": 0
}

MOTION_COOLDOWN = 3
latest_frame = None
#
# SPEECH LOG (for Dashboard)
speech_log = {	
	"last_text": "",
	"history": []
}
#

# -------------------
# FRAME STREAM
# -------------------
def generate_frames():
    global latest_frame, motion_state

    while True:
        frame = camera.capture_array()
        latest_frame = frame.copy()

        now = time.time()
        motion = motion_detector.detect_motion(frame)

        # Motion logic
        if motion and (now - motion_state["last_trigger"] > MOTION_COOLDOWN):
            motion_state["Active"] = True
            motion_state["last_trigger"] = now
            motion_state["event_count"] += 1
        elif not motion:
            motion_state["Active"] = False

        # Draw boxes (SAFE)
        for detection in ai_state["boxes"]:
            x1, y1, x2, y2 = detection["box"]
            label = detection["label"]
            confidence = detection["confidence"]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{label} {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() +
               b'\r\n')


# -------------------
# FRAME NORMALIZER
# -------------------
def normalize_frame(frame):
    if frame is None:
        return None

    if len(frame.shape) != 3:
        return None

    # Handle RGBA if it appears
    if frame.shape[-1] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    return frame


# -------------------
# TTS
# -------------------
def speak(text):
    # store for dashboard
    speech_log["last_text"] = text
    speech_log["history"].append({
        "text": text,
        "time": time.time()
    })

    # keep history small
    if len(speech_log["history"]) > 20:
        speech_log["history"].pop(0)

    # speak asynchronously
    threading.Thread(
        target=lambda: os.system(f'espeak-ng "{text}"'),
        daemon=True
    ).start()


# -------------------
# YOLO LOOP (VISION BRAIN)
# -------------------
def run_yolo_loop():
    global latest_frame, ai_state, event_state

    while True:
        if latest_frame is None:
            time.sleep(0.05)
            continue

        frame = normalize_frame(latest_frame.copy())
        if frame is None:
            continue

        results = model(frame, verbose=False)

        person_detected = False
        boxes = []

        now = time.time()

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls]
                conf = float(box.conf[0])

                if conf > 0.6:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

                    boxes.append({
                        "label": label,
                        "confidence": conf,
                        "box": [x1, y1, x2, y2]
                    })

                    if label == "person":
                        person_detected = True

        ai_state["boxes"] = boxes
        ai_state["person_detected"] = person_detected

        # EVENT UPDATE (clean separation)
        if person_detected:
            event_state["person_present"] = True
            event_state["last_seen"] = now
        else:
            if now - event_state["last_seen"] > 2:
                event_state["person_present"] = False

        time.sleep(0.1)


# -------------------
# DECISION LOOP (BRAIN SPEECH)
# -------------------
def decision_loop():
    global event_state

    while True:
        now = time.time()

        if (
            event_state["person_present"]
            and now - event_state["last_announced"] > 10
        ):
            speak("Hello, I see you, human.")
            event_state["last_announced"] = now

        time.sleep(0.2)


# -------------------
# ROUTES
# -------------------
@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/stats")
def stats():
    temps = psutil.sensors_temperatures()
    cpu_temp = round(temps['cpu_thermal'][0].current, 1)

    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "temp": cpu_temp,
        "motion": motion_state["Active"],
        "motion_events": motion_state["event_count"],
        "person": ai_state["person_detected"],
        "speech": speech_log["last_text"],
        "speech_history": speech_log["history"]
    }


@app.route("/")
def home():
    return render_template("index.html")


# -------------------
# THREAD STARTUP (IMPORTANT FIX)
# -------------------
threading.Thread(target=run_yolo_loop, daemon=True).start()
threading.Thread(target=decision_loop, daemon=True).start()


# -------------------
# MAIN
# -------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)