# app/__init__.py
import logging
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from app.modules.db import db

def create_app(conf=None):
    from config.config import Config
    if conf is None:
        conf = Config()

    app = Flask(__name__)
    app.config.from_object(conf)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    csrf = CSRFProtect(app)
    csrf.init_app(app)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    with app.app_context():
        from models import user
        from routes import routes
        db.create_all()

    if app.config['DEBUG']:
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.DEBUG)
    else:
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)

    @app.before_request
    def before_request():
        app.logger.debug(f"Handling before request for {request.path}")

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Exception (errorhandler) occurred: {str(e)}")
        return "Internal Server Error", 500

    return app
