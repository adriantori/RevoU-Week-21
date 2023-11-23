from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from tweet.model import Tweet
from auth.model import User
from db import db

tweet_blueprint = Blueprint('tweet', __name__)

@tweet_blueprint.route('', methods=['POST'])
@jwt_required()  # This decorator ensures a valid JWT is present in the request
def create_tweet():
    try:
        # Get the identity of the current user from the JWT
        current_user_id = get_jwt_identity()

        # Retrieve the user from the database based on the user_id
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error_message": "User not found"}), 404

        # Get the tweet text from the request body
        tweet_text = request.json.get('Tweet')

        if not tweet_text or len(tweet_text) > 150:
            return jsonify({"error_message": "Tweet tidak boleh lebih dari 150 karakter"}), 400

        # Create a new tweet
        new_tweet = Tweet(user_id=current_user_id, tweet=tweet_text)
        db.session.add(new_tweet)
        db.session.commit()

        # Return the created tweet information
        response_data = {
            "id": new_tweet.id,
            "published_at": new_tweet.published_at,
            "tweet": new_tweet.tweet
        }

        return jsonify(response_data), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error_message": "Internal Server Error"}), 500
