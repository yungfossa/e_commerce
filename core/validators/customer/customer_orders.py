from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf, Range

INVALID_ARG_KEY = "invalid arg"

ORDER_BY_OPTIONS = ["created_at", "total_amount"]


class OrderHistoryFilterSchema(Schema):
    offset = fields.Integer(
        required=False,
        missing=0,
        validate=Range(min=0),
        error_messages={INVALID_ARG_KEY: "Invalid offset value"},
    )
    limit = fields.Integer(
        required=False,
        missing=10,
        validate=Range(min=1, max=100),
        error_messages={INVALID_ARG_KEY: "Invalid limit value"},
    )
    order_by = fields.String(
        required=False,
        missing="created_at",
        validate=OneOf(ORDER_BY_OPTIONS),
        error_messages={INVALID_ARG_KEY: "Invalid order_by filter"},
    )
    order_direction = fields.String(
        required=False,
        missing="desc",
        validate=OneOf(["asc", "desc"]),
        error_messages={INVALID_ARG_KEY: "Invalid order direction"},
    )

    @post_load
    def get_validated_order_history_filters(self, data, **kwargs):
        return {
            "offset": data.get("offset"),
            "limit": data.get("limit"),
            "order_by": data.get("order_by"),
            "order_direction": data.get("order_direction"),
        }
