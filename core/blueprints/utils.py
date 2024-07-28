import shortuuid
from slugify import slugify
from functools import wraps
from typing import List
from flask import jsonify, current_app, url_for, render_template
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from .errors.handlers import unauthorized
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Message
import re

from .. import email_manager

# RFC 5322 compliant regexp used for email validation
email_pattern = re.compile(
    "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")"
    "@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*"
    "[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)])"
)


def required_user_type(types: List[str]):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user_type = get_jwt().get("user_type")
            if current_user_type not in types:
                return unauthorized("user not authorized")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def success_response(message: str, data=None, status_code=200):
    response = {"message": message}
    if data:
        response["data"] = data
    return jsonify(response), status_code


def valide_email(email: str) -> bool:
    return True if email_pattern.match(email) else False


def generate_confirmation_token(email: str):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=current_app.config["MAIL_CONFIRM_SALT"])


def confirm_token(token, expiration=86400):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=current_app.config["MAIL_CONFIRM_SALT"], max_age=expiration
        )
    except BadSignature or SignatureExpired:  # TODO check if it is correct
        return False
    return email


def send_confirmation_email(user_email: str):
    token = generate_confirmation_token(user_email)
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)

    msg = Message(subject="Verify Your ShopSphere Account", recipients=[user_email])
    msg.html = render_template(
        "email_verification.html",
        username=user_email.split("@")[0],
        confirmation_url=confirm_url,
    )
    email_manager.send(msg)
    return success_response(f"verification email sent successfully to {user_email}")


def generate_secure_slug(name, max_length=50):
    # create a base slug from the name, limiting its length
    base_slug = slugify(name)[: max_length - 9]  # -9 to account for '-' and 8 char uuid
    # append a short unique identifier
    unique_id = shortuuid.uuid()[:8]
    return f"{base_slug}-{unique_id}"
