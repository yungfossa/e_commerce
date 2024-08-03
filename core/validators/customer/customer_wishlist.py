from marshmallow import Schema, fields, post_load, validates, ValidationError
from marshmallow.validate import Length

from core.models import Listing, WishListEntry, WishList


class BaseSchema(Schema):
    id = fields.String(
        required=True,
        validate=Length(equal=26),
        error_messages={"required": "Missing id"},
    )


class AddToWishlistSchema(BaseSchema):
    @validates("id")
    def validate_listing(self, value: str):
        listing = Listing.query.filter_by(id=value).first()
        if listing is None:
            raise ValidationError("Invalid listing_id: Listing does not exist.")

    @post_load
    def get_validated_listing(self, data, **kwargs):
        return {"listing_id": data.get("id")}


class RemoveFromWishlistSchema(BaseSchema):
    @validates("id")
    def validate_wishlist_item(self, value: str):
        wishlist_item = WishListEntry.query.filter_by(id=value).first()
        if wishlist_item is None:
            raise ValidationError(
                "Invalid wishlist_entry_id: WishListItem does not exist."
            )

    @post_load
    def get_validated_entry(self, data, **kwargs):
        return {"wishlist_entry_id": data.get("id")}


class UpsertWishlistSchema(BaseSchema):
    wishlist_name = fields.String(
        required=True, error_messages={"required": "Missing wishlist name"}
    )

    @validates("id")
    def validate_wishlist(self, value: str):
        wishlist = WishList.query.filter_by(id=value).first()
        if wishlist is None:
            raise ValidationError("Invalid wishlist_id: WishList does not exist.")

    @post_load
    def get_validated_wishlist(self, data, **kwargs):
        return {
            "wishlist_id": data.get("id"),
            "wishlist_name": data.get("wishlist_name"),
        }


class WishlistDetailsSchema(BaseSchema):
    @validates("id")
    def validate_wishlist(self, value: str):
        wishlist = WishList.query.filter_by(id=value).first()
        if wishlist is None:
            raise ValidationError("Invalid wishlist_id: WishList does not exist.")

    @post_load
    def get_validated_wishlist(self, data, **kwargs):
        return {
            "wishlist_id": data.get("id"),
        }
