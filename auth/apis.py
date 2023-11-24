from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from auth.model import User, UserRole
from db import db

bcrypt = Bcrypt()

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/registration', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    bio = data.get("bio")
    role = data.get("role", "USER")

    if not username or not password or not bio:
        return {
            'error_message': 'username, password, dan bio tidak boleh kosong'
        }, 400

    # Check if the username is already taken
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {
            'error_message': 'username sudah digunakan'
        }, 400

    # Use Flask-Bcrypt to hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new user with the hashed password
    new_user = User(username=username, password=hashed_password, bio=bio, role=UserRole[role])

    db.session.add(new_user)
    db.session.commit()

    return {
        'user_id': new_user.id,
        'username': new_user.username,
        'bio': new_user.bio
    }
    

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            'error_message': 'username atau password tidak boleh kosong'
        }, 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if user.is_suspended:
            return {
                'error_message': 'akun telah di suspend'
            }, 401

        # Use Flask-JWT-Extended to generate a token
        access_token = create_access_token(identity=user.id)
        return {
            'token': access_token
        }, 200
    else:
        return {
            'error_message': 'username atau password tidak tepat'
        }, 401