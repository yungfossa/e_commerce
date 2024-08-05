from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from core import db
from core.blueprints.errors.handlers import bad_request
from core.blueprints.utils import required_user_type, success_response
from core.models import CartEntry, MVProductCategory, Listing, Seller
from core.validators.customer.customer_cart import (
    UpsertCartSchema,
    RemoveFromCartSchema,
)

customer_cart_bp = Blueprint("customer_cart", __name__)

validation_upsert_cart = UpsertCartSchema()
validation_remove_from_cart = RemoveFromCartSchema()


def cart_summary(entries):
    def cart_entry_to_dict(entry):
        return {
            "product_name": entry.product_name,
            "product_category": entry.product_category,
            "product_img": entry.product_img,
            "product_state": entry.product_state.value,
            "price_per_unit": entry.price_per_unit,
            "cart_entry_amount": entry.amount,
            "total_price_cart_entry": entry.total_priceRemoveCartEntrySchema_cart_entry,
            "company_name ": entry.company_name,
        }

    items = [cart_entry_to_dict(entry) for entry in entries]
    total_price = sum(entry.total_price_cart_entry for entry in entries)

    return {
        "cart_entries": items,
        "cart_total": total_price,
        "is_empty": items == len(items) == 0,
    }


@customer_cart_bp.route("/cart", methods=["GET"])
@required_user_type(["customer"])
def cart():
    cart_id = get_jwt_identity()

    cart_entries = (
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

    return success_response(message="Customer cart", data=cart_summary(cart_entries))


@customer_cart_bp.route("/cart", methods=["POST"])
@required_user_type(["customer"])
def upsert_cart_entry():
    try:
        validated_data = validation_upsert_cart.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    listing_id = validated_data.get("listing_id")
    amount = validated_data.get("amount")

    cart_id = get_jwt_identity()

    cart_entry = CartEntry.query.filter(
        CartEntry.cart_id == cart_id and CartEntry.listing_id == listing_id
    ).first()

    if not cart_entry:
        return bad_request(message="Cart entry not found")

    if amount == 0:
        if cart_entry:
            cart_entry.delete()
            return success_response(message="Cart entry removed successfully")
        else:
            return bad_request(
                message="Amount is 0."
                "It is impossibile to create a new entry in the cart"
            )

    listing = Listing.query.filter_by(id=cart_entry.listing_id).first()

    if not listing:
        return bad_request("Listing not found")

    if listing.quantity < amount:
        return bad_request(
            message=f"The selected amount {amount} is "
            f"bigger than the available quantity ({listing.quantity})"
        )

    if cart_entry:
        cart_entry.update(amount=amount)
        return success_response(message="Cart entry amount updated successfully")

    ce = CartEntry.create(
        amount=amount,
        cart_id=cart_id,
        listing_id=listing_id,
    )

    return success_response(
        message="Product added to cart successfully",
        data=ce.to_dict(),
        status_code=201,
    )


# TODO refactor as the wishlist
@customer_cart_bp.route("/cart", methods=["DELETE"])
@required_user_type(["customer"])
def remove_cart_entry():
    try:
        validated_data = validation_remove_from_cart.load(request.get_json())
    except ValidationError as err:
        return bad_request(err.messages)

    cart_entry_id = validated_data.get("cart_entry_id")

    CartEntry.query.filter_by(id=cart_entry_id).first().delete()

    return success_response(message="Cart entry removed successfully")
