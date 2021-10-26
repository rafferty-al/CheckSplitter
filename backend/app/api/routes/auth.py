from flask import Blueprint, redirect, url_for, request
from flask_login import current_user,login_required, logout_user

from backend.app.api.helpers.utils import success, error
from backend.app.api.helpers import auth


blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.route("/login", methods=["POST"])
def user_login():
    if current_user.is_authenticated:
        return success(data="Already authorized")
    return auth.login_auth_user(request.json)


@blueprint.route("/logout")
@login_required
def logout():
    return success(data="Logout") if logout_user() else error(status_code=400, description="Error while logout")


@blueprint.route("/register", methods=["POST"])
def register_user():
    return auth.register_user(request.json)
