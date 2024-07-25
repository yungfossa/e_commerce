from flask import Blueprint, request

from core import db
from core.blueprints.commons import (
    required_user_type,
    success_response,
    get_current_user,
)
from flask_jwt_extended import get_jwt_identity

from core.models import Cart, CartEntry, MVProductCategory, Listing

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


@customer_bp.route("/cart", methods=["GET"])
@required_user_type(["customer"])
def show_cart():
    email = get_jwt_identity()
    customer = get_current_user(email=email)
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


@customer_bp.route("/cart/add", methods=["PUT"])
@required_user_type(["customer"])
def add_cart_entry():
    data = request.get_json()
    listing_id = data.get("id")
    amount = data.get("quantity")

    customer_email = get_jwt_identity()
    customer_id = get_current_user(email=customer_email).id
    customer_cart_id = (
        Cart.query.filter_by(customer_id=customer_id).with_entities("id").first()
    )

    CartEntry.create(amount=amount, cart_id=customer_cart_id, listing_id=listing_id)

    return success_response("product added to cart successfully")


# TODO i need to finish it
@customer_bp.route("/cart/update", methods=["PUT"])
@required_user_type(["customer"])
def update_cart_entry():
    return success_response(message="ok")


@customer_bp.route("/cart/remove", methods=["DELETE"])
@required_user_type(["customer"])
def remove_cart_entry():
    data = request.get_json()
    cart_entry_id = data.get("id")

    CartEntry.query.filter_by(id=cart_entry_id).first().delete()

    return success_response(message="cart entry removed successfully")
