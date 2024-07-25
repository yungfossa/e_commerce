from flask import Blueprint, request

from core import db
from core.blueprints.commons import (
    required_user_type,
    success_response,
    get_user,
)
from flask_jwt_extended import get_jwt_identity

from core.blueprints.errors.handlers import bad_request
from core.models import Cart, CartEntry, MVProductCategory, Listing
from core.blueprints.commons import json_action_response

customer_bp = Blueprint("customer", __name__)


def cart_summary(entries):
    def cart_entry_to_dict(entry):
        return {
            "product_name": entry.product_name,
            "product_category": entry.product_category,
            "product_img": entry.product_img,
            "product_state": entry.product_state,
            "total_price_cart_entry": entry.total_price_cart_entry,
            "cart_entry_amount": entry.amount,
        }

    items = [cart_entry_to_dict(entry) for entry in entries]
    total_price = sum(entry.total_price_cart_entry for entry in entries)

    return {"cart_entries": items, "cart_total": total_price, "is_empty": items == []}


def get_cart(customer_id) -> Cart:
    return Cart.query.filter_by(customer_id=customer_id).first()


@customer_bp.route("/cart", methods=["GET"])
@required_user_type(["customer"])
def show_cart():
    email = get_jwt_identity()
    customer = get_user(email=email)
    cart = Cart.query.filter_by(customer_id=customer.id).first()

    entries = (
        db.session.query(MVProductCategory, CartEntry, Listing)
        .join(CartEntry, CartEntry.listing_id == Listing.id)
        .join(MVProductCategory, Listing.product_id == MVProductCategory.product_id)
        .filter(CartEntry.cart_id == cart.id)
        .with_entities(
            MVProductCategory.product_name,
            MVProductCategory.product_category,
            MVProductCategory.product_img,
            Listing.product_state,
            (Listing.price * CartEntry.amount).label("total_price_cart_entry"),
            CartEntry.amount,
        )
        .all()
    )

    return success_response("customer cart", data=cart_summary(entries))


@customer_bp.route("/cart/add_item", methods=["PUT"])
@required_user_type(["customer"])
def add_cart_entry():
    data = request.get_json()
    listing_id = data.get("listing_id")
    amount = data.get("quantity")

    customer_email = get_jwt_identity()
    customer_id = get_user(email=customer_email).id
    cart_id = get_cart(customer_id=customer_id).id

    # todo refactor with an try-catch?
    if CartEntry.query.filter_by(listing_id=listing_id).first():
        return bad_request(error="this product is already in the cart")

    CartEntry.create(amount=amount, cart_id=cart_id, listing_id=listing_id)

    return success_response("product added to cart successfully")


@customer_bp.route("/cart/update_item", methods=["PUT"])
@required_user_type(["customer"])
def update_cart_entry():
    data = request.get_json()
    cart_entry_id = data.get("cart_entry_id")
    new_amount = int(data.get("amount"))

    if new_amount == 0:
        return json_action_response(
            message="item quantity is zero. remove item from cart",
            action="remove",
            cart_entry_id=cart_entry_id,
        )

    cart_entry = CartEntry.query.filter_by(id=cart_entry_id).first()

    listing_available_qty = (
        Listing.query.filter_by(id=cart_entry.listing_id)
        .with_entities(
            Listing.quantity,
        )
        .first()
    )

    if listing_available_qty < new_amount:
        return bad_request(
            f"the selected amount ({new_amount}) is "
            f"bigger than the available quantity ({listing_available_qty})"
        )

    cart_entry.amount = new_amount
    CartEntry.update(cart_entry)

    return success_response(message="cart entry amount updated successfully")


@customer_bp.route("/cart/remove_item", methods=["DELETE"])
@required_user_type(["customer"])
def remove_cart_entry():
    data = request.get_json()
    cart_entry_id = data.get("cart_entry_id")

    CartEntry.query.filter_by(id=cart_entry_id).first().delete()

    return success_response(message="cart entry removed successfully")


@customer_bp.route("/cart/clear", methods=["DELETE"])
@required_user_type(["customer"])
def clear_cart():
    customer_email = get_jwt_identity()
    customer_id = get_user(email=customer_email).id
    cart_id = get_cart(customer_id=customer_id).id

    CartEntry.query.filter_by(cart_id=cart_id).delete()

    return success_response(message="cart cleared successfully")
