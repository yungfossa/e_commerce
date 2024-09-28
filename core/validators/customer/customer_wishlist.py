from marshmallow import Schema, ValidationError, fields, post_load, validates
from marshmallow.validate import Length

from core.models import Listing, WishList, WishListEntry


class BaseSchema(Schema):
    """
    Base schema with common fields for wishlist-related operations.
    """

    id = fields.String(
        required=True,
        validate=Length(equal=26),
        error_messages={"required": "Missing id"},
    )


class AddToWishlistSchema(BaseSchema):
    """
    Schema for validating requests to add items to a wishlist.
    """

    @validates("id")
    def validate_listing(self, value: str):
        """
        Validate that the listing exists in the database.

        Args:
            value (str): The ID of the listing to be added to the wishlist.

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


class RemoveFromWishlistSchema(BaseSchema):
    """
    Schema for validating requests to remove items from a wishlist.
    """

    @validates("id")
    def validate_wishlist_item(self, value: str):
        """
        Validate that the wishlist item exists in the database.

        Args:
            value (str): The ID of the wishlist item to be removed.

        Raises:
            ValidationError: If the wishlist item does not exist.
        """
        wishlist_item = WishListEntry.query.filter_by(id=value).first()
        if wishlist_item is None:
            raise ValidationError(
                "Invalid wishlist_entry_id: WishListItem does not exist."
            )

    @post_load
    def get_validated_entry(self, data, **kwargs):
        """Transform validated data into the expected format."""
        return {"wishlist_entry_id": data.get("id")}


class UpsertWishlistSchema(BaseSchema):
    """
    Schema for validating requests to update or insert a wishlist.
    """

    wishlist_name = fields.String(
        required=True, error_messages={"required": "Missing wishlist name"}
    )

    @validates("id")
    def validate_wishlist(self, value: str):
        """
        Validate that the wishlist exists in the database.

        Args:
            value (str): The ID of the wishlist to be updated.

        Raises:
            ValidationError: If the wishlist does not exist.
        """
        wishlist = WishList.query.filter_by(id=value).first()
        if wishlist is None:
            raise ValidationError("Invalid wishlist_id: WishList does not exist.")

    @post_load
    def get_validated_wishlist(self, data, **kwargs):
        """Transform validated data into the expected format."""
        return {
            "wishlist_id": data.get("id"),
            "wishlist_name": data.get("wishlist_name"),
        }


class WishlistsDetailsSchema(Schema):
    """
    Schema for validating requests to get details of multiple wishlists.
    """

    wishlists_ids = fields.List(fields.String, required=False)

    @post_load
    def get_validated_wishlist(self, data, **kwargs):
        """Transform validated data into the expected format."""
        return {
            "wishlists_ids": data.get("wishlists_ids"),
        }
