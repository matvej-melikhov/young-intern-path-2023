import datetime
import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///base.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

QUESTIONS_AMOUNT = 30
MAX_SCORE = 90
ADMIN_CODE = os.environ.get("ADMIN_CODE", "hamapa23")

# Москва — фиксированный UTC+3 (с 2014 года без перехода на летнее время),
# поэтому обходимся без зависимости от базы tzdata.
MSK = datetime.timezone(datetime.timedelta(hours=3))

def now_msk():
    """Текущее московское время (timezone-aware)."""
    return datetime.datetime.now(MSK)

def _parse_start_time(raw, default):
    """Разбирает время старта из env. Принимает ISO-формат, напр.
    "2026-09-01T11:00" или "2026-09-01 11:00:00". Время без таймзоны
    трактуется как московское."""
    if not raw:
        return default
    try:
        dt = datetime.datetime.fromisoformat(raw.strip())
    except ValueError:
        return default
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=MSK)
    return dt.astimezone(MSK)

# Время старта игры задаётся переменной окружения GAME_START_TIME (московское время).
# Значение по умолчанию — в прошлом, т.е. игра считается уже начатой.
GAME_START_TIME = _parse_start_time(
    os.environ.get("GAME_START_TIME"),
    datetime.datetime(2023, 9, 1, 9, 30, tzinfo=MSK),
)
