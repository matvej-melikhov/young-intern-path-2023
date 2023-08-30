import datetime
import random
from flask import session
from app import db
from app.models import Users, Questions
from app.config import QUESTIONS_AMOUNT

def db_add(obj):
    db.session.add(obj)
    db.session.commit()

def get_question_by_id(question_id):
    question = Questions.query.filter_by(id=question_id).first()
    return question

def get_question_by_hash(user, hash):
    question_id = None
    for q_id, q_hash in user.decodes.items():
        if q_hash == hash:
            question_id = q_id
    question = get_question_by_id(question_id) if question_id else None
    return question

def get_user_from_session():
    user_id = session.get("user_id")
    user = Users.query.filter_by(id=user_id).first()
    return user

def get_ranked_users(only_played=True):
    users = Users.query.order_by(Users.score.desc(), Users.registration_time.desc()).all()
    users = [u for u in users if not u.is_admin]
    if only_played:
        users = [u for u in users if u.answers]
    return users

def is_correct(question: Questions, answer: str):
    return question.answer.lower() == answer.lower()

# Приводит фамилию к женскому роду, если отчество женское (оканчивается на "на").
def feminize_surname(surname, patronymic=""):
    if not surname or not (patronymic or "").endswith("на"):
        return surname
    for masc, fem in (("ский", "ская"), ("цкий", "цкая")):
        if surname.endswith(masc):
            return surname[:-len(masc)] + fem
    if surname.endswith(("ов", "ев", "ёв", "ин", "ын")):
        return surname + "а"
    return surname

class NotEnoughQuestions(Exception):
    pass

def generate_decodes():
    question_ids = [question.id for question in Questions.query.order_by(Questions.weight).all()]
    if len(question_ids) < QUESTIONS_AMOUNT:
        raise NotEnoughQuestions(f"нужно {QUESTIONS_AMOUNT} вопросов, в базе {len(question_ids)}")
    l = list("0123456789abcdefghijklmnopqrstuvwxyz")
    d = dict()
    for question_id in question_ids[:QUESTIONS_AMOUNT]:
        d[question_id] = "".join([random.choice(l) for _ in range(20)])
    return d

def get_answer(user, question, answer, correct):
    # user_answers = pickle.loads(user.answers)
    question_id = question.id
    user_answers = user.answers.copy()
    user_answers[question_id] = {"answer": answer, "is_correct": correct}
    user.answers = user_answers
    if correct:
        user.score += question.weight
    db.session.add(user)
    db.session.commit()
    return question.weight if correct else 0

def get_time_list(seconds):
    hours = str(seconds // 3600).rjust(2, "0")
    minutes = str(seconds % 3600 // 60).rjust(2, "0")
    seconds = str(seconds % 3600 % 60).rjust(2, "0")
    return {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }

def stop_game_function(user):
    answers = user.answers.copy()
    for question_id in user.decodes:
        if question_id not in answers:
            answers[question_id] = {"answer": "", "is_correct": False}
    user.answers = answers
    user.finish_time = datetime.datetime.now()
    db_add(user)