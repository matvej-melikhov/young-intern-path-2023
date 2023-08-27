from flask import render_template, request, redirect, url_for
from app import application
from app.config import GAME_START_TIME, now_msk

@application.route("/")
def index():
    return render_template("index.html")

@application.route("/blocker", methods=["GET", "POST"])
def blocker():
    if GAME_START_TIME <= now_msk():
        return redirect(url_for("index"))

    next_endpoint = request.args.get("next")
    if next_endpoint not in application.view_functions:
        next_endpoint = "index"

    delta = max(int((GAME_START_TIME - now_msk()).total_seconds()), 0)
    return render_template("blocker.html", delta=delta, next=next_endpoint)
