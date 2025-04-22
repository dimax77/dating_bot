# app/db/db.py

import sqlite3
from contextlib import contextmanager

DB_PATH = 'data/dating_bot.db'

@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с базой данных."""
    conn = sqlite3.connect(DB_PATH)
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
