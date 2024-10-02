# app_factory.py

import logging
from flask import Flask
from config.config import Config, some_keys
#import secrets
#from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, request, render_template, redirect, url_for, flash, session
from twilio.rest import Client
import os

def create_app(conf=None):
    if conf is None:
        conf = Config()

    #app = Flask(__name__, static_folder='frontend/dist', template_folder='frontend/dist')
    app = Flask(__name__)

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
    # app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SECRET_KEY'] = some_keys['secret_key_2']
    app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdcYnkpAAAAADpQdytwQVK7UtxeJJ0C_nHsPc8R'
    app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdcYnkpAAAAAKOWGB7_cEBlY-3UlBGZY9KS6zH9'
    # TODO reactivate for production!
    app.config['WTF_CSRF_ENABLED'] = True  # Disable CSRF protection for local development

    # Set the logging level to DEBUG
    # logging.basicConfig(level=logging.DEBUG)

    # environment variables
    # Set environment variables
    os.environ['TWILIO_ACCOUNT_SID'] = 'AC4be81594cf4c35b1584973b2c234d60d'
    os.environ['TWILIO_AUTH_TOKEN'] = 'a519a34888f553ac6765b40bb56d9b50'
    os.environ['TWILIO_AUTHY_API_KEY'] = 'f9e8d720fbabfec46a32ca631804c61b'

    # TODO (in)activate debug toolbar here
    app.debug = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    return app
