from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf, Range

review_filters = {
    "date_filter": ["newest", "oldest"],
    "rate_filter": ["highest", "lowest"],
}


class EditCustomerReviewSchema(Schema):
    title = fields.String(
        required=False, error_messages={"invalid": "Invalid review title"}
    )
    description = fields.String(
        required=False, error_messages={"invalid": "Invalid review description"}
    )
    rating = fields.String(
        required=False, error_messages={"invalid": "Invalid review rating"}
    )

    @post_load
    def get_validated_edited_review(self, data, **kwargs):
        return {
            "title": data.get("title"),
            "description": data.get("description"),
            "rating": data.get("rating"),
        }


class ReviewFilterSchema(Schema):
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
    date_filter = fields.String(
        required=False,
        missing="newest",
        validate=OneOf(review_filters.get("date_filter")),
        error_messages={"invalid arg": "Invalid date_filter"},
    )
    rate_filter = fields.String(
        required=False,
        missing="highest",
        validate=OneOf(review_filters.get("rate_filter")),
        error_messages={"invalid arg": "Invalid rate_filter"},
    )

    @post_load
    def get_validated_review_filters(self, data, **kwargs):
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "date_filter": data.get("date_filter"),
            "rate_filter": data.get("rate_filter"),
        }
