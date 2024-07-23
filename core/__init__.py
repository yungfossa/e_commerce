from flask import Flask
from .extensions import bcrypt, db, jwt_manager, login_manager, cors
from .config import app_config
from datetime import datetime
from .models import ProductCategory, User, UserType
import yaml

with open("data/init.yaml") as f:
    init_data = yaml.safe_load(f)
    categories = init_data.get("categories", [])
    admin = init_data.get("admin", [])


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile("config.py")

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

        for a in admin:
            User.create(
                email=a["email"],
                name=a["name"],
                surname=a["name"],
                password=bcrypt.generate_password_hash(a["password"], 10).decode(
                    "utf-8"
                ),
                birth_date=datetime.now(),
                user_type=UserType.ADMIN,
                is_active=True,
            )

    from .blueprints.errors import errors_bp

    app.register_blueprint(errors_bp)

    from .blueprints.auth import auth_bp

    app.register_blueprint(auth_bp)

    from .blueprints.user import user_bp

    app.register_blueprint(user_bp)

    from .blueprints.products import products_bp

    app.register_blueprint(products_bp)

    return app
