from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_apscheduler import APScheduler

db = SQLAlchemy()
bcrypt = Bcrypt()
scheduler = APScheduler()
login_manager = LoginManager()
jwt_manager = JWTManager()
cors = CORS()
