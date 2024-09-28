from marshmallow import Schema, ValidationError, fields, post_load, validates_schema
from marshmallow.validate import OneOf, Range

from core.models import ReviewRate  # Add this import at the top of the file

INVALID_ARG_KEY = "invalid arg"

REVIEW_FILTERS = {
    "order": ["newest", "oldest", "highest", "lowest"],
}


class EditCustomerReviewSchema(Schema):
    """
    Schema for validating edit requests for customer reviews.

    This schema allows partial updates to review fields.
    """

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
        """Transform validated edit data into the expected format."""
        return {
            "title": data.get("title"),
            "description": data.get("description"),
            "rating": data.get("rating"),
        }


class CreateReviewSchema(Schema):
    """
    Schema for validating new review creation requests.

    This schema ensures all required fields are present and valid.
    """

    title = fields.String(
        required=True, error_messages={"invalid": "Invalid review title"}
    )
    description = fields.String(
        required=True, error_messages={"invalid": "Invalid review description"}
    )
    rating = fields.Integer(
        required=True,
        validate=Range(min=1, max=5),
        error_messages={"invalid": "Invalid review rating"},
    )

    @validates_schema
    def validate_rating(self, data, **kwargs):
        """
        Validate that the rating is a valid ReviewRate enum value.

        Args:
            data (dict): The data to validate.

        Raises:
            ValidationError: If the rating is not a valid ReviewRate enum value.
        """
        if "rating" in data:
            try:
                ReviewRate(data["rating"])
            except ValueError:
                raise ValidationError("Invalid rating value")

    @post_load
    def get_validated_review(self, data, **kwargs):
        """Transform validated review data into the expected format."""
        return {
            "title": data["title"],
            "description": data["description"],
            "rating": ReviewRate(data["rating"]),
        }


class ReviewFilterSchema(Schema):
    """
    Schema for validating review filter parameters.

    This schema defines and validates various filter options for retrieving reviews,
    including pagination and sorting.
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
    order_by = fields.String(
        required=False,
        missing="newest",
        validate=OneOf(REVIEW_FILTERS.get("order")),
        error_messages={INVALID_ARG_KEY: "Invalid order_by filter"},
    )

    @post_load
    def get_validated_review_filters(self, data, **kwargs):
        """Transform validated filter data into the expected format."""
        return {
            "limit": data.get("limit"),
            "offset": data.get("offset"),
            "order_by": data.get("order_by"),
        }
