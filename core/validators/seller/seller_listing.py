from decimal import Decimal

from marshmallow import Schema, ValidationError, fields, post_load, validates
from marshmallow.validate import Length

from core.models import ProductState


def validate_quantity(value: int):
    """
    Validate the quantity of a listing.

    Args:
        value (int): The quantity to validate.

    Raises:
        ValidationError: If the quantity is less than 1.
    """
    if value < 1:
        raise ValidationError("Invalid quantity: quantity should be at least 1")


def validate_price(value: Decimal):
    """
    Validate the price of a listing.

    Args:
        value (Decimal): The price to validate.

    Raises:
        ValidationError: If the price is not between 0.01 and 99999999.99.
    """
    if not (Decimal("0.01") <= value <= Decimal("99999999.99")):
        raise ValidationError(
            "Invalid price: Price must be between 0.01 and 99999999.99"
        )


class EditListingSchema(Schema):
    """
    Schema for validating listing edit requests.

    This schema is used when a seller wants to update an existing listing.
    """

    quantity = fields.Integer(
        required=False,
        validate=validate_quantity,
        error_messages={"required": "Missing listing quantity"},
    )

    price = fields.Decimal(
        required=False,
        places=2,
        validate=validate_price,
        error_messages={"required": "Missing listing price"},
    )

    @post_load
    def get_validated_listing_base(self, data, **kwargs):
        """Transform validated listing edit data into the expected format."""
        return {
            "quantity": data.get("quantity"),
            "price": data.get("price"),
        }


class AddListingSchema(Schema):
    """
    Schema for validating new listing creation requests.

    This schema is used when a seller wants to create a new listing.
    """

    product_id = fields.String(
        required=True,
        validate=Length(equal=26),
        error_messages={"required": "Missing product_id"},
    )
    quantity = fields.Integer(
        required=True,
        validate=validate_quantity,
        error_messages={"required": "Missing listing quantity"},
    )
    price = fields.Decimal(
        required=True,
        places=2,
        validate=validate_price,
        error_messages={"required": "Missing listing price"},
    )
    product_state = fields.String(
        required=True,
        error_messages={"required": "Missing listing state"},
    )

    @validates("product_state")
    def validate_product_state(self, value: str):
        """
        Validate the product state.

        Args:
            value (str): The product state to validate.

        Raises:
            ValidationError: If the product state is not a valid ProductState value.
        """
        if value not in [state.value for state in ProductState]:
            raise ValidationError("Invalid product_state")

    @post_load
    def get_validated_listing(self, data, **kwargs):
        """Transform validated new listing data into the expected format."""
        return {
            "product_id": data.get("product_id"),
            "quantity": data.get("quantity"),
            "price": data.get("price"),
            "product_state": data.get("product_state"),
        }


# This module defines schemas and validation functions for seller listing operations.

# Key components:
# 1. validate_quantity: Ensures that the listing quantity is at least 1.
# 2. validate_price: Ensures that the listing price is within a valid range.
# 3. EditListingSchema: Validates data for updating existing listings.
# 4. AddListingSchema: Validates data for creating new listings.

# These schemas ensure that all listing-related operations receive valid data and
# transform the data into a consistent format for further processing by the application logic.

# The use of custom validation functions (validate_quantity and validate_price) allows for
# reusable and consistent validation across different schemas.

# Note: The ProductState enum is used to validate the product_state field in AddListingSchema,
# ensuring that only valid product states are accepted when creating a new listing.
