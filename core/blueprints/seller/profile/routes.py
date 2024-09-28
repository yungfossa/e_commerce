from datetime import UTC, datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import (
    bad_request,
    handle_exception,
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
    """
    Retrieve the profile information of the authenticated seller.

    Returns:
        JSON response containing the seller's profile information.
    """
    seller_id = get_jwt_identity()

    try:
        seller = Seller.query.filter_by(id=seller_id).first()

        return success_response(
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
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=sql_err)
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


@seller_profile_bp.route("/seller/profile", methods=["POST"])
@required_user_type(["seller"])
def edit_profile():
    """
    Edit the profile information of the authenticated seller.

    Returns:
        JSON response indicating the success of the profile update.
    """
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

        return success_response(
            data=seller.id,
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


@seller_profile_bp.route("/seller/profile", methods=["DELETE"])
@required_user_type(["seller"])
def delete_profile():
    """
    Initiate the process of deleting the authenticated seller's profile.

    This creates a DeleteRequest for the seller's account, which will be processed after 30 days.

    Returns:
        JSON response indicating the success of initiating the delete process.
    """
    seller_id = get_jwt_identity()

    try:
        validated_data = validate_delete_profile.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        reason = validated_data.get("reason")

        seller = User.query.filter_by(id=seller_id).first()

        requested_at = datetime.now(UTC)
        to_be_removed_at = requested_at + timedelta(days=30)

        _dr = DeleteRequest.create(
            reason=reason,
            requested_at=requested_at,
            user_id=seller.id,
            to_be_removed_at=to_be_removed_at,
        )

        return success_response(
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


# This module defines the routes for handling seller profile operations.

# Key features:
# - Retrieve seller profile information
# - Edit seller profile information
# - Initiate the process of deleting a seller's account

# Security considerations:
# - All routes are protected by the @required_user_type decorator, ensuring only sellers can access them
# - The seller ID is obtained from the JWT token, preventing unauthorized access to other sellers' profiles

# Note: This module uses SQLAlchemy for database operations and Marshmallow for request validation.

# Error handling:
# - ValidationErrors are caught and returned as bad requests
# - SQLAlchemyErrors trigger a database rollback and are handled as exceptions
# - General exceptions are also caught and handled appropriately

# Future improvements could include:
# - Implementing profile picture upload functionality
# - Adding more detailed profile information fields
# - Implementing a mechanism to cancel a delete request within the 30-day window
# - Adding email notifications for profile changes and delete requests
