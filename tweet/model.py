from db import db
from datetime import datetime

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tweet = db.Column(db.String(150), nullable=False)
    is_spam = db.Column(db.Boolean, default=False)  # New column for flagging tweets
