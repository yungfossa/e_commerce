from core import bcrypt
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    get_jwt_identity,
)
from ..commons import (
    success_response,
    valide_email,
    send_confirmation_email,
    confirm_token,
)
from ..errors.handlers import bad_request, unauthorized, not_found
from ...models import TokenBlocklist, User, Cart, Customer
from ...extensions import jwt_manager

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = str(data.get("email")).lower()
    name = str(data.get("name")).title()
    surname = str(data.get("surname")).title()
    password = data.get("password")

    if not email or not password or not surname or not name:
        return bad_request("missing information")

    if not valide_email(email):
        return bad_request("email not valid")

    if User.query.filter_by(email=email).first():
        return bad_request("email already exists")

    customer = Customer.create(
        email=email,
        name=name,
        surname=surname,
        password=bcrypt.generate_password_hash(password, 10).decode("utf-8"),
    )

    Cart.create(customer_id=customer.id)

    send_confirmation_email(email)

    return success_response(
        message="user created successfully. "
        "please check your email to confirm your account.",
        status_code=201,
    )


@auth_bp.route("/verify/<token>")
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        return bad_request("the confirmation link is invalid or has expired")

    user = User.query.filter_by(email=email).first()

    if not user:
        return not_found("user not found")

    if user.is_verified:
        return success_response(message="account already confirmed")
    else:
        user.update(is_verified=True, verified_on=datetime.now())

    return success_response("you have confirmed your account")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = str(data.get("email")).lower()
    password = data.get("password")

    if not email or not password:
        return bad_request("missing email or password")

    if not valide_email(email):
        return bad_request("email not valid")

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return unauthorized("invalid email or password")

    if not user.is_verified:
        return unauthorized("please confirm your email before logging in")

    access_token = create_access_token(
        identity=user.id,
        additional_claims={"user_type": user.user_type.value},
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

    TokenBlocklist.create(
        jti=jti, created_at=now, expired_at=exp, user_id=get_jwt_identity()
    )

    return success_response(message="jwt token revoked successfully")
