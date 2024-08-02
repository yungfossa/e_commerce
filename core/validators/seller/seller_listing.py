from decimal import Decimal

from marshmallow import fields, post_load, validates, ValidationError, Schema
from marshmallow.validate import Range

from core.validators.customer.customer_wishlist import BaseSchema
from core.models import Product, ProductState


class AddListingSchema(BaseSchema):
    quantity = fields.Integer(
        required=True,
        validate=Range(min=1),
        error_messages={
            "required": "Missing listing quantity",
            "invalid": "Quantity must be a positive integer",
        },
    )
    price = fields.Decimal(
        required=True,
        places=2,
        validate=Range(min=Decimal("0.01"), max=Decimal("99999999.99")),
        error_messages={
            "required": "Missing listing price",
            "invalid": "Price must be between 0.01 and 99999999.99",
        },
    )
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
            "product_id": data["id"],
            "quantity": data["quantity"],
            "price": data["price"],
            "product_state": data["product_state"],
        }


class EditListingSchema(Schema):
    quantity = fields.Integer(
        required=True,
        validate=Range(min=1),
        error_messages={
            "required": "Missing listing quantity",
            "invalid": "Quantity must be a positive integer",
        },
    )

    price = fields.Decimal(
        required=True,
        places=2,
        validate=Range(min=Decimal("0.01"), max=Decimal("99999999.99")),
        error_messages={
            "required": "Missing listing price",
            "invalid": "Price must be between 0.01 and 99999999.99",
        },
    )

    @post_load
    def get_validated_edited_listing(self, data, **kwargs):
        return {
            "quantity": data["quantity"],
            "price": data["price"],
        }
