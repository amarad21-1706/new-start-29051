
# app_factory.py
import os
import logging
from flask_debugtoolbar import DebugToolbarExtension  # Ensure this import is present

from app.app import create_app
from app.modules.db import db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

# Define ExcludeRequestsFilter if it's not defined elsewhere
class ExcludeRequestsFilter:
    def __init__(self):
        pass  # Implement the necessary initialization

    def filter(self, record):
        # Implement the filter logic here
        return True

# Now you can use ExcludeRequestsFilter
request_filter = ExcludeRequestsFilter()
# Other code follows...


with app.app_context():
    # Initialize Flask-Admin instance

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

    # csrf = CSRFProtect(app)

    # app.config.from_object(conf)

    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    app.logger.debug("app_factory initialized")


