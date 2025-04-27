# app/db/seed_db.py

import sqlite3
import random
import os
from faker import Faker
from app.db import DB_PATH

fake = Faker()

def seed_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run init_db.py first.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    cities = ["Abakan", "Samara", "Moscow"]
    genders = ["male", "female"]

    user_ids = []

    # Find your user by Telegram ID
    c.execute('SELECT id FROM users WHERE telegram_id = ?', ('5070300052',))
    result = c.fetchone()

    if result:
        your_user_id = result[0]
    else:
        print("Your user not found in the database. Please create your user first.")
        conn.close()
        return

    # Insert 20 random users
    for _ in range(20):
        name = fake.first_name()
        gender = random.choice(genders)
        birthdate = fake.date_of_birth(minimum_age=18, maximum_age=50).isoformat()
        country = "Russia"
        city = random.choice(cities)
        interests = ", ".join(fake.words(nb=5))
        about = fake.sentence()
        photo = fake.image_url()
        telegram_id = str(fake.random_number(digits=9))
        birth_year = int(birthdate[:4])
        current_year = 2025
        age = current_year - birth_year

        c.execute('''
            INSERT INTO users (name, gender, birthdate, country, city, interests, about, photo, telegram_id, age)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, gender, birthdate, country, city, interests, about, photo, telegram_id, age))

        user_ids.append(c.lastrowid)

    # Add your user_id to the list for messaging
    all_user_ids = user_ids + [your_user_id]

    # Insert random messages
    for _ in range(50):  # 50 сообщений
        if random.random() < 0.4:
            # 40% сообщений с твоим аккаунтом
            sender_id = your_user_id
            receiver_id = random.choice(user_ids)
        elif random.random() < 0.4:
            sender_id = random.choice(user_ids)
            receiver_id = your_user_id
        else:
            sender_id, receiver_id = random.sample(user_ids, 2)

        message = fake.sentence()
        c.execute('''
            INSERT INTO messages (sender_id, receiver_id, message)
            VALUES (?, ?, ?)
        ''', (sender_id, receiver_id, message))

    conn.commit()
    conn.close()
    print("Database seeded successfully with your account involved.")

if __name__ == "__main__":
    seed_db()
