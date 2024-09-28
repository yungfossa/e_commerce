from marshmallow import Schema, fields, post_load, validate


class AdminUsersFiltersSchema(Schema):
    """
    Schema for validating and deserializing admin user list filters.

    This schema defines the expected structure and validation rules for
    filtering and sorting the list of users in the admin interface.
    """

    limit = fields.Integer(
        required=False, missing=10, validate=validate.Range(min=1, max=100)
    )
    offset = fields.Integer(required=False, missing=0, validate=validate.Range(min=0))
    sort_by = fields.String(
        required=False,
        missing="id",
        validate=validate.OneOf(
            ["id", "username", "email", "name", "surname", "created_at"]
        ),
    )
    sort_order = fields.String(
        required=False, missing="asc", validate=validate.OneOf(["asc", "desc"])
    )

    @post_load
    def get_validated_admin_users_filters(self, data, **kwargs):
        """
        Post-load hook to transform validated filter data.

        Args:
            data (dict): The validated filter data.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: A dictionary containing the validated and formatted filter data.
        """
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "sort_by": data.get("sort_by"),
            "sort_order": data.get("sort_order"),
        }


class AdminDeleteUserSchema(Schema):
    """
    Schema for validating and deserializing user deletion requests.

    This schema ensures that a reason is provided when an admin attempts to delete a user,
    and that the reason meets certain length requirements.
    """

    reason = fields.String(required=True, validate=validate.Length(min=10, max=500))

    @post_load
    def get_validated_delete_user_data(self, data, **kwargs):
        """
        Post-load hook to transform validated deletion request data.

        Args:
            data (dict): The validated deletion request data.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: A dictionary containing the validated deletion reason.
        """
        return {
            "reason": data.get("reason"),
        }


# This module defines Marshmallow schemas for validating and deserializing
# input data related to admin operations on users.

# Key components:
# 1. AdminUsersFiltersSchema: Used for validating and formatting filter parameters
#    when listing users in the admin interface. It includes options for pagination,
#    sorting, and ordering.
# 2. AdminDeleteUserSchema: Used for validating the reason provided when an admin
#    attempts to delete a user account.

# These schemas help ensure data integrity, provide clear constraints on input data,
# and format the data for use in the application's business logic. They contribute
# to the robustness and security of the admin interface by enforcing data validation
# rules.
