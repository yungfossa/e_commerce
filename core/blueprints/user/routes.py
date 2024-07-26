from flask import Blueprint
from ..commons import required_user_type, success_response
from ...models import User
from flask_jwt_extended import get_jwt_identity

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@required_user_type(["seller", "customer"])
def profile():
    user = User.query.filter_by(id=get_jwt_identity()).first()

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
