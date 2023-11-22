from db import db
from enum import Enum
from sqlalchemy import Enum as EnumType

class UserRole(Enum):
    MODERATOR = 'MODERATOR'
    USER = 'USER'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(200), nullable=False)
    role = db.Column(EnumType(UserRole), default=UserRole.USER, nullable=False)