from flask_login import login_user
from pony import orm
from werkzeug.security import generate_password_hash

from app.api.helpers.utils import success
from backend.app.validators.auth import LoginSchema, RegisterSchema
from backend.app.startup import db


def login_auth_user(request_body):
    login_form = LoginSchema(**request_body)
    existing_user = db.User.get(nickname=login_form.login)
    login_user(existing_user)
    return success(data="Login successfully")


def register_user(request_body):
    register_form = RegisterSchema(**request_body)
    new_user = db.User(
        nickname=register_form.login,
        password=generate_password_hash(register_form.first_password),
        fullname=register_form.fullname
    )
    orm.flush()
    return success(data=new_user.id)
