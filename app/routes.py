# app/routes.py

from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash, current_app, abort
from app.utils.forms import ProfileForm
import os
import urllib
import sqlite3
from app.db.db import get_user_by_telegram_id, get_unread_messages_count, create_user_profile, update_user_profile, delete_user_profile
from app.db.db import search_profiles_by_filters, get_all_profiles
from werkzeug.utils import secure_filename

DB_PATH = 'data/dating_bot.db'
BOT_TOKEN = os.environ.get('BOT_TOKEN')

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'static/uploads'

@main.route('/')
def index():
    user = None
    unread_count = 0
    user_id = session.get('user_id')
    current_app.logger.info("Index Route. User_Id: %s", user_id)

    if user_id:
        try:
            user_data = get_user_by_telegram_id(user_id)
            if user_data:
                user = dict(user_data)
                unread_count = get_unread_messages_count(user_id)
            else:
                # If user doesn't exist, clear session and redirect
                # session.clear()  # Remove all session data
                # session.pop("user_id", None)
                # flash("Your account no longer exists. Please log in again.", "warning")
                # return redirect(url_for("main.index"))
                return render_template('base.html',
                           content_template="fragments/intro.html",
                           body_class="welcome")
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
    init_data = data.get('initData')
    if not valid_init_data(init_data):
        abort(403, "Invalid init data!")

    telegram_id = eval(urllib.parse.parse_qs(init_data)["user"][0])["id"]
    if telegram_id:
        session["user_id"] = telegram_id
        session.modified = True
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "message": "No Telegram ID"}), 400

@main.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    telegram_id = session.get('user_id')
    if not telegram_id:
        flash("Please log in to create a profile", "warning")
        return redirect(url_for('main.index'))

    form = ProfileForm()

    if form.validate_on_submit():
        filename = None
        print(form.errors)

        if form.photo.data:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join(UPLOAD_FOLDER, filename))

        form_data = {
            'name': form.name.data,
            'gender': form.gender.data,
            # 'birthdate': form.birthdate.data,
            'birthdate': form.birthdate.data.strftime('%Y-%m-%d'),
            'country': form.country.data,
            'city': form.city.data,
            'interests': form.interests.data,
            'about': form.about.data
        }

        try:
            create_user_profile(telegram_id, form_data, filename)
            flash("Profile created successfully!", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f"Error creating profile: {e}", "danger")
            return redirect(url_for('main.create_profile'))

    return render_template('base.html', content_template='fragments/create_profile.html', form=form)

from datetime import datetime

@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    telegram_id = session.get('user_id')
    if not telegram_id:
        flash("Пожалуйста, войдите в систему", "warning")
        return redirect(url_for('main.index'))

    user_profile = get_user_by_telegram_id(telegram_id)
    if not user_profile:
        flash("Профиль не найден", "danger")
        return redirect(url_for('main.index'))

    profile_data = dict(user_profile)
    profile_data['birthdate'] = datetime.strptime(profile_data['birthdate'], '%Y-%m-%d').date() if profile_data['birthdate'] else None
    form = ProfileForm(data=profile_data)

    if request.method == 'POST' and form.validate():
        filename = user_profile['photo']
        if form.photo.data:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join(UPLOAD_FOLDER, filename))

        form_data = {
            'name': form.name.data,
            'gender': form.gender.data,
            'birthdate': form.birthdate.data,
            'country': form.country.data,
            'city': form.city.data,
            'interests': form.interests.data,
            'about': form.about.data,
        }

        try:
            update_user_profile(telegram_id, form_data, filename)
            flash("Профиль успешно обновлён!", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f"Ошибка при обновлении: {e}", "danger")
            return redirect(url_for('main.edit_profile'))

    return render_template('base.html', content_template='fragments/edit_profile.html', profile=form)

@main.route('/delete_profile', methods=['POST'])
def delete_profile():
    telegram_id = session.get('user_id')

    # If user is not logged in, redirect to the home page
    if not telegram_id:
        flash("Please log in to delete your profile", "warning")
        return redirect(url_for('main.index'))

    try:
        # Delete the user profile from the database
        delete_user_profile(telegram_id)
        flash("Profile deleted successfully!", "success")
        # After deletion, log the user out (clear the session)
        session.clear()
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f"Error deleting profile: {e}", "danger")
        return redirect(url_for('main.index'))


@main.route('/search')
def search_profiles():
    # Get search parameters
    country = request.args.get('country', '').strip()
    city = request.args.get('city', '').strip()
    gender = request.args.get('gender', '').strip()
    min_age = request.args.get('min_age', type=int, default=18)
    max_age = request.args.get('max_age', type=int, default=30)

    # Use the search function with the provided filters
    if country or city or gender or min_age or max_age:
        rows = search_profiles_by_filters(country, city, gender, min_age, max_age)
    else:
        rows = get_all_profiles()

    profiles = [dict(zip(['id', 'name', 'age', 'city', 'country', 'gender', 'interests', 'about', 'photo', 'telegram_id'], row)) for row in rows]

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

import hmac
import hashlib

def valid_init_data(init_data_str):
    parsed_data = urllib.parse.parse_qs(init_data_str, keep_blank_values=True)
    data_check_str = '\n'.join(
        f"{k}={v[0]}" for k, v in sorted(parsed_data.items()) if k!= 'hash'
    )

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_str.encode(), hashlib.sha256).hexdigest()

    provided_hash = parsed_data['hash'][0]
    return hmac.compare_digest(computed_hash, provided_hash)