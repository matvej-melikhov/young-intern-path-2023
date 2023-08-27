from flask import render_template
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
