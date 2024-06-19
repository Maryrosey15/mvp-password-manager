# Imported required modules
from flask import Flask
from flask_login import LoginManager
from app.models import init_db, User

# Initialise Flask application
app = Flask(__name__, template_folder='templates')

# Load the configuration settings
app.config.from_object('config.Config')


# Initialise LoginManager for user session management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# Import and register the main blueprint
from app.routes import main
app.register_blueprint(main)


# Initialise database within the application context
with app.app_context():
    init_db()

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

