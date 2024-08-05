from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_apscheduler import APScheduler
from flask_mail import Mail

db = SQLAlchemy()
bcrypt = Bcrypt()
scheduler = APScheduler()
email_manager = Mail()
jwt_manager = JWTManager()
cors = CORS()
