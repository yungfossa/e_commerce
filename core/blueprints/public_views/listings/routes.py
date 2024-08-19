from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from core import db
from core.blueprints.errors.handlers import bad_request, handle_exception, not_found
from core.blueprints.utils import success_response
from core.models import Listing, ListingReview, MVProductCategory, Product
from core.validators.public_views.public_products import ProductsFilterSchema

listings_bp = Blueprint("listings", __name__)

validate_products_filters = ProductsFilterSchema()


@listings_bp.route("/products", methods=["POST"])
def get_products():
    try:
        query_params = validate_products_filters.load(request.get_json())

        limit = query_params.get("limit")
        offset = query_params.get("offset")

        query = Product.query.filter_by()

        # TODO Add filters checking

        products = query.limit(limit).offset(offset).all()

        return success_response(
            message="products", data=[p.to_dict() for p in products]
        )

    except ValidationError as verr:
        return bad_request(verr.messages)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while getting products homepage"
        )


# Todo add filters to the following route ?
@listings_bp.route("/products/<string:product_ulid>", methods=["GET"])
def get_product_listings_and_reviews(product_ulid):
    product = MVProductCategory.query.filter_by(product_id=product_ulid).first()

    if not product:
        return not_found("Product not found")

    product_with_listings = (
        Product.query.options(
            joinedload(Product.listing)
            .joinedload(Listing.review)
            .joinedload(ListingReview.customer),
            joinedload(Product.listing).joinedload(Listing.seller),
        )
        .filter_by(id=product_ulid)
        .first()
    )

    product_data = {
        "name": product.product_name,
        "description": product.product_description,
        "image_src": product.product_img,
        "category": {"name": product.product_category},
        "listings": [
            {
                "price": float(listing.price),
                "quantity": listing.quantity,
                "available": listing.available,
                "product_state": listing.product_state.value,
                "seller": {"name": listing.seller.name},
                "reviews": [
                    {
                        "title": review.title,
                        "description": review.description,
                        "rating": review.rating.value,
                        "created_at": review.created_at.isoformat(),
                        "customer": {
                            "name": review.customer.name  # Assumendo che Customer abbia un campo 'name'
                        },
                    }
                    for review in listing.review
                ],
            }
            for listing in product_with_listings.listing
        ]
        if product_with_listings
        else [],
    }

    return success_response(message="product listings", data=product_data)


@listings_bp.route(
    "/products/<string:product_ulid>/<string:listing_ulid", methods=["GET"]
)
def get_listing(product_ulid, listing_ulid):
    listing = (
        Listing.query.options(
            joinedload(Listing.seller),
            joinedload(Listing.review).joinedload(ListingReview.customer),
        )
        .filter_by(id=listing_ulid, product_id=product_ulid)
        .first()
    )

    if not listing:
        return not_found("Listing not found")

    mv_product = MVProductCategory.query.filter_by(product_id=product_ulid).first()

    if not mv_product:
        return not_found("Product not found")

    listing_data = {
        "price": float(listing.price),
        "quantity": listing.quantity,
        "available": listing.available,
        "product_state": listing.product_state.value,
        "purchase_count": listing.purchase_count,
        "view_count": listing.view_count,
        "seller": {
            "name": listing.seller.name  # Assumendo che Seller abbia un campo 'name'
        },
        "product": {
            "name": mv_product.product_name,
            "description": mv_product.product_description,
            "image_src": mv_product.product_img,
            "category": mv_product.product_category,
        },
        "reviews": [
            {
                "title": review.title,
                "description": review.description,
                "rating": review.rating.value,
                "created_at": review.created_at.isoformat(),
                "customer": {
                    "name": review.customer.name  # Assumendo che Customer abbia un campo 'name'
                },
            }
            for review in listing.review
        ],
    }

    return success_response(message="listing", data=listing_data)
