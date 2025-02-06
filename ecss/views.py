import logging

import chardet

from flask import (
    render_template,
    request,
    flash,
    # jsonify,
    session,
    url_for,
    redirect,
)

from ecss import ecss
from ecss.modules.ldap import LDAP_FLASK, check_auth
from ecss.utils import process

logging.basicConfig(level=logging.DEBUG)


@ecss.route("/", methods=["POST", "GET"])
@check_auth
# def index():
#     session["name"] = "index"
#     session["prev_url"] = request.url
#     navigation = True
#     if request.method == "GET":
#         return render_template("index.html", navigation=navigation)
#     if request.method == "POST" and request.files.get("file"):
#         file = request.files["file"].stream.read().decode("utf-8").split("\n")
#         result = process(file=file)
#         return render_template("index.html", navigation=navigation, result=result)
#     return render_template("index.html", navigation=navigation)
def index():
    session["name"] = "index"
    session["prev_url"] = request.url
    navigation = True

    if request.method == "POST" and request.files.get("file"):
        file = request.files["file"]

        # Check file extension
        if "." not in file.filename or file.filename.split(".")[-1].lower() not in {
            "txt",
            "csv",
            "log",
        }:
            return render_template(
                "index.html", navigation=navigation, error="Invalid file format"
            )

        try:
            file_bytes = file.read()
            detected = chardet.detect(file_bytes)
            encoding = detected.get("encoding", "utf-8")

            # Decoding with replacement of unreadable characters
            file_content = file_bytes.decode(encoding, errors="replace").split("\n")

            result = process(file=file_content)
            return render_template("index.html", navigation=navigation, result=result)

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return render_template(
                "index.html",
                navigation=navigation,
                error=f"Error processing file: {str(e)}",
            )

    return render_template("index.html", navigation=navigation)


@ecss.route("/login", methods=["POST", "GET"])
def login():
    """
    Login page
    :return:
    """
    session["name"] = "login"
    prev_url = session.get("prev_url")
    if "user" not in session or session["user"] == "":
        if request.method == "POST":
            page_email = request.form["email"]
            page_password = request.form["password"]
            ldap_connect = LDAP_FLASK(page_email, page_password)
            if ldap_connect.bind():
                session["user"] = page_email
                flash("You were successfully logged in", "success")
                if not prev_url:
                    return redirect(url_for("index"))
                return redirect(prev_url)
            else:
                flash("May be the password is incorrect?", "danger")
                return render_template("login.html")
        else:
            return render_template("login.html")
    else:
        session["user"] = ""
        flash("You were successfully logged out", "warning")
        # return redirect(url_for("index"))
        if not prev_url:
            return redirect(url_for("index"))
        return redirect(prev_url)
