import datetime
from flask import render_template
from app import application
from app.decorators import login_required, game_started
from app.functions import get_ranked_users, get_time_list, get_user_from_session

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
