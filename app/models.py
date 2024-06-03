import sqlite3
from flask_login import UserMixin
from flask import g, session
import string
import secrets


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def close_db_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_user_by_username(username):
    db = get_db_connection()
    cursor = db.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    db.close()
    return user


def get_user_by_email(email):
    db = get_db_connection()
    cursor = db.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    db.close()
    return user


def update_user_password(email, hashed_password):
    db = get_db_connection()
    db.execute('Update users SET master_password = ? WHERE email = ?', (hashed_password, email))
    db.commit()
    db.close()


def init_db():
    db = get_db_connection()
    with open('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


class User(UserMixin):
    def __init__(self, id, username, master_password):
        self.id = id
        self.username = username
        self.master_password = master_password
        session['user_id'] = id

    @staticmethod
    def get_by_id(user_id):
        db = get_db_connection()
        user_data = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        db.close()
        if user_data is None:
            return None
        return User(user_data['id'], user_data['username'], user_data['master_password'])


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))
