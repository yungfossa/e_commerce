from core import bcrypt
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    get_jwt_identity,
)
from ..commons import success_response
from ..errors.handlers import bad_request, unauthorized
from ...models import TokenBlocklist, User, Cart, Customer
from ...extensions import jwt_manager

auth_bp = Blueprint("auth", __name__)


# TODO need to add birth_date field in the input


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = str(data.get("email")).lower()
    name = str(data.get("name")).lower()
    surname = str(data.get("surname")).lower()
    password = data.get("password")

    if not email or not password:
        return bad_request("missing email or password")

    if User.query.filter_by(email=email).first():
        return bad_request("email already exists")

    customer = Customer.create(
        email=email,
        name=name,
        surname=surname,
        password=bcrypt.generate_password_hash(password, 10).decode("utf-8"),
    )

    Cart.create(customer_id=customer.id)

    return success_response(
        message="user and his cart created successfully", status_code=201
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = str(data.get("email")).lower()
    password = data.get("password")

    if not email or not password:
        return bad_request("missing email or password")

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return unauthorized("invalid email or password")

    access_token = create_access_token(
        identity=email, additional_claims={"user_type": user.user_type.value}
    )

    return success_response(
        message="login successful", data={"access_token": access_token}
    )


# callback function to check if a JWT exists in the database blocklist
@jwt_manager.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None


# endpoint for revoking the current user access token. saved the unique identifier
# (jti) for the JWT into our database
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def revoke_token():
    jwt_payload = get_jwt()
    jti = jwt_payload["jti"]
    exp = datetime.fromtimestamp(jwt_payload["exp"], timezone.utc)
    now = datetime.now(timezone.utc)

    current_user_id = (
        User.query.with_entities(User.id).filter_by(email=get_jwt_identity()).scalar()
    )

    TokenBlocklist.create(
        jti=jti, created_at=now, expired_at=exp, user_id=current_user_id
    )

    return success_response(message="jwt token revoked successfully")
