from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from core import db
from core.blueprints.errors.handlers import bad_request
from core.blueprints.utils import (
    required_user_type,
    success_response,
)
from core.models import Listing, WishList, WishListEntry, MVProductCategory, Seller

wishlist_bp = Blueprint("wishlist", __name__)


def wishlist_summary(wishlist):
    def wishlist_entry_to_dict(entry):
        return {
            "product_name": entry.product.name,
            "product_category": entry.product_category,
            "product_img": entry.product_img,
            "product_state": entry.product_state.value,
            "price_per_unit": entry.price_per_unit,
            "company_name": entry.company_name,
        }

    items = [wishlist_entry_to_dict(entry) for entry in wishlist.wishlist_entries]

    return {
        "wishlist_id": wishlist.id,
        "wishlist_name": wishlist.name,
        "wishlist_entries": items,
        "is_empty": len(items) == 0,
    }


@wishlist_bp.route("/wishlist/<string:ulid>", methods=["POST"])
@required_user_type(["customer"])
def add_wishlist_entry(ulid):
    data = request.get_json()
    listing_id = data.get("listing_id")

    if not Listing.query.filter_by(listing_id=listing_id).first():
        return bad_request("missing listing id")

    customer_id = get_jwt_identity()

    wishlist = WishList.query.filter_by(id=ulid, customer_id=customer_id).first()

    if not wishlist:
        return bad_request("wishlist not found")

    wishlist_entry = WishListEntry.query.filter_by(
        wishlist_id=wishlist.id, listing_id=listing_id
    ).first()

    if wishlist_entry:
        return bad_request("the listing product it's already in the wishlist")

    WishListEntry.create(wishlist_id=wishlist.id, listing_id=listing_id)

    return success_response("wishlist entry added successfully")


@wishlist_bp.route("/wishlist/<string:slug>", methods=["DELETE"])
@required_user_type(["customer"])
def remove_wishlist_entry(slug):
    data = request.get_json()
    wishlist_entry_id = data.get("wishlist_entry_id")

    if not wishlist_entry_id:
        return bad_request("missing wishlist entry")

    WishListEntry.query.filter_by(
        wishlist_id=slug, wishlist_entry_id=wishlist_entry_id
    ).delete()

    return success_response("wishlist entry removed successfully")


@wishlist_bp.route("/wishlist/<string:ulid>", methods=["GET"])
@required_user_type(["customer"])
def get_wishlist_content(ulid):
    customer_id = get_jwt_identity()
    wishlist = WishList.query.filter_by(id=ulid, customer_id=customer_id).first()

    if not wishlist:
        return bad_request("wishlist not found or you don't have access to it")

    entries = (
        db.session.query(MVProductCategory, WishListEntry, Listing, Seller)
        .join(WishListEntry, WishListEntry.listing_id == Listing.id)
        .join(MVProductCategory, Listing.product_id == MVProductCategory.product_id)
        .join(Seller, Listing.seller_id == Seller.id)
        .filter(WishListEntry.wishlist_id == wishlist.id)
        .with_entities(
            MVProductCategory.product_name,
            MVProductCategory.product_category,
            MVProductCategory.product_img,
            Listing.product_state,
            Listing.price.label("price_per_unit"),
            Seller.company_name,
        )
        .all()
    )

    return success_response("wishlist", data=wishlist_summary(entries))


@wishlist_bp.route("/wishlist", methods=["GET"])
@required_user_type(["customer"])
def get_wishlists():
    customer_id = get_jwt_identity()

    wishlists = WishList.query.filter_by(customer_id=customer_id).all()

    if not wishlists:
        return success_response(message="no wishlist found")

    wishlists_list = [{"id": wl.id, "name": wl.name} for wl in wishlists]

    return success_response("wishlists", data=wishlists_list)


@wishlist_bp.route("/wishlist", methods=["POST"])
@required_user_type(["customer"])
def upsert_wishlist():
    data = request.get_json()
    wishlist_id = data.get("wishlist_id")
    wishlist_name = str(data.get("wishlist_name")).title()

    if not wishlist_name:
        return bad_request("missing wishlist name")

    customer_id = get_jwt_identity()

    existing_wishlist = WishList.query.filter_by(
        customer_id=customer_id, name=wishlist_name
    ).first()

    if existing_wishlist and (not wishlist_id or existing_wishlist.slug != wishlist_id):
        return bad_request("a wishlist with this name already exists")

    if wishlist_id:
        wishlist = WishList.query.filter_by(
            id=wishlist_id, customer_id=customer_id
        ).first()
        if not wishlist:
            return bad_request("wishlist not found")
        wishlist.update(name=wishlist_name)
        return success_response(message="wishlist updated successfully")
    else:
        wishlist = WishList.create(name=wishlist_name, customer_id=customer_id)
        return success_response(
            message="wishlist created successfully", data=wishlist.to_dict()
        )


@wishlist_bp.route("/wishlist", methods=["DELETE"])
@required_user_type(["customer"])
def remove_wishlist():
    data = request.get_json()
    wishlist_id = data.get("wishlist_id")

    if not wishlist_id:
        return bad_request("wishlist slug is missing")

    customer_id = get_jwt_identity()

    wishlist = WishList.query.filter_by(id=wishlist_id, customer_id=customer_id).first()

    if not wishlist:
        return bad_request("wishlist not found")

    wishlist.delete()

    return success_response(message="wishlist has been removed successfully")


@wishlist_bp.route("/wishlist/clear", methods=["DELETE"])
@required_user_type(["customer"])
def clear_wishlists():
    customer_id = get_jwt_identity()

    wishlists = WishList.query.filter_by(customer_id=customer_id).all()

    if not wishlists:
        return success_response(message="no wishlists to clear")

    for wl in wishlists:
        wl.delete()

    return success_response(message="wishlists cleared successfully")
