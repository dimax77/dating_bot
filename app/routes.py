from flask import Blueprint, render_template, request, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'app/static/uploads'
DB_PATH = 'data/profiles.db'

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        city = request.form['city']
        interests = request.form['interests']
        about = request.form['about']
        photo = request.files.get('photo')
        telegram_id = request.args.get('id')

        filename = None
        if photo and photo.filename:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

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


@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        return redirect(url_for('main.result'))
    return render_template('search.html')

@main.route('/result')
def result():
    return render_template('result.html')

@main.route('/dialog/<int:user_id>')
def dialog(user_id):
    return render_template('dialog.html', user_id=user_id)
