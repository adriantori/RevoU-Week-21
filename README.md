# Week 12 - Creates twitter-like back-end using Flask

## Features:

- Login / Register

- See profile; user id, username, bio, number of following and followers, 10 recent tweets

- Post tweet

- Follow / unfollow someone based on their user id

##### Advanced:

- Adds moderation page, which can only be accessed by, you guess it, MODERATOR.

- They can flag tweet as spam and suspend user.

- Changed how profile and tweet fetched.

- Also note that I only wrote the important code on Advanced section instead of changing the intermediate code. Just imagine the Advanced section codes somehow override it.

## How to use:

1. Pull the project (in case I cant deploy it)

2. run these codes (and I hope its correct):
   
   ```python
   pip install pipenv
   pipenv shell
   pipenv install
   ```

3. Uncomment this line of code on app.py to initialize database (shouldn't need to since its connected to my database, which contains necesssary column)

```python
# with app.app_context():
#     db_init()
```

3. Import the Postman collection data (should be in the root folder)

4. ????

5. Profit

## Models:

### User:

```python
from db import db
from enum import Enum
from sqlalchemy import Enum as EnumType
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class UserRole(Enum):
    MODERATOR = 'MODERATOR'
    USER = 'USER'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # Updated to store hashed passwords
    bio = db.Column(db.String(200), nullable=False)
    role = db.Column(EnumType(UserRole), default=UserRole.USER, nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
```

### Tweet:

```python
from db import db
from datetime import datetime

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tweet = db.Column(db.String(150), nullable=False)
```

### Follow:

```python
from db import db

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

## List of important codes:

### Registration:

```python
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
```

### Login:

```python
user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Use Flask-JWT-Extended to generate a token
        access_token = create_access_token(identity=user.id)
        return {
            'token': access_token
        }, 200
    else:
        return {
            'error_message': 'username atau password tidak tepat'
        }, 401
```

### Get Profile:

```python
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
```

### Post Tweet:

```python
 # Get the tweet text from the request body
        tweet_text = request.json.get('Tweet')

        if not tweet_text or len(tweet_text) > 150:
            return jsonify({"error_message": "Tweet tidak boleh lebih dari 150 karakter"}), 400

        # Create a new tweet
        new_tweet = Tweet(user_id=current_user_id, tweet=tweet_text)
        db.session.add(new_tweet)
        db.session.commit()
```

### Following / Unfollow:

```python
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
```

## Advanced:

do keep in mind that this part of codes and model overrides previous codes. I didnt change the previous codes for documentation and differentiate between intermediate and advanced tasks.

### Fetch Followed Tweets Exluding Current User:

```python
# Retrieve the IDs of all users that the current user is following, excluding the current user's ID
        following_ids = [follow.following_id for follow in Follow.query.filter_by(follower_id=current_user_id)] + [current_user_id]

        # Exclude the current user's ID from the list of following_ids
        following_ids = [user_id for user_id in following_ids if user_id != current_user_id]

        # Retrieve the 10 most recent tweets from the followed users, excluding flagged tweets
        feed_tweets = (
            Tweet.query
            .filter(Tweet.user_id.in_(following_ids), ~Tweet.is_spam)  # Exclude flagged tweets
            .order_by(Tweet.published_at.desc())
            .limit(10)
            .all()
        )

        # Prepare the response data
        response_data = {
            'tweets': [
                {
                    'id': tweet.id,
                    'user_id': tweet.user_id,
                    'username': tweet.user.username,
                    'published_at': tweet.published_at,
                    'tweet': tweet.tweet
                } for tweet in feed_tweets
            ]
        }
```

### User Suspend:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # Updated to store hashed passwords
    bio = db.Column(db.String(200), nullable=False)
    role = db.Column(EnumType(UserRole), default=UserRole.USER, nullable=False)
    is_suspended = db.Column(db.Boolean, default=False)  # New column for suspending users
```

```python
# Login():
user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        if user.is_suspended:
            return {
                'error_message': 'akun telah di suspend'
            }, 401
```

### Tweet Flag:

```python
from db import db
from datetime import datetime

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tweet = db.Column(db.String(150), nullable=False)
    is_spam = db.Column(db.Boolean, default=False)  # New column for flagging tweets

```

### User Fetch Profile Exlude Flagged:

```python
# Retrieve the 10 most recent tweets for the user, excluding flagged tweets
recent_tweets = Tweet.query.filter_by(user_id=current_user_id, is_spam=False).order_by(Tweet.published_at.desc()).limit(10).all()      )
```
