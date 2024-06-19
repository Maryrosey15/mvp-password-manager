import sqlite3
from flask_login import UserMixin
from flask import g, session
import string
import secrets
import re

# Open database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Close database connection
def close_db_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Get username data from database
def get_user_by_username(username):
    db = get_db_connection()
    cursor = db.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    db.close()
    return user

# Get user email from database
def get_user_by_email(email):
    db = get_db_connection()
    cursor = db.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    db.close()
    return user

# Update user master password into database
def update_user_password(email, hashed_password):
    db = get_db_connection()
    db.execute('Update users SET master_password = ? WHERE email = ?', (hashed_password, email))
    db.commit()
    db.close()

# Initialised database with schema
def init_db():
    db = get_db_connection()
    with open('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

# User class for Flask-Login
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

# Create strong ans random password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

# Check if password is strong
def is_password_strong(password):
    if len(password) < 8:
        return False, "Password must be at least 8 character long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search("r[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    
    return True, "Password is strong."

