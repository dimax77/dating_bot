# app/db/init_db.py

import sqlite3
import os
from app.db import DB_PATH

def init_db():
    # Ensure the directory for the DB exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create the 'users' table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        city TEXT,
        description TEXT,
        photo_url TEXT
    )
    ''')

    # Create the 'messages' table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        read INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # If you need to update the 'profiles' table (and it already exists), use ALTER TABLE
    # Check for the 'profiles' table existence and apply ALTER only if necessary
    try:
        c.execute('PRAGMA foreign_keys=off;')  # Temporarily disable foreign key checks for ALTER operations
        c.execute('''
        ALTER TABLE profiles ADD COLUMN gender TEXT;
        ALTER TABLE profiles ADD COLUMN birthdate DATE;
        ALTER TABLE profiles ADD COLUMN country TEXT;
        ''')
    except sqlite3.OperationalError:
        pass  # If 'profiles' doesn't exist, or columns are already added, this will safely pass

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Call init_db to initialize the database
init_db()
