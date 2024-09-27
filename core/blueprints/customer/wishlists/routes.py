from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import bad_request, handle_exception, not_found
from core.blueprints.utils import required_user_type, success_response
from core.models import (
    Listing,
    Product,
    ProductCategory,
    Seller,
    WishList,
    WishListEntry,
)
from core.validators.customer.customer_wishlist import (
    AddToWishlistSchema,
    RemoveFromWishlistSchema,
    UpsertWishlistSchema,
    WishlistsDetailsSchema,
)

customer_wishlists_bp = Blueprint("customer_wishlists", __name__)

validate_insert_to_wl = AddToWishlistSchema()
validate_remove_from_wl = RemoveFromWishlistSchema()
validate_upsert_wl = UpsertWishlistSchema()
validate_wl = WishlistsDetailsSchema()


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


@customer_wishlists_bp.route("/wishlists/<string:ulid>", methods=["GET"])
@required_user_type(["customer"])
def get_wishlist_content(ulid):
    customer_id = get_jwt_identity()

    try:
        wishlist = WishList.query.filter_by(id=ulid, customer_id=customer_id).first()

        if not wishlist:
            return not_found(error="Wishlist not found")

        entries = (
            db.session.query(Product, ProductCategory, WishListEntry, Listing, Seller)
            .join(WishListEntry, WishListEntry.listing_id == Listing.id)
            .join(Product, Listing.product_id == Product.id)
            .join(ProductCategory, Product.category_id == ProductCategory.id)
            .join(Seller, Listing.seller_id == Seller.id)
            .filter(WishListEntry.wishlist_id == wishlist.id)
            .with_entities(
                Product.name.label("product_name"),
                ProductCategory.title.label("product_category"),
                Product.image_src.label("product_img"),
                Listing.product_state,
                Listing.price.label("price_per_unit"),
                Seller.company_name,
            )
            .all()
        )

        return success_response(
            data=wishlist_summary(entries),
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


@customer_wishlists_bp.route("/wishlists/<string:ulid>", methods=["POST"])
@required_user_type(["customer"])
def add_wishlist_entry(ulid):
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_insert_to_wl.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        listing_id = validated_data.get("listing_id")

        wishlist = WishList.query.filter_by(id=ulid, customer_id=customer_id).first()

        if not wishlist:
            return not_found(message="Wishlist not found")

        wishlist_entry = WishListEntry.query.filter_by(
            wishlist_id=wishlist.id, listing_id=listing_id
        ).first()

        if wishlist_entry:
            return success_response(
                message="The listing product is already in the wishlist",
                status_code=200,
            )

        _we = WishListEntry.create(wishlist_id=wishlist.id, listing_id=listing_id)

        return success_response(
            data={"id": _we.id},
            status_code=201,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


@customer_wishlists_bp.route("/wishlists/<string:ulid>", methods=["DELETE"])
@required_user_type(["customer"])
def remove_wishlist_entry(ulid):
    try:
        validated_data = validate_remove_from_wl.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        wishlist_entry_id = validated_data.get("wishlist_entry_id")

        WishListEntry.query.filter_by(
            id=wishlist_entry_id,
            wishlist_id=ulid,
        ).delete()

        return success_response(
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@customer_wishlists_bp.route("/wishlists", methods=["GET"])
@required_user_type(["customer"])
def get_wishlists():
    customer_id = get_jwt_identity()

    try:
        wishlists = WishList.query.filter_by(customer_id=customer_id).all()

        if not wishlists:
            return success_response(status_code=200)

        wishlists_list = [{"id": wl.id, "name": wl.name} for wl in wishlists]

        return success_response(
            data=wishlists_list,
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@customer_wishlists_bp.route("/wishlists", methods=["POST"])
@required_user_type(["customer"])
def upsert_wishlist():
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_upsert_wl.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        wishlist_id = validated_data.get("wishlist_id")
        wishlist_name = validated_data.get("wishlist_name")

        existing_wishlist = WishList.query.filter_by(
            customer_id=customer_id, name=wishlist_name
        ).first()

        if existing_wishlist and (
            not wishlist_id or existing_wishlist.id != wishlist_id
        ):
            return bad_request(error="A wishlist with this name already exists")

        if wishlist_id:
            wishlist = WishList.query.filter_by(
                id=wishlist_id, customer_id=customer_id
            ).first()

            if not wishlist:
                return not_found(error="Wishlist not found")

            wishlist.update(name=wishlist_name)

            return success_response(
                status_code=200,
            )
        else:
            wishlist = WishList.create(name=wishlist_name, customer_id=customer_id)

            return success_response(data={"id": wishlist.id}, status_code=201)

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@customer_wishlists_bp.route("/wishlists", methods=["DELETE"])
@required_user_type(["customer"])
def remove_wishlist():
    customer_id = get_jwt_identity()

    try:
        validated_data = validate_wl.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        wishlists_ids = validated_data.get("wishlists_ids")

        if not wishlists_ids:
            return success_response(
                message="No wishlists specified for removal", status_code=200
            )

        deleted_count = WishList.query.filter(
            WishList.id.in_(wishlists_ids), WishList.customer_id == customer_id
        ).delete()

        if deleted_count == 0:
            return success_response(
                message="No wishlists were found for removal",
                status_code=200,
            )
        elif deleted_count < len(wishlists_ids):
            return success_response(
                message=f"{deleted_count} out of {len(wishlists_ids)} wishlists were remo   ved successfully",
                status_code=200,
            )
        else:
            return success_response(
                message="All specified wishlists have been removed successfully",
                status_code=200,
            )
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))
