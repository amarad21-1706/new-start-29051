#from app_factory import create_app
import os
from pathlib import Path

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageColor
from flask import session, flash, redirect, url_for, render_template, request
import random
import math
import string
import base64
from io import BytesIO
from flask_wtf import FlaskForm

from functools import wraps
from wtforms import SubmitField
from sqlalchemy.exc import IntegrityError

from app.models.user import (Post, UserRoles, Role,
                             Area, Subarea, AreaSubareas)

#app = Flask(__name__)
#app.config.from_object(Config)

# app/utils/utils.py

def menu_item_allowed(menu_item, user_roles):
    # Replace this logic with your actual permission-checking logic
    allowed_roles = menu_item.get('roles', [])
    return any(role in user_roles for role in allowed_roles)


def generate_captcha(width=300, height=100, length=5):
    # Define the path to the font file within the static/fonts directory
    project_root = Path(__file__).parent.parent
    font_path = project_root / 'static' / 'fonts' / 'Geneve.ttf'
    print(f"Font path: {font_path}")  # Debug print

    # Verify that the font file exists
    if not font_path.exists():
        raise FileNotFoundError(f"Font file not found at {font_path}")

    # Create an image with white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Load a TTF font
    try:
        font = ImageFont.truetype(str(font_path), 40)  # Convert PosixPath to string
    except IOError as e:
        print(f"Error loading font: {e}")
        raise

    # Generate random text for the CAPTCHA
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    # Calculate the size of the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Draw the text onto the image
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2
    draw.text((text_x, text_y), text, font=font, fill='black')

    # Add some noise and lines
    for _ in range(10):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='black')

    # Apply a filter to distort the image
    image = image.filter(ImageFilter.GaussianBlur(2))

    # Apply more advanced distortions
    def apply_wave(image, amplitude_range, frequency_range):
        amplitude = random.uniform(*amplitude_range)
        frequency = random.uniform(*frequency_range)
        width, height = image.size
        x_wave = [
            (x, int(amplitude * math.sin(frequency * (x / width) * 2 * math.pi)))
            for x in range(width)
        ]
        y_wave = [
            (int(amplitude * math.sin(frequency * (y / height) * 2 * math.pi)), y)
            for y in range(height)
        ]
        x_image = ImageChops.offset(image, 0, 0)
        for x, offset in x_wave:
            x_image.paste(image.crop((x, 0, x + 1, height)), (x, offset))
        y_image = ImageChops.offset(image, 0, 0)
        for y, offset in y_wave:
            y_image.paste(x_image.crop((0, y, width, y + 1)), (offset, y))
        return y_image

    image = apply_wave(image, amplitude_range=(5, 10), frequency_range=(0.1, 0.3))

    # Save the image to a byte buffer
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return text, image_base64

def get_user_roles(session=None, user_id=None):
    # Query UserRoles to get the roles for the given user ID
    user_roles = session.query(UserRoles).filter(UserRoles.user_id == user_id).all()
    # Extract role IDs from user_roles
    role_ids = [user_role.role_id for user_role in user_roles]
    # Query Role table to get role names for the extracted role IDs
    roles = session.query(Role).filter(Role.id.in_(role_ids)).all()
    # Extract role names from roles
    role_names = [role.name for role in roles]
    print('Roles for user', user_id, 'are:', role_names)
    if not role_names:
        return None
    return role_names

import sqlalchemy
from sqlalchemy.exc import IntegrityError
import logging



def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if the user has the required role
            if 'user_roles' in session and any(role.lower() == required_role.lower() for role in session['user_roles']):
                return func(*args, **kwargs)
            else:
                # If the user doesn't have the required role, abort with a 403 Forbidden error
                abort(403)
        return wrapper
    return decorator


