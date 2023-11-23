import os
from flask import Flask
from flask_jwt_extended import JWTManager

from auth.apis import auth_blueprint
from user.apis import user_blueprint
from tweet.apis import tweet_blueprint
from db import db, db_init

app = Flask(__name__)
database_url = os.getenv("DB_URI")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db.init_app(app)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_KEY")
jwt = JWTManager(app)


app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(tweet_blueprint, url_prefix="/tweet")

# with app.app_context():
#     db_init()