import os

from core import create_app
from dotenv import load_dotenv

load_dotenv()

app = create_app(os.getenv("FLASK_ENV"))
