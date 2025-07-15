from flask import Flask, send_file
import threading
import subprocess
import os

app = Flask(__name__)

@app.route("/sitemap.xml")
def serve_sitemap():
    path = os.path.join(os.path.dirname(__file__), "sitemap.xml")
    return send_file(path, mimetype="application/xml")

def run_streamlit():
    subprocess.run(["streamlit", "run", "homepage.py", "--server.port=8501", "--server.headless=true"])

if __name__ == "__main__":
    threading.Thread(target=run_streamlit).start()
    app.run(host="0.0.0.0", port=8000)
