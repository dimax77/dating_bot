# app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for
import os
import sqlite3

from werkzeug.utils import secure_filename

DB_PATH = 'data/profiles.db'
# UPLOAD_FOLDER = 'app/static/uploads'

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'static/uploads'

@main.route('/')
def index():
    return render_template('base.html', content_template="fragments/home.html", body_class="welcome")

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
        return render_template('base.html', content_template='fragments/home.html', message="Анкета успешно создана!")
        # return redirect(url_for('main.index'))
    return render_template('base.html', content_template='fragments/create_profile.html')


@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    telegram_id = request.args.get('id')  # временно, потом заменим на сессию
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        city = request.form['city']
        interests = request.form['interests']
        about = request.form['about']
        photo = request.files.get('photo')

        filename = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

        cur.execute('''
            UPDATE profiles SET name=?, age=?, city=?, interests=?, about=?, photo=?
            WHERE telegram_id=?
        ''', (name, age, city, interests, about, filename, telegram_id))
        conn.commit()
        conn.close()
        return render_template('base.html', content_template='fragments/home.html', message="Профиль обновлён!")
    
    cur.execute('SELECT * FROM profiles WHERE telegram_id=?', (telegram_id,))
    row = cur.fetchone()
    conn.close()

    profile = dict(zip(['id', 'name', 'age', 'city', 'interests', 'about', 'photo', 'telegram_id'], row)) if row else {}
    return render_template('base.html', content_template='fragments/edit_profile.html', profile=profile)


@main.route('/delete_profile', methods=['POST'])
def delete_profile():
    telegram_id = request.args.get('id')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM profiles WHERE telegram_id=?', (telegram_id,))
    conn.commit()
    conn.close()
    return render_template('base.html', content_template='fragments/home.html', message="Профиль удалён!")


@main.route('/search')
def search_profiles():
    city = request.args.get('city', '').strip()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if city:
        cur.execute('SELECT * FROM profiles WHERE city LIKE ?', (f'%{city}%',))
    else:
        cur.execute('SELECT * FROM profiles')
    rows = cur.fetchall()
    profiles = [dict(zip(['id', 'name', 'age', 'city', 'interests', 'about', 'photo', 'telegram_id'], row)) for row in rows]
    conn.close()
    return render_template('base.html', content_template='fragments/search.html', profiles=profiles)


@main.route('/chats')
def chats():
    # Заглушка — позже можно будет реализовать логику извлечения уникальных собеседников
    sample_chats = [
        {"user_id": 1, "user_name": "Анна"},
        {"user_id": 2, "user_name": "Игорь"},
    ]
    return render_template('base.html', content_template='fragments/chats.html', chats=sample_chats)


@main.route('/dialog/<int:user_id>', methods=['GET', 'POST'])
def dialog(user_id):
    if request.method == 'POST':
        sender_id = request.args.get('from')  # для MVP достаточно
        message = request.form['message']
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)',
                    (sender_id, user_id, message))
        conn.commit()
        conn.close()
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT * FROM messages WHERE sender_id=? OR receiver_id=?', (user_id, user_id))
    rows = cur.fetchall()
    messages = [dict(zip(['id', 'sender_id', 'receiver_id', 'message', 'timestamp'], row)) for row in rows]
    conn.close()
    return render_template('base.html', content_template='fragments/dialog.html', messages=messages, user_id=user_id)

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

