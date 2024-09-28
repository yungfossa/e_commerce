from marshmallow import Schema, ValidationError, fields, post_load, validate
from marshmallow.validate import Range

from core.extensions import db
from core.models import ProductCategory, ProductState

INVALID_ARG_KEY = "invalid arg"
ORDER_BY_OPTIONS = ["asc", "desc"]


def validate_product_category(title):
    """
    Validate that a product category exists in the database.

    Args:
        title (str): The title of the product category to validate.

    Raises:
        ValidationError: If the category does not exist in the database.
    """
    with db.session() as session:
        category = session.query(ProductCategory).filter_by(title=title).first()
        if not category:
            raise ValidationError(message=f"Invalid category: {title}")


class ProductsFilterSchema(Schema):
    """
    Schema for validating product filter parameters.

    This schema defines and validates various filter options for retrieving products,
    including pagination and category filtering.
    """

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
        """Transform validated filter data into the expected format."""
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "category": data.get("category"),
        }


class ListingsFilterSchema(Schema):
    """
    Schema for validating product listing filter parameters.

    This schema defines and validates various filter options for retrieving product listings,
    including pagination, sorting, and product state filtering.
    """

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
        """Transform validated filter data into the expected format."""
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "product_state": data.get("product_state"),
            "price_order_by": data.get("price_order_by"),
            "review_order_by": data.get("review_order_by"),
            "view_count_order_by": data.get("view_count_order_by"),
            "purchase_count_order_by": data.get("purchase_count_order_by"),
        }


# This module defines schemas for validating product and listing-related operations in the customer interface.

# Key components:
# 1. validate_product_category: A function to validate that a product category exists in the database.
# 2. ProductsFilterSchema: Validates filter parameters for retrieving products, including pagination and category filtering.
# 3. ListingsFilterSchema: Validates filter parameters for retrieving product listings, including pagination,
#    sorting options (price, reviews, view count, purchase count), and product state filtering.

# These schemas ensure that all product and listing-related queries receive valid filter parameters and
# transform the data into a consistent format for further processing by the application logic.

# The use of default values (missing parameter in fields) ensures that even if certain parameters are not provided,
# the queries will still have sensible defaults to work with.

# Note: The ProductState enum is used to validate the product_state field, ensuring that only valid product states are accepted.
