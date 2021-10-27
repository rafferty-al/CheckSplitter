from flask_login import LoginManager
from pony.flask import Pony
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

from app.database.models import db
from backend.app.settings import settings


def init_orm(testing=False):
    create_tables = False
    if bool(settings.IN_MEMORY) or testing:
        db.bind(provider=settings.PROVIDER, filename=":memory:")
        create_tables = True
    else:
        db.bind(
            provider=settings.PROVIDER,
            host=settings.HOST,
            port=settings.PORT,
            user=settings.USER,
            password=settings.PASSWORD,
            database=settings.DB_NAME,
        )
    db.generate_mapping(create_tables=create_tables, check_tables=True)


def configure_app(app, testing=False):
    Pony(app)
    CORS(app)
    if not testing:
        csrf = CSRFProtect(app)
        csrf.init_app(app)


def configure_login(app):
    login_manager = LoginManager(app)
    login_manager.login_view = "app.auth.user_login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.User.get(id=user_id)
