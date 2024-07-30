from datetime import datetime, timedelta

from flask import Blueprint, request

from ..utils import required_user_type, success_response
from ...models import User, DeleteRequest
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


@user_bp.route("/profile", methods=["DELETE"])
@required_user_type(["seller", "customer"])
def delete_profile():
    data = request.get_json()
    reason = data.get("reason")

    user = User.query.filter_by(id=get_jwt_identity()).first()

    requested_at = datetime.utcnow()
    removed_at = requested_at + timedelta(days=30)

    dr = DeleteRequest.create(
        reason=reason, requested_at=requested_at, user_id=user.id, removed_at=removed_at
    )

    return success_response(
        f"your account will be deleted in 30 days."
        f"you can still use it until {dr.expired_at.strftime('%d/%m/%Y')}."
    )
