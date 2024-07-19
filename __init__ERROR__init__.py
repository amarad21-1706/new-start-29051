# app/__init__.py
from flask import Flask
from flask import Blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app.routes import authentication, login, menubuilder  # Add more imports as needed


login = Blueprint('login', __name__)
menubuilder = Blueprint('menubuilder', __name__)

app = Flask(__name__)
app.config.from_object(Config)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

db = SQLAlchemy(app)

# Set the login view (replace 'login' with your actual login route)
login_manager.login_view = 'login'
