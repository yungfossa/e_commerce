from datetime import datetime, timezone

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core import bcrypt
from core.blueprints.errors.handlers import bad_request, unauthorized
from core.blueprints.utils import (
    send_confirmation_email,
    send_password_reset_email,
    success_response,
)
from core.extensions import db, jwt_manager
from core.models import Cart, Customer, DeleteRequest, TokenBlocklist, User, WishList
from core.validators.auth.user_auth import (
    LoginCredentialsSchema,
    RegisterCredentialsSchema,
    ResetPasswordRequestSchema,
    ResetPasswordSchema,
)

auth_bp = Blueprint("auth", __name__)

register_credentials_schema = RegisterCredentialsSchema()
login_credentials_schema = LoginCredentialsSchema()
request_password_schema = ResetPasswordRequestSchema()
reset_password_schema = ResetPasswordSchema()


@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        validated_data = register_credentials_schema.load(request.get_json())

        email = validated_data.get("email").lower()
        name = validated_data.get("name").title()
        surname = validated_data.get("surname").title()
        password = validated_data.get("password")

        customer = Customer.create(
            email=email,
            name=name,
            surname=surname,
            password=bcrypt.generate_password_hash(password, 10).decode("utf-8"),
        )

    except ValidationError as err:
        return bad_request(err.messages)
    except IntegrityError:
        db.session.rollback()
        return bad_request("Email already exists")

    Cart.create(customer_id=customer.id)

    WishList.create(
        name="favorites",
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
        return bad_request("The verification link is invalid or has expired")

    if user.is_verified:
        return success_response(message="Account already verified")
    else:
        user.update(is_verified=True, verified_on=datetime.now())

    return success_response("You have verified your account")


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        validated_data = login_credentials_schema.load(data=request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    email = validated_data.get("email").lower()
    password = validated_data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return bad_request("User not found")

    if not bcrypt.check_password_hash(user.password, password):
        return unauthorized("Invalid password")

    dr = DeleteRequest.query.filter_by(user_id=user.id).first()

    if dr:
        removal_date = dr.to_be_removed_at.strftime("%B %d, %Y")
        return unauthorized(
            f"Your account has been disabled."
            f"If no action is taken, it will be permanently removed on {removal_date}. "
            f"Please contact our support team for assistance or to reactivate your account."
        )

    if not user.is_verified:
        return unauthorized("Please confirm your email before logging in")

    access_token = create_access_token(
        identity=user.id,
        additional_claims={"user_type": user.user_type.value},
    )

    return success_response(
        message="Login successful", data={"access_token": access_token}
    )


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_password_token(token)

    if not user:
        return bad_request("The reset password link is invalid or has expired.")

    try:
        validated_data = reset_password_schema.load(data=request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    new_password = validated_data.get("password")

    user.update(
        password=bcrypt.generate_password_hash(new_password, 10).decode("utf-8")
    )

    return success_response("Password has been reset correctly.")


@auth_bp.route("/reset-password-request", methods=["POST"])
def request_password_change():
    try:
        validated_data = request_password_schema.load(data=request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    email = validated_data.get("email").lower()

    user = User.query.filter_by(email=email).first()

    if not user:
        return bad_request("User not found")

    send_password_reset_email(user)

    return success_response(
        message="If an account exists with that email, a password reset link has been sent."
    )


@jwt_manager.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None


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

    return success_response(message="Logout successful")
