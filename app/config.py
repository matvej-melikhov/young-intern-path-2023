import datetime
import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///base.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

QUESTIONS_AMOUNT = 30
MAX_SCORE = 90
GAME_START_TIME = datetime.datetime(2023, 9, 1, 9, 30, 00)
ADMIN_CODE = os.environ.get("ADMIN_CODE", "hamapa23")
