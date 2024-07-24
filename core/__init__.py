from flask import Flask
from .extensions import bcrypt, db, jwt_manager, login_manager, cors, scheduler
from .config import app_config
from datetime import datetime
from .models import ProductCategory, Admin, UserType as UserType
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

    # background jobs scheduler
    scheduler.init_app(app)

    from .scheduler_jobs import cleanup_tokens_blocklist as cleanup_tokens_blocklist

    scheduler.start()

    with app.app_context():
        db.drop_all()
        db.create_all()

        for c in categories:
            ProductCategory.create(title=c)

        for a in admin:
            Admin.create(
                email=a["email"],
                name=a["name"],
                surname=a["name"],
                password=bcrypt.generate_password_hash(a["password"], 10).decode(
                    "utf-8"
                ),
                birth_date=datetime.now(),
                is_active=True,
            )

    from .blueprints.errors import errors_bp

    app.register_blueprint(errors_bp)

    from .blueprints.auth import auth_bp

    app.register_blueprint(auth_bp)

    from .blueprints.user import user_bp

    app.register_blueprint(user_bp)

    from .blueprints.user.customer import customer_bp

    app.register_blueprint(customer_bp)

    from .blueprints.user.seller import seller_bp

    app.register_blueprint(seller_bp)

    from .blueprints.admin import admin_bp

    app.register_blueprint(admin_bp)

    return app
