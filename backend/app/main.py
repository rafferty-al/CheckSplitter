import os

import pony
from flask import Flask, render_template
from pydantic import ValidationError

from backend.app.api.helpers.utils import error
from backend.app.startup import init_orm, configure_app, configure_login
from backend.app.api import app_blueprint
from backend.app.validators.auth import AuthError


def create_app(testing=False):
    SECRET_KEY = os.urandom(32)

    app = Flask(__name__, template_folder="/home/shura/dev/agilecode/check_splitter/templates")
    app.register_blueprint(app_blueprint)
    app.secret_key = SECRET_KEY
    app.config.update(DEBUG=True)
    pony.options.CUT_TRACEBACK = False

    @app.errorhandler(404)
    def error_404(e):
        return render_template("404.html"), 404

    @app.errorhandler(ValidationError)
    def missing_error(e):
        missing_fields = {
            raw_error._loc: raw_error.exc.msg_template for raw_error in e.raw_errors
        }
        return error(status_code=422, description=missing_fields)

    @app.errorhandler(AuthError)
    def validation_error(e):
        missing_fields = {
            e.location: e.description
        }
        return error(status_code=e.status_code, description=missing_fields)


    init_orm(testing)
    configure_app(app, testing)
    configure_login(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
