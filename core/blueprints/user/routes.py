from flask import Blueprint
from flask_jwt_extended import get_jwt_identity
from ..errors.handlers import not_found
from ..commons import required_user_type, success_response, get_user

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@required_user_type(["seller", "customer"])
def profile():
    user_email = get_jwt_identity()
    user = get_user(user_email)

    if not user:
        return not_found("user not found")

    if user.user_type.value == "seller":
        return success_response(
            message="seller profile",
            data=user.to_dict(
                only=(
                    "email",
                    "name",
                    "surname",
                    "company",
                    "rating",
                )
            ),
        )

    return success_response(
        message="customer profile",
        data=user.to_dict(
            only=(
                "email",
                "name",
                "surname",
                "phone_number",
            )
        ),
    )
