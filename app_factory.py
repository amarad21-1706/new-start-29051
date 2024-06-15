import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from config.config import Config
import os
import psycopg2


class ExcludeRequestsFilter(logging.Filter):
    def filter(self, record):
        return not (record.args and len(record.args) > 0 and record.args[0] in ["GET", "POST", "PUT", "DELETE"])


def create_app(conf=None):
    if conf is None:
        conf = Config()

    app = Flask(__name__)

    @app.before_request
    def before_request():
        app.logger.debug("Handling request for %s", request.path)

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error("Exception occurred: %s", str(e))
        return "Internal Server Error", 500

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    if os.getenv('FLASK_ENV') == 'development':
        app.config['DEBUG'] = True
        app.logger.setLevel(logging.DEBUG)
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.DEBUG)
        request_filter = ExcludeRequestsFilter()
        werkzeug_logger.addFilter(request_filter)
    else:
        app.config['DEBUG'] = False
        app.logger.setLevel(logging.WARNING)
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)

    # Set up logging
    if not app.debug and app.logger.hasHandlers():
        app.logger.handlers.clear()

    logging.basicConfig(level=logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    csrf = CSRFProtect(app)

    app.config.from_object(conf)


    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    app.logger.debug("app_factory initialized")
    return app

