import os
from flask import Flask, send_file

app = Flask(__name__)

@app.route("/sitemap.xml")
def sitemap():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "sitemap.xml")
    return send_file(file_path, mimetype="application/xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # leggi la porta da env var, default 5000
    app.run(host="0.0.0.0", port=port)
