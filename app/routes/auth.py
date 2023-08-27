import datetime
from flask import render_template, request, redirect, url_for, session, flash
from app import application
from app.models import Users
from app.decorators import login_required, game_started
from app.functions import get_user_from_session, db_add, generate_decodes, NotEnoughQuestions

@application.route("/login", methods=["GET", "POST"])
@game_started
def login():
    if get_user_from_session():
        return redirect(url_for("map"))

    if request.method == "POST":
        try:
            decodes = generate_decodes()
        except NotEnoughQuestions:
            flash("Игра ещё не готова: администратор не добавил достаточно вопросов.")
            return render_template("login.html")

        user = Users(name=request.form['name'], last_name=request.form['last_name'],
                     middle_name=request.form['middle_name'], faculty=request.form['faculty'],
                     group=request.form['group'], registration_time=datetime.datetime.now(),
                     is_admin=0, score=0, answers=dict(), decodes=decodes)
        db_add(user)  # id назначает БД (autoincrement)
        session["user_id"] = user.id
        session["user_name"] = user.name

        flash("Начинайте искать QR-коды!")
        return redirect(url_for("map"))

    return render_template("login.html")

@application.route("/logout")
@login_required
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    return redirect(url_for("index"))
