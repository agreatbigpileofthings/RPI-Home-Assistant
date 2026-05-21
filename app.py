from flask import Flask, render_template
import psutil

app= Flask(__name__)

@app.route("/")
def home():
        cpu = psutil.cpu_percent()
        ram=psutil.virtual_memory().percent
        
        return render_template(
            "index.html",
            cpu=cpu,
            ram=ram
        )

app.run(host="0.0.0.0",port=5000)
        