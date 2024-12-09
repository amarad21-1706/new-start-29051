# app_factory.py favicon

import os
from sqlalchemy.exc import OperationalError
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
import datetime
from datetime import date, timedelta, time, timezone

from flask_babel import Babel
from flask_babel import get_locale, _
# Example function for translating text
from flask_babel import gettext as _
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

csrf = CSRFProtect()  # Define csrf globally
# babel = Babel()  # Initialize Babel without an app instance

def roles_required(*required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_roles' in session and any(r.lower() in [role.lower() for role in required_roles] for r in session['user_roles']):
                return func(*args, **kwargs)
            else:
                flash(_("You do not have the necessary permissions to access this page."), "danger")
                return redirect(request.referrer or url_for('index'))
        return wrapper
    return decorator


def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #current_app.logger.debug('Checking subscription requirement...')
        user_roles = session.get('user_roles', [])
        #current_app.logger.debug(f'user_roles: {user_roles}')

        if 'Admin' in user_roles or 'Authority' in user_roles:
            # current_app.logger.debug('User has Admin or Authority role, granting access...')
            return f(*args, **kwargs)  # Allow access if user has Admin or Authority role

        email = session.get('email')
        print('session email', email)
        #current_app.logger.debug(f'user email: {email}')
        user = Users.query.filter_by(email=email).first()

        if not user or user.subscription_status != 'active':
            flash(_('You need an active subscription to access this page.'))
            #current_app.logger.debug('No active subscription, redirecting to subscriptions page...')
            return redirect(url_for('subscriptions'))

        # current_app.logger.debug('User has an active subscription, granting access...')
        return f(*args, **kwargs)

    return decorated_function


def create_app(conf=None):
    # Load .env variables
    load_dotenv()

    if conf is None:
        conf = Config()

    # app = Flask(__name__)
    # app = Flask(__name__, static_folder='static')
    # app = Flask(__name__, static_folder="static", static_url_path="/")
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # Configuration
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

    babel = Babel(app)

    # Initialize extensions
    babel.init_app(app, locale_selector=get_locale)

    # Use direct assignment instead of decorator
    babel.locale_selector_func = lambda: (
        request.args.get('lang') or
        session.get('lang') or
        request.accept_languages.best_match(['en', 'it', 'es', 'fr', 'ar'])
    )


    def translate_text(text):
        """
        Dynamically translate database text.
        """
        if not text:
            return ""
        try:
            translated = _(text)  # Uses Flask-Babel's gettext
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Fallback to original text if translation fails

    # Register the function with Jinja2
    @app.context_processor
    def inject_translation_helpers():
        return dict(_=translate_text)

    # Explicitly set debug mode based on an environment variable or configuration
    # app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '0') == '1'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)  # Set 60-minute session lifetime

    app.config.from_object(conf)

    # Print environment details
    print(f"FLASK_ENV setting = {os.getenv('FLASK_ENV', 'Not set')}")
    print(f"FLASK_DEBUG = {os.getenv('FLASK_DEBUG', 'Not set')}")
    print(f"Environment: {app.config['ENV']}")
    print(f"Debug: {app.debug}")


    # Enable secure session cookies in production
    if os.getenv('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SQLALCHEMY_ECHO'] = False
    else:
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SQLALCHEMY_ECHO'] = False
    # Custom logger setup
    logger = logging.getLogger('app')  # Create or retrieve the logger
    logger.setLevel(logging.INFO)

    # Add handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Attach logger to app
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)

    # logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    # not for production, only for development
    # lun_sk = len(conf.SECRET_KEY)
    # print(f"S_KEY: [{lun_sk}]")

    if os.getenv('FLASK_ENV') == 'production':
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    #more secure and explicit:
    if app.config['DEBUG']:
        app.config.update({
            'SQLALCHEMY_ECHO': False,
            'DEBUG_TB_INTERCEPT_REDIRECTS': False,
            'WTF_CSRF_ENABLED': False,
        })
    else:
        app.config.update({
            'SQLALCHEMY_ECHO': False,
            'DEBUG_TB_INTERCEPT_REDIRECTS': False,
            'WTF_CSRF_ENABLED': True,
        })

    csrf = CSRFProtect()  # Initialize globally
    csrf.init_app(app)  # Attach to Flask app

    base_domains = ["dere-platform.com", "dereplatform.com"]
    allowed_origins = [f"https://{domain}" for domain in base_domains]
    allowed_origins += [f"https://www.{domain}" for domain in base_domains]
    allowed_origins.append("https://new-start-29051.onrender.com")  # Render domain

    # Allow specific domains for CORS
    if app.config['DEBUG']:
        CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for development
    else:
        CORS(app, resources={r"/*": {"origins": allowed_origins}})

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Set up Google Cloud credentials
    key_content = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if key_content:
        key_file_path = "/tmp/service-account-key.json"
        with open(key_file_path, "w") as key_file:
            key_file.write(key_content)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path
    else:
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS_JSON is not set in the environment")

    with app.app_context():
        from models import user
        from routes import routes  # Ensure your routes are imported here
        db.init_app(app)

        try:
            db.create_all()  # Create tables in the database
        except OperationalError as e:
            app.logger.error(f"Database connection failed during app initialization: {e}")
            # You can handle this more gracefully, but here we're stopping the app
            raise SystemExit("Could not connect to the database. Please check your database server.")

        # Initialize extensions with the app instance
        # babel.init_app(app)  # Initialize Babel with the app instance

    # Configure logging
    if not app.debug:

        # Set up RotatingFileHandler for error logging
        file_handler = RotatingFileHandler('error.log', maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)

    app.register_blueprint(password_reset_bp)  # Register the blueprint

    return app


def get_locale():
    # Use the language stored in the session, or default to English
    return session.get('lang', 'en')

