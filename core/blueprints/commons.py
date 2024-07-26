from functools import wraps
from typing import List
from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from .errors.handlers import unauthorized


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


def success_response(message, data=None, status_code=200):
    response = {"message": message}
    if data:
        response["data"] = data
    return jsonify(response), status_code
