from flask import (
    render_template,
    request,
    # flash,
    # jsonify,
    # session,
    # url_for,
    # redirect,
)

from app import app
from app.utils import process


@app.route("/", methods=["POST", "GET"])
def index():
    navigation = True
    if request.method == "GET":
        return render_template("index.html", navigation=navigation)
    if request.method == "POST" and request.form["file"]:
        file = request.form.get("file")
        process(file=file)
        return render_template("index.html", navigation=navigation)
    return render_template("index.html", navigation=navigation)
