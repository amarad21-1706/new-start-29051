# app_factory.py

import logging
from flask import Flask

from werkzeug.middleware.proxy_fix import ProxyFix
from config.config import Config, some_keys
#import secrets
#from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, request, render_template, redirect, url_for, flash, session
from twilio.rest import Client
import os

import psycopg2
from sqlalchemy import dialects


class ExcludeRequestsFilter(logging.Filter):
    def filter(self, record):
        return not (record.args and len(record.args) > 0 and record.args[0] in ["GET", "POST", "PUT", "DELETE"])

def create_app(conf=None):
    if conf is None:
        conf = Config()

    #app = Flask(__name__, static_folder='frontend/dist', template_folder='frontend/dist')
    app = Flask(__name__)
    # Wrap the Flask app with ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Set up logging based on the environment

    # Set up logging based on the environment
    if os.getenv('FLASK_ENV') == 'development':
        app.config['DEBUG'] = True
        # Configure Flask app logger
        app.logger.setLevel(logging.INFO)

        # Configure Werkzeug logger to suppress HTTP request logs
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.INFO)

        # Apply custom filter to suppress HTTP request logs
        request_filter = ExcludeRequestsFilter()
        werkzeug_logger.addFilter(request_filter)

    else:
        app.config['DEBUG'] = False
        # Configure Flask app logger
        app.logger.setLevel(logging.INFO)

        # Configure Werkzeug logger to suppress HTTP request logs
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)

    csrf = CSRFProtect(app)

    #Bootstrap(app)

    #app.config['SESSION_TYPE'] = 'filesystem'  # You can choose other session types as well
    #Session(app)

    app.config.from_object(conf)
    app.config['STATIC_FOLDER'] = 'static'
    app.config['ASSETS_FOLDER'] = 'assets'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Example: 1 hour

    # CAPTCHA
    # app.config['SECRET_KEY'] = some_keys['secret_key_2']

    print('mail server', app.config['SECRET_KEY'][:10], app.config['MAIL_SERVER'])
    # TODO reactivate for production!
    app.config['WTF_CSRF_ENABLED'] = True  # Disable CSRF protection for local development

    # Set the logging level to DEBUG
    # logging.basicConfig(level=logging.DEBUG)

    # environment variablesg

    app.debug = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    # toolbar = DebugToolbarExtension(app)

    return app
