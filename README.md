<h1>"The Young Intern Path" QR Quest</h1>

<img src="docs/sokt-quiz-overview.png" alt="The Young Intern's Path" width="100%">

<div align="center">
<p>
  <a href="https://sokt-profcom.ru/"><img alt="Website" src="https://img.shields.io/badge/Website-sokt--profcom.ru-1CBC78?style=for-the-badge&logo=googlechrome&logoColor=white"></a>
  <a href="https://vk.com/wall-113893523_4181"><img alt="Announcement" src="https://img.shields.io/badge/VK-Announcement-0077FF?style=for-the-badge&logo=vk&logoColor=white"></a>
  <a href="https://vk.com/wall-113893523_4194"><img alt="Winners" src="https://img.shields.io/badge/VK-Winners-0077FF?style=for-the-badge&logo=vk&logoColor=white"></a>
  <a href="README_RUS.md"><img alt="Russian README" src="https://img.shields.io/badge/GitHub-Russian README-2F2F2F?style=for-the-badge&logo=github&logoColor=white"></a>
</p>

</div>

## 📖 About

A web application for running the interactive **"The Young Intern Path" QR Quest** — an
event by the Student Career and Employment Office (SOKT) and the Trade Union Committee of
Students and Postgraduates of ETU "LETI", timed to Freshman Day.

Participants register on the website, move around the university campus in search of purple
QR codes, scan them, and answer questions about careers, the university, and student life.
Correct answers earn points; the current standings are shown in real time. At the end of the
quest, the Trade Union Committee awards the top performers.

| Parameter | Value |
|-----------|-------|
| 📅 Date & time | September 1, 2023, 11:00 |
| 📍 Venue | ETU "LETI" courtyard, Saint Petersburg |
| 👥 Participants | ~300 first-year students |
| 🏛️ Organizers | SOKT, Trade Union Committee of Students and Postgraduates of ETU "LETI" |
| 🛠️ Design + development | Matvej Melikhov — Head of the IT Department, SOKT |

## ✨ Features

| | Feature |
|---|---|
| 🔐 | **Registration & authentication** — student sign-up (name, faculty, group) with session-based auth; a separate admin login by code |
| 🗺️ | **Interactive map** — a venue map on Yandex.Maps with zone markers: students see where to go and where to find the next QR code |
| 📷 | **QR scanner & questions** — the built-in scanner opens the question for the matching zone; answers are checked and points are awarded by question weight |
| 📊 | **Profile with analytics** — completion progress, points earned, number of answers, and final stats (time and final place) |
| 🏅 | **Real-time leaderboard** — a moderator-zone screen (projector) that auto-refreshes without reloading, plus a mobile leaderboard for students |
| 🛠️ | **Admin panel** — adding questions, managing participants, statistics, manual game start/stop |
| ⏳ | **Countdown** — before the start, game pages are locked behind a screen with a countdown to the quest |

## 🏆 Winners

<table>
<tr>
<td valign="top">

**Bachelor's**
1. Дмитрий Бужинский — ФКТИ
2. Никита Журухин — ФКТИ
3. Анастасия Колесникова — ФКТИ

</td>
<td valign="top">

**Master's**
1. Никита Шахин — ФКТИ
2. Виолетта Кругликова — ФКТИ

</td>
<td valign="top">

**International**
1. Linh Khanh — ИНПРОТЕХ
2. Чэнь Цзиюань — ФЭА

</td>
</tr>
</table>

<details>
<summary>📸 Winners photo</summary>

<br>

<img alt="QR quest winners" width="640" src="https://sun9-27.vkuserphoto.ru/s/v1/ig2/jJ6XcHvEa2ZARnC1KWSQ9iYw653lLikYL4uuc0G9DGv1UdBteI8gXsprqV4alcMA68xL0C5s3PeQwvmDFsEwAUvO.jpg?quality=95&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x303,640x359,720x404,1080x607,1280x719,1440x809,2560x1438&from=bu&u=7AOyMIJT4SGalQWw7CuA9Mn0xNGJiEl0mMIPb9bWWqA&cs=640x0">

</details>

## 🧱 Tech stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python 3.9, Flask 3.1, Flask-SQLAlchemy |
| Database | SQLite |
| Frontend | Jinja2, HTML, SCSS/CSS, Styrene font, Font Awesome |
| Map | Yandex.Maps constructor |
| QR scanner | html5-qrcode |

## 📂 Project structure

```
sokt-quiz/
├── app/
│   ├── __init__.py          # Flask app and database initialization
│   ├── config.py            # configuration, game start time, constants
│   ├── models.py            # SQLAlchemy models: Users, Questions
│   ├── decorators.py        # login_required, game_started, admin_required
│   ├── functions.py         # business logic and helpers (ranking, questions, time)
│   ├── routes/              # routes split by area
│   │   ├── main.py          # home page and countdown screen
│   │   ├── auth.py          # registration and logout
│   │   ├── game.py          # map, scanner, questions, results
│   │   ├── rating.py        # leaderboard (projector) and mobile leaderboard
│   │   ├── admin.py         # admin panel, questions, users, statistics
│   │   └── errors.py        # 401/403/404 handlers
│   ├── templates/           # Jinja2 page templates
│   └── static/              # styles (css/scss), fonts, images, pdf
├── main.py                  # application entry point
├── requirements.txt         # dependencies
└── README.md
```

## 🚀 Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The app starts at `http://127.0.0.1:5000`. The game start time, secret key, and admin code
are set via the `GAME_START_TIME`, `SECRET_KEY`, and `ADMIN_CODE` environment variables.

> [!NOTE]
> The `instance/base.db` database is created automatically on first run and is not tracked in the repository.
