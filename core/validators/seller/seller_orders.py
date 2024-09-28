from marshmallow import Schema, fields, post_load, validate


class OrderFilterSchema(Schema):
    status = fields.String(
        required=False,
        validate=validate.OneOf(["pending", "shipped", "delivered", "cancelled"]),
    )
    offset = fields.Integer(
        required=False,
        missing=0,
        validate=validate.Range(min=0),
        error_messages={"invalid arg": "Invalid offset value"},
    )
    limit = fields.Integer(
        required=False,
        missing=10,
        validate=validate.Range(min=1, max=100),
        error_messages={"invalid arg": "Invalid limit value"},
    )
    order_by = fields.String(
        required=False, validate=validate.OneOf(["purchased_at", "total_amount"])
    )
    order_direction = fields.String(
        required=False, validate=validate.OneOf(["asc", "desc"])
    )

    @post_load
    def make_filter_dict(self, data, **kwargs):
        return {
            "status": data.get("status"),
            "offset": data.get("offset"),
            "limit": data.get("limit"),
            "order_by": data.get("order_by", "purchased_at"),
            "order_direction": data.get("order_direction", "desc"),
        }


class UpdateOrderStatusSchema(Schema):
    status = fields.String(
        required=True,
        validate=validate.OneOf(["pending", "shipped", "delivered", "cancelled"]),
    )

    @post_load
    def make_update_dict(self, data, **kwargs):
        return {"status": data["status"]}
