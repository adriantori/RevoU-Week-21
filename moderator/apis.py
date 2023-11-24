from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, request

from auth.model import User, UserRole
from follow.model import Follow
from tweet.model import Tweet

from db import db

moderator_blueprint = Blueprint('moderator', __name__)

# Flag Tweet API
@moderator_blueprint.route('/tweet', methods=['POST'])
@jwt_required()  # This decorator ensures a valid JWT is present in the request
def flag_tweet():
    try:
        # Get the identity of the current user from the JWT
        current_user_id = get_jwt_identity()

        # Retrieve the user from the database based on the user_id
        user = User.query.get(current_user_id)

        # Check if the user has the MODERATOR role
        if user.role != UserRole.MODERATOR:
            return jsonify({"error_message": "User tidak dapat melakukan aksi ini"}), 403

        # Retrieve tweet_id and is_spam from the request body
        data = request.get_json()
        tweet_id = data.get("tweet_id")
        is_spam = data.get("is_spam")

        # Retrieve the tweet from the database based on the tweet_id
        tweet = Tweet.query.get(tweet_id)

        if not tweet:
            return jsonify({"error_message": "Tweet tidak ditemukan"}), 404

        # Flag the tweet by updating the is_spam column
        tweet.is_spam = is_spam
        db.session.commit()

        # Get the updated tweet information
        updated_tweet = {
            'tweet_id': tweet.id,
            'is_spam': tweet.is_spam
        }

        return jsonify(updated_tweet), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error_message": "Internal Server Error"}), 500



# Suspend User API
@moderator_blueprint.route('/user', methods=['POST'])
@jwt_required()  # This decorator ensures a valid JWT is present in the request
def suspend_user():
    try:
        # Get the identity of the current user from the JWT
        current_user_id = get_jwt_identity()

        # Retrieve the user from the database based on the user_id
        moderator = User.query.get(current_user_id)

        # Check if the user has the MODERATOR role
        if moderator.role != UserRole.MODERATOR:
            return jsonify({"error_message": "User tidak dapat melakukan aksi ini"}), 403

        # Retrieve user_id and is_suspended from the request body
        data = request.get_json()
        user_id = data.get("user_id")
        is_suspended = data.get("is_suspended")

        # Retrieve the user to be suspended from the database
        user_to_suspend = User.query.get(user_id)

        if not user_to_suspend:
            return jsonify({"error_message": "User tidak ditemukan"}), 404

        # Suspend or unsuspend the user by updating the is_suspended column
        user_to_suspend.is_suspended = is_suspended
        db.session.commit()

        # Get the updated user information
        updated_user = {
            'user_id': user_to_suspend.id,
            'is_suspended': user_to_suspend.is_suspended
        }

        return jsonify(updated_user), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error_message": "Internal Server Error"}), 500