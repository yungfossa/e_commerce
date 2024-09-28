import os

from dotenv import load_dotenv

from core import create_app

# Load environment variables from .env file
load_dotenv()

# Create the Flask application instance
app = create_app(os.getenv("FLASK_ENV"))
