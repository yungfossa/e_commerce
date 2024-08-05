from flask import Flask
from .extensions import bcrypt, db, jwt_manager, cors, scheduler, email_manager
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
    jwt_manager.init_app(app)
    email_manager.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)

    from .scheduler_jobs import (
        cleanup_tokens_blocklist as cleanup_tokens_blocklist,
        cleanup_delete_requests as cleanup_delete_requests,
    )

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
                is_verified=True,
                verified_on=datetime.now(),
            )

    from .blueprints.errors import errors_bp

    app.register_blueprint(errors_bp)

    from core.blueprints.public_views.auth import auth_bp

    app.register_blueprint(auth_bp)

    from core.blueprints.public_views.listings import listings_bp

    app.register_blueprint(listings_bp)

    from core.blueprints.customer import customer_bp

    app.register_blueprint(customer_bp)

    from core.blueprints.customer.cart import customer_cart_bp

    app.register_blueprint(customer_cart_bp)

    from core.blueprints.customer.wishlists import customer_wishlists_bp

    app.register_blueprint(customer_wishlists_bp)

    from core.blueprints.customer.profile import customer_profile_bp

    app.register_blueprint(customer_profile_bp)

    from core.blueprints.seller import seller_bp

    app.register_blueprint(seller_bp)

    from core.blueprints.seller.profile import seller_profile_bp

    app.register_blueprint(seller_profile_bp)

    from core.blueprints.seller.listings import seller_listings_bp

    app.register_blueprint(seller_listings_bp)

    from .blueprints.admin import admin_bp

    app.register_blueprint(admin_bp)

    from .blueprints.admin.products import admin_products_bp

    app.register_blueprint(admin_products_bp)

    from .blueprints.admin.users import admin_users_bp

    app.register_blueprint(admin_users_bp)

    return app
