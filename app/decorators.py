from flask import session, abort, redirect, url_for, request
from app.config import GAME_START_TIME, now_msk
from app.functions import get_user_from_session

def login_required(function):
    def inner(*args, **kwargs):
        if "user_id" in session:
            return function(*args, **kwargs)
        return abort(401)
    inner.__name__ = function.__name__
    return inner

def game_started(function):
    def inner(*args, **kwargs):
        if GAME_START_TIME <= now_msk():
            return function(*args, **kwargs)
        return redirect(url_for("blocker", next=request.endpoint))
    inner.__name__ = function.__name__
    return inner

def admin_required(function):
    def inner(*args, **kwargs):
        user = get_user_from_session()
        if not user:
            return abort(401)
        if user.is_admin:
            return function(*args, **kwargs)
        else:
            return abort(403)
    inner.__name__ = function.__name__
    return inner
