from pydantic import BaseModel, validator
from werkzeug.security import check_password_hash

from backend.app.startup import db


class BaseError(Exception):
    def __init__(self, location: str, description: str, status_code=400):
        self.location = location
        self.description = description
        self.status_code = status_code


class AuthError(BaseError):
    pass


class LoginSchema(BaseModel):
    login: str
    password: str

    @validator("login")
    def check_login(cls, login):
        if login:
            existing_user = db.User.get(nickname=login)
            if existing_user is None:
                raise AuthError(location="login", description="User not found", status_code=401)
        return login

    @validator("password")
    def check_password(cls, password, values):
        login = values.get("login", "")
        if login and password:
            existing_user = db.User.get(nickname=login)
            if not check_password_hash(existing_user.password, password):
                raise AuthError(location="password", description="Wrong password", status_code=401)
        return password


class RegisterSchema(BaseModel):
    login: str
    first_password: str
    second_password: str
    fullname: str

    @validator("login")
    def check_existing_user(cls, login):
        if login:
            existing_user = db.User.get(nickname=login)
            if existing_user is not None:
                raise AuthError(location="login", description="Login is already taken", status_code=403)
        return login

    @validator("first_password")
    def check_passwords_strength(cls, password):
        if not (any(map(str.isupper, password)) and any(map(str.islower, password))
                and any(map(str.isdigit, password)) and len(password) >= 8):
            raise AuthError(location="first_password", description="Password too simple", status_code=403)
        return password

    @validator("second_password")
    def check_password_matching(cls, second_password, values):
        first_password = values.get("first_password", "")
        if first_password and second_password:
            if first_password != second_password:
                raise AuthError(location="second_password", description="Password mismatch", status_code=403)
        return second_password
