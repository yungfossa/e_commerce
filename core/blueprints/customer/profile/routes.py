from datetime import UTC, datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow.validate import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import (
    bad_request,
    handle_exception,
    not_found,
)
from core.blueprints.utils import required_user_type, success_response
from core.models import (
    Customer,
    DeleteRequest,
    ListingReview,
    User,
)
from core.validators.customer.customer_review import (
    CreateReviewSchema,
    EditCustomerReviewSchema,
    ReviewFilterSchema,
)
from core.validators.user_profile import DeleteProfileSchema, EditProfileSchema

customer_profile_bp = Blueprint("customer_profile", __name__)

validate_edit_profile = EditProfileSchema()
validate_delete_profile = DeleteProfileSchema()
validate_edit_review = EditCustomerReviewSchema()
validate_create_review = CreateReviewSchema()
validate_review_filters = ReviewFilterSchema()


@customer_profile_bp.route("/profile", methods=["GET"])
@required_user_type(["customer"])
def get_profile():
    """
    Retrieve the profile information of the authenticated customer.

    Returns:
        JSON response containing customer profile data or an error message.
    """
    customer_id = get_jwt_identity()

    try:
        customer = Customer.query.get(customer_id)

        if not customer:
            return not_found(error="Customer not found")

        profile_data = {
            "email": customer.email,
            "first_name": customer.name,
            "last_name": customer.surname,
            "birth_date": customer.birth_date,
            "phone_number": customer.phone_number,
            "profile_img": customer.profile_img,
        }

        return success_response(data=profile_data, status_code=200)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        return handle_exception(
            error=str(e),
        )


@customer_profile_bp.route("/profile", methods=["POST"])
@required_user_type(["customer"])
def edit_profile():
    """
    Edit the profile information of the authenticated customer.

    Returns:
        JSON response indicating success or an error message.
    """
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_edit_profile.load(request.get_json())
    except ValidationError as verr:
        return bad_request(error=verr.messages)

    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()

        update_data = {
            key: value for key, value in validated_data.items() if value is not None
        }

        if update_data:
            customer.update(**update_data)

        return success_response(
            status_code=200,
        )
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


@customer_profile_bp.route("/profile", methods=["DELETE"])
@required_user_type(["customer"])
def delete_profile():
    """
    Create a delete request for the authenticated customer's profile.

    Returns:
        JSON response indicating success or an error message.
    """
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_delete_profile.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        reason = validated_data.get("reason")

        customer = User.query.filter_by(id=customer_id).first()

        requested_at = datetime.now(UTC)
        to_be_removed_at = requested_at + timedelta(days=30)

        _dr = DeleteRequest.create(
            reason=reason,
            requested_at=requested_at,
            user_id=customer.id,
            to_be_removed_at=to_be_removed_at,
        )

        return success_response(
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@customer_profile_bp.route("/profile/reviews", methods=["GET"])
@required_user_type(["customer"])
def get_reviews():
    """
    Retrieve reviews created by the authenticated customer.

    Returns:
        JSON response containing a list of reviews and pagination information.
    """
    customer_id = get_jwt_identity()

    try:
        query_params = validate_review_filters.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        order_by = query_params.get("order_by")
        limit = query_params.get("limit")
        offset = query_params.get("offset")

        query = ListingReview.query.filter_by(customer_id=customer_id)

        if order_by == "newest":
            query = query.order_by(ListingReview.modified_at.desc())
        elif order_by == "oldest":
            query = query.order_by(ListingReview.modified_at.asc())
        elif order_by == "highest":
            query = query.order_by(ListingReview.rating.desc())
        elif order_by == "lowest":
            query = query.order_by(ListingReview.rating.asc())

        reviews = query.limit(limit).offset(offset).all()

        review_list = [
            {
                "title": review.title,
                "description": review.description,
                "rating": review.rating,
                "modified_at": review.modified_at,
            }
            for review in reviews
        ]

        total_reviews = query.count()

        response = {
            "total_reviews": total_reviews,
            "limit": limit,
            "offset": offset,
            "reviews": review_list,
        }

        return success_response(
            data=response,
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


@customer_profile_bp.route(
    "/products/<string:product_ulid>/<string:listing_ulid>/review", methods=["POST"]
)
@required_user_type(["customer"])
def create_review(product_ulid, listing_ulid):
    """
    Create a new review for a specific product listing.

    Args:
        product_ulid (str): The ULID of the product.
        listing_ulid (str): The ULID of the listing.

    Returns:
        JSON response containing the new review ID or an error message.
    """
    customer_id = get_jwt_identity()

    try:
        data = validate_create_review.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        _lr = ListingReview.create(
            customer_id=customer_id,
            rating=data.get("rating"),
            title=data.get("title"),
            description=data.get("description"),
            listing_id=listing_ulid,
        )

        return success_response(data={"id": _lr.id}, status_code=201)

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


@customer_profile_bp.route("/profile/reviews/<string:review_ulid>", methods=["PUT"])
@required_user_type(["customer"])
def edit_review(review_ulid):
    """
    Edit an existing review created by the authenticated customer.

    Args:
        review_ulid (str): The ULID of the review to edit.

    Returns:
        JSON response indicating success or an error message.
    """
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_edit_review.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        review = ListingReview.query.filter_by(
            id=review_ulid, customer_id=customer_id
        ).first()

        if not review:
            return not_found(error="Review not found")

        update_data = {
            key: value for key, value in validated_data.items() if value is not None
        }

        if update_data:
            review.update(**update_data)

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


@customer_profile_bp.route("/profile/reviews/<string:review_ulid>", methods=["DELETE"])
@required_user_type(["customer"])
def delete_customer_review(review_ulid):
    """
    Delete a review created by the authenticated customer.

    Args:
        review_ulid (str): The ULID of the review to delete.

    Returns:
        JSON response indicating success or an error message.
    """
    customer_id = get_jwt_identity()

    try:
        review = ListingReview.query.filter_by(
            id=review_ulid, customer_id=customer_id
        ).first()

        if not review:
            return not_found(error="Review not found or already deleted")

        review.delete()

        return success_response(
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


# This module defines the customer profile management endpoints.

# Key features:
# - Retrieve and edit customer profile information
# - Create a delete request for the customer's profile
# - Manage customer reviews (create, edit, delete, and retrieve)

# Security considerations:
# - All endpoints are protected by the @required_user_type decorator, ensuring only customers can access them
# - The customer ID is obtained from the JWT token, preventing unauthorized access to other users' profiles and reviews

# Note: This module uses SQLAlchemy for database operations and Marshmallow for request validation.

# Error handling:
# - ValidationErrors are caught and returned as bad requests
# - SQLAlchemyErrors trigger a database rollback and are handled as exceptions
# - General exceptions are also caught and handled appropriately

# Future improvements could include:
# - Implementing a more robust profile picture upload system
# - Adding support for customer preferences or settings
# - Implementing a review moderation system
