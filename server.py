from flask import Flask, send_file
import subprocess

app = Flask(__name__)

@app.route("/sitemap.xml")
def sitemap():
    return send_file("sitemap.xml", mimetype="application/xml")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def streamlit_app(path):
    # avvia streamlit (solo in ambiente Render)
    return subprocess.run(["streamlit", "run", "streamlit_app.py"]).stdout
