# app/db/db.py

import sqlite3
from contextlib import contextmanager
from flask import current_app


DB_PATH = 'data/dating_bot.db'

@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с базой данных."""
    conn = sqlite3.connect(DB_PATH)
    current_app.logger.info("DB connection established: %s", conn)
    conn.row_factory = sqlite3.Row  # Чтобы результат был как словарь
    try:
        yield conn
    finally:
        conn.close()

def get_user_by_telegram_id(telegram_id):
    """Получить пользователя по его telegram_id."""
    query = "SELECT * FROM users WHERE telegram_id = ?"
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (telegram_id,))
        row = cur.fetchone()
    return row

def get_unread_messages_count(user_id):
    """Получить количество непрочитанных сообщений для пользователя."""
    query = '''
    SELECT COUNT(*) FROM messages
    WHERE receiver_id = ? AND read IS NULL
    '''
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        count = cur.fetchone()[0]
    return count

from datetime import datetime
def calculate_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def create_user_profile(form_data, telegram_id, filename=None):
    """Create a new user profile in the database."""
    query = '''
    INSERT INTO users (name, gender, birthdate, country, city, interests, about, photo, telegram_id, age)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            current_app.logger.info("Trying insert data: %s", form_data)
            # birthdate = datetime.strptime(form_data['birthdate'], '%Y-%m-%d')  # Преобразует строку в объект datetime
            birthdate = form_data['birthdate']
            age = calculate_age(birthdate)
            current_app.logger.info("Calculated age for user: %s", age)

            cur.execute(query, (
                form_data['name'],
                form_data['gender'],
                # form_data['birthdate'].strftime('%Y-%m-%d'),
                birthdate,
                form_data['country'],
                form_data['city'],
                form_data['interests'],
                form_data['about'],
                filename,
                telegram_id,
                age
            ))
            conn.commit()
            return {"success": True, "message": "User profile created successfully."}
    except sqlite3.IntegrityError as e:
        # Например, если у тебя ограничение UNIQUE на telegram_id
        current_app.logger.info("Error adding user to DB: %s", e)
        return {"success": False, "error": f"Integrity error: {e}"}
    except sqlite3.OperationalError as e:
        # Ошибки типа "нет такой таблицы" или неправильный SQL синтаксис
        current_app.logger.info("Error adding user to DB: %s", e)

        return {"success": False, "error": f"Operational error: {e}"}
    except Exception as e:
        # Ловим все остальные ошибки
        current_app.logger.info("Error adding user to DB: %s", e)

        return {"success": False, "error": f"Unexpected error: {e}"}
    
def update_user_profile(telegram_id, form_data, filename=None):
    """Update the user profile in the database."""
    query = '''
    UPDATE users
    SET name = ?, gender = ?, birthdate = ?, country = ?, city = ?, interests = ?, about = ?, photo = ?
    WHERE telegram_id = ?
    '''

    # birthdate = datetime.strptime(form_data['birthdate'], '%Y-%m-%d')  # Преобразует строку в объект datetime
    # birthdate = datetime.strptime(form_data['birthdate'], '%Y-%m-%d').date()

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (
            form_data['name'],
            form_data['gender'],
            form_data['birthdate'].strftime('%Y-%m-%d'),
            # birthdate,
            form_data['country'],
            form_data['city'],
            form_data['interests'],
            form_data['about'],
            filename,
            telegram_id
        ))
        conn.commit()

def delete_user_profile(telegram_id):
    """Delete the user profile from the database."""
    query = "DELETE FROM users WHERE telegram_id = ?"
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (telegram_id,))
        conn.commit()

# def search_profiles_by_filters(country, city, gender, min_age, max_age):
#     """Search for user profiles based on filters."""
#     query = "SELECT * FROM users WHERE 1=1"
#     params = []

#     if country:
#         query += " AND country LIKE ?"
#         params.append(f"%{country}%")

#     if city:
#         query += " AND city LIKE ?"
#         params.append(f"%{city}%")

#     if gender:
#         query += " AND gender = ?"
#         params.append(gender)

#     if min_age:
#         query += " AND age >= ?"
#         params.append(min_age)

#     if max_age:
#         query += " AND age <= ?"
#         params.append(max_age)

#     with get_db_connection() as conn:
#         cur = conn.cursor()
#         cur.execute(query, tuple(params))
#         rows = cur.fetchall()
#     return rows
from datetime import date, timedelta

def calculate_birthdate_range(min_age, max_age):
    today = date.today()
    max_birthdate = today - timedelta(days=int(min_age)*365.25) if min_age else None
    min_birthdate = today - timedelta(days=int(max_age)*365.25) if max_age else None
    return min_birthdate, max_birthdate

def search_profiles_by_filters(country, city, gender, min_age, max_age):
    """Search for user profiles based on filters."""
    query = "SELECT *, CAST((julianday('now') - julianday(birthdate)) / 365.25 AS INTEGER) AS age FROM users WHERE 1=1"
    params = []

    if country:
        query += " AND country LIKE ?"
        params.append(f"%{country}%")

    if city:
        query += " AND city LIKE ?"
        params.append(f"%{city}%")

    if gender:
        query += " AND gender = ?"
        params.append(gender)

    if min_age:
        query += " AND CAST((julianday('now') - julianday(birthdate)) / 365.25 AS INTEGER) >= ?"
        params.append(int(min_age))

    if max_age:
        query += " AND CAST((julianday('now') - julianday(birthdate)) / 365.25 AS INTEGER) <= ?"
        params.append(int(max_age))

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
    return rows


def get_all_profiles():
    """Get all user profiles."""
    query = "SELECT * FROM users"
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    return rows