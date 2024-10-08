from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import func
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
    Customer,
    Listing,
    ListingReview,
    Product,
    ProductCategory,
    ProductState,
    Seller,
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
    """
    Retrieve all product categories.

    Returns:
        JSON response containing all product categories.
    """
    product_categories = ProductCategory.query.all()

    return success_response(
        message="Product categories:", data=[c.to_dict() for c in product_categories]
    )


@listings_bp.route("/listings/<string:listing_ulid>/reviews", methods=["POST"])
def get_listings_reviews(listing_ulid):
    """
    Retrieve reviews for a specific listing.

    Args:
        listing_ulid (str): The unique identifier of the listing.

    Returns:
        JSON response containing the reviews for the specified listing.
    """
    try:
        query_params = validate_review_filters.load(request.get_json())

        order_by = query_params.get("order_by")
        limit = query_params.get("limit")
        offset = query_params.get("offset")

        query = ListingReview.query.filter_by(listing_id=listing_ulid)

        # Apply ordering based on the order_by parameter
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
    """
    Retrieve products based on specified filters.

    Returns:
        JSON response containing the filtered products.
    """

    def to_dict(p: Product, min_price: float) -> dict:
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "image_src": p.image_src,
            "category": p.category.title,
            "min_price": min_price,
        }

    try:
        query_params = validate_products_filters.load(request.get_json())

        limit = query_params.get("limit")
        offset = query_params.get("offset")
        category = query_params.get("category")
    except ValidationError as verr:
        return bad_request(verr.messages)

    try:
        query = (
            db.session.query(
                Product, func.coalesce(func.min(Listing.price), None).label("min_price")
            )
            .outerjoin(Listing)
            .group_by(Product.id)
        )

        if category:
            query = query.join(ProductCategory).filter(
                ProductCategory.title == category
            )

        products = query.limit(limit).offset(offset).all()

        return success_response(
            data=[to_dict(p, min_price) for p, min_price in products],
            status_code=200,
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(error=str(e))
    except Exception as e:
        db.session.rollback()
        return internal_server_error(error=str(e))


@listings_bp.route("/products/<string:product_ulid>", methods=["POST"])
def get_product_listings_and_reviews(product_ulid):
    """
    Retrieve listings and reviews for a specific product.

    Args:
        product_ulid (str): The unique identifier of the product.

    Returns:
        JSON response containing the product details, listings, and reviews.
    """
    try:
        data = validate_listings_filters.load(request.get_json())
    except ValidationError as verr:
        return bad_request(message=verr.messages)

    try:
        limit = data.get("limit")
        offset = data.get("offset")
        price_order_by = data.get("price_order_by")
        review_order_by = data.get("review_order_by")
        product_state = data.get("product_state")
        view_count_order_by = data.get("view_count_order_by")
        purchase_count_order_by = data.get("purchase_count_order_by")

        product = Product.query.filter_by(id=product_ulid).first()

        if not product:
            return not_found(error="Product not found")

        query = (
            Listing.query.join(Product)
            .options(
                joinedload(Listing.review).joinedload(ListingReview.customer),
                joinedload(Listing.seller),
            )
            .filter(Product.id == product_ulid)
        )

        # Apply ordering based on the provided parameters
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

        if product_state:
            query = query.filter(Listing.product_state == ProductState(product_state))
        if review_order_by:
            if review_order_by == "asc":
                query = query.join(Listing.review).order_by(ListingReview.rating.asc())
            elif review_order_by == "desc":
                query = query.join(Listing.review).order_by(ListingReview.rating.desc())

        listings = query.limit(limit).offset(offset).all()

        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "image_src": product.image_src,
            "category": {
                "name": product.category.title,
            },
            "listings": [
                {
                    "id": listing.id,
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

        return success_response(data=product_data, status_code=200)

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as err:
        db.session.rollback()
        return handle_exception(error=str(err))


@listings_bp.route(
    "/products/<string:product_ulid>/<string:listing_ulid>", methods=["GET"]
)
def get_listing(product_ulid, listing_ulid):
    """
    Retrieve details for a specific listing of a product.

    Args:
        product_ulid (str): The unique identifier of the product.
        listing_ulid (str): The unique identifier of the listing.

    Returns:
        JSON response containing the listing details, including product information and reviews.
    """
    try:
        listing = (
            Listing.query.options(
                joinedload(Listing.seller),
                joinedload(Listing.review).joinedload(ListingReview.customer),
            )
            .filter_by(id=listing_ulid, product_id=product_ulid)
            .first()
        )

        if not listing:
            return not_found(message="Listing not found")

        product = (
            Product.query.options(joinedload(Product.category))
            .filter_by(id=product_ulid)
            .first()
        )

        if not product:
            return not_found(message="Product not found")

        listing_data = {
            "id": listing.id,
            "price": float(listing.price),
            "quantity": listing.quantity,
            "is_available": listing.is_available,
            "product_state": listing.product_state.value,
            "purchase_count": listing.purchase_count,
            "view_count": listing.view_count,
            "seller": {"name": listing.seller.name},
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "image_src": product.image_src,
                "category": product.category.title,
            },
            "reviews": [
                {
                    "id": review.id,
                    "title": review.title,
                    "description": review.description,
                    "rating": review.rating.value,
                    "created_at": review.created_at.isoformat(),
                    "customer": {"name": review.customer.name},
                }
                for review in listing.review
            ],
        }

        return success_response(data=listing_data, status_code=200)

    except SQLAlchemyError as sql_err:
        return handle_exception(str(sql_err))
    except Exception as e:
        return handle_exception(str(e))


@listings_bp.route("/products/<string:seller_ulid>", methods=["GET"])
def get_seller_listings(seller_ulid):
    """
    Retrieve all listings for a specific seller.

    Args:
        seller_ulid (str): The unique identifier of the seller.

    Returns:
        JSON response containing all listings for the specified seller.
    """
    try:
        seller = Seller.query.filter_by(id=seller_ulid).first()

        if not seller:
            return not_found(message="Seller not found")

        listings = (
            Listing.query.filter_by(seller_id=seller_ulid)
            .options(joinedload(Listing.product))
            .all()
        )

        response = [
            {
                "id": listing.id,
                "price": float(listing.price),
                "quantity": listing.quantity,
                "is_available": listing.is_available,
                "product_state": listing.product_state.value,
                "purchase_count": listing.purchase_count,
                "view_count": listing.view_count,
                "seller": {"name": listing.seller.name},
                "product": {
                    "id": listing.product.id,
                    "name": listing.product.name,
                    "description": listing.product.description,
                    "image_src": listing.product.image_src,
                    "category": listing.product.category.title,
                },
            }
            for listing in listings
        ]

        return success_response(
            data=response,
            status_code=200,
        )
    except SQLAlchemyError as sql_err:
        return handle_exception(str(sql_err))
    except Exception as e:
        return handle_exception(str(e))


@listings_bp.route("/products/<string:seller_ulid>/reviews", methods=["GET"])
def get_seller_reviews(seller_ulid):
    """
    Retrieve all reviews for a specific seller's listings.

    Args:
        seller_ulid (str): The unique identifier of the seller.

    Returns:
        JSON response containing all reviews for the specified seller's listings.
    """
    try:
        seller = Seller.query.filter_by(id=seller_ulid).first()

        if not seller:
            return not_found(message="Seller not found")

        reviews = (
            ListingReview.query.join(Listing)
            .join(Customer)
            .filter(Listing.seller_id == seller_ulid)
            .options(
                joinedload(ListingReview.customer), joinedload(ListingReview.listing)
            )
            .all()
        )

        response = [
            {
                "id": review.id,
                "title": review.title,
                "description": review.description,
                "rating": review.rating.value,
                "created_at": review.created_at.isoformat(),
                "modified_at": review.modified_at.isoformat(),
                "customer": {"name": review.customer.name},
                "listing": {"id": review.listing.id},
            }
            for review in reviews
        ]

        return success_response(
            data=response,
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        return handle_exception(str(sql_err))
    except Exception as e:
        return handle_exception(str(e))


# This module defines the routes for handling product listings, reviews, and related operations.

# Key features:
# - Retrieve product categories
# - Get reviews for specific listings
# - Fetch products with filtering and pagination
# - Retrieve product listings and reviews
# - Get details for specific listings
# - Fetch listings and reviews for specific sellers

# Note: This module uses SQLAlchemy for database operations and Marshmallow for request validation.

# Error handling:
# - ValidationErrors are caught and returned as bad requests
# - SQLAlchemyErrors and general exceptions are handled and appropriate error responses are returned

# Future improvements could include:
# - Implementing caching for frequently accessed data (e.g., product categories)
# - Adding more advanced filtering and search capabilities
# - Implementing rate limiting to prevent abuse of these endpoints
