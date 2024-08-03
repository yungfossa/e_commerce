from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from core.blueprints.errors.handlers import bad_request
from core.blueprints.utils import required_user_type, success_response
from core.models import ProductCategory, Product
from core.validators.admin.admin_products import AddProductSchema, CategorySchema

admin_products_bp = Blueprint("admin_products", __name__)

validate_add_product = AddProductSchema()
validate_add_category = CategorySchema()
validate_remove_category = CategorySchema()


# todo add filters
@admin_products_bp.route("/admin/products", methods=["POST"])
@required_user_type(["admin"])
def get_products():
    data = request.get_json()
    limit = data.get("limit")
    offset = data.get("offset")

    ps = Product.query.filter_by().limit(limit).offset(offset).all()

    return success_response(message="products", data=[p.to_dict() for p in ps])


@admin_products_bp.route("/admin/products", methods=["PUT"])
@required_user_type(["admin"])
def create_product():
    try:
        validated_data = validate_add_product.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

    name = validated_data.get("name").title()
    description = validated_data.get("description")
    image_src = validated_data.get("image_sr")
    category = validated_data.get("category").lower()

    c = ProductCategory.query.filter_by(title=category).first()

    if not c:
        return bad_request(message="Category not found")

    Product.create(
        name=name, description=description, image_src=image_src, category_id=c.id
    )

    return success_response(message="Product created successfully", status_code=201)


# TODO require admin access, first implement integration test authentication in bash
@admin_products_bp.route("/admin/category", methods=["GET"])
@required_user_type(["admin"])
def get_categories():
    cs = ProductCategory.query.all()

    return success_response(
        message="Product categories:", data=[c.to_dict() for c in cs]
    )


# TODO require admin access, first implement integration test authentication in bash
@admin_products_bp.route("/admin/category", methods=["PUT"])
@required_user_type(["admin"])
# @required_permission([Permissions.CAN_CREATE_CATEGORY])
def create_category():
    try:
        validated_data = validate_add_category.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

    title = validated_data.get("title")

    try:
        _pc = ProductCategory.create(title=title)
    except IntegrityError:
        return bad_request(error="Product category already exists.")

    return success_response(
        message="Product category created successfully", status_code=201
    )


# TODO require admin access, first implement integration test authentication in bash
# TODO figure out what to do with admin using this category, should they be assigned to generic one?
@admin_products_bp.route("/admin/category", methods=["DELETE"])
@required_user_type(["admin"])
def delete_category():
    try:
        validated_data = validate_remove_category.load(request.get_json())
    except ValidationError as verr:
        return bad_request(verr.messages)

    title = validated_data.get("title").lower()

    _pc = ProductCategory.query.filter_by(title=title).first().delete()

    return success_response(message="Category removed successfully.")