def generate_menu_tree(menu, depth=0):
    """
    Recursively generates a clean tree from the menu structure.

    Args:
    - menu (dict): The menu structure.
    - depth (int): The depth of the current recursion.

    Returns:
    - str: The generated tree as a string.
    """
    tree = ""
    # Indentation based on the depth
    indentation = "  " * depth

    for key, value in menu.items():
        # Skip the "url" and "protected" keys
        if key not in ["url", "protected"]:
        #if key not in ["url"]:

            # Append the current label to the tree
            tree += f"{indentation}- {value['label']}\n"

            # Recursively process submenus
            if "submenus" in value:
                tree += generate_menu_tree(value["submenus"], depth + 1)

    return tree



def create_message(session=None, user_id=None, message_type=None, subject=None, body=None, sender=None, company_id=None,
                   lifespan='one-off', allow_overwrite=False):
    try:
        # Check if a similar message already exists
        existing_message = session.query(Post).filter_by(user_id=user_id, subject=subject,
                                                            message_type=message_type).first()

        if existing_message:
            # Handle existing message
            if allow_overwrite:
                # Update the existing message
                existing_message.body = body
                existing_message.sender = sender
                existing_message.created_at = datetime.utcnow()
                session.commit()  # Commit the transaction
                logging.info("Message updated successfully.")
            else:
                # Append the message if overwriting is not allowed
                logging.warning("Message already exists and overwriting is not allowed.")
        else:
            # Create a new Message instance
            message_content = Post(
                user_id=user_id,
                message_type=message_type,
                subject=subject,
                body=body,
                sender=sender,
                company_id=company_id,
                lifespan=lifespan,
                created_at=datetime.utcnow()  # Ensure UTC datetime
            )
            # Add the message to the session
            session.add(message_content)
            session.commit()  # Commit the transaction
            logging.info("Message created successfully.")

    except IntegrityError as e:
        session.rollback()  # Rollback the transaction
        logging.error("Integrity error occurred while creating message: %s", str(e))

    except sqlalchemy.exc.SQLAlchemyError as e:
        session.rollback()  # Rollback the transaction
        logging.error("Error occurred while creating message: %s", str(e))

    except Exception as e:
        session.rollback()  # Rollback the transaction
        logging.error("Unexpected error occurred while creating message: %s", str(e))


# Example usage:
# create_message(session, user_id=1, message_type='last_access', subject='Last Access Notification', body='You accessed the system.', allow_overwrite=True)
# create_message(session, user_id=1, message_type='email', subject='New Notification', body='You have a new notification.')


# Example usage:
# Assuming you have an active SQLAlchemy session named 'session'
# create_message(session, user_id=1, message_type='email', subject='New Notification', body='You have a new notification.')



def redirect_based_on_role(user):
    if user.has_role('Admin'):
        return redirect(url_for('routes.admin_page'))
    elif user.has_role('Authority'):
        return redirect(url_for('routes.authority_page'))
    elif user.has_role('Manager'):
        return redirect(url_for('routes.manager_page'))
    elif user.has_role('Employee'):
        return redirect(url_for('routes.employee_page'))
    elif user.has_role('Provider'):
        return redirect(url_for('routes.provider_page'))
    elif user.has_role('Guest'):
        return redirect(url_for('routes.guest_page'))
    else:
        return redirect(url_for('routes.guest_page'))



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
    from config.config import Config
    config_instance = Config()

    return config_instance.EXCEPT_FIELDS

def get_current_directory():
    from config.config import Config
    config_instance = Config()

    return config_instance.CURRENT_DIRECTORY



def get_parent_directory():
    return Path(__file__).resolve().parent.parent  # Adjust to get the project root


def reset_to_guest():
    from app.utils.utils import reset_current_user_to_guest
    from app import logout_user, redirect, url_for  # Import other necessary functions

    logout_user()
    reset_current_user_to_guest()
    flash('Current user reset to "Guest"', 'info')
    return redirect(url_for('index'))

def reset_current_user_to_guest():
    from app import user_manager, login_user
    from app.modules.userManager101 import TemporaryUser
    guest_user = user_manager.load_user_by_username("Guest")
    if guest_user is not None:
        login_user(guest_user)
    else:
        # If "Guest" user is not found, create a temporary user
        temporary_user = TemporaryUser(user_id=None)
        login_user(temporary_user)

    session['user_roles'] = ['Guest']

