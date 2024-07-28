from flask import Blueprint, request

from core import db
from core.blueprints.utils import (
    required_user_type,
    success_response,
    generate_secure_slug,
)
from flask_jwt_extended import get_jwt_identity

from core.blueprints.errors.handlers import bad_request
from core.models import (
    CartEntry,
    MVProductCategory,
    Listing,
    WishList,
    WishListEntry,
    Seller,
)

customer_bp = Blueprint("customer", __name__)


def cart_summary(entries):
    def cart_entry_to_dict(entry):
        return {
            "product_name": entry.product_name,
            "product_category": entry.product_category,
            "product_img": entry.product_img,
            "product_state": entry.product_state.value,
            "price_per_unit": entry.price_per_unit,
            "cart_entry_amount": entry.amount,
            "total_price_cart_entry": entry.total_price_cart_entry,
            "company_name ": entry.company_name,
        }

    items = [cart_entry_to_dict(entry) for entry in entries]
    total_price = sum(entry.total_price_cart_entry for entry in entries)

    return {
        "cart_entries": items,
        "cart_total": total_price,
        "is_empty": items == len(items) == 0,
    }


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
        "wishlist_name": wishlist.name,
        "wishlist_slug": wishlist.slug,
        "wishlist_entries": items,
        "is_empty": len(items) == 0,
    }


@customer_bp.route("/cart", methods=["GET"])
@required_user_type(["customer"])
def cart():
    cart_id = get_jwt_identity()

    entries = (
        db.session.query(MVProductCategory, CartEntry, Listing)
        .join(CartEntry, CartEntry.listing_id == Listing.id)
        .join(MVProductCategory, Listing.product_id == MVProductCategory.product_id)
        .join(Seller, Listing.seller_id == Seller.id)
        .filter(CartEntry.cart_id == cart_id)
        .with_entities(
            MVProductCategory.product_name,
            MVProductCategory.product_category,
            MVProductCategory.product_img,
            Listing.product_state,
            Listing.price.label("price_per_unit"),
            (Listing.price * CartEntry.amount).label("total_price_cart_entry"),
            CartEntry.amount,
            Seller.company_name,
        )
        .all()
    )

    return success_response("customer cart", data=cart_summary(entries))


@customer_bp.route("/cart", methods=["POST"])
@required_user_type(["customer"])
def upsert_cart_entry():
    data = request.get_json()
    listing_id = data.get("listing_id")
    amount = data.get("quantity")

    if not listing_id or amount is None:
        return bad_request("missing listing_id or quantity")

    cart_id = get_jwt_identity()

    cart_entry = CartEntry.query.filter(
        CartEntry.cart_id == cart_id and CartEntry.listing_id == listing_id
    ).first()

    if not cart_entry:
        return bad_request("cart entry not found")

    if amount == 0:
        if cart_entry:
            cart_entry.delete()
            return success_response("cart entry removed successfully")
        else:
            return bad_request("amount is 0. can't create a new entry in the cart")

    listing = Listing.query.filter_by(id=cart_entry.listing_id).first()

    if not listing:
        return bad_request("listing not found")

    if listing.quantity < amount:
        return bad_request(
            f"the selected amount ({amount}) is "
            f"bigger than the available quantity ({listing.quantity})"
        )

    if cart_entry:
        CartEntry.update(amount=amount)
        return success_response("cart entry amount updated successfully")

    c = CartEntry.create(amount=amount, cart_id=cart_id, listing_id=listing_id)

    return success_response("product added to cart successfully", data=c.to_dict())


@customer_bp.route("/cart", methods=["DELETE"])
@required_user_type(["customer"])
def remove_cart_entry():
    data = request.get_json()
    cart_entry_id = data.get("cart_entry_id")

    if not cart_entry_id:
        return bad_request("cart_entry_id is missing")

    CartEntry.query.filter_by(id=cart_entry_id).first().delete()

    return success_response(message="cart entry removed successfully")


@customer_bp.route("/cart/clear", methods=["DELETE"])
@required_user_type(["customer"])
def clear_cart():
    cart_id = get_jwt_identity()

    cart_entries = CartEntry.query.filter_by(cart_id=cart_id).all()

    if not cart_entries:
        return success_response(message="no cart entry to remove")

    for ce in cart_entries:
        ce.delete()

    return success_response(message="cart cleared successfully")


# TODO missing add and remove wishlist entry
@customer_bp.route("/wishlists/<string:slug>", methods=["POST"])
@required_user_type(["customer"])
def add_wishlist_entry(slug):
    return success_response("wishlist entry added successfully")


@customer_bp.route("/wishlists/<string:slug>", methods=["DELETE"])
@required_user_type(["customer"])
def remove_wishlist_entry(slug):
    return success_response("wishlist entry removed successfully")


@customer_bp.route("/wishlists/<string:slug>", methods=["GET"])
@required_user_type(["customer"])
def get_wishlist_content(slug):
    customer_id = get_jwt_identity()
    wishlist = WishList.query.filter_by(slug=slug, customer_id=customer_id).first()

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


@customer_bp.route("/wishlists", methods=["GET"])
@required_user_type(["customer"])
def get_wishlists():
    customer_id = get_jwt_identity()

    wishlists = WishList.query.filter_by(customer_id=customer_id).all()

    if not wishlists:
        return success_response(message="no wishlist found")

    wishlists_list = [{"name": wl.name, "slug": wl.slug} for wl in wishlists]

    return success_response("wishlists", data=wishlists_list)


@customer_bp.route("/wishlists", methods=["POST"])
@required_user_type(["customer"])
def upsert_wishlist():
    data = request.get_json()
    wishlist_slug = data.get("slug")
    wishlist_name = str(data.get("name")).title()

    if not wishlist_name:
        return bad_request("missing wishlist name")

    customer_id = get_jwt_identity()

    existing_wishlist = WishList.query.filter_by(
        customer_id=customer_id, name=wishlist_name
    ).first()

    if existing_wishlist and (
        not wishlist_slug or existing_wishlist.slug != wishlist_slug
    ):
        return bad_request("a wishlist with this name already exists")

    if wishlist_slug:
        wishlist = WishList.query.filter_by(
            slug=wishlist_slug, customer_id=customer_id
        ).first()
        if not wishlist:
            return bad_request("wishlist not found")
        wishlist.update(name=wishlist_name)
        return success_response(message="wishlist updated successfully")
    else:
        slug = generate_secure_slug(
            wishlist_name
        )  # TODO how to manage possible collisions?
        wishlist = WishList.create(
            name=wishlist_name, slug=slug, customer_id=customer_id
        )
        return success_response(
            message="wishlist created successfully", data=wishlist.to_dict()
        )


@customer_bp.route("/wishlists", methods=["DELETE"])
@required_user_type(["customer"])
def remove_wishlist():
    data = request.get_json()
    wishlist_slug = data.get("slug")

    if not wishlist_slug:
        return bad_request("wishlist slug is missing")

    customer_id = get_jwt_identity()

    wishlist = WishList.query.filter_by(
        slug=wishlist_slug, customer_id=customer_id
    ).first()

    if not wishlist:
        return bad_request("wishlist not found")

    wishlist.delete()

    return success_response(message="wishlist has been removed successfully")


@customer_bp.route("/wishlists/clear", methods=["DELETE"])
@required_user_type(["customer"])
def clear_wishlists():
    customer_id = get_jwt_identity()

    wishlists = WishList.query.filter_by(customer_id=customer_id).all()

    if not wishlists:
        return success_response(message="no wishlists to clear")

    for wl in wishlists:
        wl.delete()

    return success_response(message="wishlists cleared successfully")
