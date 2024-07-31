from core import bcrypt
from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    get_jwt_identity,
)
from core.blueprints.utils import (
    success_response,
    validate_email,
    send_confirmation_email,
    send_password_reset_email,
)
from core.blueprints.errors.handlers import bad_request, unauthorized
from core.models import TokenBlocklist, User, Cart, Customer, WishList, DeleteRequest
from core.extensions import jwt_manager

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = str(data.get("email")).lower()
    name = str(data.get("name")).title()
    surname = str(data.get("surname")).title()
    password = data.get("password")

    if not email:
        return bad_request("Email is missing.")

    if not password:
        return bad_request("Password is missing.")

    if not surname:
        return bad_request("Surname is missing.")

    if not name:
        return bad_request("Name is missing.")

    if not validate_email(email):
        return bad_request("Email not valid.")

    if User.query.filter_by(email=email).first():
        return bad_request("Email already exists")

    customer = Customer.create(
        email=email,
        name=name,
        surname=surname,
        password=bcrypt.generate_password_hash(password, 10).decode("utf-8"),
    )

    Cart.create(customer_id=customer.id)

    WishList.create(
        name="Favorites",
        customer_id=customer.id,
    )

    send_confirmation_email(customer)

    return success_response(
        message="User created successfully. "
        "Please check your email to confirm your account.",
        status_code=201,
    )


@auth_bp.route("/verify/<token>", methods=["GET"])
def confirm_email(token):
    user = User.verify_account_verification_token(token)

    if not user:
        return bad_request("The verification link is invalid or has expired.")

    if user.is_verified:
        return success_response(message="Account already verified.")
    else:
        user.update(is_verified=True, verified_on=datetime.now())

    return success_response("You have verified your account.")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = str(data.get("email")).lower()
    password = data.get("password")

    if not email:
        return bad_request("Missing email.")

    if not password:
        return bad_request("Missing password.")

    if not validate_email(email):
        return bad_request("Email not valid.")

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return unauthorized("Invalid email or password.")

    dr = DeleteRequest.query.filter_by(user_id=user.id).first()

    if dr:
        removal_date = dr.removed_at.strftime("%B %d, %Y")
        return unauthorized(
            f"Your account has been disabled."
            f"If no action is taken, it will be permanently removed on {removal_date}. "
            f"Please contact our support team for assistance or to reactivate your account."
        )

    if not user.is_verified:
        return unauthorized("Please confirm your email before logging in.")

    access_token = create_access_token(
        identity=user.id,
        additional_claims={"user_type": user.user_type.value},
    )

    return success_response(
        message="Login successful.", data={"access_token": access_token}
    )


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_password_token(token)

    if not user:
        return bad_request("The reset password link is invalid or has expired.")

    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password:
        return bad_request("Missing new password.")

    user.update(
        password=bcrypt.generate_password_hash(new_password, 10).decode("utf-8")
    )

    return success_response("Password has been reset correctly.")


@auth_bp.route("/reset-password-request", methods=["POST"])
def request_password_change():
    data = request.get_json()
    email = str(data.get("email")).lower()

    if not email:
        return bad_request("Missing email")

    if not validate_email(email):
        return bad_request("Email not valid")

    user = User.query.filter_by(email=email).first()

    if not user:
        return bad_request("User not found")

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
