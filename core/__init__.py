from flask import Flask
from flask_cors import CORS

from .extensions import (
    bcrypt,
    db,
    jwt_manager,
    login_manager,
)

from .config import app_config
from .models import *


def create_app(config_name):
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt_manager.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app
