from datetime import datetime

import yaml
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from prometheus_flask_exporter import PrometheusMetrics

from .config import app_config
from .extensions import bcrypt, cors, db, email_manager, jwt_manager, scheduler
from .instrumentation import build_instrumentation
from .models import Admin, ProductCategory
from .models import UserType as UserType

with open("data/init.yaml") as f:
    init_data = yaml.safe_load(f)
    categories = init_data.get("categories", [])
    admin = init_data.get("admin", [])


def create_app(config_name):
    if config_name == "production":
        build_instrumentation(
            app_config[config_name].AGENT_HOSTNAME, app_config[config_name].AGENT_PORT
        )

    app = Flask(__name__)
    metrics = PrometheusMetrics.for_app_factory()

    if config_name == "production":
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile("config.py")

    metrics.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)
    jwt_manager.init_app(app)
    email_manager.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)

    from .scheduler_jobs import (
        cleanup_delete_requests as cleanup_delete_requests,
    )
    from .scheduler_jobs import (
        cleanup_tokens_blocklist as cleanup_tokens_blocklist,
    )

    scheduler.start()

    with app.app_context():
        db.drop_all()
        db.create_all()

        SQLAlchemyInstrumentor().instrument(engine=db.engine)

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
