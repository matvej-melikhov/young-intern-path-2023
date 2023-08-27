import random
from flask import render_template, request, redirect, url_for, abort, flash
from app import application, db
from app.models import Users, Questions
from app.config import ADMIN_CODE
from app.decorators import login_required, admin_required
from app.functions import get_user_from_session, db_add

@application.route("/admin", methods=["GET", "POST"])
@login_required
def admin_login():
    user = get_user_from_session()

    if request.method == "POST":
        code = request.form["code"]
        if code.lower() == ADMIN_CODE.lower():
            user.is_admin = 1
            db_add(user)
            return redirect(url_for("profile"))
        abort(403)

    if user.is_admin:
        return redirect(url_for("profile"))
    return render_template("admin-login.html")

@application.route("/admin-logout", methods=["GET", "POST"])
@admin_required
def admin_logout():
    user = get_user_from_session()
    user.is_admin = 0
    db_add(user)
    return redirect(url_for("profile"))

@application.route("/admin-panel", methods=["GET", "POST"])
@login_required
@admin_required
def admin_panel():
    return render_template("admin-panel.html")

@application.route("/new-question", methods=["GET", "POST"])
@admin_required
def new_question():
    if request.method == "POST":
        text = request.form.get("question-text")
        options = [request.form.get("option-1"), request.form.get("option-2"), request.form.get("option-3")]
        answer = request.form.get("answer")
        category = request.form.get("category")
        weight = request.form.get("weight", type=int)

        if not text or not answer or not all(options) or weight is None:
            flash("Заполните все поля, вес должен быть числом.")
        elif answer not in options:
            flash("Правильный ответ должен совпадать с одним из вариантов.")
        else:
            new_question = Questions(id=random.randint(1, 1_000_000_000_000), text=text, options=options,
                                     answer=answer, weight=weight, category=category)
            db_add(new_question)
            flash("Вопрос добавлен!")
    return render_template("new-question.html")

@application.route("/stats")
@admin_required
def stats():
    users = list(Users.query.order_by(Users.score.desc(), Users.registration_time.desc()).all())
    questions = list(Questions.query.order_by(Questions.weight).all())
    return render_template("stats.html", users=users, questions=questions)

@application.route("/delete-user", methods=["GET", "POST"])
@admin_required
def delete_user():
    if request.method == "POST":
        user_ids = [int(id) for id in request.form.getlist("user_id")]
        for user_id in user_ids:
            user = Users.query.filter_by(id=user_id).first()
            if user:
                db.session.delete(user)
        db.session.commit()

    search = request.args.get("search", type=int)
    if search:
        users = Users.query.filter(Users.id.contains(search))
    else:
        users = Users.query.order_by(-Users.score).all()
    current_id = get_user_from_session().id
    return render_template("delete-user.html", users=users, current_id=current_id)
