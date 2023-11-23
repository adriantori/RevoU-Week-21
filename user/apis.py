from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, jsonify
from auth.model import User
from tweet.model import Tweet
from follow.model import Follow

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('', methods=['GET'])
@jwt_required()  # This decorator ensures a valid JWT is present in the request
def get_profile():
    try:
        # Get the identity of the current user from the JWT
        current_user_id = get_jwt_identity()

        # Retrieve the user from the database based on the user_id
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error_message": "User not found"}), 404

        # Retrieve the 10 most recent tweets for the user
        recent_tweets = Tweet.query.filter_by(user_id=current_user_id).order_by(Tweet.published_at.desc()).limit(10).all()

        # Count the number of followers and following
        followers_count = Follow.query.filter_by(following_id=current_user_id).count()
        following_count = Follow.query.filter_by(follower_id=current_user_id).count()

        response_data = {
            'user_id': user.id,
            'username': user.username,
            'bio': user.bio,
            'following': following_count,
            'followers': followers_count,
            'tweets': [
                {
                    'id': tweet.id,
                    'published_at': tweet.published_at,
                    'tweet': tweet.tweet
                } for tweet in recent_tweets
            ]
        }

        return jsonify(response_data), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error_message": "Internal Server Error"}), 500