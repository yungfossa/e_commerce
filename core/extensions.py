from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
jwt_manager = JWTManager()
