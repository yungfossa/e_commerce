import datetime
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from core import User, bcrypt, UserType
from ..utils import success_response
from ..errors.handlers import bad_request, unauthorized

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    surname = data.get('surname')
    password = data.get('password')
    
    if not email or not password:
        return bad_request('missing email or password')
    
    if User.query.filter_by(email=email).first():
        return bad_request('email already exists')
    
    # todo add try-catch ?
    User.create(
        email=email,
        name=name,
        surname=surname,
        password=bcrypt.generate_password_hash(password, 10).decode('utf-8'),
        birth_date=datetime.datetime.now(),
        user_type=UserType.ADMIN
    )

    return success_response(message='user created successfully', status_code=201)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return bad_request('missing email or password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not bcrypt.check_password_hash(user.password, password):
        return unauthorized('invalid email or password')
    
    access_token = create_access_token(identity=email, additional_claims={'user_type': user.user_type.value})
    
    return success_response(message='login successful', data={'access_token': access_token})