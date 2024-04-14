from flask import Flask
from .extensions import (
    bcrypt,
    login_manager,
    db
)

from .config import app_config
from .models import *


def create_app(config_name):
    app = Flask(__name__)
    # load app configuration
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    # initialize app extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    # create all db models
    with app.app_context():
        db.create_all()

    # test route (it will be removed)
    @app.route('/')
    def test():
        return "<h1>Hi, this is a test!</h1>"

    return app
