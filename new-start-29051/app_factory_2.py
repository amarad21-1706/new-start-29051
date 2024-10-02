# app_factory.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config

def create_app_2(conf=None):
    if conf is None:
        conf = Config()

    app_2 = Flask(__name__, static_folder='frontend/dist2', template_folder='frontend/dist2')
    app_2.config.from_object(conf)
    app_2.config['STATIC_FOLDER'] = 'static'
    app_2.config['ASSETS_FOLDER'] = 'assets'

    return app_2
