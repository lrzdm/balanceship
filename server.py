from flask import Flask, send_file, redirect
import subprocess
import threading
import os

app = Flask(__name__)

@app.route("/sitemap.xml")
def sitemap():
    return send_file("sitemap.xml", mimetype="application/xml")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def streamlit_redirect(path):
    return redirect(f"/streamlit/{path}", code=302)

def run_streamlit():
    os.system("streamlit run homepage.py --server.port=8501 --server.headless=true")

if __name__ == "__main__":
    threading.Thread(target=run_streamlit).start()
    app.run(host="0.0.0.0", port=8000)
