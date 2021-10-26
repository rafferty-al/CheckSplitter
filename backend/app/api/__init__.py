from flask import Blueprint

from .views import blueprint as views_blueprint
from .routes.auth import blueprint as login_blueprint

app_blueprint = Blueprint("app", __name__, url_prefix="/app")

app_blueprint.register_blueprint(views_blueprint)
app_blueprint.register_blueprint(login_blueprint)
