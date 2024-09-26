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

DELETION_PERIOD_DAYS = 30


@admin_users_bp.route("/admin/users", methods=["GET"])
@required_user_type(["admin"])
def get_users():
    try:
        data = validation_users_filters.load(request.get_json())
    except ValidationError as err:
        return handle_exception(message="Validation error", errors=err.messages)

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
            message="Users",
            data={
                "users": [u.to_dict(rules=("-password",)) for u in users],
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                },
            },
        )
    except SQLAlchemyError:
        return handle_exception(
            message="Error while fetching the users from the database"
        )
    except AttributeError:
        return handle_exception(message="Invalid sort_by field")
    except Exception:
        return handle_exception(
            message="Unexpected error occurred while fetching users"
        )


@admin_users_bp.route("/admin/users/<string:user_ulid>", methods=["GET"])
@required_user_type(["admin"])
def get_user(user_ulid):
    user = User.query.get(user_ulid)
    if not user:
        return not_found(message="User not found")
    return success_response(message="User", data=user.to_dict(rules=("-password",)))


@admin_users_bp.route("/admin/users/<string:user_ulid>", methods=["POST"])
@required_user_type(["admin"])
def delete_user(user_ulid):
    try:
        data = validation_delete_user.load(request.get_json())
    except ValidationError as err:
        return handle_exception(message="Validation error", errors=err.messages)

    try:
        reason = data.get("reason")

        user = User.query.get(user_ulid)
        if not user:
            return not_found(message="User not found")

        if user.user_type == UserType.ADMIN:
            return handle_exception(message="You cannot delete an admin user")

        existing_delete_request = DeleteRequest.query.filter_by(
            user_id=user_ulid
        ).first()
        if existing_delete_request:
            return handle_exception(
                message="A delete request already exists for this user"
            )

        to_be_removed_at = datetime.now(UTC) + timedelta(days=DELETION_PERIOD_DAYS)
        _delete_request = DeleteRequest.create(
            user_id=user_ulid, reason=reason, to_be_removed_at=to_be_removed_at
        )

        return success_response(status_code=200)
    except SQLAlchemyError:
        return handle_exception(
            message="Error while creating delete request in the database"
        )
    except Exception:
        return handle_exception(
            message="Unexpected error occurred while processing delete user request"
        )
