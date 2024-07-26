import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


# TODO check if the app load correctly the config


class Config(object):
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SECURITY_SALT = os.getenv("SECURITY_PASSWORD_SALT")
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


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SCHEDULER_API_ENABLED: True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(DevelopmentConfig):
    TESTING = True


app_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
