from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config
from app.models.user import User

#from dbb import dbb
appb = Flask(__name__)
appb.config.from_object(Config)
dbb = SQLAlchemy(appb)

class User(dbb.Model):
    id = dbb.Column(dbb.Integer, primary_key=True)
    username = dbb.Column(dbb.String(80), unique=True, nullable=False)
    password = dbb.Column(dbb.String(128), nullable=False)
    #hashing_version = dbb.Column(dbb.Integer, default=1)  # Add a column to store hashing version

def rehash_passwords():
    users = User.query.all()

    for user in users:
        #if user.hashing_version < 2:
        # Rehash the password using the new logic
        new_hashed_password = generate_password_hash(user.password)

        # Update the user record with the new hashed password and hashing version
        user.password = new_hashed_password
        #user.hashing_version = 2

    dbb.session.commit()

if __name__ == '__main__':
    with appb.app_context():
        rehash_passwords()
