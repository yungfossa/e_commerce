from decimal import Decimal

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import bad_request, handle_exception, not_found
from core.blueprints.utils import required_user_type, success_response
from core.models import Cart, CartEntry, Listing, Product, ProductCategory, Seller
from core.validators.customer.customer_cart import (
    RemoveFromCartSchema,
    UpsertCartSchema,
)

customer_cart_bp = Blueprint("customer_cart", __name__)

validation_upsert_cart = UpsertCartSchema()
validation_remove_from_cart = RemoveFromCartSchema()


def cart_summary(entries):
    def cart_entry_to_dict(entry):
        current_price = entry.price_per_unit
        current_amount = Decimal(current_price * entry.quantity)
        return {
            "product_name": entry.product_name,
            "product_category": entry.product_category,
            "product_img": entry.product_img,
            "product_state": entry.product_state.value,
            "price_per_unit": current_price,
            "quantity": entry.quantity,
            "amount": round(float(current_amount), 2),
            "company_name": entry.company_name,
        }

    items = [cart_entry_to_dict(entry) for entry in entries]
    total_price = sum(
        Decimal(entry.price_per_unit * entry.quantity) for entry in entries
    )

    return {
        "cart_entries": items,
        "cart_total": round(float(total_price), 2),
        "is_empty": len(items) == 0,
    }


@customer_cart_bp.route("/cart", methods=["GET"])
@required_user_type(["customer"])
def get_cart():
    cart_id = get_jwt_identity()

    try:
        cart_entries = (
            db.session.query(CartEntry, Listing, Seller, Product, ProductCategory)
            .join(Listing, CartEntry.listing_id == Listing.id)
            .join(Seller, Listing.seller_id == Seller.id)
            .join(Product, Listing.product_id == Product.id)
            .join(ProductCategory, Product.category_id == ProductCategory.id)
            .filter(CartEntry.cart_id == cart_id)
            .with_entities(
                Product.name.label("product_name"),
                ProductCategory.title.label("product_category"),
                Product.image_src.label("product_img"),
                Listing.product_state,
                Listing.price.label("price_per_unit"),
                CartEntry.quantity,
                Seller.company_name,
            )
            .all()
        )
        return success_response(data=cart_summary(cart_entries), status_code=200)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        return handle_exception(
            error=str(e),
        )


@customer_cart_bp.route("/cart", methods=["POST"])
@required_user_type(["customer"])
def upsert_cart_entry():
    cart_id = get_jwt_identity()

    try:
        validated_data = validation_upsert_cart.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        listing_id = validated_data.get("listing_id")
        quantity = validated_data.get("quantity")

        listing = Listing.query.filter_by(id=listing_id).first()
        if not listing:
            return not_found(error="Listing not found")

        if listing.quantity < quantity:
            return bad_request(
                error=f"The selected quantity {quantity} is "
                f"bigger than the available quantity ({listing.quantity})"
            )

        cart_entry = CartEntry.query.filter_by(
            cart_id=cart_id, listing_id=listing_id
        ).first()

        if quantity == 0:
            if cart_entry:
                cart_entry.delete()
                return success_response(
                    message="Cart entry removed successfully",
                    status_code=200,
                )
            else:
                return success_response(
                    message="No action needed, cart entry doesn't exist",
                    status_code=200,
                )

        if cart_entry:
            cart_entry.quantity = quantity
            cart_entry.update()
            return success_response(data={"id": cart_entry.id}, status_code=200)

        _ce = CartEntry.create(
            cart_id=cart_id, listing_id=listing_id, quantity=quantity
        )
        return success_response(
            data={"id": _ce.id},
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        return handle_exception(error=str(e))


@customer_cart_bp.route("/cart", methods=["DELETE"])
@required_user_type(["customer"])
def remove_cart_item():
    customer_id = get_jwt_identity()

    try:
        validated_data = validation_remove_from_cart.load(request.get_json())
    except ValidationError as err:
        return handle_exception(error=err.messages)

    try:
        cart_item_ids = validated_data.get("cart_item_ids")

        cart_entries = (
            CartEntry.query.join(Cart)
            .filter(CartEntry.id.in_(cart_item_ids), Cart.customer_id == customer_id)
            .all()
        )

        deleted_count = len(cart_entries)

        for entry in cart_entries:
            db.session.delete(entry)

        db.session.commit()

        if deleted_count == 0:
            return success_response(status_code=200)
        elif deleted_count < len(cart_item_ids):
            return success_response(status_code=200)
        else:
            return success_response(status_code=200)

    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(error=str(e))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))
