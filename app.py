from flask import Flask, render_template, Response
from picamera2 import Picamera2
import cv2
import psutil

app= Flask(__name__)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"size": (640,480)}))
camera.start()

def generate_frames():
	while True:
		frame = camera.capture_array()
		##Convert to JPG
		ret,buffer = cv2.imencode('.jpg',frame)
		frame = buffer.tobytes()
		yield (b'--frame\r\n'
			b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video')
def video():
	return Response(generate_frames(),
		mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stats")
def stats():
	temps = psutil.sensors_temperatures()
	cpu_temp = temps['cpu_thermal'][0].current
	cpu_temp = round(cpu_temp,1)

	return {
	"cpu": psutil.cpu_percent(),
	"ram": psutil.virtual_memory().percent,
	"temp": cpu_temp
}


@app.route("/")
def home():
	cpu = psutil.cpu_percent()
	ram=psutil.virtual_memory().percent

	return render_template(
		"index.html",
		cpu=cpu,
		ram=ram,
		camera=camera
	)

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5000)
        
