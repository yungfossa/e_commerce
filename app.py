import os

from dotenv import load_dotenv

from core import create_app

load_dotenv()

app = create_app(os.getenv("FLASK_ENV"))
