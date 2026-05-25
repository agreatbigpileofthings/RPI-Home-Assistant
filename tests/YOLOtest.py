from ultralytics import YOLO
from picamera2 import Picamera2
import cv2

model = YOLO("yolov8n.pt")


camera = Picamera2()
config = camera.create_preview_configuration(
    main={"size": (640,480), "format": "RGB888"})
camera.configure(config)
camera.start()
frame = camera.capture_array()
results = model(frame)

for box in results[0].boxes:
    cls = int(box.cls[0])
    conf = box.conf[0]
    print(f"Detected: {model.names[cls]} ({conf:.2f})")

#print(frame.shape)
#print(results)