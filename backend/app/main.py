import os
from flask import Flask

from app.settings import settings
from app.startup import init_orm, configure_app, configure_login
from app.api.views import blueprint as views_blueprint

template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)
app.register_blueprint(views_blueprint)
app.secret_key = settings.SECRET_KEY
app.config.update(DEBUG=True)

init_orm()
configure_app(app)
configure_login(app)


if __name__ == '__main__':
    app.run()
