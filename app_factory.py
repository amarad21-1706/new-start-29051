# app_factory.py

import os
from flask import Flask, request, session, flash, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.config import Config
from db import db
from models.user import Users
from functools import wraps
from password_reset import password_reset_bp  # Import the blueprint

def my_locale_selector():
    return 'en_EN'  # Example for French

def roles_required(*required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_roles' in session and any(role.lower() in [r.lower() for role in session['user_roles']] for role in required_roles):
                return func(*args, **kwargs)
            else:
                flash("You do not have the necessary permissions to access this page.", "danger")
                return redirect(request.referrer or url_for('index'))
        return wrapper
    return decorator

def create_app(conf=None):
    if conf is None:
        conf = Config()

    app = Flask(__name__)
    app.config.from_object(conf)

    lun_sk = len(conf.SECRET_KEY)
    print(f"S_KEY: [{lun_sk}]")

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    if os.getenv('FLASK_ENV') == 'development':
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        app.config['WTF_CSRF_ENABLED'] = False
    else:
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        app.config['WTF_CSRF_ENABLED'] = True

    csrf = CSRFProtect(app)
    mail = Mail(app)
    CORS(app)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    with app.app_context():
        from models import user
        from routes import routes  # Ensure your routes are imported here
        db.create_all()

    app.register_blueprint(password_reset_bp)  # Register the blueprint

    return app
