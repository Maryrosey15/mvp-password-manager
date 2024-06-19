import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.routes import create_app
from app.models import init_db, close_db_connection  # Import init_db and close_db_connection

@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'MAIL_SUPPRESS_SEND': True,
        'MAIL_DEFAULT_SENDER': 'test@example.com',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'password',
        'DATABASE': 'test_database.db',  # Use a test database
    })

    with app.app_context():
        init_db()  # Initialize the database before running tests
        yield app
        # Close the database connection after tests run
        close_db_connection()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()
