import os
from flask import Flask
from .extensions import bcrypt, db, jwt_manager, cors, scheduler, email_manager
from .config import app_config
from datetime import datetime
from .models import ProductCategory, Admin, UserType as UserType
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import logging

import yaml

with open("data/init.yaml") as f:
    init_data = yaml.safe_load(f)
    categories = init_data.get("categories", [])
    admin = init_data.get("admin", [])

AGENT_HOSTNAME = os.getenv("AGENT_HOSTNAME", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "4317"))


class SpanFormatter(logging.Formatter):
    def format(self, record):
        trace_id = trace.get_current_span().get_span_context().trace_id
        if trace_id == 0:
            record.trace_id = None
        else:
            record.trace_id = "{trace:032x}".format(trace=trace_id)
        return super().format(record)


resource = Resource(attributes={"service.name": "ss-backend"})

trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_exporter = OTLPSpanExporter(
    endpoint=f"{AGENT_HOSTNAME}:{AGENT_PORT}", insecure=True
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))


def create_app(config_name):
    app = Flask(__name__)
    metrics = PrometheusMetrics.for_app_factory()

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
        cleanup_tokens_blocklist as cleanup_tokens_blocklist,
        cleanup_delete_requests as cleanup_delete_requests,
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
