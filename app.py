from flask import Flask
from flask_login import LoginManager
from pony.flask import Pony
from config import settings

from models import db

app = Flask(__name__)
app.secret_key = settings['secret_key']
Pony(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.User.get(user_id)
