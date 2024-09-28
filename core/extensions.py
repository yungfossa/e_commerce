from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy for database operations
db = SQLAlchemy()

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

# Initialize APScheduler for task scheduling
scheduler = APScheduler()

# Initialize Flask-Mail for email functionality
email_manager = Mail()

# Initialize JWTManager for JSON Web Token handling
jwt_manager = JWTManager()

# Initialize CORS for Cross-Origin Resource Sharing
cors = CORS()

# This module initializes various Flask extensions used throughout the application.
# These extensions provide additional functionality to the Flask app, such as:

# 1. SQLAlchemy (db): ORM for database operations
#    Used for defining models and interacting with the database.

# 2. Bcrypt (bcrypt): Password hashing
#    Used for securely hashing and checking passwords.

# 3. APScheduler (scheduler): Task scheduling
#    Used for scheduling and running background tasks.

# 4. Flask-Mail (email_manager): Email functionality
#    Used for sending emails from the application.

# 5. JWTManager (jwt_manager): JSON Web Token handling
#    Used for creating and verifying JWTs for authentication.

# 6. CORS (cors): Cross-Origin Resource Sharing
#    Used to handle cross-origin requests, typically in API scenarios.

# Usage:
# These extensions are typically initialized in the application factory
# (usually in __init__.py) using their respective init_app methods.

# Example:
#   def create_app(config_name):
#       app = Flask(__name__)
#       db.init_app(app)
#       bcrypt.init_app(app)
#       scheduler.init_app(app)
#       email_manager.init_app(app)
#       jwt_manager.init_app(app)
#       cors.init_app(app)
#       ...

# By centralizing the extension initialization here, we keep the main app
# creation clean and make it easier to manage and update extensions.
