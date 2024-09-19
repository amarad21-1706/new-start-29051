# app_factory.py

import os
from flask import Flask, request, session, flash, redirect, url_for, send_from_directory
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.config import Config
from db import db
from models.user import Users #, Plan, Product
from functools import wraps
from password_reset import password_reset_bp  # Import the blueprint
# from flask_babel import Babel

csrf = CSRFProtect()  # Define csrf globally
# babel = Babel()  # Initialize Babel without an app instance

def my_locale_selector():
    return 'en_EN'  # Example for French


def roles_required(*required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_roles' in session and any(r.lower() in [role.lower() for role in required_roles] for r in session['user_roles']):
                return func(*args, **kwargs)
            else:
                flash("You do not have the necessary permissions to access this page.", "danger")
                return redirect(request.referrer or url_for('index'))
        return wrapper
    return decorator



def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #current_app.logger.debug('Checking subscription requirement...')
        user_roles = session.get('user_roles', [])
        #current_app.logger.debug(f'user_roles: {user_roles}')

        print('decorator: status is 2. user roles', user_roles)

        if 'Admin' in user_roles or 'Authority' in user_roles:
            # current_app.logger.debug('User has Admin or Authority role, granting access...')
            return f(*args, **kwargs)  # Allow access if user has Admin or Authority role

        email = session.get('email')
        print('session email', email)
        #current_app.logger.debug(f'user email: {email}')
        user = Users.query.filter_by(email=email).first()

        if not user or user.subscription_status != 'active':
            flash('You need an active subscription to access this page.')
            #current_app.logger.debug('No active subscription, redirecting to subscriptions page...')
            return redirect(url_for('subscriptions'))

        # current_app.logger.debug('User has an active subscription, granting access...')
        return f(*args, **kwargs)

    return decorated_function

def create_app(conf=None):
    if conf is None:
        conf = Config()

    # app = Flask(__name__)
    # app = Flask(__name__, static_folder='static')
    # app = Flask(__name__, static_folder="static", static_url_path="/")
    app = Flask(__name__, static_folder="static")

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

    # csrf = CSRFProtect(app) # already defined globally
    mail = Mail(app)
    CORS(app)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    with app.app_context():
        from models import user
        from routes import routes  # Ensure your routes are imported here
        db.init_app(app)
        db.create_all()
        # Initialize extensions with the app instance
        # babel.init_app(app)  # Initialize Babel with the app instance

    app.register_blueprint(password_reset_bp)  # Register the blueprint

    return app
