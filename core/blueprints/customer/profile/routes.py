from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow.validate import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime, timedelta

from core import db
from core.blueprints.errors.handlers import (
    not_found,
    bad_request,
    internal_server_error,
    handle_exception,
)
from core.blueprints.utils import required_user_type, success_response
from core.models import User, DeleteRequest, Customer, ListingReview
from core.validators.customer.customer_review import (
    EditCustomerReviewSchema,
    ReviewFilterSchema,
)
from core.validators.user_profile import EditProfileSchema, DeleteProfileSchema

customer_profile_bp = Blueprint("customer_profile", __name__)

validate_edit_profile = EditProfileSchema()
validate_delete_profile = DeleteProfileSchema()
validate_edit_review = EditCustomerReviewSchema()
validate_review_filters = ReviewFilterSchema()


@customer_profile_bp.route("/profile", methods=["GET"])
@required_user_type(["customer"])
def get_profile():
    customer = Customer.query.filter_by(id=get_jwt_identity()).first()

    return success_response(
        message="profile",
        data=customer.to_dict(
            only=(
                "email",
                "name",
                "surname",
                "birth_date",
                "phone_number",
                "profile_img",
            )
        ),
    )


@customer_profile_bp.route("/profile", methods=["POST"])
@required_user_type(["customer"])
def edit_profile():
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_edit_profile.load(request.get_json())

        customer = Customer.query.filter_by(customer_id=customer_id).first()

        update_data = {
            key: value for key, value in validated_data.items() if value is not None
        }

        if update_data:
            customer.update(**update_data)

        return success_response(message="Profile edited successfully")

    except ValidationError as verr:
        return bad_request(verr.messages)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while updating the profile")
    except Exception:
        db.session.rollback()
        return internal_server_error()


@customer_profile_bp.route("/profile", methods=["DELETE"])
@required_user_type(["customer"])
def delete_profile():
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_delete_profile.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    customer = User.query.filter_by(id=customer_id).first()

    requested_at = datetime.utcnow()
    removed_at = requested_at + timedelta(days=30)

    dr = DeleteRequest.create(
        reason=validated_data["reason"],
        requested_at=requested_at,
        user_id=customer.id,
        removed_at=removed_at,
    )

    return success_response(
        f"your account will be deleted in 30 days."
        f"you can still use it until {dr.expired_at.strftime('%d/%m/%Y')}."
    )


@customer_profile_bp.route("/profile/reviews", methods=["POST"])
@required_user_type(["customer"])
def get_reviews():
    costumer_id = get_jwt_identity()

    try:
        query_params = validate_review_filters.load(request.get_json())

        date_filter = query_params.get("date_filter")
        rate_filter = query_params.get("rate_filter")
        limit = query_params["limit"]
        offset = query_params["offset"]

        query = ListingReview.query.filter_by(customer_id=costumer_id)

        if date_filter == "newest":
            query = query.order_by(ListingReview.modified_at.desc())
        elif date_filter == "oldest":
            query = query.order_by(ListingReview.modified_at.asc())

        if rate_filter == "highest":
            query = query.order_by(ListingReview.rating.desc())
        elif rate_filter == "lowest":
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
    except ValidationError as verr:
        return bad_request(verr.messages)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while getting customer reviews"
        )
    except Exception:
        db.session.rollback()
        return internal_server_error()


@customer_profile_bp.route("/profile/reviews/<string:review_ulid>", methods=["PUT"])
def edit_review(review_ulid):
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_edit_review.load(request.get_json())

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

        return success_response(message="Review edited successfully")

    except ValidationError as verr:
        return bad_request(verr.messages)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while updating the profile")
    except Exception:
        db.session.rollback()
        return internal_server_error()


@customer_profile_bp.route("/profile/reviews/<string:review_ulid>", methods=["DELETE"])
@required_user_type(["customer"])
def delete_customer_review(review_ulid):
    customer_id = get_jwt_identity()

    review = ListingReview.query.filter_by(
        id=review_ulid, customer_id=customer_id
    ).first()

    if not review:
        return not_found(message="Review not found or already deleted")

    review.delete()

    return success_response(message="Review successfully deleted")


# TODO implement get_orders_history
@customer_profile_bp.route("/profile/orders-history", methods=["GET"])
@required_user_type(["customer"])
def get_orders_history():
    return "hello"
