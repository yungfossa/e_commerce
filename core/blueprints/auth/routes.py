from core import bcrypt
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    get_jwt_identity,
)
from ..utils import (
    success_response,
    validate_email,
    send_confirmation_email,
    generate_secure_slug,
    send_password_reset_email,
)
from ..errors.handlers import bad_request, unauthorized
from ...models import TokenBlocklist, User, Cart, Customer, WishList
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

    if not validate_email(email):
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

    default_wishlist_name = "Favorites"

    WishList.create(
        name=default_wishlist_name,
        customer_id=customer.id,
        slug=generate_secure_slug(default_wishlist_name),
    )

    send_confirmation_email(customer)

    return success_response(
        message="user created successfully. "
        "please check your email to confirm your account.",
        status_code=201,
    )


@auth_bp.route("/verify/<token>", methods=["GET"])
def confirm_email(token):
    user = User.verify_account_verification_token(token)

    if not user:
        return bad_request("the confirmation link is invalid or has expired")

    if user.is_verified:
        return success_response(message="account already confirmed")
    else:
        user.update(is_verified=True, verified_on=datetime.now())  # TODO try-catch?

    return success_response("you have confirmed your account")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = str(data.get("email")).lower()
    password = data.get("password")

    if not email or not password:
        return bad_request("missing email or password")

    if not validate_email(email):
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


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_password_token(token)

    if not user:
        return bad_request("the reset password link is invalid or has expired")

    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password:
        return bad_request("missing password")

    user.update(
        password=bcrypt.generate_password_hash(new_password, 10).decode("utf-8")
    )  # TODO try-catch?

    return success_response("password has been reset correctly")


@auth_bp.route("/reset-password-request", methods=["POST"])
def request_password_change():
    data = request.get_json()
    email = str(data.get("email")).lower()

    if not email:
        return bad_request("missing email")

    if not validate_email(email):
        return bad_request("email not valid")

    user = User.query.filter_by(email=email).first()

    if not user:
        return bad_request("user not found")

    send_password_reset_email(user)

    return success_response(
        message="If an account exists with that email, a password reset link has been sent."
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
