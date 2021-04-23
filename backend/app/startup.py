from flask_login import LoginManager
from pony.flask import Pony
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

from app.database.models import db
from backend.app.settings import settings


def init_orm():
    if bool(settings.IN_MEMORY):
        db.bind(provider=settings.PROVIDER,
                filename=':memory:')
    else:
        db.bind(provider=settings.PROVIDER,
                host=settings.HOST,
                port=settings.PORT,
                user=settings.USER,
                password=settings.PASSWORD,
                database=settings.DB_NAME)
    db.generate_mapping(check_tables=True)


def configure_app(app):
    Pony(app)
    CORS(app)
    csrf = CSRFProtect(app)
    csrf.init_app(app)


def configure_login(app):
    login_manager = LoginManager(app)
    login_manager.login_view = 'app.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return db.User.get(id=user_id)
