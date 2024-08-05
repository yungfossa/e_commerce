from marshmallow import fields, post_load, validates, ValidationError
from core.validators.customer.customer_wishlist import BaseSchema

from core.models import Listing, Cart, CartEntry


class AddToCartSchema(BaseSchema):
    @validates("id")
    def validate_listing(self, value: str):
        listing = Listing.query.filter_by(id=value).first()
        if listing is None:
            raise ValidationError("Invalid listing_id: Listing does not exist.")

    @post_load
    def get_validated_listing(self, data, **kwargs):
        return {"listing_id": data.get("id")}


class RemoveFromCartSchema(BaseSchema):
    @validates("id")
    def validate_cart_item(self, value: str):
        cart_item = CartEntry.query.filter_by(id=value).first()
        if cart_item is None:
            raise ValidationError("Invalid cart_entry_id: CartEntry does not exist.")

    @post_load
    def get_validated_entry(self, data, **kwargs):
        return {"cart_entry_id": data.get("id")}


class CartDetailsSchema(BaseSchema):
    @validates("id")
    def validate_cart(self, value: str):
        cart = Cart.query.filter_by(id=value).first()
        if cart is None:
            raise ValidationError("Invalid cart_id: Cart does not exist.")

    @post_load
    def get_validated_cart(self, data, **kwargs):
        return {
            "cart_id": data.get("id"),
        }


class UpsertCartSchema(AddToCartSchema):
    amount = fields.Integer(
        required=True, error_messages={"required": "Missing amount"}
    )

    @validates("id")
    def validate_listing(self, value: str):
        listing = Listing.query.filter_by(id=value).first()
        if listing is None:
            raise ValidationError("Invalid listing_id: Listing does not exist.")

    @post_load
    def get_validated_cart_data(self, data, **kwargs):
        return {
            "listing_id": data.get("id"),
            "amount": data.get("amount"),
        }
