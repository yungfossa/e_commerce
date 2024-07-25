from functools import wraps
from typing import List
from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from .errors.handlers import unauthorized
from sqlalchemy.orm.exc import NoResultFound
from ..models import User
from .errors.handlers import not_found


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


def get_user(email: str) -> User:
    try:
        return User.query.filter_by(email=email).first()
    except NoResultFound:
        not_found(f"user with email {email} not found")


def json_action_response(action, message, **kwargs):
    """
    create a JSON response indicating an action that should be taken by the client.

    :param action: The action that should be taken (e.g., 'remove', 'update')
    :param message: A message describing the action
    :param kwargs: Additional key-value pairs to include in the response
    :return: A JSON response with a 200 status code
    """
    response_data = {"action": action, "message": message, **kwargs}
    return jsonify(response_data), 200


def success_response(message, data=None, status_code=200):
    response = {"message": message}
    if data:
        response["data"] = data
    return jsonify(response), status_code
