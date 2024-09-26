from datetime import UTC, datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow.validate import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import (
    bad_request,
    handle_exception,
    internal_server_error,
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
    customer_id = get_jwt_identity()

    try:
        customer = Customer.query.get(customer_id)

        if not customer:
            return handle_exception(message="Customer not found", status_code=404)

        profile_data = {
            "email": customer.email,
            "first_name": customer.name,
            "last_name": customer.surname,
            "birth_date": customer.birth_date,
            "phone_number": customer.phone_number,
            "profile_img": customer.profile_img,
        }

        return success_response(
            message="Customer profile retrieved successfully", data=profile_data
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="A database error occurred while fetching the profile. Please try again later.",
            error=str(e),
        )
    except Exception as e:
        return handle_exception(
            message="An unexpected error occurred while fetching the profile. Please try again later.",
            error=str(e),
        )


@customer_profile_bp.route("/profile", methods=["POST"])
@required_user_type(["customer"])
def edit_profile():
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_edit_profile.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()

        update_data = {
            key: value for key, value in validated_data.items() if value is not None
        }

        if update_data:
            customer.update(**update_data)

        return success_response(message="Profile edited successfully")
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while updating the profile", error=str(e)
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while updating the profile. Please try again later.",
            error=str(e),
        )


@customer_profile_bp.route("/profile", methods=["DELETE"])
@required_user_type(["customer"])
def delete_profile():
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_delete_profile.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    try:
        reason = validated_data.get("reason")

        customer = User.query.filter_by(id=customer_id).first()

        requested_at = datetime.now(UTC)
        to_be_removed_at = requested_at + timedelta(days=30)

        dr = DeleteRequest.create(
            reason=reason,
            requested_at=requested_at,
            user_id=customer.id,
            to_be_removed_at=to_be_removed_at,
        )

        return success_response(
            message=f"your account will be deleted in 30 days."
            f"you can still use it until {dr.expired_at.strftime('%d/%m/%Y')}.",
            status_code=200,
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while deleting the profile", error=str(e)
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while deleting the profile. Please try again later.",
            error=str(e),
        )


@customer_profile_bp.route("/profile/reviews", methods=["GET"])
@required_user_type(["customer"])
def get_reviews():
    costumer_id = get_jwt_identity()

    try:
        query_params = validate_review_filters.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    try:
        order_by = query_params.get("order_by")
        limit = query_params.get("limit")
        offset = query_params.get("offset")

        query = ListingReview.query.filter_by(customer_id=costumer_id)

        if order_by == "newest":
            query = query.order_by(ListingReview.modified_at.desc())
        elif order_by == "oldest":
            query = query.order_by(ListingReview.modified_at.asc())
        elif order_by == "highest":
            query = query.order_by(ListingReview.rating.desc())
        elif order_by == "lowest":
            query = query.order_by(ListingReview.rating.desc())

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

        return success_response(message="Reviews", data=response)
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while getting customer reviews", error=str(e)
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while getting customer reviews. Please try again later.",
            error=str(e),
        )


@customer_profile_bp.route(
    "/products/<string:product_ulid>/<string:listing_ulid>/review", methods=["POST"]
)
@required_user_type(["customer"])
def create_review(product_ulid, listing_ulid):
    customer_id = get_jwt_identity()

    try:
        data = validate_create_review.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    try:
        _lr = ListingReview.create(
            customer_id=customer_id,
            rating=data.get("rating"),
            title=data.get("title"),
            description=data.get("description"),
            listing_id=listing_ulid,
        )

        return success_response(status_code=201)
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while createing a review", error=str(e)
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while creating a review. Please try again later.",
            error=str(e),
        )


@customer_profile_bp.route("/profile/reviews/<string:review_ulid>", methods=["PUT"])
def edit_review(review_ulid):
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_edit_review.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    try:
        review = ListingReview.query.filter_by(
            id=review_ulid, customer_id=customer_id
        ).first()

        if not review:
            return not_found(message="Review not found")

        update_data = {
            key: value for key, value in validated_data.items() if value is not None
        }

        if update_data:
            review.update(**update_data)

        return success_response(message="Review edited successfully", status_code=200)
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while updating the profile", error=str(e)
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            message="An unexpected error occurred while updating the profile. Please try again later.",
            error=str(e),
        )


@customer_profile_bp.route("/profile/reviews/<string:review_ulid>", methods=["DELETE"])
@required_user_type(["customer"])
def delete_customer_review(review_ulid):
    customer_id = get_jwt_identity()

    try:
        review = ListingReview.query.filter_by(
            id=review_ulid, customer_id=customer_id
        ).first()

        if not review:
            return not_found(message="Review not found or already deleted")

        review.delete()

        return success_response(message="Review successfully deleted", status_code=200)

    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="A database error occurred while deleting the review.", error=str(e)
        )
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            message="An unexpected error occurred while deleting the review.",
            error=str(e),
        )
