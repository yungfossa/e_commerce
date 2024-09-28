from datetime import UTC, datetime, timedelta

from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core.blueprints.errors.handlers import handle_exception, not_found
from core.blueprints.utils import required_user_type, success_response
from core.models import DeleteRequest, User, UserType
from core.validators.admin.admin_users import (
    AdminDeleteUserSchema,
    AdminUsersFiltersSchema,
)

admin_users_bp = Blueprint("admin_users", __name__)

validation_delete_user = AdminDeleteUserSchema()
validation_users_filters = AdminUsersFiltersSchema()


@admin_users_bp.route("/admin/users", methods=["GET"])
@required_user_type(["admin"])
def get_users():
    """
    Retrieve a list of users with filtering and pagination.

    This endpoint allows admins to fetch a list of users with sorting and pagination options.

    Returns:
        A JSON response containing the list of users and pagination information.
    """
    try:
        data = validation_users_filters.load(request.get_json())
    except ValidationError as err:
        return handle_exception(error=err.messages)

    try:
        limit = data.get("limit")
        offset = data.get("offset")
        user_field = data.get("sort_by")
        sort_order = data.get("sort_order")

        query = User.query

        # Apply sorting
        sort_column = getattr(User, user_field)
        if sort_order == "desc":
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        users = query.limit(limit).offset(offset).all()

        return success_response(
            data={
                "users": [u.to_dict(rules=("-password",)) for u in users],
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                },
            },
        )
    except SQLAlchemyError as sql_err:
        return handle_exception(error=str(sql_err))
    except AttributeError as att_err:
        return handle_exception(error=str(att_err))
    except Exception as e:
        return handle_exception(error=str(e))


@admin_users_bp.route("/admin/users/<string:user_ulid>", methods=["GET"])
@required_user_type(["admin"])
def get_user(user_ulid):
    """
    Retrieve details of a specific user.

    This endpoint allows admins to fetch details of a specific user by their ULID.

    Args:
        user_ulid (str): The ULID of the user to retrieve.

    Returns:
        A JSON response containing the user's details (excluding password).
    """
    try:
        user = User.query.get(user_ulid)
        if not user:
            return not_found(error="User not found")
        return success_response(
            data=user.to_dict(rules=("-password",)), status_code=200
        )
    except SQLAlchemyError as sql_err:
        return handle_exception(error=str(sql_err))
    except Exception as e:
        return handle_exception(error=str(e))


@admin_users_bp.route("/admin/users/<string:user_ulid>", methods=["POST"])
@required_user_type(["admin"])
def delete_user(user_ulid):
    """
    Create a delete request for a user.

    This endpoint allows admins to create a delete request for a user. The user will be
    scheduled for deletion after 30 days.

    Args:
        user_ulid (str): The ULID of the user to be deleted.

    Returns:
        A JSON response indicating success or failure of the delete request creation.
    """
    try:
        data = validation_delete_user.load(request.get_json())
    except ValidationError as err:
        return handle_exception(error=err.messages)

    try:
        reason = data.get("reason")

        user = User.query.get(user_ulid)
        if not user:
            return not_found(error="User not found")

        if user.user_type == UserType.ADMIN:
            return handle_exception(error="You cannot delete an admin user")

        existing_delete_request = DeleteRequest.query.filter_by(
            user_id=user_ulid
        ).first()
        if existing_delete_request:
            return handle_exception(
                error="A delete request already exists for this user"
            )

        to_be_removed_at = datetime.now(UTC) + timedelta(days=30)
        _delete_request = DeleteRequest.create(
            user_id=user_ulid, reason=reason, to_be_removed_at=to_be_removed_at
        )

        return success_response(status_code=200)
    except SQLAlchemyError as sql_err:
        return handle_exception(error=str(sql_err))
    except Exception as e:
        return handle_exception(error=str(e))


# This module defines the admin user management endpoints.
# It includes functionality for retrieving user lists, getting specific user details,
# and creating delete requests for users.

# Key features:
# - Pagination and sorting for user list retrieval
# - Detailed error handling for database operations and validation errors
# - User deletion process with a 30-day delay
# - Prevention of admin user deletion

# Note: All endpoints require admin privileges, enforced by the @required_user_type decorator.

# Important considerations:
# - User passwords are excluded from the returned data for security reasons
# - Delete requests are used instead of immediate deletion to allow for potential recovery
# - The module uses UTC for timestamp calculations to ensure consistency across different timezones
