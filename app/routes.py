from flask import render_template, flash
from app.functions import *
from app.config import *
from app import application

@application.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@application.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@application.errorhandler(401)
def not_auth_error(error):
    return render_template('401.html'), 401

@application.route("/")
def index():
    return render_template("index.html")

@application.route("/map")
@game_started
@login_required
def map():
    return render_template("map.html")

@application.route("/profile")
@game_started
@login_required
def profile():
    question_ids = [question.id for question in Questions.query.order_by(Questions.weight).all()]
    user = get_user_from_session()
    return render_template("profile.html", user=user, question_ids=question_ids,
                           questions_amount=QUESTIONS_AMOUNT, max_score=MAX_SCORE)

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

@application.route("/scanner")
@game_started
@login_required
def scanner():
    return render_template("scanner.html")

@application.route("/logout")
@login_required
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    return redirect(url_for("index"))

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

@application.route("/question", methods=["GET", "POST"])
@game_started
@login_required
def question():
    user = get_user_from_session()
    hash = request.args.get("hash")
    current_question = get_question_by_hash(user, hash)

    if len(user.answers) == QUESTIONS_AMOUNT:
        return redirect(url_for("result"))

    if not hash:
        abort(404)

    if not current_question:
        return abort(404)

    if hash not in user.decodes.values(): # на самом деле здесь должна быть не 403. не факт, что такой хеш, у кого-то есть
        abort(403)

    question_number = list(Questions.query.order_by(Questions.weight)).index(current_question) + 1
    reading = True if current_question.id in user.answers else False

    if request.method == "POST":
        if current_question.id in user.answers:
            abort(403)
        answer = request.form.get("answer")
        if answer not in (current_question.options or []):
            abort(400)
        bonus = get_answer(user, current_question, answer, correct=is_correct(current_question, answer))

        flash(f"+{bonus} к очкам! Переходи к следующей локации!" if bonus else "Ответ принят! Переходи к следующей локации!")

        if len(user.answers) == QUESTIONS_AMOUNT:
            if not user.finish_time:
                user.finish_time = datetime.datetime.now()
                db_add(user)
            return redirect(url_for("result"))
        return redirect(url_for("map"))

    return render_template("question.html", question=current_question,
                           question_number=question_number, user=user, reading=reading)

@application.route("/gen", methods=["GET", "POST"])
@game_started
@login_required
def generate_question_url():
    question_id = request.args.get("id")

    if not question_id:
        abort(404)

    user = get_user_from_session()
    hash = user.decodes.get(int(question_id))

    if not hash:
        abort(404)

    return redirect(url_for("question", hash=hash)) #render_template("question.html", question=current_question, user=user, reading=reading)

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

@application.route("/result")
@game_started
@login_required
def result():
    user = get_user_from_session()
    if not user or len(user.answers) != QUESTIONS_AMOUNT or not user.finish_time:
        abort(404)
    correct_answers = [answer for answer in user.answers.values() if answer["is_correct"]]
    duration = int((user.finish_time - user.registration_time).total_seconds())
    time_list = get_time_list(duration)
    ranked = get_ranked_users()
    place = next((i + 1 for i, u in enumerate(ranked) if u.id == user.id), len(ranked))
    total_players = len(ranked)
    return render_template("result.html", user=user, correct_answers=correct_answers,
                           time_list=time_list, questions_amount=QUESTIONS_AMOUNT, max_score=MAX_SCORE,
                           place=place, total_players=total_players)

@application.route("/rating")
@game_started
def rating():
    users = get_ranked_users(only_played=False)
    return render_template("rating.html", users=users)

@application.route("/mobile-rating")
@game_started
@login_required
def mobile_rating():
    users = get_ranked_users()
    times = [get_time_list(int(((user.finish_time or datetime.datetime.now()) - user.registration_time).total_seconds())) for user in users]
    cur_user = get_user_from_session()
    return render_template("rating-mobile.html", users=users, cur_user=cur_user, times=times)

@application.route("/stop-game", methods=["GET", "POST"])
@game_started
@login_required
def stop_game():
    if request.method == "POST":
        user = get_user_from_session()
        stop_game_function(user)
        return redirect(url_for("result"))
    return render_template("stop-game.html")

@application.route("/blocker", methods=["GET", "POST"])
def blocker():
    if GAME_START_TIME <= now_msk():
        return redirect(url_for("index"))

    next_endpoint = request.args.get("next")
    if next_endpoint not in application.view_functions:
        next_endpoint = "index"

    delta = max(int((GAME_START_TIME - now_msk()).total_seconds()), 0)
    return render_template("blocker.html", delta=delta, next=next_endpoint)