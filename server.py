from flask import Flask, send_file


app = Flask(__name__)

@app.route("/sitemap.xml")
def sitemap():
    return send_file("sitemap.xml", mimetype="application/xml")
