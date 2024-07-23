from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from ...models import User
from ..errors.handlers import not_found
from ..utils import required_user_type, success_response

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@required_user_type(["seller", "customer", "admin"])
def get_current_user_profile():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return not_found("user not found")

    return success_response(message="profile", data=user.to_dict())


@user_bp.route("/users", methods=["GET"])
@required_user_type(["admin"])
def users():
    us = User.query.all()
    return jsonify(users=[u.to_dict() for u in us]), 200
