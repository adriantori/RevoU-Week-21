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
