import datetime
from flask import render_template, request, redirect, url_for, abort, flash
from app import application
from app.models import Questions
from app.config import QUESTIONS_AMOUNT, MAX_SCORE
from app.decorators import login_required, game_started
from app.functions import (get_user_from_session, get_question_by_hash, is_correct,
                           get_answer, get_time_list, get_ranked_users, stop_game_function, db_add)

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

@application.route("/scanner")
@game_started
@login_required
def scanner():
    return render_template("scanner.html")

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

@application.route("/stop-game", methods=["GET", "POST"])
@game_started
@login_required
def stop_game():
    if request.method == "POST":
        user = get_user_from_session()
        stop_game_function(user)
        return redirect(url_for("result"))
    return render_template("stop-game.html")
