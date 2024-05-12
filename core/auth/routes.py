import datetime
from functools import wraps
from typing import List

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from core import User, bcrypt

bp = Blueprint('auth', __name__)


@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    surname = data.get('surname')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'missing email or password'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'email already exists'}), 400

    User.create(
        email=email,
        name=name,
        surname=surname,
        password=bcrypt.generate_password_hash(password, 10).decode('utf-8'),
        birth_date=datetime.datetime.now(),
        user_type="customer"
    )

    return jsonify({'message': 'user created successfully'}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'missing email or password'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'invalid email or password'}), 401

    access_token = create_access_token(identity=email, additional_claims={'user_type': user.user_type})
    return jsonify(access_token=access_token), 200


def required_user_type(types: List[str]):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user = get_jwt()
            if current_user.get('user_type') not in types:
                return jsonify({'message': 'Unauthorized'}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


@bp.route('/protected', methods=['GET'])
@required_user_type(['customer', 'admin'])
def protected():
    current_user = get_jwt()
    print(current_user)
    return jsonify(logged_in_as=current_user.get('sub'),user_type=current_user.get('user_type')), 200
