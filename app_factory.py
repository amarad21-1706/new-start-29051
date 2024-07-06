

# app_factory.py

# import logging
import os
from flask import Flask, request

from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_babelex import Babel
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.config import Config
from db import db

'''
class ExcludeRequestsFilter(logging.Filter):
    def filter(self, record):
        # Modify this condition based on what you want to filter out
        return not (record.args and len(record.args) > 0 and record.args[0] in ["GET", "POST", "PUT", "DELETE"])
'''

'''

HOW TO REPLACE STRING IN container

UPDATE container
SET content = jsonb_set(content, '{url}', '"\/deadlines_1"', false)
WHERE content->>'url' = '/dashboard/company/dashboard_audit';

'''
def my_locale_selector():
    # Your logic to determine user locale
    return 'en_EN'  # Example for French


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
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for local development
        # app.logger.setLevel(logging.DEBUG)
        # werkzeug_logger = logging.getLogger('werkzeug')
        # werkzeug_logger.setLevel(logging.INFO)
    else:
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        app.config['WTF_CSRF_ENABLED'] = True
        # app.logger.setLevel(logging.WARNING)
        # werkzeug_logger = logging.getLogger('werkzeug')
        #werkzeug_logger.setLevel(logging.WARNING)

    csrf = CSRFProtect(app)
    # babel = Babel(app, locale_selector=my_locale_selector)
    mail = Mail(app)
    CORS(app)  # Allow all origins (for development only)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    db.init_app(app)

    app.config['SQLALCHEMY_ECHO'] = False

    # Set up logging before any operations
    '''
    logging.basicConfig(level=logging.ERROR)  # Set root logger level

    # Set up specific loggers for SQLAlchemy
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.ERROR)

    sqlalchemy_pool_logger = logging.getLogger('sqlalchemy.pool')
    sqlalchemy_pool_logger.setLevel(logging.ERROR)
    '''

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    with app.app_context():
        from models import user  # Importing models to create tables
        from routes import routes  # Importing routes to register them
        db.create_all()

    # toolbar = DebugToolbarExtension(app)  # Ensure this line comes after app.config is set

    return app
