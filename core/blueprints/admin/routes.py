from sqlalchemy import exc
from flask import Blueprint, request, jsonify
from ..errors.handlers import bad_request
from ..utils import required_user_type, success_response
from ...models import Product, ProductCategory, User

admin_bp = Blueprint("admin", __name__)


# todo add filters
@admin_bp.route("/admin/products", methods=["POST"])
def products():
    data = request.get_json()
    limit = data.get("limit")
    offset = data.get("offset")

    ps = Product.query.filter_by().limit(limit).offset(offset)

    return success_response(message="products", data=[p.to_dict() for p in ps])


@admin_bp.route("/admin/products", methods=["PUT"])
@required_user_type(["admin"])
def create_product():
    data = request.get_json()
    name = str(data.get("name")).title()
    description = data.get("description")
    image_src = data.get("image_src")
    category = str(data.get("category")).lower()

    c = ProductCategory.query.filter_by(title=category).first()

    if not c:
        return bad_request("category not found")

    p = Product.create(
        name=name, description=description, image_src=image_src, category_id=c.id
    )

    return success_response(message="Product created successfully.", data=p.to_dict())


# TODO require admin access, first implement integration test authentication in bash
@admin_bp.route("/admin/category", methods=["GET"])
@required_user_type(["admin"])
def get_categories():
    cs = ProductCategory.query.all()

    return success_response(
        message="product categories:", data=[c.to_dict() for c in cs]
    )


# TODO require admin access, first implement integration test authentication in bash
@admin_bp.route("/admin/category", methods=["PUT"])
@required_user_type(["admin"])
# @required_permission([Permissions.CAN_CREATE_CATEGORY])
def create_category():
    data = request.get_json()
    title = str(data.get("title")).lower()

    try:
        _pc = ProductCategory.create(title=title)
    except exc.IntegrityError:
        return bad_request(error="Product category already exists.")

    return success_response(message="Product category created successfully.")


# TODO require admin access, first implement integration test authentication in bash
# TODO figure out what to do with admin using this category, should they be assigned to generic one?
@admin_bp.route("/admin/category", methods=["DELETE"])
@required_user_type(["admin"])
def delete_category():
    data = request.get_json()
    title = str(data.get("title")).lower()

    _pc = ProductCategory.query.filter_by(title=title).first().delete()

    return success_response(message=f"{title.title()} category removed successfully.")


@admin_bp.route("/admin/users", methods=["GET"])
@required_user_type(["admin"])
def users():
    us = User.query.all()

    return jsonify(users=[u.to_dict(rules=("-password",)) for u in us]), 200
