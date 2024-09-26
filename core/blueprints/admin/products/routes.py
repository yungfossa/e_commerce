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
    try:
        validated_data = validate_add_product.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

    try:
        name = validated_data.get("name").title()
        description = validated_data.get("description")
        image_src = validated_data.get("image_src")
        category = validated_data.get("category").title()

        c = ProductCategory.query.filter_by(title=category).first()

        if not c:
            return bad_request(message="Category not found")

        _p = Product.create(
            name=name, description=description, image_src=image_src, category_id=c.id
        )

        return success_response(status_code=201)
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while creating the product")
    except Exception:
        db.session.rollback()
        return handle_exception(
            message="An unexpected error occurred while creating the product"
        )


@admin_products_bp.route("/admin/products", methods=["GET"])
@required_user_type(["admin"])
def get_products():
    try:
        data = validate_product_filters.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

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
            message="Products",
            data={
                "products": [p.to_dict() for p in ps],
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                },
            },
        )
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while getting products")
    except Exception:
        db.session.rollback()
        return handle_exception(
            message="An unexpected error occurred while getting products"
        )


@admin_products_bp.route("/admin/products/<string:product_ulid>", methods=["GET"])
@required_user_type(["admin"])
def get_product(product_ulid):
    try:
        p = Product.query.get(product_ulid)
        if not p:
            return not_found(message="Product not found")

        return success_response(message="Product", data=p.to_dict())
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while getting the product")
    except Exception:
        db.session.rollback()
        return handle_exception(
            message="An unexpected error occurred while getting the product"
        )


@admin_products_bp.route("/admin/category", methods=["GET"])
@required_user_type(["admin"])
def get_categories():
    try:
        data = request.get_json()

        limit = data.get("limit", 10)
        offset = data.get("offset", 0)

        query = ProductCategory.query

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        cs = query.all()

        return success_response(
            message="Product categories", data=[c.to_dict() for c in cs]
        )
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while getting categories")
    except Exception:
        db.session.rollback()
        return handle_exception(
            message="An unexpected error occurred while getting categories"
        )


@admin_products_bp.route("/admin/category", methods=["PUT"])
@required_user_type(["admin"])
def create_category():
    try:
        validated_data = validate_add_category.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

    title = validated_data.get("title").title()

    try:
        _pc = ProductCategory.create(title=title)
    except IntegrityError:
        return bad_request(error="Product category already exists")

    return success_response(status_code=201)


@admin_products_bp.route("/admin/category", methods=["DELETE"])
@required_user_type(["admin"])
def delete_category():
    try:
        validated_data = validate_remove_category.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

    try:
        title = validated_data.get("title").title()

        pc = ProductCategory.query.filter_by(title=title).first()

        if not pc:
            return success_response(message="Category already removed")

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
    except SQLAlchemyError:
        db.session.rollback()
        return handle_exception(message="An error occurred while deleting the category")
    except Exception:
        db.session.rollback()
        return handle_exception(
            message="An unexpected error occurred while deleting the category"
        )
