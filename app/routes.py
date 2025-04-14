from flask import Blueprint, render_template, request, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


# @main.route('/create_profile', methods=['GET', 'POST'])
# def create_profile():
#     if request.method == 'POST':
#         # Обработка формы создания профиля
#         pass
#     return render_template('create_profile.html')

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Обработка формы поиска
        return redirect(url_for('main.result'))
    return render_template('search.html')

@main.route('/result')
def result():
    # Показать результаты поиска
    return render_template('result.html')

@main.route('/dialog/<int:user_id>')
def dialog(user_id):
    # Показать диалог с пользователем
    return render_template('dialog.html', user_id=user_id)

# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'static/uploads'

# @main.route('/create_profile', methods=['GET', 'POST'])
# def create_profile():
#     if request.method == 'POST':
#         name = request.form['name']
#         age = request.form['age']
#         city = request.form['city']
#         interests = request.form['interests']
#         about = request.form['about']
#         photo = request.files.get('photo')

#         photo_path = None
#         if photo and photo.filename:
#             filename = secure_filename(photo.filename)
#             photo_path = os.path.join(UPLOAD_FOLDER, filename)
#             photo.save(photo_path)

#         # 💾 TODO: сохранить данные в SQLite
#         print(f"Создан профиль: {name}, {age}, {city}, {interests}, {about}, {photo_path}")

#         return redirect(url_for('main.index'))

#     return render_template('create_profile.html')


import sqlite3

DB_PATH = 'data/profiles.db'
UPLOAD_FOLDER = 'app/static/uploads'

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            city TEXT,
            interests TEXT,
            about TEXT,
            photo TEXT,
            telegram_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@main.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        city = request.form['city']
        interests = request.form['interests']
        about = request.form['about']
        photo = request.files.get('photo')
        telegram_id = request.args.get('id')  # если мы получаем id через query params из Telegram

        filename = None
        if photo and photo.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

        # 💾 сохраняем профиль
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO profiles (name, age, city, interests, about, photo, telegram_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, city, interests, about, filename, telegram_id))
        conn.commit()
        conn.close()

        return redirect(url_for('main.index'))

    return render_template('create_profile.html')
