from flask import Flask
from .extensions import bcrypt, db, jwt_manager, login_manager, cors
from .config import app_config
from .models import *

categories = [
    'Tech',
    'Food',
]

def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    
    cors.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt_manager.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()

        for c in categories:
            ProductCategory.create(title=c)
    
    from .blueprints.errors import errors_bp
    app.register_blueprint(errors_bp)

    from .blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .blueprints.user import user_bp
    app.register_blueprint(user_bp)

    from .blueprints.products import products_bp
    app.register_blueprint(products_bp)

    return app
