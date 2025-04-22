# app/routes.py

from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash, current_app
from app.utils.forms import ProfileForm
import os
import sqlite3
from app.db.db import get_user_by_telegram_id, get_unread_messages_count

from werkzeug.utils import secure_filename

DB_PATH = 'data/dating_bot.db'

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'static/uploads'

@main.route('/')
def index():
    user = None
    unread_count = 0
    user_id = session.get('user_id')

    if user_id:
        try:
            user_data = get_user_by_telegram_id(user_id)
            if user_data:
                user = dict(user_data)
                unread_count = get_unread_messages_count(user_id)
            else:
                # If user doesn't exist, clear session and redirect
                session.clear()  # Remove all session data
                flash("Your account no longer exists. Please log in again.", "warning")
                return redirect(url_for("main.index"))
        except Exception as e:
            current_app.logger.error(f"Ошибка при получении данных: {e}")
            flash("Ошибка сервера. Попробуйте позже.")
            return redirect(url_for("main.index"))
        
        return render_template('base.html',
                               content_template="fragments/home.html",
                               user=user,
                               unread_count=unread_count,
                               body_class="welcome")

    return render_template('base.html',
                           content_template="fragments/intro.html",
                           body_class="welcome")



    


@main.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    telegram_id = data.get("telegram_id")
    
    if telegram_id:
        session["user_id"] = telegram_id
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "message": "No Telegram ID"}), 400



@main.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    form = ProfileForm()

    if request.method == 'POST' and form.validate_on_submit():
        telegram_id = session.get('user_id')
        filename = None

        if form.photo.data:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join(UPLOAD_FOLDER, filename))

        # Сохраняем в базу (пример с SQLite)
        from app.db import DB_PATH
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO users (name, gender, birthdate, country, city, interests, about, photo, telegram_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            form.name.data,
            form.gender.data,
            form.birthdate.data.strftime('%Y-%m-%d'),
            request.form.get("country"),
            request.form.get("city"),
            form.interests.data,
            form.about.data,
            filename,
            telegram_id
        ))
        conn.commit()
        conn.close()

        flash("Профиль создан!")
        return redirect(url_for('main.index'))

    return render_template('base.html', content_template='fragments/create_profile.html', form=form)

@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    telegram_id = session.get('user_id')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if request.method == 'POST':
        
        name = request.form['name']
        gender = request.form['gender']
        birthdate = request.form['birthdate']
        country = request.form['country']
        city = request.form['city']
        interests = request.form['interests']
        about = request.form['about']
        photo = request.files.get('photo')

        filename = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

        cur.execute('''
            UPDATE users SET name=?, gender=?, birthdate=?, country=?, city=?, interests=?, about=?, photo=?
            WHERE telegram_id=?
        ''', (name, gender, birthdate, country, city, interests, about, filename, telegram_id))
        conn.commit()
        conn.close()
        flash("Профиль обновлён!")
        return redirect(url_for('main.index'))
    
    cur.execute('SELECT * FROM users WHERE telegram_id=?', (telegram_id,))
    row = cur.fetchone()
    conn.close()

    profile = dict(zip(['id', 'name', 'gender', 'birthdate', 'country', 'city', 'interests', 'about', 'photo', 'telegram_id'], row)) if row else {}
    return render_template('base.html', content_template='fragments/edit_profile.html', profile=profile)


@main.route('/delete_profile', methods=['POST'])
def delete_profile():
    telegram_id = request.args.get('id')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE telegram_id=?', (telegram_id,))
    conn.commit()
    conn.close()
    flash("Профиль удалён!")
    return redirect(url_for('main.index'))


@main.route('/search')
def search_profiles():
    city = request.args.get('city', '').strip()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if city:
        cur.execute('SELECT * FROM users WHERE city LIKE ?', (f'%{city}%',))
    else:
        cur.execute('SELECT * FROM users')
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
    my_id = session.get("user_id")

    if request.method == 'POST':
        # sender_id = request.args.get('from')
        message = request.form['message']
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('INSERT INTO messages (sender_id, receiver_id, message, read) VALUES (?, ?, ?, 0)',
                    (my_id, user_id, message))
        conn.commit()
        conn.close()

        # Add here function call to inform user about new message via dating_bot
        # Format: You have new message from <User>: <Message>
        # May be add later a brief deep link to chat or leave as is
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        UPDATE messages SET read = 1
        WHERE receiver_id = ? AND sender_id = ? AND read = 0
    ''', (my_id, user_id))
    conn.commit()

    cur.execute('''
        SELECT * FROM messages
        WHERE (sender_id=? AND receiver_id=?)
        OR (sender_id=? AND receiver_id=?)
    ''', (my_id, user_id, user_id, my_id))
    rows = cur.fetchall()
    messages = [dict(zip(['id', 'sender_id', 'receiver_id', 'message', 'read', 'timestamp'], row)) for row in rows]
    conn.close()

    return render_template('base.html', content_template='fragments/dialog.html', messages=messages, user_id=user_id)
