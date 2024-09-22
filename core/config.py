import os
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    NAME: Optional[str] = None

    AGENT_HOSTNAME = os.getenv("AGENT_HOSTNAME", "127.0.0.1")
    AGENT_PORT = int(os.getenv("AGENT_PORT", "4317"))

    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # mail configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_CONFIRM_SALT = os.getenv("MAIL_CONFIRM_SALT")


class ProductionConfig(Config):
    NAME = "production"


class DevelopmentConfig(Config):
    NAME = "development"

    DEBUG = True
    SCHEDULER_API_ENABLED: True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(DevelopmentConfig):
    NAME = "testing"

    TESTING = True


app_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
