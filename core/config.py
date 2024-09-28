import os
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(object):
    """
    Base configuration class for the application.

    This class contains settings that are common across all environments.
    Specific environments (development, testing, production) can inherit from
    this class and override or add settings as needed.
    """

    NAME: Optional[str] = None

    # OpenTelemetry agent configuration
    AGENT_HOSTNAME = os.getenv("AGENT_HOSTNAME", "127.0.0.1")
    AGENT_PORT = int(os.getenv("AGENT_PORT", "4317"))

    # Flask and database configuration
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Email configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_CONFIRM_SALT = os.getenv("MAIL_CONFIRM_SALT")


class ProductionConfig(Config):
    """Configuration for the production environment."""

    NAME = "production"


class DevelopmentConfig(Config):
    """Configuration for the development environment."""

    NAME = "development"

    DEBUG = True
    SCHEDULER_API_ENABLED: True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(DevelopmentConfig):
    """Configuration for the testing environment."""

    NAME = "testing"

    TESTING = True


# Dictionary mapping environment names to their respective configuration classes
app_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

# This module defines the configuration settings for different environments
# of the application (development, testing, production).

# The Config class serves as a base configuration, with environment-specific
# classes inheriting from it and overriding or adding settings as needed.

# Usage:
# The appropriate configuration is selected in the application factory
# (typically in __init__.py) based on the current environment.

# Example:
# app.config.from_object(app_config[config_name])

# Environment variables:
# This configuration relies heavily on environment variables, which should be
# set in a .env file or in the deployment environment. The dotenv library is
# used to load these variables from a .env file if present.

# Security Note:
# Sensitive information like SECRET_KEY and database URIs should always be
# set via environment variables and never hard-coded or committed to version control.
