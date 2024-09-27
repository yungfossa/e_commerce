from marshmallow import Schema, ValidationError, fields, post_load, validate
from marshmallow.validate import Range

from core.extensions import db
from core.models import ProductCategory, ProductState

INVALID_ARG_KEY = "invalid arg"
ORDER_BY_OPTIONS = ["asc", "desc"]


def validate_product_category(title):
    with db.session() as session:
        category = session.query(ProductCategory).filter_by(title=title).first()
        if not category:
            raise ValidationError(message=f"Invalid category: {title}")


class ProductsFilterSchema(Schema):
    limit = fields.Integer(
        required=False,
        missing=10,
        validate=Range(min=1, max=100),
        error_messages={INVALID_ARG_KEY: "Invalid limit"},
    )
    offset = fields.Integer(
        required=False,
        missing=0,
        validate=Range(min=0),
        error_messages={INVALID_ARG_KEY: "Invalid offset"},
    )
    category = fields.String(
        required=False,
        missing=None,
        validate=validate_product_category,
    )

    @post_load
    def get_validated_review_filters(self, data, **kwargs):
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "category": data.get("category"),
        }


class ListingsFilterSchema(Schema):
    limit = fields.Integer(
        required=False,
        missing=10,
        validate=Range(min=1, max=100),
        error_messages={INVALID_ARG_KEY: "Invalid limit"},
    )
    offset = fields.Integer(
        required=False,
        missing=0,
        validate=Range(min=0),
        error_messages={INVALID_ARG_KEY: "Invalid offset"},
    )
    price_order_by = fields.String(
        required=False,
        missing="desc",
        validate=validate.OneOf(ORDER_BY_OPTIONS),
        error_messages={INVALID_ARG_KEY: "Invalid price_order_by"},
    )
    review_order_by = fields.String(
        required=False,
        missing="highest",
        validate=validate.OneOf(ORDER_BY_OPTIONS),
        error_messages={INVALID_ARG_KEY: "Invalid review_order_by"},
    )
    product_state = fields.String(
        required=False,
        missing=ProductState.NEW.value,
        validate=validate.OneOf([state.value for state in ProductState]),
    )
    view_count_order_by = fields.String(
        required=False, missing="desc", validate=validate.OneOf(ORDER_BY_OPTIONS)
    )
    purchase_count_order_by = fields.String(
        required=False, missing="desc", validate=validate.OneOf(ORDER_BY_OPTIONS)
    )

    @post_load
    def get_validated_filters(self, data, **kwargs):
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "product_state": data.get("product_state"),
            "price_order_by": data.get("price_order_by"),
            "review_order_by": data.get("review_order_by"),
            "view_count_order_by": data.get("view_count_order_by"),
            "purchase_count_order_by": data.get("purchase_count_order_by"),
        }
