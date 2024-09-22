from decimal import Decimal

from marshmallow import Schema, ValidationError, fields, post_load, validates

from core.models import Product, ProductState
from core.validators.customer.customer_wishlist import BaseSchema


def validate_quantity(value: int):
    if value < 1:
        raise ValidationError("Invalid quantity: quantity should be at least 1")


def validate_price(value: Decimal):
    if not (Decimal("0.01") <= value <= Decimal("99999999.99")):
        raise ValidationError(
            "Invalid price: Price must be between 0.01 and 99999999.99"
        )


class ListingSchemaBase(Schema):
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

    @post_load
    def get_validated_listing_base(self, data, **kwargs):
        return {
            "quantity": data["quantity"],
            "price": data["price"],
        }


class EditListingSchema(ListingSchemaBase):
    pass


class AddListingSchema(BaseSchema, ListingSchemaBase):
    product_state = fields.String(
        required=True,
        error_messages={"required": "Missing listing state"},
    )

    @validates("id")
    def validate_product(self, value: str):
        if not Product.query.filter_by(id=value).first():
            raise ValidationError("Invalid product_id: Product does not exist.")

    @validates("product_state")
    def validate_product_state(self, value: str):
        if value not in [state.value for state in ProductState]:
            raise ValidationError("Invalid product_state")

    @post_load
    def get_validated_listing(self, data, **kwargs):
        validated_data = self.get_validated_listing_base(data)
        validated_data.update(
            {
                "product_id": data["id"],
                "product_state": data["product_state"],
            }
        )
        return validated_data
