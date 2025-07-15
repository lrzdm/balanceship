from flask import Flask, send_file
import subprocess
import threading
import os

app = Flask(__name__)

@app.route("/sitemap.xml")
def sitemap():
    return send_file("sitemap.xml", mimetype="application/xml")

def run_streamlit():
    os.system("streamlit run streamlit_app.py --server.port=8501 --server.headless=true")

if __name__ == "__main__":
    threading.Thread(target=run_streamlit).start()
    app.run(host="0.0.0.0", port=8000)
