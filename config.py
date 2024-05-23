import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_app_secret_key'
    DATABASE = 'database.db'

