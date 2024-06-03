from flask import Flask
from flask_login import LoginManager
from app.models import init_db, User


app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app.routes import main
app.register_blueprint(main)

with app.app_context():
    init_db()

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

