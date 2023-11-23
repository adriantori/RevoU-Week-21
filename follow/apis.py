from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from auth.model import User
from follow.model import Follow
from db import db

follow_blueprint = Blueprint('follow', __name__)

@follow_blueprint.route('', methods=['POST'])
@jwt_required()  # This decorator ensures a valid JWT is present in the request
def follow_unfollow():
    try:
        # Get the identity of the current user from the JWT
        current_user_id = get_jwt_identity()

        # Get the user_id to follow/unfollow from the request body
        target_user_id = request.json.get('user_id')

        # Check if the target user exists
        target_user = User.query.get(target_user_id)
        if not target_user:
            return jsonify({"error_message": "User to follow/unfollow not found"}), 404

        # Check if the user is trying to follow/unfollow themselves
        if current_user_id == target_user_id:
            return jsonify({"error_message": "Tidak bisa follow diri sendiri"}), 400

        # Check if the user is already following the target user
        is_following = Follow.query.filter_by(follower_id=current_user_id, following_id=target_user_id).first()

        # Toggle follow/unfollow status
        if is_following:
            # If already following, unfollow
            db.session.delete(is_following)
            following_status = "unfollow"
        else:
            # If not following, follow
            new_follow = Follow(follower_id=current_user_id, following_id=target_user_id)
            db.session.add(new_follow)
            following_status = "follow"

        db.session.commit()

        return jsonify({"following_status": following_status}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error_message": "Internal Server Error"}), 500
