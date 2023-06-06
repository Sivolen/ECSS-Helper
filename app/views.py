from flask import (
    render_template,
    request,
    flash,
    # jsonify,
    session,
    url_for,
    redirect,
)

from app import app
from app.modules.ldap import LDAP_FLASK, check_auth
from app.utils import process


@app.route("/", methods=["POST", "GET"])
@check_auth
def index():
    session["prev_url"] = request.url
    navigation = True
    if request.method == "GET":
        return render_template("index.html", navigation=navigation)
    if request.method == "POST" and request.files.get("file"):
        file = request.files["file"].stream.read().decode("utf-8").split("\n")
        result = process(file=file)
        return render_template("index.html", navigation=navigation, result=result)
    return render_template("index.html", navigation=navigation)


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    Login page
    :return:
    """
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
