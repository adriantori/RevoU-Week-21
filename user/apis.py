from flask import Blueprint, request, jsonify
from user.model import User
from db import db

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/registration', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    bio = data.get("bio")
    role = data.get("role", "USER")

    if not username or not password or not bio:
        return {
            'error_message': 'username atau password tidak boleh kosong'
        }, 400

    # Check if the username is already taken
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {
            'error_message': 'username sudah digunakan'
        }, 400

    # Create a new user
    new_user = User(username=username, password = password, bio=bio, role=role)

    db.session.add(new_user)
    db.session.commit()

    return {
        'user_id': new_user.id,
        'username': new_user.username,
        'bio': new_user.bio
    }
    

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            'error_message': 'username atau password tidak boleh kosong'
        }, 400

    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        return {
            'token': 'abcdef'
        }, 200
    else:
        return {
            'error_message': 'username atau password tidak tepat'
        }, 401