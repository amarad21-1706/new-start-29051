# app/__init__.py

import json
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.modules.db import db
from app.modules.menu_builder import MenuBuilder
from app.utils.utils import menu_item_allowed

# NO! db = SQLAlchemy()
login_manager = LoginManager()

def create_app(conf=None):
    from config.config import Config
    if conf is None:
        conf = Config()

    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config.from_object(conf)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    from app.models.user import Users

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    from app.routes.routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    @app.context_processor
    def utility_processor():
        return dict(menu_item_allowed=menu_item_allowed)

    with app.app_context():
        # Construct the correct path for the JSON file within the 'app/static' directory
        json_file_path = Path(app.root_path) / 'static/js/menuStructure101.json'
        if not json_file_path.exists():
            app.logger.error(f"File not found: {json_file_path}")
        else:
            with open(json_file_path, 'r') as file:
                main_menu_items = json.load(file)
            menu_builder = MenuBuilder(main_menu_items, ["Guest"])
            parsed_menu_data = menu_builder.parse_menu_data(user_roles=["Guest"], is_authenticated=False, include_protected=False)
            app.parsed_menu_data = parsed_menu_data

    return app
