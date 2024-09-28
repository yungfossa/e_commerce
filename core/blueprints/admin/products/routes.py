from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import bad_request, handle_exception, not_found
from core.blueprints.utils import required_user_type, success_response
from core.models import Product, ProductCategory
from core.validators.admin.admin_products import AddProductSchema, CategorySchema
from core.validators.public_views.public_products import ProductsFilterSchema

admin_products_bp = Blueprint("admin_products", __name__)

validate_add_product = AddProductSchema()
validate_add_category = CategorySchema()
validate_remove_category = CategorySchema()
validate_product_filters = ProductsFilterSchema()


@admin_products_bp.route("/admin/products", methods=["PUT"])
@required_user_type(["admin"])
def create_product():
    """
    Create a new product.

    This endpoint allows an admin to create a new product with the provided details.

    Returns:
        A JSON response with the new product's ID on success, or an error message on failure.
    """
    try:
        validated_data = validate_add_product.load(request.get_json())
    except ValidationError as verr:
        return bad_request(error=verr.messages)

    try:
        name = validated_data.get("name").title()
        description = validated_data.get("description")
        image_src = validated_data.get("image_src")
        category = validated_data.get("category").title()

        c = ProductCategory.query.filter_by(title=category).first()

        if not c:
            return bad_request(error="Category not found")

        _p = Product.create(
            name=name, description=description, image_src=image_src, category_id=c.id
        )

        return success_response(data={"id": _p.id}, status_code=201)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@admin_products_bp.route("/admin/products", methods=["GET"])
@required_user_type(["admin"])
def get_products():
    """
    Retrieve a list of products.

    This endpoint allows an admin to retrieve a list of products with optional filtering.

    Returns:
        A JSON response with the list of products and pagination information.
    """
    try:
        data = validate_product_filters.load(request.get_json())
    except ValidationError as verr:
        return bad_request(error=verr.messages)

    try:
        limit = data.get("limit")
        offset = data.get("offset")
        category = data.get("category")

        query = Product.query

        if category:
            query = query.join(ProductCategory).filter(
                ProductCategory.title == category
            )

        total_count = query.count()
        ps = query.limit(limit).offset(offset).all()

        return success_response(
            data={
                "products": [p.to_dict() for p in ps],
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                },
            },
            status_code=200,
        )
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@admin_products_bp.route("/admin/products/<string:product_ulid>", methods=["GET"])
@required_user_type(["admin"])
def get_product(product_ulid):
    """
    Retrieve a specific product by its ULID.

    This endpoint allows an admin to retrieve details of a specific product.

    Args:
        product_ulid (str): The ULID of the product to retrieve.

    Returns:
        A JSON response with the product details on success, or an error message if not found.
    """
    try:
        p = Product.query.get(product_ulid)
        if not p:
            return not_found(error="Product not found")

        return success_response(data=p.to_dict(), status_code=200)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=sql_err)
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@admin_products_bp.route("/admin/category", methods=["GET"])
@required_user_type(["admin"])
def get_categories():
    """
    Retrieve a list of product categories.

    This endpoint allows an admin to retrieve a list of product categories with pagination.

    Returns:
        A JSON response with the list of categories.
    """
    try:
        data = request.get_json()

        limit = data.get("limit", 10)
        offset = data.get("offset", 0)

        query = ProductCategory.query.limit(limit).offset(offset)

        cs = query.all()

        return success_response(data=[c.to_dict() for c in cs], status_code=200)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@admin_products_bp.route("/admin/category", methods=["PUT"])
@required_user_type(["admin"])
def create_category():
    """
    Create a new product category.

    This endpoint allows an admin to create a new product category.

    Returns:
        A JSON response with the new category's ID on success, or an error message on failure.
    """
    try:
        validated_data = validate_add_category.load(request.get_json())
    except ValidationError as verr:
        return bad_request(error=verr.messages)

    title = validated_data.get("title").title()

    try:
        _pc = ProductCategory.create(title=title)
    except IntegrityError as int_e:
        return bad_request(error=str(int_e))

    return success_response(data={"id": _pc.id}, status_code=201)


@admin_products_bp.route("/admin/category", methods=["DELETE"])
@required_user_type(["admin"])
def delete_category():
    """
    Delete a product category.

    This endpoint allows an admin to delete a product category. If the category contains products,
    they will be reassigned to a generic category.

    Returns:
        A JSON response indicating success or an error message on failure.
    """
    try:
        validated_data = validate_remove_category.load(request.get_json())
    except ValidationError as verr:
        return bad_request(error=verr.messages)

    try:
        title = validated_data.get("title").title()

        pc = ProductCategory.query.filter_by(title=title).first()

        if not pc:
            return success_response(message="Category already removed", status_code=200)

        # Ensure a generic category exists
        generic_category = ProductCategory.query.filter_by(title="Generic").first()
        if not generic_category:
            generic_category = ProductCategory.create(title="Generic")

        # Reassign products to the generic category
        products = Product.query.filter_by(category_id=pc.id).all()
        for product in products:
            product.category_id = generic_category.id
            db.session.add(product)

        # Commit the changes and delete the category
        with db.session.begin():
            db.session.commit()
            pc.delete()

        return success_response(status_code=200)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=sql_err)
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


# This module defines the admin product management endpoints.
# It includes functionality for creating, retrieving, and managing products and categories.
# Key features:
# - CRUD operations for products and categories
# - Pagination and filtering for product and category retrieval
# - Error handling for database operations and validation errors
# - Automatic reassignment of products to a generic category when deleting a category
# Note: All endpoints require admin privileges, enforced by the @required_user_type decorator.
