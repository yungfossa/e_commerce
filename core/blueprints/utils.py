import re
from functools import wraps
from typing import Any, List, Optional

from flask import current_app, jsonify, render_template, url_for
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from flask_mail import Message

from .. import email_manager
from ..models import User
from .errors.handlers import unauthorized

# RFC 5322 compliant regexp used for email validation
email_pattern = re.compile(
    "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")"
    "@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*"
    "[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)])"
)


def required_user_type(types: List[str]):
    """
    Decorator to restrict access to specific user types.

    Args:
        types (List[str]): List of allowed user types.

    Returns:
        function: Decorated function that checks user type before execution.
    """

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


def success_response(
    message: Optional[str] = None, data: Any = None, status_code: int = 200
):
    """
    Generate a standardized success response.

    Args:
        message (Optional[str]): Optional success message.
        data (Any): Optional data to include in the response.
        status_code (int): HTTP status code, defaults to 200.

    Returns:
        tuple: JSON response and status code.
    """
    response = {}
    if message is not None:
        response["message"] = message
    if data is not None:
        response["data"] = data

    if not response:
        return "ok", status_code
    else:
        return jsonify(response), status_code


def send_email(subject, sender, recipients, html_body, text_body=None):
    """
    Send an email using Flask-Mail.

    Args:
        subject (str): Email subject.
        sender (str): Sender's email address.
        recipients (list): List of recipient email addresses.
        html_body (str): HTML content of the email.
        text_body (str, optional): Plain text content of the email.

    Returns:
        None
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    email_manager.send(msg)


def send_confirmation_email(user: User):
    """
    Send an account verification email to a user.

    Args:
        user (User): User object to send the email to.

    Returns:
        tuple: Success response tuple.
    """
    token = user.get_account_verification_token()
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    send_email(
        subject="Verify Your ShopSphere Account",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        html_body=render_template(
            "email_verification.html",
            username=user.email.split("@")[0],
            confirmation_url=confirm_url,
        ),
    )
    return success_response(status_code=200)


def send_password_reset_email(user: User):
    """
    Send a password reset email to a user.

    Args:
        user (User): User object to send the email to.

    Returns:
        tuple: Success response tuple.
    """
    token = user.get_reset_password_token()
    reset_password_url = url_for("auth.reset_password", token=token, _external=True)
    send_email(
        subject="Reset Your ShopSphere Account Password",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        html_body=render_template(
            "password_reset.html",
            username=user.email.split("@")[0],
            reset_url=reset_password_url,
        ),
    )
    return success_response(status_code=200)


def send_order_confirmation_email(user: User, order_id: str):
    """
    Send an order confirmation email to a user.

    Args:
        user (User): User object to send the email to.
        order_id (str): ID of the order being confirmed.

    Returns:
        tuple: Success response tuple.
    """
    send_email(
        subject="ShopSphere Order Confirmation",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        html_body=render_template(
            "order_confirmation.html",
            username=user.email.split("@")[0],
            order_id=order_id,
        ),
    )
    return success_response(status_code=200)


def send_order_cancellation_email(user: User, order_id: str):
    """
    Send an order cancellation email to a user.

    Args:
        user (User): User object to send the email to.
        order_id (str): ID of the order being cancelled.

    Returns:
        tuple: Success response tuple.
    """
    send_email(
        subject="ShopSphere Order Cancellation",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        html_body=render_template(
            "order_cancellation.html",
            username=user.email.split("@")[0],
            order_id=order_id,
        ),
    )
    return success_response(status_code=200)


# This module contains utility functions for the ShopSphere application.
# It includes functions for user authentication, response formatting, and email sending.

# Key features:
# - User type-based access control decorator
# - Standardized success response function
# - Email sending utilities for various application events (account verification, password reset, order confirmation/cancellation)
# - RFC 5322 compliant email validation pattern

# Note: This module relies on Flask-Mail for email functionality and Flask-JWT-Extended for authentication.
# Ensure these extensions are properly configured in the main application.

# Security considerations:
# - The required_user_type decorator ensures that only authorized user types can access certain routes
# - Email templates should be carefully reviewed to prevent any potential XSS vulnerabilities
# - Tokens used in email verification and password reset should have appropriate expiration times

# Future improvements could include:
# - Adding logging for email sending attempts and results
# - Implementing rate limiting for email sending to prevent abuse
# - Adding support for localization in email templates
