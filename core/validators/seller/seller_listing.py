from decimal import Decimal

from marshmallow import Schema, ValidationError, fields, post_load, validates
from marshmallow.validate import Length

from core.models import ProductState


def validate_quantity(value: int):
    if value < 1:
        raise ValidationError("Invalid quantity: quantity should be at least 1")


def validate_price(value: Decimal):
    if not (Decimal("0.01") <= value <= Decimal("99999999.99")):
        raise ValidationError(
            "Invalid price: Price must be between 0.01 and 99999999.99"
        )


class EditListingSchema(Schema):
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
        return {
            "quantity": data.get("quantity"),
            "price": data.get("price"),
        }


class AddListingSchema(Schema):
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
        if value not in [state.value for state in ProductState]:
            raise ValidationError("Invalid product_state")

    @post_load
    def get_validated_listing(self, data, **kwargs):
        return {
            "product_id": data.get("product_id"),
            "quantity": data.get("quantity"),
            "price": data.get("price"),
            "product_state": data.get("product_state"),
        }
