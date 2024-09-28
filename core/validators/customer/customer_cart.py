from marshmallow import Schema, ValidationError, fields, post_load, validates

from core.models import Cart, CartEntry, Listing
from core.validators.customer.customer_wishlist import BaseSchema


class AddToCartSchema(BaseSchema):
    """
    Schema for validating requests to add items to the cart.

    Inherits from BaseSchema which likely includes common fields like 'id'.
    """

    @validates("id")
    def validate_listing(self, value: str):
        """
        Validate that the listing exists in the database.

        Args:
            value (str): The ID of the listing to be added to the cart.

        Raises:
            ValidationError: If the listing does not exist.
        """
        listing = Listing.query.filter_by(id=value).first()
        if listing is None:
            raise ValidationError("Invalid listing_id: Listing does not exist.")

    @post_load
    def get_validated_listing(self, data, **kwargs):
        """Transform validated data into the expected format."""
        return {"listing_id": data.get("id")}


class RemoveFromCartSchema(BaseSchema):
    """Schema for validating requests to remove items from the cart."""

    cart_item_ids = fields.List(fields.String(), required=True)

    @validates("cart_item_ids")
    def validate_cart_items(self, value):
        """
        Validate that all provided cart item IDs exist in the database.

        Args:
            value (List[str]): List of cart item IDs to be removed.

        Raises:
            ValidationError: If the list is empty or if any ID is invalid.
        """
        if not value:
            raise ValidationError("At least one cart_item_id must be provided.")

        for item_id in value:
            cart_item = CartEntry.query.filter_by(id=item_id).first()
            if cart_item is None:
                raise ValidationError(
                    f"Invalid cart_item_id: CartEntry with id {item_id} does not exist."
                )

    @post_load
    def get_validated_entries(self, data, **kwargs):
        """Transform validated data into the expected format."""
        return {"cart_item_ids": data.get("cart_item_ids")}


class CartDetailsSchema(BaseSchema):
    """Schema for validating requests to get cart details."""

    @validates("id")
    def validate_cart(self, value: str):
        """
        Validate that the cart exists in the database.

        Args:
            value (str): The ID of the cart.

        Raises:
            ValidationError: If the cart does not exist.
        """
        cart = Cart.query.filter_by(id=value).first()
        if cart is None:
            raise ValidationError("Invalid cart_id: Cart does not exist.")

    @post_load
    def get_validated_cart(self, data, **kwargs):
        """Transform validated data into the expected format."""
        return {
            "cart_id": data.get("id"),
        }


class UpsertCartSchema(Schema):
    """Schema for validating requests to update or insert cart items."""

    listing_id = fields.String(
        required=True, error_messages={"required": "Missing listing_id"}
    )
    quantity = fields.Integer(
        required=True, error_messages={"required": "Missing amount"}
    )

    @post_load
    def get_validated_cart_data(self, data, **kwargs):
        """Transform validated data into the expected format."""
        return {
            "listing_id": data.get("listing_id"),
            "quantity": data.get("quantity"),
        }
