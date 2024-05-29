#from app_factory import create_app
from config.config import Config
from flask import session, flash

from models.user import (
        Answer, Company, Area, Subarea, AreaSubareas)
from flask import Flask
from config.config import Config
from flask_wtf import FlaskForm

from wtforms import SubmitField

#app = Flask(__name__)
#app.config.from_object(Config)

config_instance = Config()

class DeleteConfirmationForm(FlaskForm):
    submit = SubmitField('Delete')


def get_current_intervals(session):
    # Define the logic to retrieve intervals from the database
    # This function should return intervals
    pass


def get_areas() -> list[Area]:
    return Area.query.all()


def get_subareas(area_id):

    # Query subareas based on area_id
    subareas = Subarea.query.join(AreaSubareas).filter(AreaSubareas.area_id == area_id).all()

    # Convert the list of SQLAlchemy objects to a list of Subarea instances
    subareas_list = [subarea for subarea in subareas]

    return subareas_list


def get_except_fields():
    return config_instance.EXCEPT_FIELDS

def get_current_directory():
    return config_instance.CURRENT_DIRECTORY

def reset_to_guest():
    from utils import reset_current_user_to_guest
    from app import logout_user, redirect, url_for  # Import other necessary functions

    logout_user()
    reset_current_user_to_guest()
    flash('Current user reset to "Guest"', 'info')
    return redirect(url_for('index'))

def reset_current_user_to_guest():
    from app import user_manager, login_user
    from userManager101 import TemporaryUser
    guest_user = user_manager.load_user_by_username("Guest")
    if guest_user is not None:
        login_user(guest_user)
    else:
        # If "Guest" user is not found, create a temporary user
        temporary_user = TemporaryUser(user_id=None)
        login_user(temporary_user)

    session['user_roles'] = ['Guest']

