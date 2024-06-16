# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config.config import Config
from app.modules.menu_builder import MenuBuilder
from app.modules.db import db
import json
from pathlib import Path

# db = SQLAlchemy()
login_manager = LoginManager()

def create_app(conf=None):
    if conf is None:
        conf = Config()

    print('config ok')
    app = Flask(__name__, template_folder='templates', static_folder='static')
    print('app init ok')
    app.config.from_object(conf)
    print('app config ok')

    db.init_app(app)
    print('db init ok')

    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'
    print('login routes ok')

    from app.models.user import Users

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    from app.routes.routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    print('bp registered ok')

    with app.app_context():
        # Construct the correct path for the JSON file within the 'app/static' directory
        json_file_path = Path(app.root_path) / 'static/js/menuStructure101.json'
        if not json_file_path.exists():
            app.logger.error(f"File not found: {json_file_path}")

            print(json_file_path, ' path ko')
        else:
            with open(json_file_path, 'r') as file:
                main_menu_items = json.load(file)
            menu_builder = MenuBuilder(main_menu_items, ["Guest"])
            parsed_menu_data = menu_builder.parse_menu_data(user_roles=["Guest"], is_authenticated=False, include_protected=False)
            app.parsed_menu_data = parsed_menu_data

            print('>path ok', json_file_path, parsed_menu_data)

    print('app return ok')
    return app
