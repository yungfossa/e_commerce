import datetime
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from core import User, bcrypt, UserType, TokenBlocklist
from ..utils import success_response
from ..errors.handlers import bad_request, unauthorized
from ...extensions import jwt_manager

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

# callback function to check if a JWT exists in the database blocklist
@jwt_manager.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).scalar()
    
    return token is not None

# endpoint for revoking the current user access token. saved the unique identifier
# (jti) for the JWT into our database
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def revoke_token():
    # todo add try-catch ?
    TokenBlocklist.create(
        jti=get_jwt()["jti"],
        created_at=datetime.datetime.now()
    )
    
    return success_response(message="jwt token revoked successfully")