from datetime import UTC, datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import (
    bad_request,
    handle_exception,
    internal_server_error,
)
from core.blueprints.utils import required_user_type, success_response
from core.models import DeleteRequest, Seller, User
from core.validators.user_profile import DeleteProfileSchema, EditSellerProfileSchema

seller_profile_bp = Blueprint("seller_profile", __name__)

validate_delete_profile = DeleteProfileSchema()
validate_edit_profile = EditSellerProfileSchema()


@seller_profile_bp.route("/seller/profile", methods=["GET"])
@required_user_type(["seller"])
def get_profile():
    seller_id = get_jwt_identity()

    try:
        seller = Seller.query.filter_by(id=seller_id).first()

        return success_response(
            message="profile",
            data=seller.to_dict(
                only=(
                    "email",
                    "name",
                    "surname",
                    "birth_date",
                    "phone_number",
                    "profile_img",
                    "company_name",
                )
            ),
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while fetching the seller profile", error=str(e)
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while fetching the seller profile. Please try again later.",
            error=str(e),
        )


@seller_profile_bp.route("/seller/profile", methods=["POST"])
@required_user_type(["seller"])
def edit_profile():
    seller_id = get_jwt_identity()

    try:
        validated_data = validate_edit_profile.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    try:
        seller = Seller.query.filter_by(seller_id=seller_id).first()

        update_data = {
            key: value for key, value in validated_data.items() if value is not None
        }

        if update_data:
            seller.update(**update_data)

        return success_response(data=seller.id, status_code=200)

    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while updating the profile")
    except Exception:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while updating the profile. Please try again later."
        )


@seller_profile_bp.route("/seller/profile", methods=["DELETE"])
@required_user_type(["seller"])
def delete_profile():
    seller_id = get_jwt_identity()

    try:
        validated_data = validate_delete_profile.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    try:
        reason = validated_data.get("reason")

        seller = User.query.filter_by(id=seller_id).first()

        requested_at = datetime.now(UTC)
        to_be_removed_at = requested_at + timedelta(days=30)

        dr = DeleteRequest.create(
            reason=reason,
            requested_at=requested_at,
            user_id=seller.id,
            to_be_removed_at=to_be_removed_at,
        )

        return success_response(
            f"Your account will be deleted in 30 days. "
            f"You can still use it until {dr.to_be_removed_at.strftime('%d/%m/%Y')}."
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while processing the delete request",
            error=str(e),
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while processing the delete request. Please try again later.",
            error=str(e),
        )
