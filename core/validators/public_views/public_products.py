from marshmallow import Schema, fields, post_load
from marshmallow.validate import Range

# TODO add filters for product homepage visualization


class ProductsFilterSchema(Schema):
    limit = fields.Integer(
        required=False,
        missing=10,
        validate=Range(min=1, max=100),
        error_messages={"invalid arg": "Invalid limit"},
    )
    offset = fields.Integer(
        required=False,
        missing=0,
        validate=Range(min=0),
        error_messages={"invalid arg": "Invalid offset"},
    )

    @post_load
    def get_validated_review_filters(self, data, **kwargs):
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
        }
