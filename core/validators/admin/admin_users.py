from marshmallow import Schema, fields, post_load, validate


class AdminUsersFiltersSchema(Schema):
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
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "sort_by": data.get("sort_by"),
            "sort_order": data.get("sort_order"),
        }


class AdminDeleteUserSchema(Schema):
    reason = fields.String(required=True, validate=validate.Length(min=10, max=500))

    @post_load
    def get_validated_delete_user_data(self, data, **kwargs):
        return {
            "reason": data.get("reason"),
        }
