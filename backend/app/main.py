import os
from flask import Flask, render_template

from app.startup import init_orm, configure_app, configure_login
from app.api.views import blueprint as views_blueprint


def create_app(testing=False):
    SECRET_KEY = os.urandom(32)

    app = Flask(__name__, template_folder="/home/shura/dev/agilecode/check_splitter/templates")
    app.register_blueprint(views_blueprint)
    app.secret_key = SECRET_KEY
    app.config.update(DEBUG=True)

    @app.errorhandler(404)
    def error_404(e):
        return render_template("404.html"), 404

    init_orm(testing)
    configure_app(app, testing)
    configure_login(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
