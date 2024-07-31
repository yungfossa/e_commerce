from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, case

from core import db
from core.blueprints.errors.handlers import not_found
from core.blueprints.utils import required_user_type, success_response
from core.models import Listing, MVProductCategory, ListingReview, ReviewRate

seller_bp = Blueprint("seller", __name__)


def listings_summary(entries):
    def listing_to_dict(entry):
        return {
            "listing_id": entry.listing_id,
            "product_name": entry.product_name,
            "product_category": entry.product_category,
            "product_description": entry.product_description,
            "product_image": entry.product_img,
            "listing_quantity": entry.quantity,
            "listing_price": entry.price,
            "listing_product_state": entry.product_state.value,
            "is_available": entry.available,
            "purchase_count": entry.purchase_count,
            "view_count": entry.view_count,
            "listing_review_rate": entry.average_rating,
            "listing_review_count": entry.review_count,
        }

    items = [listing_to_dict(entry) for entry in entries]

    return {
        "listings": items,
        "is_empty": items == len(items) == 0,
    }


# TODO refactor?
@seller_bp.route("/seller/listings", methods=["GET"])
@required_user_type(["seller"])
def listings():
    seller_id = get_jwt_identity()

    listing_entries = (
        db.session.query(MVProductCategory, Listing)
        .join(Listing, Listing.product_id == MVProductCategory.product_id)
        .outerjoin(
            db.session.query(
                ListingReview.listing_id,
                func.avg(
                    case(
                        (ListingReview.rating == ReviewRate.ONE, 1),
                        (ListingReview.rating == ReviewRate.TWO, 2),
                        (ListingReview.rating == ReviewRate.THREE, 3),
                        (ListingReview.rating == ReviewRate.FOUR, 4),
                        (ListingReview.rating == ReviewRate.FIVE, 5),
                    )
                ).label("average_rating"),
                func.count(ListingReview.id).label("review_count"),
            )
            .group_by(ListingReview.listing_id)
            .subquery(),
            Listing.id == ListingReview.listing_id,
        )
        .filter(Listing.seller_id == seller_id)
        .with_entities(
            Listing.id.label("listing_id"),
            MVProductCategory.product_name,
            MVProductCategory.product_category,
            MVProductCategory.product_description,
            MVProductCategory.product_img,
            Listing.quantity,
            Listing.price,
            Listing.product_state.value,
            Listing.purchase_count,
            Listing.view_count,
            Listing.available,
            func.coalesce(ListingReview.c.average_rating, 0).label("average_rating"),
            func.coalesce(ListingReview.c.review_count, 0).label("review_count"),
        )
        .all()
    )

    return success_response(
        message="Your listings: ", data=listings_summary(listing_entries)
    )


@seller_bp.route("/seller/listings", methods=["POST"])
@required_user_type(["seller"])
def create_listing():
    data = request.get_json()
    quantity = data.get("quantity")
    price = data.get("price")
    product_state = data.get("product_state")
    product_id = data.get("product_id")

    seller_id = get_jwt_identity()

    new_listing = Listing.create(
        quantity=quantity,
        price=price,
        available=(quantity != 0),
        product_state=product_state,
        seller_id=seller_id,
        product_id=product_id,
    )

    return success_response(message="New listing added", data=new_listing.to_dict())


@seller_bp.route("/seller/listings/<string:ulid>", methods=["GET"])
@required_user_type(["seller"])
def get_listing(ulid):
    listing = Listing.query.filter_by(id=ulid).first()

    if not listing:
        return not_found("Listing not found.")

    return success_response(message=f"Listing #{ulid}", data=listing.to_dict())


@seller_bp.route("/seller/listings/<string:ulid>", methods=["DELETE"])
@required_user_type(["seller"])
def delete_listing(ulid):
    listing = Listing.query.filter_by(id=ulid).first()

    if not listing:
        return not_found("Listing not found: it has been already deleted.")

    listing.delete()

    return success_response(f"Listing #{ulid} has been deleted successfully.")


@seller_bp.route("/seller/listings/<string:ulid>", methods=["PUT"])
@required_user_type(["seller"])
def edit_listing(ulid):
    data = request.get_json()
    quantity = data.get("quantity")
    price = data.get("price")

    listing = Listing.query.filter_by(id=ulid).first()

    if not listing:
        return not_found("Listing not found.")

    listing.update(
        quantity=quantity,
        available=(quantity != 0),
        price=price,
    )

    return success_response(f"Listing #{ulid} edited successfully.")
