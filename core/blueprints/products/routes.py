from datetime import datetime

import psycopg2.errors
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from core import Product, ProductCategory
from core import User, bcrypt, TokenBlocklist, UserType
from ..utils import success_response
from ..errors.handlers import bad_request, unauthorized
from ...extensions import jwt_manager
from sqlalchemy import exc
from ..utils import required_user_type


products_bp = Blueprint('products', __name__)


@products_bp.route('/products', methods=['POST'])
def products():
    data = request.get_json()
    limit = data.get('limit')
    offset = data.get('offset')

    ps = (Product.query
          .filter_by()
          .limit(limit)
          .offset(offset))

    return success_response(message="ok", data=[p.to_dict() for p in ps])


@products_bp.route('/product', methods=['PUT'])
def create_product():
    print(request.data)
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    image_src = data.get('image_src')
    category = str(data.get('category')).lower()

    c = (ProductCategory.query
         .filter_by(title=category)
         .first())
    if not c:
        return bad_request('category not found')

    p = Product.create(name=name, description=description, image_src=image_src, category_id=c.id)

    return success_response(message="ok", data=p.to_dict())


# TODO require admin access, first implement integration test authentication in bash
@products_bp.route('/admin/category', methods=['GET'])
@required_user_type([UserType.ADMIN])
def get_categories():
    cs = ProductCategory.query.all()
    return success_response(message="ok", data=[c.to_dict() for c in cs])


# TODO require admin access, first implement integration test authentication in bash
@products_bp.route('/admin/category', methods=['PUT'])
@required_user_type([UserType.ADMIN])
# @required_permission([Permissions.CAN_CREATE_CATEGORY])
def create_category():
    data = request.get_json()
    title = str(data.get('title')).lower()

    try:
        pc = ProductCategory.create(title=title)
    except exc.IntegrityError:
        return bad_request(error="category already exists")

    return success_response(message="ok")


# TODO require admin access, first implement integration test authentication in bash
# TODO figure out what to do with products using this category, should they be assigned to generic one?
@products_bp.route('/admin/category', methods=['DELETE'])
@required_user_type([UserType.ADMIN])
def delete_category():
    data = request.get_json()
    title = str(data.get('title')).lower()

    pc = ProductCategory.query.filter_by(title=title).first().delete()

    return success_response(message="ok")


