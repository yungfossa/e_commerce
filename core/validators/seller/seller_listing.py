from marshmallow import fields, post_load, validates, ValidationError, Schema

from decimal import Decimal
from core.validators.customer.customer_wishlist import BaseSchema
from core.models import Product, ProductState


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
        required=True,
        validate=validate_quantity,
        error_messages={
            "required": "Missing listing quantity",
        },
    )

    price = fields.Decimal(
        required=True,
        places=2,
        validate=validate_price,
        error_messages={
            "required": "Missing listing price",
        },
    )

    @post_load
    def get_validated_edited_listing(self, data, **kwargs):
        return {
            "quantity": data.get("quantity"),
            "price": data.get("price"),
        }


class AddListingSchema(BaseSchema, EditListingSchema):
    product_state = fields.String(
        required=True,
        error_messages={"required": "Missing listing state"},
    )

    @validates("id")
    def validate_product(self, value: str):
        product = Product.query.filter_by(id=value).first()
        if product is None:
            raise ValidationError("Invalid product_id: Product does not exist.")

    @validates("product_state")
    def validate_product_state(self, value: str):
        valid_states = [state.value for state in ProductState]
        if value not in valid_states:
            raise ValidationError("Invalid product_state")

    @post_load
    def get_validated_listing(self, data, **kwargs):
        return {
            "product_id": data.get("id"),
            "quantity": data.get("quantity"),
            "price": data.get("price"),
            "product_state": data.get("product_state"),
        }
