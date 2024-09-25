from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from core import db
from core.blueprints.errors.handlers import (
    bad_request,
    handle_exception,
    internal_server_error,
    not_found,
)
from core.blueprints.utils import success_response
from core.models import (
    Listing,
    ListingReview,
    MVProductCategory,
    Product,
    ProductCategory,
)
from core.validators.customer.customer_review import ReviewFilterSchema
from core.validators.public_views.public_products import (
    ListingsFilterSchema,
    ProductsFilterSchema,
)

listings_bp = Blueprint("listings", __name__)

validate_products_filters = ProductsFilterSchema()
validate_review_filters = ReviewFilterSchema()
validate_listings_filters = ListingsFilterSchema()


@listings_bp.route("/categories", methods=["GET"])
def get_categories():
    product_categories = ProductCategory.query.all()

    return success_response(
        message="Product categories:", data=[c.to_dict() for c in product_categories]
    )


@listings_bp.route("/listings/<string:listing_ulid>/reviews", methods=["POST"])
def get_listings_reviews(listing_ulid):
    try:
        query_params = validate_review_filters.load(request.get_json())

        order_by = query_params.get("order_by")
        limit = query_params.get("limit")
        offset = query_params.get("offset")

        query = ListingReview.query.filter_by(listing_id=listing_ulid)

        if order_by == "newest":
            query = query.order_by(ListingReview.modified_at.desc())
        elif order_by == "oldest":
            query = query.order_by(ListingReview.modified_at.asc())
        elif order_by == "highest":
            query = query.order_by(ListingReview.rating.desc())
        elif order_by == "lowest":
            query = query.order_by(ListingReview.rating.asc())

        reviews = query.limit(limit).offset(offset).all()

        review_list = [
            {
                "title": review.title,
                "description": review.description,
                "rating": review.rating,
                "modified_at": review.modified_at,
            }
            for review in reviews
        ]

        total_reviews = query.count()

        response = {
            "total_reviews": total_reviews,
            "limit": limit,
            "offset": offset,
            "reviews": review_list,
        }

        return success_response(message="Reviews", data=response)
    except ValidationError as verr:
        return bad_request(verr.messages)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while getting listing reviews"
        )
    except Exception:
        db.session.rollback()
        return internal_server_error()


@listings_bp.route("/products", methods=["POST"])
def get_products():
    def to_dict(p: Product) -> dict:
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "image_src": p.image_src,
            "category": p.category.title,
        }

    try:
        query_params = validate_products_filters.load(request.get_json())

        limit = query_params.get("limit")
        offset = query_params.get("offset")
        category = query_params.get("category")

        query = Product.query

        if category:
            query = query.join(ProductCategory).filter(
                ProductCategory.title == category
            )

        products = query.limit(limit).offset(offset).all()

        return success_response(message="products", data=[to_dict(p) for p in products])

    except ValidationError as verr:
        return bad_request(verr.messages)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while getting products homepage"
        )


@listings_bp.route("/products/<string:product_ulid>", methods=["GET"])
def get_product_listings_and_reviews(product_ulid):
    try:
        # Load and validate query parameters
        query_params = validate_listings_filters.load(request.args)

        limit = query_params.get("limit")
        offset = query_params.get("offset")
        price_order_by = query_params.get("price_order_by")
        review_order_by = query_params.get("review_order_by")
        product_state = query_params.get("product_state")
        view_count_order_by = query_params.get("view_count_order_by")
        purchase_count_order_by = query_params.get("purchase_count_order_by")

        # Fetch the product by ULID
        product = Product.query.filter_by(id=product_ulid).first()

        if not product:
            return not_found("Product not found")

        # Build the query for listings
        query = (
            Listing.query.join(Product)
            .options(
                joinedload(Listing.review).joinedload(ListingReview.customer),
                joinedload(Listing.seller),
            )
            .filter(Product.id == product_ulid)
        )

        # Apply ordering based on query parameters
        order_by_mapping = {
            "price": price_order_by,
            "view_count": view_count_order_by,
            "purchase_count": purchase_count_order_by,
        }

        for key, value in order_by_mapping.items():
            if value:
                query = query.order_by(
                    getattr(Listing, key).desc()
                    if value == "desc"
                    else getattr(Listing, key).asc()
                )

        # Apply filters
        if product_state:
            query = query.filter(Listing.product_state == product_state)
        if review_order_by:
            if review_order_by == "asc":
                query = query.join(Listing.review).order_by(ListingReview.rating.asc())
            elif review_order_by == "desc":
                query = query.join(Listing.review).order_by(ListingReview.rating.desc())

        # Fetch listings with pagination
        listings = query.limit(limit).offset(offset).all()

        # Prepare the response data
        product_data = {
            "name": product.name,
            "description": product.description,
            "image_src": product.image_src,
            "category": {
                "name": product.category.title,
            },
            "listings": [
                {
                    "price": float(listing.price),
                    "quantity": listing.quantity,
                    "is_available": listing.is_available,
                    "product_state": listing.product_state.value,
                    "seller": {"id": listing.seller.id, "name": listing.seller.name},
                    "reviews": [
                        {
                            "title": review.title,
                            "description": review.description,
                            "rating": review.rating.value,
                            "created_at": review.created_at.isoformat(),
                            "customer": {
                                "id": review.customer.id,
                                "name": review.customer.name,
                            },
                        }
                        for review in listing.review
                    ],
                }
                for listing in listings
            ]
            if listings
            else [],
        }

        return success_response(message="product listings", data=product_data)

    except ValidationError as verr:
        return bad_request(verr.messages)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(
            message="An error occurred while getting product listings and reviews"
        )


@listings_bp.route(
    "/products/<string:product_ulid>/<string:listing_ulid>", methods=["GET"]
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
        "is_available": listing.is_available,
        "product_state": listing.product_state.value,
        "purchase_count": listing.purchase_count,
        "view_count": listing.view_count,
        "seller": {"name": listing.seller.name},
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
                "customer": {"name": review.customer.name},
            }
            for review in listing.review
        ],
    }

    return success_response(message="listing", data=listing_data)
