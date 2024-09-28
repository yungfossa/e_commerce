import yaml
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from prometheus_flask_exporter import PrometheusMetrics

from .config import app_config
from .extensions import bcrypt, cors, db, email_manager, jwt_manager, scheduler
from .instrumentation import build_instrumentation
from .utils import init_db


def create_app(config_name):
    """
    Create and configure the Flask application.

    This function sets up the Flask app with all necessary extensions,
    configurations, and blueprints based on the specified configuration name.

    Args:
        config_name (str): The name of the configuration to use (e.g., 'development', 'production').

    Returns:
        Flask: The configured Flask application instance.
    """
    # Set up OpenTelemetry instrumentation for production
    if config_name == "production":
        build_instrumentation(
            app_config[config_name].AGENT_HOSTNAME, app_config[config_name].AGENT_PORT
        )

    # Create Flask app and set up Prometheus metrics
    app = Flask(__name__)
    metrics = PrometheusMetrics.for_app_factory()

    # Set up additional instrumentation for production
    if config_name == "production":
        SQLAlchemyInstrumentor().instrument(engine=db.engine)
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()

    # Load configuration
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile("config.py")

    # Initialize Flask extensions
    metrics.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)
    jwt_manager.init_app(app)
    email_manager.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)

    # Import scheduler jobs
    from .scheduler_jobs import (
        cleanup_delete_requests as cleanup_delete_requests,
    )
    from .scheduler_jobs import (
        cleanup_tokens_blocklist as cleanup_tokens_blocklist,
    )

    # Start the scheduler
    scheduler.start()

    # Initialize database with data from YAML file
    with app.app_context():
        with open("data/init.yaml") as f:
            init_data = yaml.safe_load(f)
        init_db(init_data)

    # Register blueprints
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

    from core.blueprints.customer.orders import customer_orders_bp

    app.register_blueprint(customer_orders_bp)

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

    from .blueprints.seller.orders import seller_orders_bp

    app.register_blueprint(seller_orders_bp)

    return app


# This module is responsible for creating and configuring the Flask application.
# It sets up all necessary extensions, loads configurations, initializes the database,
# and registers all blueprints for different parts of the application.

# The create_app function follows the application factory pattern, which allows
# for easy creation of the app with different configurations (e.g., for testing).

# Key components:
# - OpenTelemetry instrumentation for tracing (in production)
# - Prometheus metrics for monitoring
# - Various Flask extensions (CORS, JWT, email, scheduler, etc.)
# - Database initialization with data from a YAML file
# - Multiple blueprints for different areas of the application (public views,
#   customer views, seller views, admin views)

# Note: The configuration and some imports are assumed to be defined in other files
# within the 'core' package.
