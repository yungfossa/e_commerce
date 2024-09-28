from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import case, func
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import bad_request, handle_exception, not_found
from core.blueprints.utils import required_user_type, success_response
from core.models import (
    Listing,
    ListingReview,
    Product,
    ProductCategory,
    ProductState,
    ReviewRate,
)
from core.validators.seller.seller_listing import AddListingSchema, EditListingSchema

seller_listings_bp = Blueprint("seller_listings", __name__)

validate_add_listing = AddListingSchema()
validate_edited_listing = EditListingSchema()


def listings_summary(entries):
    """
    Generate a summary of listings from database entries.

    Args:
        entries: A list of database entries containing listing information.

    Returns:
        dict: A dictionary containing a list of formatted listings and an 'is_empty' flag.
    """

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
            "is_available": entry.is_available,
            "purchase_count": entry.purchase_count,
            "view_count": entry.view_count,
            "listing_review_rate": entry.average_rating,
            "listing_review_count": entry.review_count,
        }

    items = [listing_to_dict(entry) for entry in entries]

    return {
        "listings": items,
        "is_empty": len(items) == 0,
    }


@seller_listings_bp.route("/seller/listings", methods=["GET"])
@required_user_type(["seller"])
def listings():
    """
    Retrieve all listings for the authenticated seller.

    Returns:
        JSON response containing all listings for the seller.
    """
    seller_id = get_jwt_identity()

    try:
        listing_entries = (
            db.session.query(Product, ProductCategory, Listing)
            .join(ProductCategory, Product.category_id == ProductCategory.id)
            .join(Listing, Listing.product_id == Product.id)
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
                Product.name.label("product_name"),
                ProductCategory.title.label("product_category"),
                Product.description.label("product_description"),
                Product.image_src.label("product_img"),
                Listing.quantity,
                Listing.price,
                Listing.product_state.value,
                Listing.purchase_count,
                Listing.view_count,
                Listing.is_available,
                func.coalesce(ListingReview.c.average_rating, 0).label(
                    "average_rating"
                ),
                func.coalesce(ListingReview.c.review_count, 0).label("review_count"),
            )
            .all()
        )

        return success_response(
            data=listings_summary(listing_entries),
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


@seller_listings_bp.route("/seller/listings", methods=["POST"])
@required_user_type(["seller"])
def create_listing():
    """
    Create a new listing for the authenticated seller.

    Returns:
        JSON response containing the ID of the newly created listing.
    """
    seller_id = get_jwt_identity()

    try:
        data = validate_add_listing.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        price = data.get("price")
        product_state = data.get("product_state").lower()
        is_available = quantity != 0

        product = Product.query.filter_by(id=product_id).first()

        if not product:
            return not_found(error="Product not found")

        listing = Listing.create(
            quantity=quantity,
            is_available=is_available,
            price=price,
            product_state=ProductState(product_state),
            seller_id=seller_id,
            product_id=product_id,
        )

        return success_response(
            data={"id": listing.id},
            status_code=201,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        db.session.rollback()
        return bad_request(
            error=str(e),
        )


@seller_listings_bp.route("/seller/listings/<string:ulid>", methods=["GET"])
@required_user_type(["seller"])
def get_listing(ulid):
    """
    Retrieve a specific listing for the authenticated seller.

    Args:
        ulid (str): The unique identifier of the listing.

    Returns:
        JSON response containing the details of the specified listing.
    """
    seller_id = get_jwt_identity()

    try:
        listing = Listing.query.filter_by(id=ulid, seller_id=seller_id).first()

        if not listing:
            return not_found(error="Listing not found")

        return success_response(
            data=listing.to_dict(),
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


@seller_listings_bp.route("/seller/listings/<string:ulid>", methods=["DELETE"])
@required_user_type(["seller"])
def delete_listing(ulid):
    """
    Delete a specific listing for the authenticated seller.

    Args:
        ulid (str): The unique identifier of the listing to be deleted.

    Returns:
        JSON response indicating the success of the deletion.
    """
    seller_id = get_jwt_identity()

    try:
        listing = Listing.query.filter_by(id=ulid, seller_id=seller_id).first()

        if not listing:
            return not_found(error="Listing not found")

        listing.delete()

        return success_response(
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@seller_listings_bp.route("/seller/listings/<string:ulid>", methods=["PUT"])
@required_user_type(["seller"])
def edit_listing(ulid):
    """
    Edit a specific listing for the authenticated seller.

    Args:
        ulid (str): The unique identifier of the listing to be edited.

    Returns:
        JSON response containing the ID of the updated listing.
    """
    seller_id = get_jwt_identity()

    try:
        validated_data = validate_edited_listing.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        quantity = validated_data.get("quantity")
        price = validated_data.get("price")
        is_available = quantity != 0

        listing = Listing.query.filter_by(id=ulid, seller_id=seller_id).first()

        if not listing:
            return not_found(error="Listing not found.")

        _listing = listing.update(
            quantity=quantity,
            is_available=is_available,
            price=price,
        )

        return success_response(
            data={"id": _listing.id},
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


# This module defines the routes for handling seller listings operations.

# Key features:
# - Retrieve all listings for a seller
# - Create a new listing
# - Get details of a specific listing
# - Delete a listing
# - Edit a listing

# Security considerations:
# - All routes are protected by the @required_user_type decorator, ensuring only sellers can access them
# - The seller ID is obtained from the JWT token, preventing unauthorized access to other sellers' listings

# Note: This module uses SQLAlchemy for database operations and Marshmallow for request validation.

# Error handling:
# - ValidationErrors are caught and returned as bad requests
# - SQLAlchemyErrors trigger a database rollback and are handled as exceptions
# - General exceptions are also caught and handled appropriately

# Future improvements could include:
# - Implementing pagination for the listings retrieval
# - Adding more advanced filtering options for listings
# - Implementing bulk operations (e.g., bulk create, update, or delete)
