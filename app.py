
# DEBUG LOGGING LOGGER TOOLBAR: see app_factory.py

# app.py (or run.py)
import traceback
import re
import requests
import stripe

import logging
from logging import FileHandler, Formatter
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_, and_, desc, func, not_, null, exists, extract, select

from sqlalchemy.orm import sessionmaker

from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from db import db
from flask import g, make_response
from flask import flash
import datetime
from dateutil import rrule
from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import Email, InputRequired, NumberRange

from flask_session import Session
from wtforms import SubmitField
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from userManager101 import UserManager
from workflow_manager import (add_transition_log, create_card,
                              get_model_statistics, create_deadline_card,
                              create_model_card, deadline_approaching)

from app_defs import get_user_roles, create_message, generate_menu_tree
from models.user import (Users, UserRoles, Event, Role, Container, Questionnaire, Question,
        QuestionnaireQuestions, PlanProducts,
        Answer, Company, Area, Subarea, AreaSubareas,
        QuestionnaireCompanies, CompanyUsers, Status, Lexic,
        Interval, Subject,
        AuditLog, Post, Ticket, StepQuestionnaire,
        Workflow, Step, BaseData, DataMapping, Container, WorkflowSteps, WorkflowBaseData,
         StepBaseData, Config, Product, Cart,
         Plan, Users, UserPlans, Subscription, # Adjust based on actual imports
         Questionnaire_psf, Response_psf)

# from master_password_reset import admin_reset_password, AdminResetPasswordForm

from forms.forms import (AddPlanToCartForm, SignupForm, UpdateAccountForm, TicketForm, ResponseForm, LoginForm, ForgotPasswordForm,
                         ResetPasswordForm101, RegistrationForm, EventForm,
                         QuestionnaireCompanyForm, CustomBaseDataForm,
        QuestionnaireQuestionForm, WorkflowStepForm, WorkflowBaseDataForm,
                         BaseDataWorkflowStepForm,
        UserRoleForm, CompanyUserForm, UserDocumentsForm, StepBaseDataInlineForm,
        create_dynamic_form, CustomFileLoaderForm,
        CustomSubjectAjaxLoader, BaseSurveyForm, AuditLogForm, PlanProductsForm,
                         UpdateCartItemForm, AddProductToCartForm, SubscriptionForm)

from flask_mail import Mail, Message
from flask_babel import lazy_gettext as _  # Import lazy_gettext and alias it as _

from app_factory import create_app, roles_required, subscription_required

from config.config import (get_current_intervals,
        generate_company_questionnaire_report_data, generate_area_subarea_report_data,
        generate_html_cards, get_session_workflows,
        generate_html_cards_progression_with_progress_bars111, generate_html_cards_progression_with_progress_bars_in_short,
        get_pd_report_from_base_data_wtq, get_areas,
        get_subareas, generate_company_user_report_data, generate_user_role_report_data,
        generate_questionnaire_question_report_data, generate_workflow_step_report_data,
        generate_workflow_document_report_data, generate_document_step_report_data, get_cet_time)

from mail_service import send_simple_message, send_simple_message333
from wtforms import Form

from utils.utils import get_current_directory
from wtforms import (SelectField)
from flask_login import login_required, LoginManager
from flask_login import login_user, current_user
from flask_cors import CORS
from modules.chart_service import ChartService

from modules.admin_routes import admin_bp

from flask import flash, current_app, get_flashed_messages
# from flask_admin.exceptions import ValidationError

from flask_bcrypt import Bcrypt
from flask import abort
from functools import wraps

from crud_blueprint import create_crud_blueprint

from menu_builder import MenuBuilder

from flask_bootstrap import Bootstrap

import datetime
from datetime import datetime, timedelta
from jinja2 import Undefined

from flask import session
from flask_admin import expose, expose_plugview
from flask_admin.actions import action  # Import the action decorator
from flask_admin.contrib.sqla import ModelView

from flask_admin.model.widgets import XEditableWidget
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from smtplib import SMTPAuthenticationError
from flask import send_file
from flask import render_template, redirect, url_for
from wtforms import StringField, FileField, MultipleFileField, SelectMultipleField, SearchField

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import base64
import io
from pathlib import Path
import json
import pdb
import pyotp
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask import request

from flask_admin import BaseView, expose
from flask import jsonify
from werkzeug.utils import secure_filename

# Example of using the function with ImmutableMultiDict
from werkzeug.datastructures import ImmutableMultiDict

from flask_login import login_user, logout_user, current_user
import os

from flask_caching import Cache
import geocoder

from opencage.geocoder import OpenCageGeocode

# for graphical representation of workflows
# Additional libraries for visualization (choose one)
# Option 1: Flask-Vis (lightweight)
#from flask_wtf import FlaskForm
#from wtforms import SelectField, SubmitField

# Option 2: Plotly (more powerful)
# import plotly.graph_objects as go

import plotly.graph_objects as go
from custom_encoder import CustomJSONEncoder
# Use the custom JSON encoder

from admin_views import create_admin_views  # Import the admin views module

import pycountry
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
from phonenumbers.phonenumberutil import NumberParseException, PhoneNumberType

from cachetools import TTLCache, cached

# OPENCAGE API KEY
# aad0f13ea1af46c6b89153e6b7bd7928

app = create_app()

# Setup Mail
mail = Mail(app)
print('mail server active')


app.json_encoder = CustomJSONEncoder
print('JSON decoder on')

#cache = Cache(app)
# Choose one geocoder based on your preference:
# geocoder = geocoder.geocoder  # Original implementation
geocoder = OpenCageGeocode('aad0f13ea1af46c6b89153e6b7bd7928')  # Using OpenCageGeocode
GEONAMES_USERNAME = 'amarad21'

cache = TTLCache(maxsize=100, ttl=86400)  # Adjust cache size and TTL as needed
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

print('geo-names on')
# Create a cache with a TTL of 600 seconds and a max size of 100 items

# Setup Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
print('limiter active')

# Setup CORS
CORS(app)
print('CORS active')

# Setup LoginManager
login_manager = LoginManager(app)

stripe.api_key = app.config['STRIPE_API_KEY']
stripe.publishable_key = app.config['STRIPE_PUBLISHABLE_KEY']

# Register the password reset route
# app.add_url_rule('/admin_reset_password', 'admin_reset_password', admin_reset_password, methods=['GET', 'POST'])
# print('url rule set')

@login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(int(user_id))
    if user:
        session['user_roles'] = [role.name for role in user.roles] if user.roles else []
    return user

def initialize_app(app):
    with app.app_context():

        try:
            if get_areas():
                app.config['AREAS'] = get_areas()

                for i in range(len(get_areas())):
                    if get_subareas(i):
                        app.config['SUBAREAS_' + str(i)] = get_subareas(i)

        except OperationalError:
            flash('Database connection failed. Please check your internet connection.', 'danger')

        intervals = get_current_intervals(db.session)
        app.config['CURRENT_INTERVALS'] = intervals
        return intervals

intervals = initialize_app(app)

# Initialize the admin views
admin_app1, admin_app2, admin_app3, admin_app4, admin_app10 = create_admin_views(app, intervals)
print('intervals', intervals)

@app.route('/set_session')
def set_session():
    session['key'] = 'value'
    return 'Session set'


@app.route('/get_session')
def get_session():
    value = session.get('key')
    return f'Session value: {value}'


def check_internet():
    url = "https://www.google.com"
    timeout = 10
    try:
        response = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False

@app.before_request
def before_request():
    try:
        if current_user.is_authenticated:
            session['session_workflows'] = get_session_workflows(db.session, current_user)
            # print('session w', session['session_workflows'])
            g.current_user = current_user
            session.permanent = True
            session.modified = True
    except Exception as e:
        logging.error(f"Error in before_request: {str(e)}")
        raise e
    pass


bcrypt = Bcrypt(app)
# Set the login view (replace 'login' with your actual login route)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'  # Specify the category for flash messages

# Use the userManager101 for authentication
user_manager = UserManager(db)
user_roles = []

# TODO check directory for the prod env in Render!
session_dir = get_current_directory() + '/static/files/'

if not os.path.exists(session_dir):
    os.makedirs(session_dir)

app.config['SESSION_FILE_DIR'] = session_dir
# app.config['SESSION_TYPE'] = 'filesystem'
# Initialize Flask-Session
Session(app)

bootstrap = Bootstrap(app)

# Serializer for generating tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# TODO - eliminati tutti i blueprint per i quali c'è Admin?
# pyobjc
with app.app_context():
    # db.create_all()

    #app.register_blueprint(admin_bp)

    app.register_blueprint(admin_bp, url_prefix='/admin')

    user_roles_blueprint = create_crud_blueprint(UserRoles, 'user_roles')
    app.register_blueprint(user_roles_blueprint, url_prefix='/model_user_roles')

    company_users_blueprint = create_crud_blueprint(CompanyUsers, 'company_users')
    app.register_blueprint(company_users_blueprint, url_prefix='/model_company_users')

    questionnaire_questions_blueprint = create_crud_blueprint(QuestionnaireQuestions, 'questionnaire_questions')
    app.register_blueprint(questionnaire_questions_blueprint, url_prefix='/model_questionnaire_questions')

    base_data_blueprint = create_crud_blueprint(BaseData, 'base_data')
    app.register_blueprint(base_data_blueprint, url_prefix='/model_base_data')

    workflow_base_data_blueprint = create_crud_blueprint(WorkflowBaseData, 'workflow_base_data')
    app.register_blueprint(workflow_base_data_blueprint, url_prefix='/model_workflow_base_data')

    step_base_data_blueprint = create_crud_blueprint(StepBaseData, 'step_base_data')
    app.register_blueprint(step_base_data_blueprint, url_prefix='/model_step_base_data')

    model_document = create_crud_blueprint('model_document', __name__)


# Load menu items from JSON file
json_file_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'menuStructure101.json')
# json_file_path = get_current_directory() + "/static/js/menuStructure101.json"
with open(Path(json_file_path), 'r') as file:
    main_menu_items = json.load(file)


# Create an instance of MenuBuilder
menu_builder = MenuBuilder(main_menu_items, ["Guest"])
parsed_menu_data = menu_builder.parse_menu_data(user_roles=["Guest"], is_authenticated=False, include_protected=False)
print('parsed_menu_data', parsed_menu_data)

def is_user_role(session, user_id, role_name):
    # Get user roles for the specified user ID
    user_roles = get_user_roles(session, user_id)
    # Check if the specified role name (in lowercase) is in the user's roles
    return role_name in user_roles



def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except SignatureExpired:
        return None  # valid token, but expired
    except:
        return None  # invalid token
    return email


# Function to get documents query based on user's role
def get_documents_query(session, current_user):
    query = session.query(BaseData).filter(BaseData.file_path != None).all()
    if current_user.is_authenticated:
        if current_user.has_role('Admin') or current_user.has_role('Authority'):
            return query
        elif current_user.has_role('Manager'):
            # Manager can only see records related to their company_users
            # Assuming you have a relationship named 'user_companies' between Users and CompanyUsers models
            subquery = session.query(CompanyUsers.company_id).filter(
                CompanyUsers.user_id == current_user.id
            ).subquery()
            query = query.filter(BaseData.company_id.in_(subquery))
        elif current_user.has_role('Employee'):
            # Employee can only see their own records
            query = query.filter(BaseData.user_id == current_user.id)
            return query

    # For other roles or anonymous users, return an empty query
    return query.filter(BaseData.id < 0)


def create_company_folder222(company_id, subfolder):
    try:
        base_path = '/path/to/company/folders'
        company_folder_path = os.path.join(base_path, str(company_id), str(subfolder))
        os.makedirs(company_folder_path, exist_ok=True)
        #logging.info(f'Created folder: {company_folder_path}')
    except Exception as e:
        #logging.error(f'Error creating company folder: {e}')
        #raise
        pass

def create_company_folder(company_id, subfolder):
    """
    Creates a folder for the given company_id in the specified directory.
    Args:
        company_id (int): The ID of the company.
    Returns:
        str: The path of the created folder or None if it already exists.
    """

    folder_path = None
    try:
        folder_name = f"company_id_{company_id}/{subfolder}"
        folder_path = os.path.join(app.config['COMPANY_FILES_DIR'], folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print('Folder created:', folder_path)

        else:
            print('Folder already exists')
            #return None  # Folder already exists

    except Exception as e:
        #logging.error(f'Error creating company folder: {e}')
        #raise
        pass

    if folder_path:
        print('return folder path', folder_path)
        return folder_path
    else:
        return None


def generate_password_reset_token(email):
    salt = app.config['SECURITY_PASSWORD_SALT']
    return serializer.dumps(email, salt=salt)


# TODO unused?
def verify_password_reset_token(token, expiration=1800):
    salt = app.config['SECURITY_PASSWORD_SALT']
    try:
        email = serializer.loads(token, salt=salt, max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None
    return email



# Define the custom Jinja2 filter
def list_intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

# Create a custom filter to replace Undefined with None
def replace_undefined(value):
    return None if value is Undefined else value


def next_is_valid(next_url):
    # Check if the provided next_url is a valid URL
    # This is a basic example; you might want to check against a list of allowed URLs
    pdb.set_trace()
    allowed_urls = ['index', 'protected']  # Add your allowed URLs here
    if next_url and next_url in allowed_urls:
        return True
    else:
        return False


# Define the menu_item_allowed function
def menu_item_allowed(menu_item, user_roles):
    # Your implementation here
    # Example: Check if the user has the required role to access the menu_item
    # WHEN the phrase on the right was present, the landing page was empty A.R. 15Feb2024
    return True #menu_item['allowed_roles'] and any(role in user_roles for role in menu_item['allowed_roles'])

def generate_route_and_menu(route, allowed_roles, template, include_protected=False, limited_menu=False):
    def decorator(func):
        @app.route(route)
        @wraps(func)
        def wrapper(*args, **kwargs):

            if callable(getattr(current_user, 'is_authenticated', None)):
                is_authenticated = current_user.is_authenticated()
            else:
                is_authenticated = current_user.is_authenticated

            username = current_user.username if current_user.is_authenticated else "Guest"
            user_roles = session.get('user_roles', ['Guest'])

            intersection = set(user_roles) & {"Employee", "Manager", "Authority", "Admin", "Provider"}

            allowed_roles = list(intersection) if intersection else ["Guest"]

            menu_builder_instance = MenuBuilder(main_menu_items, allowed_roles=allowed_roles)

            if limited_menu:
                menu_data = menu_builder_instance.parse_menu_data(user_roles=user_roles,
                                                                  is_authenticated=False, include_protected=False)
            else:
                menu_data = menu_builder_instance.parse_menu_data(user_roles=user_roles,
                                                                  is_authenticated=is_authenticated, include_protected=include_protected)

            buttons = []
            admin_url = url_for('open_admin.index')
            admin_2_url = url_for('open_admin_2.index')
            admin_3_url = url_for('open_admin_3.index')
            admin_4_url = url_for('open_admin_4.index')
            admin_10_url = url_for('open_admin_10.index')

            company_name = ' '
            if current_user:
                user_id = current_user.id if current_user.is_authenticated else 0
                company_name = db.session.query(Company.name) \
                    .join(CompanyUsers, CompanyUsers.company_id == Company.id) \
                    .filter(CompanyUsers.user_id == user_id) \
                    .first()
            else:
                pass

            if is_authenticated:
                unread_notices_count = Post.query.filter_by(user_id=current_user.id, marked_as_read=False).count()
            else:
                unread_notices_count = 0

            if is_authenticated:
                if 'Admin' in [role.name for role in current_user.roles]:
                    admin_tickets_count = Ticket.query.filter_by(status_id=2, marked_as_read=False).count()
                    open_tickets_count = 0
                else:
                    admin_tickets_count = 0
                    open_tickets_count = Ticket.query.filter_by(user_id=current_user.id, status_id=2, marked_as_read=False).count()
            else:
                admin_tickets_count = 0
                open_tickets_count = 0

            role_ids = []
            for role_name in user_roles:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    role_ids.append(role.id)

            try:
                containers = Container.query.filter(
                    Container.role_id.in_(role_ids)
                ).order_by(Container.container_order).all()
            except:
                containers = None

            company_id = session.get('company_id')
            card_data = get_cards(company_id)

            # Check cookies_accepted in the database
            cookies_accepted = 'true' if current_user.is_authenticated and current_user.cookies_accepted else 'false'
            show_cookie_banner = 'Admin' not in user_roles and cookies_accepted == 'false'

            #current_app.logger.debug(f"User Roles: {user_roles}")
            #current_app.logger.debug(f"Show Cookie Banner: {show_cookie_banner}")
            #current_app.logger.debug(f"Cookies Accepted: {cookies_accepted}")

            additional_data = {
                "username": username,
                "company_name": company_name,
                "is_authenticated": is_authenticated,
                "main_menu_items": menu_data,
                "admin_menu_data": None,
                "authority_menu_data": None,
                "manager_menu_data": None,
                "employee_menu_data": None,
                "guest_menu_data": None,
                "user_roles": user_roles,
                "allowed_roles": allowed_roles,
                "limited_menu": limited_menu,
                "buttons": buttons,
                "admin_url": admin_url,
                "admin_2_url": admin_2_url,
                "admin_3_url": admin_3_url,
                "admin_4_url": admin_4_url,
                "admin_10_url": admin_10_url,
                "left_menu_items": menu_data,
                "unread_notices_count": unread_notices_count,
                "admin_tickets_count": admin_tickets_count,
                "open_tickets_count": open_tickets_count,
                "containers": containers,
                "cards": card_data,
                "show_cookie_banner": show_cookie_banner,
            }

            return render_template(template, **additional_data)

        return wrapper

    return decorator


def redirect_based_on_role(user):
    if user.has_role('Admin'):
        return redirect(url_for('admin_page'))
    elif user.has_role('Authority'):
        return redirect(url_for('authority_page'))
    elif user.has_role('Manager'):
        return redirect(url_for('manager_page'))
    elif user.has_role('Employee'):
        return redirect(url_for('employee_page'))
    elif user.has_role('Provider'):
        return redirect(url_for('provider_page'))
    elif user.has_role('Guest'):
        return redirect(url_for('guest_page'))
    else:
        return redirect(url_for('guest_page'))



# TODO unused?
def generate_new_id(model):
    # Get the maximum ID from the database
    max_id = db.session.query(db.func.max(model.id)).scalar()
    # If there are no records in the table, start with ID 1
    if max_id is None:
        return 1
    else:
        # Otherwise, increment the maximum ID by one
        return max_id + 1


def get_cards(company_id):
  cards = []
  # Use SQLAlchemy to query the 'container' table
  containers = db.session.query(Container).filter_by(
      company_id=company_id, content_type='card'
  ).all()

  for container in containers:
    content = container.content

    # Check data type before decoding
    if isinstance(content, str):
      card_data = json.loads(content)
    elif isinstance(content, dict):
      card_data = content  # Already a dictionary
    else:
      # Handle unexpected data type (optional)
      # You can log a warning or raise an exception here
      print(f"Unexpected data type for container content: {type(content)}")
      continue  # Skip this container

    cards.append(card_data)

  return cards


def get_containers(company_id):
    containers = db.session.query(Container).filter_by(company_id=company_id).all()
    container_data = []

    for container in containers:
        container_info = {
            'content_type': container.content_type,
            'content': container.content
        }
        container_data.append(container_info)

    return container_data


def get_cards001(company_id):
    cards = []
    # Use SQLAlchemy to query the 'container' table
    containers = db.session.query(Container).filter_by(
        company_id=company_id
    ).all()

    for container in containers:
        content = container.content

        # Check data type before decoding
        if isinstance(content, str):
            card_data = json.loads(content)
        elif isinstance(content, dict):
            card_data = content  # Already a dictionary
        else:
            # Handle unexpected data type (optional)
            # You can log a warning or raise an exception here
            print(f"Unexpected data type for container content: {type(content)}")
            continue  # Skip this container

        # Include content_type in the card data
        card_data['content_type'] = container.content_type
        cards.append(card_data)

    return cards



class MoveDocumentForm(FlaskForm):
    next_step = SelectField('Next Step')
    submit = SubmitField('Move Document')

    def __init__(self, available_steps, current_step=None, **kwargs):
        super(MoveDocumentForm, self).__init__(**kwargs)
        self.next_step.choices = [(step.id, step.name) for step in available_steps]
        self.current_step = current_step  # Store for potential use in template

    def validate(self):
        if not self.next_step.data:
            return False
        return True


@app.errorhandler(SMTPAuthenticationError)
def handle_smtp_authentication_error(error):
    # Handle SMTP authentication errors gracefully
    return "SMTP Authentication Error: Failed to authenticate with the SMTP server.", 500


@app.errorhandler(OperationalError)
def handle_db_error(error):
   return render_template('db_error.html'), 500



@app.route('/forgot_password', methods=['GET', 'POST'])
@login_required
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        try:
            user = Users.query.filter_by(email=form.email.data).first()
            if user:
                user_email = form.email.data
                token = generate_password_reset_token(user_email)
                user.user_2fa_secret = token
                db.session.commit()
                # Send password reset email using Flask-Mail (example)
                msg = Message(sender="Auditors Digital Platform <info@firstauditors.org>",
                              recipients=[user.email])
                reset_url = url_for('reset_password', token=token, _external=True)
                msg.body = f'Click the link to reset your password: {reset_url}'

                mail.send(msg)

                # Convert LazyString to str before passing to flash
                flash(str(_('An email has been sent with instructions to reset your password.')), 'success')
            else:
                flash(str(_('No user found with that email address.')), 'danger')
            return redirect(url_for('forgot_password'))
        except Exception as e:
            flash(str(_('An error occurred while processing your request. Please try again later.')), 'danger')
            return render_template('access/forgot_password.html', form=form)
    return render_template('access/forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@login_required
def reset_password(token):
    user = Users.query.filter_by(user_2fa_secret=token).first()
    if not user:
        flash('The password reset token is invalid or expired.', 'warning')
        return redirect(url_for('login'))

    form = ResetPasswordForm101()  # Assuming you have a ResetPasswordForm for new password entry
    if form.validate_on_submit():
        user.set_password(form.password.data)  # Use a secure password hashing method
        user.user_2fa_secret = None  # Invalidate the token after reset
        db.session.commit()
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('access/reset_password.html', form=form, token=token)



@app.route("/send_email___")
@login_required
def send_email___():
    mail = Mail(app)
    msg = Message("Hello from ILM",
                  sender="amarad21@gmail.com",
                  recipients=["astridel.radulescu1@gmail.com"])
    msg.body = "This is a test email sent from my App using Postfix."
    mail.send(msg)
    return "Email sent successfully!"


@app.route("/send_email")
@login_required
def send_email():
    # Example usage
    api_key = "20cb76ced830ab536fa7cd718d1c1141-b02bcf9f-5936b742"
    domain =  "sandbox8fe87aee4b91456c9d17ffcb802d8b20.mailgun.org"
    sender = "Mailgun Sandbox <postmaster@sandbox8fe87aee4b91456c9d17ffcb802d8b20.mailgun.org>"
    recipient = "amarad21@gmail.com"
    subject = "Test MG Email"
    text = "This is a test email sent via Mailgun."

    # Call the function to send the email
    # send_simple_message(api_key, domain, sender, recipient, subject, text)
    send_simple_message333()
    # Set flash message
    flash('Mail sent successfully', 'success')
    return redirect(url_for('index'))  # Redirect to your home page


@app.route('/confirmation')
def confirmation_page():
    return redirect(url_for('login'))


@app.route('/access/login', methods=['GET', 'POST'])
@limiter.limit("200/day;96/hour;12/minute")
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == 'POST':
        # Verify CAPTCHA
        user_captcha = request.form['captcha']
        if 'captcha' in session and session['captcha'] == user_captcha:
            try:
                # CAPTCHA entered correctly
                username = form.username.data
                password = form.password.data
                user = user_manager.authenticate_user(username, password)
                if user:
                    # Log out any existing user and clear the session
                    logout_user()
                    session.clear()

                    if not current_user.is_authenticated:
                        login_user(user)
                        flash('Login Successful')
                        cet_time = get_cet_time()
                        try:
                            create_message(db.session, user_id=user.id, message_type='email', subject='Security check',
                                           body='È stato rilevato un nuovo accesso al tuo account il ' +
                                                cet_time.strftime('%Y-%m-%d') + '. Se eri tu, non devi fare nulla. ' +
                                                'In caso contrario, ti aiuteremo a proteggere il tuo account; ' +
                                                "non rispondere a questo messaggio, apri un ticket o contatta " +
                                                "l'amministratore del sistema.",
                                           sender='System', company_id=None,
                                           lifespan='one-off', allow_overwrite=True)
                        except Exception as e:
                            print('Error creating logon message:', e)

                        session['user_roles'] = [role.name for role in user.roles] if user.roles else []
                        session['user_id'] = user.id
                        session['username'] = username
                        session['email'] = user.email

                        try:
                            company_user = CompanyUsers.query.filter_by(user_id=user.id).first()
                            company_id = company_user.company_id if company_user else None
                            session['company_id'] = company_id
                        except Exception as e:
                            print('Error retrieving company ID:', e)
                            company_id = None

                        if company_id is not None and isinstance(company_id, int):
                            try:
                                subfolder = datetime.now().year
                            except Exception as e:
                                print('Error setting subfolder:', e)

                    # Redirect based on user roles
                    return redirect_based_on_role(user)
                else:
                    flash('Invalid username or password. Please try again.', 'error')
                    captcha_text, captcha_image = generate_captcha(300, 100, 5)
                    session['captcha'] = captcha_text
                    return render_template('access/login.html', form=form, captcha_image=captcha_image)
            except OperationalError as e:
                return handle_db_error(e)
        else:
            # CAPTCHA entered incorrectly
            flash('Incorrect CAPTCHA! Please try again.', 'error')
            captcha_text, captcha_image = generate_captcha(300, 100, 5)
            session['captcha'] = captcha_text
            return render_template('access/login.html', form=form, captcha_image=captcha_image)

    # Generate and render CAPTCHA image within the template
    captcha_text, captcha_image = generate_captcha(300, 100, 5)
    session['captcha'] = captcha_text
    return render_template('access/login.html', form=form, captcha_image=captcha_image)



@app.route('/left_menu', methods=['GET', 'POST'])
# TODO left_menu.html of home.html?
#@generate_route_and_menu('/home', allowed_roles=["Employee"], template='home/left_menu.html')
@generate_route_and_menu('/home', allowed_roles=["Employee"], template='home/home.html')
def left_menu():
    username = current_user.username if current_user.is_authenticated else "Guest"
    if callable(getattr(current_user, 'is_authenticated', None)):
        is_authenticated = current_user.is_authenticated()
    else:
        is_authenticated = current_user.is_authenticated

    user_roles = session.get('user_roles', [])
    allowed_roles = ["Employee", "Manager", "Authority", "Admin", "Provider"]

    # Fetch role IDs
    role_ids = []
    for role_name in user_roles:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            role_ids.append(role.id)

    # Fetch containers based on role IDs
    containers = []
    if role_ids:
        try:
            containers = Container.query.filter(
                Container.role_id.in_(role_ids)
            ).order_by(Container.page.desc()).all()

            # Iterate over the containers and print the 'container' field
            for container in containers:
                print('container:', container.page, container.content_type, container.content)
        except Exception as e:
            app.logger.error(f"Error fetching containers: {e}")
            containers = []

    # Check if the lists intersect
    intersection = set(user_roles) & set(allowed_roles)

    left_menu_items = []
    if intersection:
        left_menu_items = get_left_menu_items(list(intersection))

    # Check for unread notices
    unread_notices_count = 0
    if is_authenticated:
        unread_notices_count = Post.query.filter_by(user_id=current_user.id, marked_as_read=False).count()

    additional_data = {
        "username": username,
        "is_authenticated": is_authenticated,
        "user_roles": user_roles,
        "unread_notices_count": unread_notices_count,
        "main_menu_items": None,
        "admin_menu_data": None,
        "authority_menu_data": None,
        "manager_menu_data": None,
        "employee_menu_data": None,
        "guest_menu_data": None,
        "allowed_roles": allowed_roles,
        "limited_menu": None,  # Assuming limited_menu is defined elsewhere
        "left_menu_items": left_menu_items,
        "containers": containers,
    }

    return render_template('home/home.html', **additional_data)


@app.route('/')
@generate_route_and_menu('/', allowed_roles=["Guest"], template='home/home.html', include_protected=False, limited_menu=True)
def index():
    user_id = session.get('user_id')
    user_roles = session.get('user_roles', [])
    analytics = request.cookies.get('analytics', 'false')
    marketing = request.cookies.get('marketing', 'false')
    cookies_accepted = request.cookies.get('cookies_accepted', 'false')

    # Determine if the cookie banner should be shown
    show_cookie_banner = 'Admin' not in user_roles and cookies_accepted == 'false'

    # Create MenuBuilder with user roles
    menu_builder = MenuBuilder(main_menu_items, allowed_roles=user_roles)
    # Generate menu for the current user
    generated_menu = menu_builder.generate_menu(user_roles=user_roles, is_authenticated=True, include_protected=False)

    # Check if the user has events
    try:
        if user_id:
            events = Event.query.filter_by(user_id=user_id).count()
            has_events = events > 0
        else:
            has_events = False
    except Exception as e:
        app.logger.error(f"Error checking for events: {e}")
        has_events = False

    return render_template('home/home.html',
                           analytics=analytics, marketing=marketing,
                           generated_menu=generated_menu,
                           show_cookie_banner=show_cookie_banner,
                           has_events=has_events)



@app.route('/access/logout', methods=['GET'])
@login_required
def logout():


    # Clear the user roles from the session
    session.pop('user_roles', None)
    # Clear the user session
    session.clear()

    # Clear user-specific session data but preserve CAPTCHA and other necessary data

    '''user_specific_keys = ['user_id', 'username', 'user_roles']
    for key in user_specific_keys:
        session.pop(key, None)
        '''

    # Build 'Guest' menu
    guest_menu_builder = MenuBuilder(main_menu_items, allowed_roles=["Guest"])
    guest_menu_data = guest_menu_builder.parse_menu_data(user_roles=["Guest"],
                                                         is_authenticated=False, include_protected=False)
    # Render the home page with 'Guest' menu
    additional_data = {
        "username": "Guest",
        "is_authenticated": False,
        "main_menu_items": guest_menu_data,
        "admin_menu_data": None,
        "authority_menu_data": None,
        "manager_menu_data": None,
        "employee_menu_data": None,
        "guest_menu_data": None,
        "user_roles": ["Guest"],
        "allowed_roles": ["Guest"]
    }

    return render_template('access/logout.html', **additional_data)


@app.route('/show_cards')
@login_required
def show_cards():
  company_id = session['company_id']  # Access company ID from session
  #card_data = get_cards(company_id)
  containers_data = get_containers(company_id)

  # optional? Alternative to 'cards' above
  '''
  card_data = [
      {
          'title': 'Area 1',
          'stats': get_model_statistics(db.session, BaseData, {"area_id": 1}),  # Filter criteria as a dictionary
          'body': 'This is the body content for Card 1.',
          'card_class': 'bg-primary'  # Optional card class
      },
      {
          'title': 'Area 2',
          'stats': get_model_statistics(db.session, BaseData, {"area_id": 2}),  # Filter criteria as a di
          'footer': 'Footer for Card 2',
          # 'visibility': 'd-none'  # Initially hide this card
      },
      {
          'title': 'Area 3',
          'stats': get_model_statistics(db.session, BaseData, {"area_id": 3}),  # Filter criteria as a di
          'footer': 'Footer for Card 2',
          # 'visibility': 'd-none'  # Initially hide this card
      },
      {
          'title': 'Upcoming Deadline',
          'stats': get_model_statistics(db.session, BaseData, {"area_id": 3}),  # Filter criteria as a di
          'footer': 'Footer for Card 2',
          # 'visibility': 'd-none'  # Initially hide this card
      }
  ]
  '''

  return render_template('base_cards_template.html', containers=containers_data, create_card=create_card)


# TODO add Home and Back buttons
@app.route('/document_workflow_visualization_d3js')
@login_required
def workflow_visualization():
    return render_template('document_workflow_visualization_d3js.html')


@app.route('/custom_base_atti')
@login_required
def custom_base_atti_index():
    form = CustomFileLoaderForm()  # Instantiate your form object here
    return render_template('custom_file_loader.html', form=form)



@app.route('/user_documents_d3')
@login_required
def user_documents_d3():
    # Define colors
    LIGHT_GRAY = '#D3D3D3'
    LIGHT_BLUE = '#5588FF'

    # Execute the query to get documents
    documents_query = get_documents_query(db.session, current_user)

    # Convert the query result to a list if needed
    documents = documents_query.all() if hasattr(documents_query, 'all') else [documents_query]

    documents_data = []

    for document_list in documents:
        for document_obj in document_list:
            # Check if user exists for the document
            user_last_name = document_obj.user.last_name if document_obj.user else None

            # document_data = {"id": document_obj.id, "current_step": None, "steps": []}

            # path here
            file_name, file_extension = extract_filename_and_extension(document_obj.file_path)

            document_data = {
                "id": document_obj.id,
                "file_path": file_name,  # document_obj.file_path,  # Assuming this is how file_path is accessed
                "user_last_name": user_last_name,
                "current_step": None,
                "steps": []
            }

            # Check if workflow_base_data exists within the BaseData object
            if document_obj.workflow_base_data:
                workflow_base_data = document_obj.workflow_base_data

                for data in workflow_base_data:
                    workflow_id = data.workflow_id
                    workflow_steps = WorkflowSteps.query.filter_by(workflow_id=workflow_id).all()
                    step_ids = [step.step_id for step in workflow_steps]
                    steps = Step.query.filter(Step.id.in_(step_ids)).all()

                    # Append each step to the list of steps within document_data
                    document_data["steps"].extend(
                        [{"id": step.id, "name": step.name, "color": LIGHT_GRAY} for step in steps])

                # Fetch current step information from StepBaseData table
                current_step_data = StepBaseData.query.filter_by(base_data_id=document_obj.id).first()
                if current_step_data:
                    current_step_id = current_step_data.step_id
                    current_step = Step.query.get(current_step_id)
                    if current_step:
                        document_data["current_step"] = current_step.name

            # Assign colors to steps
            for step_data in document_data["steps"]:
                if document_data["current_step"] and step_data["name"] == document_data["current_step"]:
                    step_data["color"] = LIGHT_BLUE

            # --- Modified section to remove duplicate steps ---
            unique_steps = []
            seen_ids = set()
            for step_data in document_data["steps"]:
                if step_data["id"] not in seen_ids:
                    unique_steps.append(step_data)
                    seen_ids.add(step_data["id"])
            document_data["steps"] = unique_steps

            documents_data.append(document_data)
    return jsonify(documents_data)



@app.route('/custom_action/', methods=['GET', 'POST'])
@login_required
def custom_action():
    if request.method == 'POST':
        # Process the form data and perform complex operations
        perform_complex_operations(request.form)
        # Redirect back to the original view or any other desired page

        # Redirect the user to the Flask-Admin list view for YourModel
        # return redirect(url_for('admin.index_view', view_name='atti_data_view'))
        # Redirect the user back to the previous page
        #return redirect(request.referrer)

        # Redirect the user back to the Flask-Admin atti_data_view
        return redirect('open_admin/atti_data_view')

    else:
        # Render the data input template
        return render_template('set_dws_rich_data.html')


@app.route('/user_documents')
@login_required
def user_documents():
    form = UserDocumentsForm()

    try:
        documents_query = get_documents_query(db.session, current_user)

        # Execute the query and check if it returns a single object or a list
        if hasattr(documents_query, 'all'):  # Check if it's a query object
            documents = documents_query.all()
        else:
            documents = [documents_query]  # Assuming it's a single object

        if documents:
            # Access the first element of the nested list (assuming the first document)
            document_data = documents[0][0]  # This is the actual BaseData object

            # Check if workflow_base_data exists within the BaseData object
            if document_data.workflow_base_data:
                workflow_base_data = document_data.workflow_base_data

                # Process workflow data for the first WorkflowBaseData object
                data = workflow_base_data[0]
                workflow_id = data.workflow_id
                workflow_steps = WorkflowSteps.query.filter_by(workflow_id=workflow_id).all()
                step_ids = [step.step_id for step in workflow_steps]
                steps = Step.query.filter(Step.id.in_(step_ids)).all()

                # Create Plotly graph
                fig = go.Figure(data=[go.Scatter(x=[node.id for node in steps], y=[0 for node in steps], text=[node.name for node in steps])])

                if fig:
                    fig.update_layout(title="Document Workflow", xaxis_title="Steps", yaxis_title="", showlegend=False)

                    plot_config = fig.to_image(format='png')
                    plot_html = fig.to_html(full_html=False)

                    return render_template('workflow/document_workflow.html', user_id=current_user.id,  # Assuming user_id is available
                                           document=document_data, plot_config=plot_config, plot_html=plot_html, form=form)
                else:
                    pass

            else:
                #app.logger.info("No workflow data found for the first document")
                #return render_template('workflow/no_workflow_data.html')  # Handle case where no workflow data exists
                pass

        else:
            #app.logger.info("No documents found for the current user")
            #return render_template('workflow/no_documents.html')  # Handle the case where no documents exist
            pass

    except Exception as e:
        #app.logger.error("An error occurred: %s", e)
        return render_template('error.html', error_message=str(e))  # Render a generic error page



# Document workflow view route (using Plotly)
@app.route('/documents/<int:company_id>/<int:base_data_id>/<int:workflow_id>', methods=['GET', 'POST'])
@login_required
def document_workflow(company_id, base_data_id, workflow_id):
    document = BaseData.query.filter_by(company_id=company_id, id=base_data_id, workflow_id=workflow_id).first()

    # ... (logic to retrieve document and steps)

    # Prepare data for visualization
    nodes = [{"id": step.id, "label": step.name} for step in WorkflowSteps.filter_by(workflow_id=workflow_id).first().steps]
    edges = []  # Fill with connections between steps based on workflow logic

    # Create Plotly graph (adjust layout and styling as desired)
    fig = go.Figure(data=[go.Graph(x=[node["id"] for node in nodes],
                                    y=[0 for node in nodes],  # Adjust y-coordinates if needed
                                    text=[node["label"] for node in nodes],
                                    edges=edges)])
    fig.update_layout(
        title="Document Workflow",
        xaxis_title="Steps",
        yaxis_title="",  # Remove y-axis if not used
        showlegend=False
    )

    # ... (rest of the route logic)
    return render_template('workflow/document_workflow.html', document=document, figure=fig)


# TODO unused?
class CustomStepQuestionnaireForm(Form):
    inline_form = None


@app.route('/file-upload', methods=['POST'])
@login_required
def upload_file():
    # Check if file is uploaded
    if 'file_path' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    # Get the uploaded file
    uploaded_file = request.files['file_path']

    # Check if filename is empty (user didn't select a file)
    if uploaded_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Secure the filename (avoid potential security issues)
    filename = secure_filename(uploaded_file.filename)

    # Save the uploaded file (replace with your desired location and logic)
    # uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Process the uploaded file content (replace with your logic)
    # file_content = uploaded_file.read()
    # # Analyze file content and generate dynamic controls based on logic
    # dynamic_controls_html = generate_controls(file_content)  # hypothetical function

    # Currently, no dynamic controls are generated based on the file
    dynamic_controls_html = ""

    return jsonify({'controls': dynamic_controls_html})


@app.route('/load_workflow_controls', methods=['GET'])
@login_required
def load_workflow_controls():
    # Query your database for workflows
    workflows = Workflow.query.all()

    # Generate the HTML for the dropdown
    dropdown_html = '<select name="workflow">'
    for workflow in workflows:
       dropdown_html += f'<option value="{workflow.id}">{workflow.name}</option>'
    dropdown_html += '</select>'

    # Current date for the date picker default
    current_date = datetime.date.today().strftime('%Y-%m-%d')

    # HTML for the date picker
    date_picker_html = f'<input type="date" name="deadline_date" value="{current_date}">'

    # HTML for the checkbox
    checkbox_html = '<input type="checkbox" name="auto_transition"> Auto Transition'

    # Combine all controls HTML
    controls_html = f"{dropdown_html}<br>{date_picker_html}<br>{checkbox_html}"

    return jsonify({'controls': controls_html})

# TOD how to eliminate relationship fields in the Question and workflow CREATE templates?


@app.route('/open_admin_app_4')
@login_required
@roles_required('Admin')
# Define the index route
def open_admin_app_4():
    user_id = current_user.id
    return redirect(url_for('open_admin_4.index'))


'''

@login_required
@roles_required('Admin')
@app.route('/master_reset_password')
def master_reset_password():
    return redirect(url_for('admin_reset_password'))
'''



@app.route('/open_admin_app_1')
@login_required
@subscription_required
def open_admin_app_1():
    user_id = current_user.id

    company_row = db.session.query(Company.name) \
        .join(CompanyUsers, CompanyUsers.company_id == Company.id) \
        .filter(CompanyUsers.user_id == user_id) \
        .first()

    company_name = company_row[0] if company_row else None  # Extracting the name attribute

    user_subscription_plan = current_user.subscription_plan
    user_subscription_status = current_user.subscription_status

    template = "Area di controllo 1 - Atti, iniziative, documenti"
    placeholder_value = company_name if company_name else None
    formatted_string = template.format(placeholder_value) if placeholder_value else template

    admin_app1.name = formatted_string

    return redirect(url_for('open_admin.index'))



@app.route('/open_admin_app_2')
@login_required
@subscription_required
def open_admin_app_2():
    user_id = current_user.id
    company_row = db.session.query(Company.name) \
        .join(CompanyUsers, CompanyUsers.company_id == Company.id) \
        .filter(CompanyUsers.user_id == user_id) \
        .first()

    company_name = company_row[0] if company_row else None  # Extracting the name attribute
    template = "Area di controllo 2 - Elementi quantitativi"
    placeholder_value = company_name if company_name else None
    formatted_string = template.format(placeholder_value) if placeholder_value else template
    admin_app2.name = formatted_string

    return redirect(url_for('open_admin_2.index'))


# Define the index route
@app.route('/open_admin_app_3')
@login_required
def open_admin_app_3():
    user_id = current_user.id
    company_row = db.session.query(Company.name) \
        .join(CompanyUsers, CompanyUsers.company_id == Company.id) \
        .filter(CompanyUsers.user_id == user_id) \
        .first()

    company_name = company_row[0] if company_row else None  # Extracting the name attribute

    template = "Area di controllo 3 - Contratti e documenti"
    placeholder_value = company_name
    formatted_string = template.format(placeholder_value) if placeholder_value else template
    admin_app3.name = formatted_string

    return redirect(url_for('open_admin_3.index'))


@app.route('/open_admin_app_10')
@login_required
@roles_required('Admin', 'Manager', 'Employee')
# Define the index route
def open_admin_app_10():
    user_id = current_user.id
    company_row = db.session.query(Company.name) \
        .join(CompanyUsers, CompanyUsers.company_id == Company.id) \
        .filter(CompanyUsers.user_id == user_id) \
        .first()

    company_name = company_row[0] if company_row else None  # Extracting the name attribute

    template = "Surveys & Questionnaires"
    placeholder_value = company_name
    formatted_string = template.format(placeholder_value) if placeholder_value else template
    admin_app10.name = formatted_string

    return redirect(url_for('open_admin_10.index'))


# TODO: ***** inserire come action: move one step forward!


@app.route('/detach_documents_from_workflow_step', methods=['POST'])
@login_required
def detach_documents_from_workflow_step():
    try:
        # Get the selected document IDs from the request body
        data = request.get_json()
        ids_list = data.get('ids')
        workflow_id = data.get('workflow_id')

        '''
        print('one step forward ->')
        # Assuming you have a step_base_data object
        step_base_data = StepBaseData.query.first()  # Get the first one as an example
        # Move the document one step forward
        s t e p _ b a s e _data.step_away(1)
        print('-> one step forward>')
        # Change the status of the document
        #step_base_data.status_change('Submitted')
        '''

        step_id = data.get('step_id')

        # Delete the StepBaseData records corresponding to the selected document IDs
        query = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids_list),
                                           StepBaseData.workflow_id == workflow_id,
                                           StepBaseData.step_id == step_id)
        deleted_count = query.delete()

        # Commit the changes
        db.session.commit()

        # Prepare success message
        success_message = f'{deleted_count} record(s) deleted.'

        return jsonify({'success_message': success_message, 'error_message': None})

    except Exception as e:
        # Handle exceptions
        db.session.rollback()
        error_message = f"Error deleting documents linked to workflow and phases: {str(e)}"
        return jsonify({'success_message': None, 'error_message': error_message})


@app.route('/plans_with_products')
@login_required
def plans_with_products():
    plans = Plan.query.all()
    plans_with_products = []

    for plan in plans:
        associated_products = PlanProducts.query.filter_by(plan_id=plan.id).all()
        products_info = []

        for ap in associated_products:
            product = Product.query.get(ap.product_id)
            products_info.append({
                'product_id': product.id,
                'name': product.name,
                'description': product.description
            })

        plans_with_products.append({
            'plan_id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'products': products_info
        })

    return render_template('plans_with_products.html', plans_with_products=plans_with_products)


@app.route('/attach_documents_to_workflow_step', methods=['POST'])
@login_required
def attach_documents_to_workflow_step():
    #try:
    # Get the selected Workflow and Step IDs from the form data
    workflow_id = request.form.get('workflow')
    step_id = request.form.get('step')
    ids_str = request.form.get('ids')

    ids_list = ids_str.split(',')

    records_added = 0
    # Check if the StepBaseData record already exists for the selected Workflow and Step
    for id in ids_list:
        existing_record = StepBaseData.query.filter_by(base_data_id=id, workflow_id=workflow_id, step_id=step_id).first()
        if not existing_record:
            # If the StepBaseData record doesn't exist, create a new one

            # new_record = StepBaseData(base_data_id=id, workflow_id=workflow_id, step_id=step_id, hidden_data='default_value')
            new_record = StepBaseData(
                base_data_id=id,
                workflow_id=workflow_id,
                step_id=step_id,
                hidden_data='default_value',
                start_recall=0,
                deadline_recall=0,
                end_recall=0,
                recall_unit='...',
                open_action='new',
                auto_move=False # Include start_recall in the initialization
            )

            db.session.add(new_record)
            records_added += 1

    # Commit the changes
    db.session.commit()

    if records_added == 0:
        success_message = 'No records added - existing records found.'
    else:
        success_message = f'{records_added} record(s) created successfully'

    # Pass the messages to the template
    return jsonify({'success_message': success_message, 'error_message': None})




@app.route('/manage_plan_products', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_plan_products():
    form = PlanProductsForm()
    message = None

    try:
        # Populate choices for plans and products
        form.plan_id.choices = [(plan.id, plan.name) for plan in Plan.query.all()]
        form.product_id.choices = [(product.id, product.name) for product in Product.query.all()]

        if request.method == 'POST':
            if form.validate_on_submit():
                if form.cancel.data:
                    # Handle cancel button
                    return redirect(url_for('index'))
                elif form.add.data:
                    # Handle add button
                    plan_id = form.plan_id.data
                    product_id = form.product_id.data

                    # Check if the plan-product association already exists
                    existing_plan_product = PlanProducts.query.filter_by(plan_id=plan_id, product_id=product_id).first()

                    if existing_plan_product:
                        message = "Association plan-product already exists."
                    else:
                        # Add logic to associate the plan with the selected product
                        new_association = PlanProducts(plan_id=plan_id, product_id=product_id)
                        db.session.add(new_association)
                        db.session.commit()
                        # Set a success message
                        message = "Association plan-product added successfully."

                elif form.delete.data:
                    # Handle delete button
                    plan_id = form.plan_id.data
                    product_id = form.product_id.data

                    # Find and delete the plan-product association
                    association_to_delete = PlanProducts.query.filter_by(plan_id=plan_id, product_id=product_id).first()

                    if association_to_delete:
                        db.session.delete(association_to_delete)
                        db.session.commit()
                        message = "Association plan-product deleted successfully."
                    else:
                        message = "Association plan-product not found."
            else:
                message = "Form validation failed. Please check your input."
    except Exception as e:
        # Log the error and set a message for the template
        app.logger.error(f"Error managing plan products: {e}")
        message = "An unexpected error occurred. Please try again later."

    # Handle GET request or any case where form validation failed
    return render_template('manage_plan_products.html', form=form, message=message)


@app.route('/action_manage_dws_deadline', methods=['POST'])
@login_required
def manage_deadline():
    # Parse the list of IDs
    ids_str = request.form.get('ids')
    ids_list = ids_str.split(',')

    # Get the data set in the form
    new_date = request.form.get('deadline_date')  # Example: Accessing form field named 'deadline'
    new_date_obj = datetime.strptime(new_date, '%Y-%m-%d')  # Assuming format 'YYYY-MM-DD'

    # Parse recall_deadline and recall_unit values
    recall_deadline = request.form.get('deadline_alert')
    recall_unit = request.form.get('time_unit')
    # Check if the checkbox is checked
    automatic_transition = request.form.get('automatic_transition')
    if automatic_transition == 'on':
        automatic_transition = True
    else:
        automatic_transition = False

    # Handle the form submission and update the deadline accordingly
    records_updated = 0
    if new_date_obj:
        for id in ids_list:
            existing_record = StepBaseData.query.get(id)

            if existing_record:
                existing_record.deadline_date = new_date_obj
                existing_record.deadline_recall = recall_deadline
                existing_record.recall_unit = recall_unit
                existing_record.auto_move = automatic_transition
                db.session.commit()
                records_updated += 1

        # Example: Return success or error response
        return jsonify({'success_message': f'Deadline set successfully for {records_updated} records.'})
    else:
        return jsonify({'error_message': 'Failed to set deadline.'}), 400


# TODO unused?
def execute_workflow(workflow_id):
    workflow = session.query(Workflow).get(workflow_id)
    if workflow.status == 'active':
       for step in workflow.steps.order_by(Step.order):
           if step.action == 'create':
                # create a new record in the target model
                pass
           elif step.action == 'update':
                # update an existing record in the target model
                pass
           elif step.action == 'delete':
                # delete an existing record in the target model
                pass
           else:
                # handle other actions
                pass
       workflow.status = 'completed'
       session.commit()
    else:
       # handle inactive or completed workflows
       pass


# Route to get subject names based on subject IDs
@app.route('/get_subject_names/<int:subject_id>')
@login_required
def get_subject_name(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()

    if subject:
        return jsonify({'name': subject.name})
    else:
        return jsonify({'name': 'Not Found'})

@app.route('/handle_dynamic_url/<endpoint>')
@login_required
def handle_dynamic_url(endpoint):
    # You can handle the dynamic URL here, for example, redirect to a default view
    return redirect(url_for('index'))


# Register the context processor
@app.context_processor
def utility_processor():
    return dict(menu_item_allowed=menu_item_allowed)


def custom_roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated() and any(role in [role.name for role in current_user.roles] for role in roles):
                return fn(*args, **kwargs)
            else:
                abort(403)  # Forbidden
        return wrapper
    return decorator


@app.route('/admin')
@generate_route_and_menu('/admin', allowed_roles=["Admin"], template='home/home.html', include_protected=True)
def admin_page():
    print("***ADMIN PAGE***")
    pass


@app.route('/authority')
@generate_route_and_menu('/authority', allowed_roles=["Authority"], template='home/home.html')
def authority_page():
    pass


@app.route('/manager')
@generate_route_and_menu('/manager', allowed_roles=["Manager"], template='home/home.html')
def manager_page():
    pass


@app.route('/employee')
@generate_route_and_menu('/home', allowed_roles=["Employee"], template='home/home.html')
def employee_page():

    #session['user_roles'] = [role.name for role in users.roles] if users.roles else []
    left_menu = get_left_menu_items(["Employee"])
    try:
        additional_data = {
            'left_menu_items': left_menu,
            'user_roles': session.get('user_roles', []),
            'allowed_roles': ["Manager", "Employee", "Admin"],
        }
        return render_template('home/home.html', **additional_data)

    except Exception as e:
        #app.logger.error(str(e))
        return render_template('error.html')


def get_left_menu_items(role):
    # Load the left menu structure from the JSON file
    json_file_path = get_current_directory() + '/static/js/left_menu_structure.json'
    with open(Path(json_file_path), 'r') as file:
        left_menu_items = json.load(file)

    # Create a MenuBuilder instance for the "Guest" role
    left_menu_builder = MenuBuilder(left_menu_items, role)
    left_menu_items = left_menu_builder.parse_menu_data(user_roles=role, is_authenticated=True, include_protected=True)
    # Pass the "Guest" menu data to the template
    return left_menu_items


def get_left_menu_items_limited(role, area):
    # Load the left menu structure from the JSON file

    if area:
        json_file_path = get_current_directory() + '/static/js/left_menu_structure_' + area + '.json'
        with open(Path(json_file_path), 'r') as file:
            left_menu_items = json.load(file)
    else:
        json_file_path = get_current_directory() + '/static/js/left_menu_structure.json'
        with open(Path(json_file_path), 'r') as file:
            left_menu_items = json.load(file)

    # Create a MenuBuilder instance for the "Guest" role
    left_menu_builder = MenuBuilder(left_menu_items, role)
    left_menu_items = left_menu_builder.parse_menu_data(user_roles=role, is_authenticated=True, include_protected=True)
    return left_menu_items


@app.route('/guest')
@generate_route_and_menu('/index', allowed_roles=["Guest"], template='home/home.html', include_protected=False)
def guest_page():

    # app.logger.debug("Home route accessed")
    is_authenticated = current_user.is_autenticated
    # Render the home page with 'Guest' menu
    additional_data = {
        "username": "Guest",
        "is_authenticated": is_authenticated,
        "main_menu_items": guest_menu_data,
        "admin_menu_data": guest_menu_data,
        "authority_menu_data": guest_menu_data,
        "manager_menu_data": guest_menu_data,
        "employee_menu_data": guest_menu_data,
        "guest_menu_data": guest_menu_data,
        "user_roles": ["Guest"],
        "allowed_roles": ["Guest"]
    }
    pass


# TODO Verifica esistenza stesso username o stessa mail (già presente?)
# TODO Usare user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one()
# TODO oppure users = db.session.execute(db.select(User).order_by(Users.username)).scalars()


import pycountry

# Get all countries
# countries = [{'name': country.name, 'code': country.alpha_2} for country in pycountry.countries]

# Get subdivisions for a specific country
# country_code = 'US'  # Example for the United States
# subdivisions = [{'name': subdivision.name} for subdivision in pycountry.subdivisions.get(country_code)]

import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code

'''
@app.route('/invalidate_cache')
def invalidate_cache():
    cache.delete('/countries')
    cache.delete('/regions')
    cache.delete('/provinces')
    cache.delete('/cities')
    cache.delete('/zip_codes')
    cache.delete('/streets')
    cache.delete('/phone_prefixes')
    return jsonify({'message': 'Cache invalidated'})
'''

# Get phone prefixes
# prefixes = [{'country': region_code_for_country_code(country_code), 'prefix': f'+{country_code}'}
#             for country_code in phonenumbers.SUPPORTED_REGIONS]



# Function to fetch phone prefixes
# @cached(cache)
def fetch_phone_prefixes():
    prefixes = []
    for country in pycountry.countries:
        try:
            example_number = phonenumbers.example_number_for_type(country.alpha_2, PhoneNumberType.MOBILE)
            phone_prefix = f"+{example_number.country_code}" if example_number else None
            if phone_prefix:
                prefixes.append({'prefix': phone_prefix, 'country': country.name})
        except (NumberParseException, AttributeError, KeyError) as e:
            print(f"Error with country {country.name}: {e}")
            continue  # Skip countries that cause exceptions
    return prefixes

@app.route('/phone_prefixes', methods=['GET'])
def get_phone_prefixes():
    return jsonify(fetch_phone_prefixes())

# Function to fetch regions
@app.route('/regions')
# @cached(cache)
def get_regions():
    country_code = request.args.get('country_code')
    if not country_code:
        return jsonify({'error': 'Country code is required'}), 400

    url = f'http://api.geonames.org/countryInfoJSON?country={country_code}&username=amarad21'
    response = requests.get(url)
    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    country_geoname_id = data['geonames'][0].get('geonameId', None)
    if not country_geoname_id:
        return jsonify({'error': 'Could not find geonameId for the country'}), 500

    url = f'http://api.geonames.org/childrenJSON?geonameId={country_geoname_id}&username=amarad21'
    response = requests.get(url)
    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    regions = [{'code': region.get('geonameId', 'No geonameId'), 'name': region.get('name', 'No name')} for region in data.get('geonames', [])]
    return jsonify(regions)


@app.route('/provinces')
def get_provinces():
    region_code = request.args.get('region_code')
    if not region_code:
        return jsonify({'error': 'Region code is required'}), 400

    url = f'http://api.geonames.org/childrenJSON?geonameId={region_code}&username=amarad21'
    response = requests.get(url)
    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    provinces = [{'code': province.get('geonameId', 'No geonameId'), 'name': province.get('name', 'No name')} for province in data.get('geonames', [])]
    return jsonify(provinces)

@app.route('/cities')
def get_cities():
    province_code = request.args.get('province_code')
    if not province_code:
        return jsonify({'error': 'Province code is required'}), 400

    url = f'http://api.geonames.org/childrenJSON?geonameId={province_code}&username=amarad21'
    response = requests.get(url)
    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    cities = [{'name': city.get('name', 'No name'), 'geonameId': city.get('geonameId', 'No geonameId')} for city in data.get('geonames', [])]
    return jsonify(cities)

@app.route('/streets')
def get_streets():
    city_id = request.args.get('city_id')
    if not city_id:
        return jsonify({'error': 'City ID is required'}), 400

    url = f'http://api.geonames.org/streetSearchJSON?geonameId={city_id}&maxRows=1000&username=amarad21'
    response = requests.get(url)
    data = response.json()
    streets = [{'name': place.get('street', 'Undefined')} for place in data.get('streets', [])]
    return jsonify(streets)

@app.route('/zip_codes')
def get_zip_codes():
    city_name = request.args.get('city_name')
    if not city_name:
        return jsonify({'error': 'City name is required'}), 400

    url = f'http://api.geonames.org/postalCodeSearchJSON?placename={city_name}&maxRows=1000&username=amarad21'
    response = requests.get(url)
    data = response.json()
    zip_codes = [{'postalCode': place.get('postalCode', 'Undefined')} for place in data.get('postalCodes', [])]
    return jsonify(zip_codes)


@app.route('/countries', methods=['GET'])
def get_countries():
    countries = [{'alpha2Code': country.alpha_2, 'name': country.name} for country in pycountry.countries]
    return jsonify(countries)


@app.route('/access/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = Users(
                username=form.username.data,
                email=form.email.data,
                title=form.title.data,
                first_name=form.first_name.data,
                mid_name=form.mid_name.data,
                last_name=form.last_name.data,
                country=form.country.data,
                region=form.region.data,
                province=form.province.data,
                zip_code=form.zip_code.data,
                city=form.city.data,
                street=form.street.data,
                address=form.address.data,
                address1=form.address1.data,
                phone_prefix=form.phone_prefix.data,
                mobile_phone=form.mobile_phone.data,
                work_phone=form.work_phone.data,
                tax_code=form.tax_code.data,
                terms_accepted=form.terms_accepted.data,
                created_on=datetime.utcnow(),
                updated_on=datetime.utcnow(),
                user_2fa_secret=pyotp.random_base32()  # Generate the 2FA secret
            )

            new_user.set_password(form.password.data)
            try:
                db.session.add(new_user)

                db.session.commit()

                flash('Your account has been created! You can now log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error committing to the database: {e}")
                logging.error(traceback.format_exc())
                flash('An error occurred during signup', 'error')
        else:
            flash('Form validation failed. Please check your input.', 'error')

    return render_template('access/signup.html', title='Sign Up', form=form)


@app.route('/terms-of-use')
@login_required
def terms_of_use():
    return render_template('home/terms_of_use.html')



@app.route('/create_step', methods=['GET', 'POST'])
@login_required
# TODO this is a test route. TB cancelled
@roles_required('Admin')
def create_step():
    if request.method == 'POST':
        new_step = Step(
            name="Test Step",
            description="This is a test step",
            action="Test Action",
            order=1
        )
        try:
            db.session.add(new_step)
            db.session.commit()
            return "Step created successfully!"
        except Exception as e:
            db.session.rollback()
            # logging.error(f'Error creating step: {e}')
            return f"Error: {e}"
    return '''
        <form method="post">
            <input type="submit" value="Create Step">
        </form>
    '''

@app.route('/home/contact/contact_us',  methods=['GET', 'POST'])
def contact_us():
    return render_template('home/contact.html')


@app.route('/home/privacy_policy',  methods=['GET', 'POST'])
def privacy_policy():
    return render_template('home/privacy_policy.html')


@app.route('/test_carousel',  methods=['GET', 'POST'])
def test_carousel():
    return render_template('carousel/wrapper_test.html')


@app.route('/home/mission',  methods=['GET', 'POST'])
def mission():
    return render_template('home/mission.html')

@app.route('/home/products',  methods=['GET', 'POST'])
def products():
    return render_template('home/services.html')

@app.route('/home/history',  methods=['GET', 'POST'])
def history():
    return render_template('home/history.html')


@app.route('/workflow/control_areas/area_1', methods=['GET', 'POST'])
@login_required
def area_1():
    if request.method == 'GET' and current_user.is_authenticated:
        # Assuming user_id is available, adjust the query accordingly
        user_id = current_user.id  # Implement your user authentication logic

        # Assuming there is a relationship between CompanyUser and Table
        specific_table = Table.query.filter_by(user_id=user_id, name='Tabella 1').all()

        return render_template('workflow/control_areas/area_1.html', specific_table=specific_table)

    elif request.method == 'POST':
        action = request.form.get('action')
        if action == 'edit_row':
            # Implement logic to edit a row
            row_id = request.form.get('row_id')
            # Assuming other form fields like 'new_value' are present in the form
            new_column1 = request.form.get('column1')

            # Implement your edit logic here, for example, updating the database
            # UpdateTable is a placeholder for your actual database update logic
            #update_result = UpdateTable(row_id, new_column1)

            #if update_result:
            return jsonify({"message": "Row edited successfully"})
            #else:
            #    return jsonify({"message": "Error editing row"})

        elif action == 'add_row':
            # Implement logic to add a new row
            # Access form data using request.form
            # Implement add logic here
            # Access form data using request.form
            new_row_data = {
                'column1': request.form.get('column1'),
                'column2': request.form.get('column2'),
                # Add other columns as needed
            }

            # Create a new row and add it to the database
            new_row = Table(user_id=current_user.id, name='Tabella 1', **new_row_data)
            db.session.add(new_row)
            db.session.commit()

            return jsonify({"message": "Row added successfully"})

        elif action == 'remove_row':
            # Implement logic to remove a row
            #row_id = request.form.get('row_id')
            # Implement remove logic here
            return jsonify({"message": "Row removed successfully"})

        elif action == 'commit_data':
            # Implement logic to commit data
            # Access form data using request.form
            # Implement commit logic here
            return jsonify({"message": "Data committed successfully"})

        return jsonify({"message": "Card content saved successfully"})

    # Handle other HTTP methods if needed
    return jsonify({"message": "Invalid request method"})


# ... (Other imports and setup)
# F l a s k  route to handle saving card content
@app.route('/save_card', methods=['POST'])
@login_required
def save_card():

    # Get data from the request
    card_id = request.form.get('card_id')
    edited_content = request.form.get('edited_content')
    # Implement logic to save the edited content to the database
    # For example, you can use SQLAlchemy to update the corresponding record
    try:
        table_row = Table.query.get(card_id)
        table_row.column2 = edited_content  # Adjust this based on your actual column names
        db.session.commit()
        return jsonify({"message": "Card content saved successfully"})
    except Exception as e:
        return jsonify({"message": "Error saving card content"})

@app.route('/workflow/control_areas/area_3',  methods=['GET', 'POST'])
@login_required
def area_3():
    # Assuming user_id is available, adjust the query accordingly
    user_id = current_user.id  # Implement your user authentication logic
    specific_table = Table.query.filter_by(user_id=user_id, name='Tabella 3').first()
    # Replace 1 with the actual ID of the table you want to display
    tables = Table.query.filter_by(user_id=user_id, name='Tabella 3').all()

    return render_template('workflow/control_areas/area_3.html',
                           specific_table=specific_table, tables=tables)


@app.route('/update_cell', methods=['POST'])
@login_required
def update_cell():
    if request.method == 'POST':
        column = request.form.get('column')
        row_id = request.form.get('id')
        new_value = request.form.get('new_value')

        # Perform the necessary database update using SQLAlchemy or your preferred ORM
        # Example SQLAlchemy assuming you have a 'Table' model
        table_row = Table.query.get(row_id)
        if table_row:
            setattr(table_row, column, new_value)
            db.session.commit()

        return jsonify({'success': True, 'message': 'Cell updated successfully'})

    # Handle other HTTP methods if needed
    return jsonify({'success': False, 'message': 'Invalid request method'})


@app.route('/home/aboutus_1',  methods=['GET', 'POST'])
def aboutus_1():
    return render_template('home/aboutus_1.html')



@app.route('/dashboard/company')
@login_required
def dashboard_company():
    # Your view logic goes here
    return render_template('dashboard/company.html')


@app.route('/overview_statistics_1')
@login_required
@roles_required('Admin')
def overview_statistics_1():
    user_id = current_user.id  # Implement your user authentication logic
    if not user_id:
        user_id = request.args.get('user_id')  # Assuming you retrieve user_id from the request

    # get deadline approaching events

    card_data = [
        {
            'title': 'Area 1',
            'stats': get_model_statistics(db.session, BaseData, {"area_id": 1}),  # Filter criteria as a dictionary
            'body': 'This is the body content for Card 1.',
            'card_class': 'bg-primary'  # Optional card class
        },
        {
            'title': 'Area 2',
            'stats': get_model_statistics(db.session, BaseData, {"area_id": 2}),  # Filter criteria as a di
            'footer': 'Footer for Card 2',
            #'visibility': 'd-none'  # Initially hide this card
        },
        {
            'title': 'Area 3',
            'stats': get_model_statistics(db.session, BaseData, {"area_id": 3}),  # Filter criteria as a di
            'footer': 'Footer for Card 2',
            #'visibility': 'd-none'  # Initially hide this card
        },
        {
            'title': 'Upcoming Deadline',
            'stats': get_model_statistics(db.session, BaseData, {"area_id": 3}),  # Filter criteria as a di
            'footer': 'Footer for Card 2',
            # 'visibility': 'd-none'  # Initially hide this card
        }
    ]

    return render_template('base_cards_template.html', containers=card_data, create_card=create_card)

@app.route('/deadlines_1')
@login_required
def deadlines_1():
    user_id = current_user.id  # Implement your user authentication logic
    if not user_id:
        user_id = request.args.get('user_id')  # Assuming you retrieve user_id from the request

    # get deadline approaching events
    cards_data = deadline_approaching(db.session)

    # Prepare data for each card
    cards = []
    for card_data in cards_data:
        if not isinstance(card_data, dict):
            raise ValueError("Each card_data object must be a dictionary.")

        # Generate HTML for the current card_data
        card_html = create_deadline_card(card_data)

        # Append card data to the list
        cards.append({'html': card_html, 'id': card_data['id'], 'deadline_before': card_data['deadline_before']})

    return render_template('base_cards_deadlines_template.html', cards=cards)


@app.route('/dashboard_company_audit')
@login_required
def dashboard_company_audit():

    session = db.session  # Create a new database session object
    engine = db.engine  # Get the engine object from SQLAlchemy
    # Your view logic goes here
    # Perform the SQL query to get information for each company
    """
    Generates cards for companies with data in BaseData, including company name, data count, and a new metric.

    Args:
        session: SQLAlchemy session object.

    Returns:
        A list of company cards, where each card is a dictionary containing:
            company_id: The company ID.
            company_name: The company name.
            count: The total number of records for the company.
            new_metric: The number of records grouped by fi0, interval_id, area_id, subarea_id.
    """

    sorted_values = get_pd_report_from_base_data_wtq(engine)
    # Example usage
    # Get all companies from the database
    all_companies = Company.query.all()
    html_cards = generate_html_cards(sorted_values, all_companies)

    # Write HTML code to a file
    with open('report_cards1.html', 'w') as f:
        f.write(html_cards)

    return render_template('admin_cards.html', html_cards=html_cards, user_roles=user_roles)


# Define the route for handling card clicks
@app.route('/handle_card_click')
@login_required
def handle_card_click():
    card_id = request.args.get('id')
    # Handle the card click action here, if needed
    return redirect(url_for('open_admin', card_id=card_id))


''' 
System setup, admin: Company->User(s)
'''

@app.route('/dashboard_setup_companies_users')
@login_required
@roles_required('Admin')
def dashboard_setup_companies_users():
    # Assuming you have access to the session object
    '''
    with app.app_context():
        bind_key = 'db1'  # Use the bind key corresponding to the desired database
        options = {'url': str(db.engine.url)}  # Your options dictionary
        # Create the SQLAlchemy engine using db object
        engine = db._make_engine(bind_key, options, app)
        # Usage example here:
        Session = sessionmaker(bind=engine)
        session = Session()  # Create a session object
    '''

    # Generate HTML report
    report_data = generate_company_user_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="User-Company Relationship Report", columns=["Company", "User", "Last Name"], rows=report_data)


''' 
System setup, admin: User->Role(s)
'''

@app.route('/dashboard_setup_user_roles')
@login_required
@roles_required('Admin')
def dashboard_setup_user_roles():

    # Generate HTML report
    report_data = generate_user_role_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="User-Role Relationship Report", columns=["User", "Last Name", "Role"], rows=report_data)


''' 
System setup, admin: Questionnaire->Question(s)
'''

@app.route('/dashboard_setup_questionnaire_questions')
@login_required
@roles_required('Admin')
def dashboard_setup_questionnaire_questions():
    # Assuming you have access to the session object
    # Generate HTML report
    report_data = generate_questionnaire_question_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="Questionnaire Structure", columns=["Questionnaire id", "Name", "Question"], rows=report_data)


''' 
System setup, admin: Company - > Questionnaire(s)
'''
@app.route('/generate_setup_company_questionnaire')
@login_required
def generate_setup_company_questionnaire():
    # Generate HTML report
    report_data = generate_company_questionnaire_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="Questionnaires and Companies", columns=["Company", "Questionnaire name", "Questionnaire id"], rows=report_data)

#@login_required

@app.route('/dashboard_setup_workflow_steps')
@login_required
@roles_required('Admin')
def dashboard_setup_workflow_steps():
    # Generate HTML report
    report_data = generate_workflow_step_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="Workflows and Steps", columns=["Workflow id", "Workflow name", "Step id", "Step name"], rows=report_data)

'''
report of workflow of documents
'''
#@login_required
@app.route('/dashboard_setup_workflow_base_data')
@login_required
@roles_required('Admin')
def dashboard_setup_workflow_base_data():

    # Generate HTML report
    report_data_raw = generate_workflow_document_report_data(db.session)
    report_data = []
    for data in report_data_raw:
        file_name, file_extension = extract_filename_and_extension(data[0])
        report_data.append([f"{file_name}{file_extension}", data[1]])

    # Render the template with the report data
    return render_template('generic_report.html', title="Workflow of Documents", columns=["Document", "Workflow"], rows=report_data)

'''
Route to manage trilateral link document/workflow/step
'''

@app.route('/dashboard_setup_step_base_data')
@login_required
@roles_required('Admin')
def dashboard_setup_step_base_data():
    # Generate HTML report

    report_data = []
    report_data_raw = generate_document_step_report_data(db.session)
    columns = ["Document id", "Document name", "Area", "Subarea", "Company",
               "Workflow id",
               "Step", "Step name", "Start", "Deadline", "Completion", "Auto"]
    for data in report_data_raw:
        # Find the index of the column containing "file_path"
        file_path_index = columns.index(
            "Document name")  # Replace "your_column_names_list" with the actual list of column names
        file_name, file_extension = extract_filename_and_extension(data[file_path_index])
        # Replace the value at the file_path_index with 'some_value'
        data[file_path_index] = f"{file_name}{file_extension}"

        report_data.append(data)
        # Print the modified data
        #print(data)

    # Render the template with the report data
    return render_template('generic_report.html',
                           title="Status of Documents Workflow",
                           columns=columns,
                           rows=report_data)

''' 
System setup, admin: Area->Subareas
'''

@app.route('/dashboard_setup_area_subareas')
@login_required
@roles_required('Admin')
def dashboard_setup_area_subareas():
    # Generate HTML report
    report_data = generate_area_subarea_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="Control Areas and Subareas", columns=["Area", "Subarea", "Data Type"], rows=report_data)

@app.route('/dashboard_company_audit_progression')
@login_required
def dashboard_company_audit_progression():

    session = db.session  # Create a new database session object
    engine = db.engine  # Get the engine object from SQLAlchemy
    # TODO time_scope vs time_qualifier here below?
    time_scope = 'current'

    def filter_records_by_time_qualifier(records, time_qualifier):
        filtered_records = []
        for record in records:
            if record['time_qualifier'] == time_qualifier:
                filtered_records.append(record)
        return filtered_records

    print('step 0', time_scope)

    sorted_values_raw = get_pd_report_from_base_data_wtq(engine)
    print('step 1', sorted_values_raw)
    # Example usage to filter 'current' records
    sorted_values = filter_records_by_time_qualifier(sorted_values_raw, time_scope)

    if is_user_role(session, current_user.id, 'Admin'):
        print('admin')
        company_id = None  # will list all companies' cards
    else:
        company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        print('non-admin', company_id)

    print('values', sorted_values)
    html_cards = generate_html_cards_progression_with_progress_bars_in_short(sorted_values, time_scope or {}, session,
                                                                       company_id)

    # Write HTML code to a file
    with open('report_cards1.html', 'w') as f:
        f.write(html_cards)

    return render_template('admin_cards_progression.html', html_cards=html_cards, user_roles=user_roles)


@app.route('/company_overview_current')
@login_required
def company_overview_current():
    session = db.session  # Create a new database session object
    engine = db.engine  # Get the engine object from SQLAlchemy
    time_scope = 'current'

    def filter_records_by_time_qualifier(records, time_qualifier):
        filtered_records = []
        for record in records:
            if record['time_qualifier'] == time_qualifier:
                filtered_records.append(record)
        return filtered_records

    try:
        sorted_values_raw = get_pd_report_from_base_data_wtq(engine)

        # Check if no data was found
        if not sorted_values_raw:
            return render_template('no_records.html')

        # Example usage to filter 'current' records
        sorted_values = filter_records_by_time_qualifier(sorted_values_raw, time_scope)

        if is_user_role(session, current_user.id, 'Admin'):
            company_id = None  # will list all companies' cards
        else:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id

        html_cards = generate_html_cards_progression_with_progress_bars111(
            sorted_values, time_scope or {}, db.session, company_id
        )

        # Write HTML code to a file
        with open('report_cards1.html', 'w') as f:
            f.write(html_cards)

        return render_template('admin_cards_progression.html', html_cards=html_cards, user_roles=user_roles)

    except Exception as e:
        # logging.error(f'Error in company_overview_current: {e}')
        return render_template('error.html', error_message=str(e)), 500



@app.route('/company_overview_current222')
@login_required
def company_overview_current222():
    # logging.basicConfig(level=logging.DEBUG)

    session = db.session  # Create a new database session object
    engine = db.engine  # Get the engine object from SQLAlchemy
    time_scope = 'current'

    try:
        def filter_records_by_time_qualifier(records, time_qualifier):
            filtered_records = []
            for record in records:
                if record['time_qualifier'] == time_qualifier:
                    filtered_records.append(record)
            return filtered_records

        print('step 0 - filtered records', filtered_records, time_scope)
        sorted_values_raw = get_pd_report_from_base_data_wtq(engine)

        print('step 1 - raw records', sorted_values_raw, time_scope)
        # Example usage to filter 'current' records
        sorted_values = filter_records_by_time_qualifier(sorted_values_raw, time_scope)

        print('step 2 - sorted records', sorted_values, time_scope)
        if is_user_role(session, current_user.id, 'Admin'):
            company_id = None  # will list all companies' cards
        else:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id

        html_cards = generate_html_cards_progression_with_progress_bars111(
            sorted_values, time_scope or {}, db.session, company_id
        )

        # Write HTML code to a file
        with open('report_cards1.html', 'w') as f:
            f.write(html_cards)

        return render_template('admin_cards_progression.html', html_cards=html_cards, user_roles=user_roles)

    except Exception as e:
        # logging.error(f'Error in company_overview_current: {e}')
        return render_template('error.html', error_message=str(e)), 500


@app.route('/company_overview_historical')
@login_required
def company_overview_historical():
    session = db.session  # Create a new database session object
    engine = db.engine  # Get the engine object from SQLAlchemy
    time_scope = 'past'

    def filter_records_by_time_qualifier(records, time_qualifier):
        filtered_records = []
        for record in records:
            if record['time_qualifier'] == time_qualifier:
                filtered_records.append(record)
        return filtered_records

    sorted_values_raw = get_pd_report_from_base_data_wtq(engine)

    # Check if no data was found
    if not sorted_values_raw:
        return render_template('no_records.html')

    # Example usage to filter 'current' records
    sorted_values = filter_records_by_time_qualifier(sorted_values_raw, time_scope)

    if is_user_role(db.session, current_user.id, 'Admin'):
        company_id = None  # will list all companies' cards
    else:
        company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id

    html_cards = generate_html_cards_progression_with_progress_bars111(sorted_values, time_scope, db.session, company_id)

    # Write HTML code to a file
    with open('report_cards1.html', 'w') as f:
        f.write(html_cards)

    return render_template('admin_cards_progression.html', html_cards=html_cards, user_roles=user_roles)



@app.route('/company_overview_historical222')
@login_required
def company_overview_historical222():
    try:
        session = db.session  # Create a new database session object
        engine = db.engine  # Get the engine object from SQLAlchemy
        time_scope = 'past'

        def filter_records_by_time_qualifier(records, time_qualifier):
            filtered_records = []
            for record in records:
                if record['time_qualifier'] == time_qualifier:
                    filtered_records.append(record)
            return filtered_records

        # Initialize filtered_records to avoid referencing before assignment
        filtered_records = []

        print('step 0 - filtered records', filtered_records, time_scope)

        sorted_values_raw = get_pd_report_from_base_data_wtq(engine)
        print('step 1 - sorted values raw', sorted_values_raw)

        # Example usage to filter 'current' records
        sorted_values = filter_records_by_time_qualifier(sorted_values_raw, time_scope)
        print('step 2 - sorted values', sorted_values)

        if is_user_role(db.session, current_user.id, 'Admin'):
            company_id = None  # will list all companies' cards
        else:
            company_user = CompanyUsers.query.filter_by(user_id=current_user.id).first()
            if company_user:
                company_id = company_user.company_id
            else:
                company_id = None
            print('step 3 - company id', company_id)

        html_cards = generate_html_cards_progression_with_progress_bars111(sorted_values, time_scope, db.session, company_id)
        print('step 4 - html cards generated')

        # Write HTML code to a file
        with open('report_cards1.html', 'w') as f:
            f.write(html_cards)

        return render_template('admin_cards_progression.html', html_cards=html_cards, user_roles=user_roles)

    except Exception as e:
        logging.error(f"Error in company_overview_historical: {e}")
        return str(e), 500


@app.route('/control_area_1')
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def control_area_1():
    # Get the current route from the request object
    current_route = request.url_rule
    user_roles = session.get('user_roles', [])

    if 'current_app' not in globals():
        return render_template('404.html'), 404  # Ensure you have a 404.html template

    # Your view logic goes here
    current_route_url = current_app.url_for('control_area_1')

    if "area_1" in current_route_url:
        left_menu_items = get_left_menu_items_limited(user_roles, 'area_1')
        # Render the template using the current route information and left menu items
        return render_template('control_area_1.html',
                               current_route=current_route, left_menu_items=left_menu_items, current_app=current_app)

    # If the condition is not met, you should still return a response
    return render_template('control_area_1.html',
                           current_route=current_route, left_menu_items=None)

@app.route('/control_area_2')
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def control_area_2():
    # Get the current route from the request object
    current_route = request.url_rule
    user_roles = session.get('user_roles', [])

    if 'current_app' not in globals():
        return render_template('404.html'), 404  # Ensure you have a 404.html template

    # Your view logic goes here
    current_route_url = current_app.url_for('control_area_2')

    if "area_2" in current_route_url:
        left_menu_items = get_left_menu_items_limited(user_roles, 'area_2')

        # Render the template using the current route information and left menu items
        return render_template('control_area_2.html',
                               current_route=current_route, left_menu_items=left_menu_items)

    # If the condition is not met, you should still return a response
    return render_template('control_area_2.html',
                           current_route=current_route, current_app=current_app)

@app.route('/control_area_3')
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def control_area_3():
    # Get the current route from the request object
    current_route = request.url_rule
    user_roles = session.get('user_roles', [])

    if 'current_app' not in globals():
        return render_template('404.html'), 404  # Ensure you have a 404.html template

    # Your view logic goes here
    current_route_url = current_app.url_for('control_area_3')

    if "area_3" in current_route_url:
        left_menu_items = get_left_menu_items_limited(user_roles, 'area_3')

        # Render the template using the current route information and left menu items
        return render_template('control_area_3.html',
                               current_route=current_route, left_menu_items=left_menu_items)

    # If the condition is not met, you should still return a response
    return render_template('control_area_3.html',
                           current_route=current_route_url, current_app=current_app)


@app.route('/home/site_map', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def site_map():
    # ... (your existing code)

    # Load and read the content of menuStructure.json
    with open(json_file_path, 'r') as file:
        menu_structure = json.load(file)

    # Generate the menu tree
    menu_tree = generate_menu_tree(menu_structure)

    # Pass the menu_tree to the template
    return render_template('home/site_map.html', menu_tree=menu_tree)


def generate_captcha(width, height, length):
    characters = "&%?ABCDEFGHJKLMNPRSTUVWXYZ2345679"
    captcha_text = ''.join(random.choice(characters) for _ in range(length))

    image = Image.new('RGB', (width, height), color=(255, 255, 255))

    # Define the path to the font file within the static/fonts directory
    font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'Geneve.ttf')

    # Load the font using the relative path
    font = ImageFont.truetype(font_path, size=40)

    # Apply random rotation and distortion to each character
    for i, char in enumerate(captcha_text):
        char_image = Image.new('RGBA', (50, 50), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((10, 10), char, (0, 0, 0), font=font)
        char_image = char_image.rotate(random.randint(-30, 30), expand=True)

        # Apply random distortion
        distorted_image = Image.new('RGBA', char_image.size)
        for x in range(char_image.width):
            for y in range(char_image.height):
                src_x = int(x + random.choice([-2, -1, 1, 2]))
                src_y = int(y + random.choice([-2, -1, 1, 2]))
                if 0 <= src_x < char_image.width and 0 <= src_y < char_image.height:
                    distorted_image.putpixel((x, y), char_image.getpixel((src_x, src_y)))

        image.paste(distorted_image, (i * 40 + 10, 10), distorted_image)

    image = image.filter(ImageFilter.GaussianBlur(radius=1))

    # Save image data to a BytesIO buffer
    image_buffer = io.BytesIO()
    image.save(image_buffer, format='PNG')
    image_data = base64.b64encode(image_buffer.getvalue()).decode('utf-8')

    return captcha_text, image_data


@app.route('/clear_flashed_messages', methods=['POST'])
def clear_flashed_messages():
    messages = get_flashed_messages(True)  # Clear flashed messages without retrieving them
    return jsonify({"message": "Flashed messages cleared successfully"})


@app.route('/manage_user_roles', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_user_roles():
    form = UserRoleForm()
    message = None

    # Populate choices for users and roles
    form.user.choices = [(user.id, user.username) for user in Users.query.all()]
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.cancel.data:
                # Handle cancel button
                return redirect(url_for('index'))
            elif form.add.data:
                # Handle add button
                user_id = form.user.data
                role_id = form.role.data

                # Check if the user-role association already exists
                existing_user_role = UserRoles.query.filter_by(user_id=user_id, role_id=role_id).first()

                if existing_user_role:
                    message = "User role already exists."
                else:
                    # Add logic to associate the user with the selected role
                    new_user_role = UserRoles(user_id=user_id, role_id=role_id)
                    db.session.add(new_user_role)
                    db.session.commit()
                    # Set a success message
                    message = "User role added successfully."

            elif form.delete.data:
                # Handle delete button
                user_id = form.user.data
                role_id = form.role.data

                # Find and delete the user-role association
                user_role_to_delete = UserRoles.query.filter_by(user_id=user_id, role_id=role_id).first()

                if user_role_to_delete:
                    db.session.delete(user_role_to_delete)
                    db.session.commit()
                    message = "User role deleted successfully."
                else:
                    message = "User role not found."
        else:
            message = "Form validation failed. Please check your input."

    # Handle GET request or any case where form validation failed
    return render_template('manage_user_roles.html', form=form, message=message)


@app.route('/manage_workflow_steps', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def manage_workflow_steps():
    form = WorkflowStepForm()
    message = None

    # Populate choices for workflows and steps
    form.workflow.choices = [(workflow.id, workflow.name) for workflow in Workflow.query.all()]
    form.step.choices = [(step.id, step.name) for step in Step.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.cancel.data:
                # Handle cancel button
                return redirect(url_for('index'))
            elif form.add.data:
                # Handle add button
                workflow_id = form.workflow.data
                step_id = form.step.data

                # Check if the workflow-step association already exists
                existing_workflow_step = WorkflowSteps.query.filter_by(workflow_id=workflow_id, step_id=step_id).first()

                if existing_workflow_step:
                    message = "Workflow step already exists."
                else:
                    # Add logic to associate the workflow to the selected step
                    new_workflow_step = WorkflowSteps(workflow_id=workflow_id, step_id=step_id)
                    db.session.add(new_workflow_step)
                    db.session.commit()
                    # Set a success message
                    message = "Workflow step added successfully."

            elif form.delete.data:
                # Handle delete button
                workflow_id = form.workflow.data
                step_id = form.step.data

                # Find and delete the wkf-step association
                workflow_step_to_delete = WorkflowSteps.query.filter_by(workflow_id=workflow_id, step_id=step_id).first()

                if workflow_step_to_delete:
                    db.session.delete(workflow_step_to_delete)
                    db.session.commit()
                    message = "Workflow step deleted successfully."
                else:
                    message = "Workflow step not found."
        else:
            message = "Form validation failed. Please check your input."

    # Handle GET request or any case where form validation failed
    return render_template('manage_workflow_steps.html', form=form, message=message)



@app.route('/manage_workflow_base_data', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')  # Example roles
def manage_workflow_base_data():
    form = WorkflowBaseDataForm()
    message = None

    # Populate choices for workflows and steps
    form.workflow.choices = [(workflow.id, workflow.name) for workflow in Workflow.query.all()]
    form.base_data.choices = [(base_data.id, base_data.file_path) for base_data in
                              BaseData.query.filter(BaseData.file_path.isnot(None)).all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.cancel.data:
                # Handle cancel button
                return redirect(url_for('index'))
            elif form.add.data:
                # Handle add button
                workflow_id = form.workflow.data
                base_data_id = form.base_data.data

                # Get the selected workflow name
                selected_workflow = Workflow.query.get(workflow_id)
                workflow_name = selected_workflow.name

                # Check if the workflow-base_data association already exists
                existing_workflow_base_data = WorkflowBaseData.query.filter_by(workflow_id=workflow_id, base_data_id=base_data_id).first()

                if existing_workflow_base_data:
                    message = f"Document link to <{workflow_name}> already exists."
                else:
                    # Add logic to associate the workflow to the selected base_data
                    new_workflow_base_data = WorkflowBaseData(workflow_id=workflow_id, base_data_id=base_data_id)
                    db.session.add(new_workflow_base_data)
                    db.session.commit()
                    # Set a success message
                    message = f"Document linked to the <{workflow_name}> workflow."

            elif form.delete.data:
                # Handle delete button
                workflow_id = form.workflow.data
                base_data_id = form.base_data.data

                # Get the selected workflow name
                selected_workflow = Workflow.query.get(workflow_id)
                workflow_name = selected_workflow.name

                # Find and delete the workflow-base_data association
                workflow_base_data_to_delete = WorkflowBaseData.query.filter_by(workflow_id=workflow_id, base_data_id=base_data_id).first()

                if workflow_base_data_to_delete:
                    db.session.delete(workflow_base_data_to_delete)
                    db.session.commit()
                    message = f"Document link to <{workflow_name}> deleted successfully."
                else:
                    message = "Workflow-document link not found."
        else:
            message = "Form validation failed. Please check your input."

    # Handle GET request or any case where form validation failed
    return render_template('manage_workflow_base_data.html', form=form, message=message)



def extract_filename_and_extension(file_path):
    if file_path is None:
        return None, None  # Return None for both filename and extension if file_path is None

    # Convert file_path to string if it's not already
    if isinstance(file_path, int):
        file_path_str = str(file_path)
    else:
        file_path_str = file_path

    file_name_with_extension = os.path.basename(file_path_str)

    file_name, file_extension = os.path.splitext(file_name_with_extension)
    return file_name, file_extension


'''
trilateral relationship route (workflow-step_base_data)
'''
@app.route('/add_records_bws', methods=['GET', 'POST'])
def add_records_bws():
    form = BaseDataWorkflowStepForm()
    message = "No records added."
    i = 0
    # Retrieve JSON data sent from the client-side
    forms_data = request.json.get('forms_data', [])

    for form_data in forms_data:
        # Parse the form data
        parsed_data = parse_form_data_bws(form_data)

        # Extract values from the parsed data
        base_data_id = parsed_data.get('base_data')
        workflow_id = parsed_data.get('workflow')
        step_id = parsed_data.get('step')
        auto_move_id = parsed_data.get('auto_move')
        hidden_data = parsed_data.get('hidden_data', '')  # Handle potential missing value
        auto_move_value = parsed_data.get('auto_move', '')
        if isinstance(auto_move_value, dict) or auto_move_value == '':
            auto_move = False
        else:
            auto_move = True if auto_move_value == 'y' else False

        # Check if any key ends with '-id'
        if any(key.endswith('-id') for key in parsed_data):
            continue  # Skip this iteration if any key ends with '-id'

        # Check if the record already exists
        existing_record = StepBaseData.query.filter_by(
            base_data_id=base_data_id,
            workflow_id=workflow_id,
            step_id=step_id
        ).first()

        if existing_record:
            print('Record already exists for base_data_id:', base_data_id,
                  ', workflow_id:', workflow_id,
                  ', step_id:', step_id)
        else:
            # Create a new record if essential values are present
            if base_data_id and workflow_id and step_id:
                new_record = StepBaseData(
                    base_data_id=base_data_id,
                    workflow_id=workflow_id,
                    step_id=step_id,
                    status_id=1,
                    hidden_data=hidden_data,
                    auto_move=auto_move,
                    start_date=datetime.now(),
                    deadline_date = None

                )

                if auto_move:
                    new_record.deadline_date = datetime.now() + timedelta(days=90)

                try:
                    i += 1
                    db.session.add(new_record)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    print('IntegrityError: Duplicate record detected for base_data_id:',
                          base_data_id, ', workflow_id:', workflow_id, ', step_id:', step_id)
            else:
                null_keys = [key for key, value in parsed_data.items() if value == 'n.a.']

    if i > 0:
        return jsonify({'message': f'{i} records added successfully.'}), 200
    else:
        return jsonify({'message': 'Request processed successfully but no changes were made.'}), 200


def parse_form_data_bws(form_data):
    parsed_data = {}

    for key, value in form_data.items():
        if 'id' not in key:
            match = re.match(r'(.*)-(\d+)$', key)
            if match:
                base_key, number = match.groups()
                parsed_data[f'{base_key}'] = value
            else:
                parsed_data[key] = value

    return parsed_data


@app.route('/delete_records_bws', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def delete_records_bws():
    # Retrieve JSON data sent from the client-side
    forms_data = request.json.get('forms_data', [])

    records_deleted = 0

    for form_data in forms_data:
        # Parse the form data
        parsed_data = parse_form_data_bws(form_data)

        # Extract values from the parsed data
        base_data_id = parsed_data.get('base_data')
        workflow_id = parsed_data.get('workflow')
        step_id = parsed_data.get('step')

        # Check if the record exists
        existing_record = StepBaseData.query.filter_by(
            base_data_id=base_data_id,
            workflow_id=workflow_id,
            step_id=step_id
        ).first()

        if existing_record:
            # Delete the record if it exists
            db.session.delete(existing_record)
            db.session.commit()
            print('Record deleted for base_data_id:', base_data_id,
                  ', workflow_id:', workflow_id,
                  ', step_id:', step_id)
            records_deleted += 1
        else:
            print('Record not found for base_data_id:', base_data_id,
                  ', workflow_id:', workflow_id,
                  ', step_id:', step_id)

    if records_deleted > 0:
        return jsonify({'message': f'{records_deleted} record(s) deleted successfully.'}), 200
    else:
        return jsonify({'message': 'No records deleted.'}), 200


''' 
Trilateral entry form route - SERVER SIDE I, Jsonify combos
Complex (involves trilateral relationship table)
'''
@app.route('/get_steps', methods=['GET'])
def get_steps():
    workflow_id = request.args.get('workflow_id')

    # Query the WorkflowBaseData model to get workflow IDs associated with the selected base_data_id
    workflow_step = WorkflowSteps.query.filter_by(workflow_id=workflow_id).all()

    # Extract the workflow IDs from the query result
    step_ids = [wb.step_id for wb in workflow_step]

    # Query the Workflow model to get details of workflows based on the extracted workflow IDs
    steps = Step.query.filter(Step.id.in_(step_ids)).all()

    # Prepare the list of workflows to be sent as a JSON response
    step_list = [{'id': w.id, 'name': w.name} for w in steps]

    return jsonify(steps=step_list)


@app.route('/get_workflows', methods=['GET'])
def get_workflows():
    base_data_id = request.args.get('base_data_id')

    # Query the WorkflowBaseData model to get workflow IDs associated with the selected base_data_id
    workflow_base_data = WorkflowBaseData.query.filter_by(base_data_id=base_data_id).all()

    # Extract the workflow IDs from the query result
    workflow_ids = [wb.workflow_id for wb in workflow_base_data]

    # Query the Workflow model to get details of workflows based on the extracted workflow IDs
    workflows = Workflow.query.filter(Workflow.id.in_(workflow_ids)).all()

    # Prepare the list of workflows to be sent as a JSON response
    workflow_list = [{'id': w.id, 'name': w.name} for w in workflows]

    return jsonify(workflows=workflow_list)


''' 
Trilateral entry form route - 3-key entry_trilateral_tiangle_triangolo_SERVER SIDE II
'''

@app.route('/manage_base_data_workflow_step', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_base_data_workflow_step():

    form = BaseDataWorkflowStepForm()
    message = None

    # Populate choices for workflows
    form.workflow.choices = [(workflow.id, workflow.name) for workflow in Workflow.query.all()]

    # Populate choices for steps based on selected workflow
    if form.workflow.data:
        selected_workflow_id = form.workflow.data
        steps = Step.query.join(WorkflowSteps).filter(WorkflowSteps.workflow_id == selected_workflow_id).all()
        form.step.choices = [(step.id, step.name) for step in steps]
    else:
        form.step.choices = []

    # Populate choices for documents
    form.base_data.choices = [(base_data.id,
                               f"{extract_filename_and_extension(base_data.file_path)[0]}{extract_filename_and_extension(base_data.file_path)[1]}")
                               for base_data in BaseData.query.filter(BaseData.file_path.isnot(None)).all()]

    if form.validate_on_submit():
        if form.cancel.data:
            # Handle cancel button
            return redirect(url_for('index'))
        elif form.add.data:
            # Handle add button
            base_data_id = form.base_data.data
            workflow_id = form.workflow.data
            step_id = form.step.data

            auto_move = form.auto_move.data  # Get the value of auto_move field

            # Check if the document-step association already exists for the selected workflow
            existing_step_base_data_query = StepBaseData.query \
                .join(WorkflowSteps, WorkflowSteps.step_id == StepBaseData.step_id) \
                .join(Workflow, Workflow.id == WorkflowSteps.workflow_id) \
                .filter(Workflow.id == workflow_id,
                        StepBaseData.step_id == step_id,
                        StepBaseData.base_data_id == base_data_id)

            existing_step_base_data = existing_step_base_data_query.first()

            if existing_step_base_data:
                message = "Document already assigned to the step in the selected workflow."
            else:
                # Get the current date in format YYYY-MM-DD
                current_date = datetime.now()
                # Add logic to associate the document with the step in the selected workflow
                new_step_base_data = StepBaseData(step_id=step_id, workflow_id=workflow_id,
                                                  base_data_id=base_data_id, start_date=current_date,
                                                  auto_move=auto_move)
                db.session.add(new_step_base_data)
                db.session.commit()
                message = f"Document assigned successfully to the step in the selected workflow on {current_date}."

        elif form.delete.data:

            records_to_delete = []

            for i in range(0, 1): # range(len(form.base_data.entries)):
                records_to_delete = []
                # Handle delete button
                base_data_id = form.base_data.data
                workflow_id = form.workflow.data
                step_id = form.step.data

                # Find and delete the document-step association for the selected workflow
                step_base_data_to_delete = StepBaseData.query \
                    .join(WorkflowSteps, WorkflowSteps.step_id == StepBaseData.step_id) \
                    .join(Workflow, Workflow.id == WorkflowSteps.workflow_id) \
                    .filter(Workflow.id == workflow_id,
                            StepBaseData.step_id == step_id,
                            StepBaseData.base_data_id == base_data_id) \
                    .first()

                if step_base_data_to_delete:
                    records_to_delete.append(step_base_data_to_delete)

            # Delete the selected records
            for record in records_to_delete:
                db.session.delete(record)

            db.session.commit()
            message = f"{len(records_to_delete)} record(s) deleted."

    return render_template('manage_base_data_workflow_step.html', form=form, message=message)



@app.route('/manage_company_users', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_company_users():
    form = CompanyUserForm()
    message = None

    # Populate choices for users and roles
    form.company.choices = [(company.id, company.name) for company in Company.query.all()]
    form.user.choices = [(user.id, user.username) for user in Users.query.all()]

    if form.validate_on_submit():
        if form.cancel.data:
            # Handle cancel button
            return redirect(url_for('index'))
        elif form.add.data:
            # Handle add button
            company_id = form.company.data
            user_id = form.user.data

            # Check if the user-role association already exists
            existing_company_user = CompanyUsers.query.filter_by(company_id=company_id, user_id=user_id).first()

            if existing_company_user:
                message = "Link company-user already exists."

            else:
                # Add logic to associate the user with the selected role
                new_company_user = CompanyUsers(company_id=company_id, user_id=user_id)
                db.session.add(new_company_user)
                db.session.commit()
                # Set a success message
                message = "Company user added successfully."

        elif form.delete.data:
            # Handle delete button
            company_id = form.company.data
            user_id = form.user.data

            # Find and delete the user-role association
            company_user_to_delete = CompanyUsers.query.filter_by(company_id=company_id, user_id=user_id).first()

            if company_user_to_delete:
                db.session.delete(company_user_to_delete)
                db.session.commit()
                message = "Company User deleted successfully."

            else:
                message = "Company User not found."

    return render_template('manage_company_users.html', form=form, message=message)


@app.route('/manage_questionnaire_companies', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_questionnaire_companies():
    form = QuestionnaireCompanyForm()
    message = None

    # Populate choices for users and roles
    form.questionnaire.choices = [(questionnaire.id, questionnaire.name) for questionnaire in Questionnaire.query.all()]
    form.company.choices = [(company.id, company.name) for company in Company.query.all()]

    if form.validate_on_submit():

        if form.cancel.data:
            # Handle cancel button
            return redirect(url_for('index'))
        elif form.add.data:
            # Handle add button
            questionnaire_id = form.questionnaire.data
            company_id = form.company.data

            # Check if the user-role association already exists
            existing_questionnaire_company = QuestionnaireCompanies.query.filter_by(
                company_id=company_id, questionnaire_id=questionnaire_id).first()

            if existing_questionnaire_company:
                message = "Link questionnaire-to-company already exists."

            else:
                # Add logic to associate the user with the selected role
                new_questionnaire_company = QuestionnaireCompanies(
                    company_id=company_id, questionnaire_id=questionnaire_id)
                db.session.add(new_questionnaire_company)
                db.session.commit()
                # Set a success message
                message = "Questionnaire assigned successfully to company."

        elif form.delete.data:
            # Handle delete button
            company_id = form.company.data
            questionnaire_id = form.questionnaire.data

            # Find and delete the user-role association
            questionnaire_company_to_delete = QuestionnaireCompanies.query.filter_by(
                company_id=company_id, questionnaire_id=questionnaire_id).first()

            if questionnaire_company_to_delete:
                db.session.delete(questionnaire_company_to_delete)
                db.session.commit()
                message = "Questionnaire assignment to company deleted successfully."

            else:
                message = "Association of this questionnaire to company not found."

    return render_template('manage_questionnaire_companies.html', form=form, message=message)




@login_required
@app.route('/submit_confirmed', methods=['POST'])
def submit_confirmed():
    pending_data = session.pop('pending_answer_data', None)
    questionnaire_id = request.form.get('questionnaire_id', default=None)

    if request.form['submit_button'] == 'cancel':
        # Retrieve questionnaire_id safely
        questionnaire_id = request.form.get('questionnaire_id', default=None)
        if questionnaire_id is None:
            flash("No questionnaire ID provided.", "error")
            return redirect(url_for('open_admin_10.index')) # Redirect to a default route or error page

        try:
            questionnaire_id = int(questionnaire_id)
        except ValueError:
            flash("Invalid questionnaire ID.", "error")
            return redirect(url_for('open_admin_10.index'))

        return redirect(url_for('show_survey', questionnaire_id=questionnaire_id))

    if pending_data:
        # Directly use the pending_data dictionary in the save_answers call
        save_answers(pending_data)
        return redirect(url_for('thank_you'))
    else:
        flash('No data to save or session expired.', 'error')
        return redirect(url_for('show_survey', questionnaire_id=request.form.get('questionnaire_id')))

@login_required
@app.route('/manage_questionnaire_questions', methods=['GET', 'POST'])
def manage_questionnaire_questions():
    form = QuestionnaireQuestionForm()
    message = None

    # Populate choices for users and roles
    form.questionnaire.choices = [(questionnaire.id, questionnaire.name) for questionnaire in Questionnaire.query.all()]
    #form.question.choices = [(question.id, question.text) for question in Question.query.all()]
    form.question.choices = [(question.id, question.text) for question in Question.query.order_by('question_id').all()]

    if form.validate_on_submit():
        if form.cancel.data:
            # Handle cancel button
            return redirect(url_for('index'))
        elif form.add.data:
            # Handle add button
            questionnaire_id = form.questionnaire.data
            question_id = form.question.data

            # Check if the user-role association already exists
            existing_questionnaire_question = QuestionnaireQuestions.query.filter_by(
                question_id=question_id, questionnaire_id=questionnaire_id).first()

            if existing_questionnaire_question:
                message = "Link questionnaire-to-question already exists."

            else:
                # Add logic to associate the user with the selected role
                try:
                    new_questionnaire_question = QuestionnaireQuestions(
                        question_id=question_id, questionnaire_id=questionnaire_id)
                    db.session.add(new_questionnaire_question)
                    db.session.commit()
                    # Set a success message
                    message = f"Question {question_id} assigned successfully to questionnaire {questionnaire_id}."
                except Exception as e:
                    db.session.rollback()
                    message = f"Question {question_id} not assigned to questionnaire {questionnaire_id}. Error: {e}."

        elif form.delete.data:
            # Handle delete button
            question_id = form.question.data
            questionnaire_id = form.questionnaire.data

            # Find and delete the user-role association
            questionnaire_question_to_delete = QuestionnaireQuestions.query.filter_by(
                question_id=question_id, questionnaire_id=questionnaire_id).first()

            if questionnaire_question_to_delete:
                db.session.delete(questionnaire_question_to_delete)
                db.session.commit()
                message = "Question assignment to questionnaire deleted successfully."

            else:
                message = "Association of this question to questionnaire not found."

    return render_template('manage_questionnaire_questions.html', form=form, message=message)


def fetch_questions(questionnaire_id):
    # Query the QuestionnaireQuestions table to fetch the records associated with the given questionnaire_id
    questionnaire_questions = QuestionnaireQuestions.query.filter_by(questionnaire_id=questionnaire_id).all()

    questions = []
    # Iterate through each record and fetch the corresponding Question object
    for qq in questionnaire_questions:
        # Fetch the Question object using the question_id
        question = Question.query.get(qq.question_id)
        if question:
            questions.append(question)

    return questions


def fetch_answer_data(questionnaire_id):
    try:
        # Retrieve answer data for the specified questionnaire
        questionnaire = Questionnaire.query.filter_by(id=questionnaire_id).first()

        if questionnaire:
            # Retrieve all answers associated with the questionnaire
            answers = Answer.query.filter_by(questionnaire_id=questionnaire_id).all()

            # Initialize a dictionary to store answer data for each question
            answer_data = {}

            questions = fetch_questions(questionnaire_id)
            # Loop through each question in the questionnaire
            for question in questions:
                # Initialize a list to store answers for the current question
                question_answers = []

                # Retrieve all answers for the current question
                question_answers_query = [answer for answer in answers if answer.question_id == question.id]

                # Loop through each answer and append it to the list
                for answer in question_answers_query:
                    question_answers.append({
                        "id": answer.id,
                        "user_id": answer.user_id,
                        "company_id": answer.company_id,
                        "timestamp": answer.timestamp,
                        "submitted": answer.submitted,
                        "answer_data": answer.get_answer_data()
                    })

                # Add the list of answers to the dictionary with question_id as the key
                answer_data[question.question_id] = question_answers

            return answer_data
        else:
            print("Questionnaire not found.")
            return None
    except Exception as e:
        print(f"Error fetching answer data: {e}")
        return None


@login_required
@app.route('/overwrite_answer', methods=['POST'])
def overwrite_answer():

    # Retrieve the questionnaire_id from the form data
    questionnaire_id = request.form.get('questionnaire_id')
    company_id = request.form.get('questionnaire_id')
    user_id = request.form.get('questionnaire_id')

    # Process the overwrite action here

    # Perform the overwrite action (e.g., update the existing answer)
    # Replace this with your actual overwrite logic

    # Redirect back to the show _ survey page after overwriting
    return redirect(url_for('show_survey', questionnaire_id=questionnaire_id))

def update_question_answer_fields():
    all_questions = Question.query.all()

    for question in all_questions:
        answer_types = [atype.strip() for atype in question.answer_type.split(',')]

        try:
            # Attempt to parse the widths and apply minimum and maximum bounds
            widths = [max(25, min(int(width.strip()), 1500)) for width in question.answer_width.split(',')]
            # Ensure that the widths list matches the length of the answer_types list
            if len(widths) != len(answer_types):
                raise ValueError("Widths and types length mismatch")
        except Exception as e:
            # If parsing fails or lengths mismatch, use default width for all types
            widths = [200] * len(answer_types)  # Set all widths to 200

        # Now you can assign these widths to your answer fields or handle them as needed
        answer_fields = [{'type': atype, 'value': '', 'width': width} for atype, width in zip(answer_types, widths)]
        # Assuming you want to convert these to JSON or further process them
        question.answer_fields = json.dumps(answer_fields, ensure_ascii=False)

    # Commit to the database
    db.session.commit()


# You can see a record of this email in your logs: https://app.mailgun.com/app/logs.

# You can send up to 300 emails/day from this sandbox server.
# Next, you should add your own domain so you can send 10000 emails/month for free.


def merge_answer_fields(base_fields_json, answer_data_json):
    try:
        base_fields = json.loads(base_fields_json)
        answer_data = json.loads(answer_data_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Parsing error: {str(e)}")

    # Create a lookup dictionary from the base fields to easily find and fill missing types
    base_lookup = {item['type']: item for item in base_fields}

    # Use answer data as the primary source and update missing fields from the base fields if necessary
    merged_fields = []
    seen_types = set()  # Track types we've added to avoid duplicates

    # First add all fields from the answer data, updating them with values and widths from the base fields if needed
    for answer in answer_data:
        type = answer['type']
        seen_types.add(type)
        if type in base_lookup:
            base_item = base_lookup[type]
            # Update 'value' if missing or empty
            if 'value' not in answer or answer['value'] == '':
                answer['value'] = base_item.get('value', '')
            # Update 'width' if missing or empty
            if 'width' not in answer or answer['width'] == '':
                answer['width'] = base_item.get('width', None)

        merged_fields.append(answer)

    # Now add any additional types from the base fields that weren't in the answer data
    for type, field in base_lookup.items():
        if type not in seen_types:
            merged_fields.append(field)

    return json.dumps(merged_fields)  # Return as JSON string if needed for consistency

def merge_answer_fields(base_fields_json, answer_data_json):

    try:
        base_fields = json.loads(base_fields_json)
        answer_data = json.loads(answer_data_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Parsing error: {str(e)}")

    # Create a lookup dictionary from the base fields to easily find and fill missing types
    base_lookup = {item['type']: item for item in base_fields}

    # Use answer data as the primary source and update missing fields from the base fields if necessary
    merged_fields = []
    seen_types = set()  # Track types we've added to avoid duplicates

    # First add all fields from the answer data, updating them with values and widths from the base fields if needed
    for answer in answer_data:
        type = answer['type']
        seen_types.add(type)
        if type in base_lookup:
            base_item = base_lookup[type]
            # Update 'value' if missing or empty
            if 'value' not in answer or answer['value'] == '':
                answer['value'] = base_item.get('value', '')
            # Update 'width' if missing or empty
            if 'width' not in answer or answer['width'] == '':
                answer['width'] = base_item.get('width', None)

        merged_fields.append(answer)

    # Now add any additional types from the base fields that weren't in the answer data
    for type, field in base_lookup.items():
        if type not in seen_types:
            merged_fields.append(field)

    return json.dumps(merged_fields)  # Return as JSON string if needed for consistency


@app.route('/redirect_to_survey/<int:questionnaire_id>')
def redirect_to_survey(questionnaire_id):
    return redirect(url_for('show_survey', questionnaire_id=questionnaire_id))


# @login_required
@app.route('/show_survey/<int:questionnaire_id>', methods=['GET', 'POST'])
def show_survey(questionnaire_id):
    form = BaseSurveyForm()
    headers = None
    user_id = current_user.id
    company = CompanyUsers.query.filter_by(user_id=user_id).first()
    company_id = company.company_id if company else None

    if request.method == 'POST':
        if form.validate_on_submit():
            answers_to_save = serialize_answers(request.form)

            return handle_post_submission(form, company_id, user_id, questionnaire_id, answers_to_save)
        else:
            flash('Error with form data. Please check your entries.', 'error')

    # Fetch the questionnaire details and questions via QuestionnaireQuestions
    # reset answer_fields in Question
    update_question_answer_fields()
    selected_questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    raw_headers = selected_questionnaire.headers

    headers = []  # Default to an empty list if there's a problem

    if raw_headers:
        if isinstance(raw_headers, str):
            try:
                headers = json.loads(raw_headers)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        elif isinstance(raw_headers, dict):
            headers = raw_headers

        elif isinstance(raw_headers, list):
            # Assuming you want to use the list as it is
            headers = raw_headers

    horizontal = selected_questionnaire.questionnaire_type.endswith('H')

    if request.method == 'POST':
        if form.validate_on_submit():
            answers_to_save = serialize_answers(request.form)
            return handle_post_submission(form, company_id, user_id, questionnaire_id, answers_to_save)
        else:
            flash('Error with form data. Please check your entries.', 'error')

    questionnaire_questions = QuestionnaireQuestions.query.filter_by(
        questionnaire_id=questionnaire_id
    ).join(Question).order_by(Question.question_id).all()

    questions = []
    form_data = {}
    for qq in questionnaire_questions:
        question = qq.question
        existing_answer = Answer.query.filter_by(
            company_id=company_id, user_id=user_id, questionnaire_id=questionnaire_id, question_id=question.id
        ).first()

        if existing_answer and existing_answer.answer_data:
            merged_fields = merge_answer_fields(question.answer_fields, existing_answer.answer_data)  # Make sure this function is set to merge JSON fields correctly
            form_data[str(question.id)] = merged_fields
        else:
            form_data[str(question.id)] = question.answer_fields

        questions.append({
            'id': question.id,
            'question_id': question.question_id,
            'text': question.text,
            'answer_type': question.answer_type,
            'answer_width': question.answer_width,
            'answer_fields': form_data[str(question.id)]
        })
    dynamic_html = create_dynamic_form(form, {'questions': questions, 'form_data': form_data}, company_id, horizontal)  # Adjust this function to accept horizontal flag
    return render_template('survey.html', form=form, headers=headers, dynamic_html=dynamic_html, questionnaire_name=selected_questionnaire.name, today=datetime.now().date())


# Example use within the Flask view function
@login_required
@app.route('/show_survey_sqlite/<int:questionnaire_id>', methods=['GET', 'POST'])
def show_survey_sqlite(questionnaire_id):

    form = BaseSurveyForm()
    headers = None
    user_id = current_user.id
    company = CompanyUsers.query.filter_by(user_id=user_id).first()
    company_id = company.company_id if company else None

    if request.method == 'POST':
        if form.validate_on_submit():
            answers_to_save = serialize_answers(request.form)
            return handle_post_submission(form, company_id, user_id, questionnaire_id, answers_to_save)
        else:
            flash('Error with form data. Please check your entries.', 'error')

    # Fetch the questionnaire details and questions via QuestionnaireQuestions
    # reset answer_fields in Question
    update_question_answer_fields()
    selected_questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    raw_json = selected_questionnaire.headers

    headers = []  # Default to an empty list if there's a problem
    if raw_json:
        try:
            headers = json.loads(raw_json)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

    horizontal = selected_questionnaire.questionnaire_type.endswith('H')

    if request.method == 'POST':
        if form.validate_on_submit():
            answers_to_save = serialize_answers(request.form)
            return handle_post_submission(form, company_id, user_id, questionnaire_id, answers_to_save)
        else:
            flash('Error with form data. Please check your entries.', 'error')

    questionnaire_questions = QuestionnaireQuestions.query.filter_by(
        questionnaire_id=questionnaire_id
    ).join(Question).order_by(Question.question_id).all()

    questions = []
    form_data = {}
    for qq in questionnaire_questions:
        question = qq.question
        existing_answer = Answer.query.filter_by(
            company_id=company_id, user_id=user_id, questionnaire_id=questionnaire_id, question_id=question.id
        ).first()

        if existing_answer and existing_answer.answer_data:
            merged_fields = merge_answer_fields(question.answer_fields, existing_answer.answer_data)  # Make sure this function is set to merge JSON fields correctly
            form_data[str(question.id)] = merged_fields
        else:
            form_data[str(question.id)] = question.answer_fields

        questions.append({
            'id': question.id,
            'question_id': question.question_id,
            'text': question.text,
            'answer_type': question.answer_type,
            'answer_width': question.answer_width,
            'answer_fields': form_data[str(question.id)]
        })

    dynamic_html = create_dynamic_form(form, {'questions': questions, 'form_data': form_data}, company_id, horizontal)  # Adjust this function to accept horizontal flag
    return render_template('survey.html', form=form, headers=headers, dynamic_html=dynamic_html, questionnaire_name=selected_questionnaire.name, today=datetime.now().date())


def handle_post_submission(form, company_id, user_id, questionnaire_id, answers_to_save):
    action_id = request.form.get('action_id', 'load')

    if check_existing_data(company_id, user_id, questionnaire_id):
        flash('Existing data found, please confirm to overwrite.', 'warning')
        session['pending_answer_data'] = {
            'action_id': action_id,
            'company_id': company_id,
            'user_id': user_id,
            'questionnaire_id': questionnaire_id,
            'answer_data': json.dumps(answers_to_save, ensure_ascii=False)
        }
        return render_template('confirmation_save_submit.html', form=form, questionnaire_id=questionnaire_id)
    else:
        return save_answers({
            'action_id': action_id,
            'company_id': company_id,
            'user_id': user_id,
            'questionnaire_id': questionnaire_id,
            'answer_data': json.dumps(answers_to_save, ensure_ascii=False)
        })


def serialize_answers(form_data):
    answers = {}
    print('serialize answers, form_data:', form_data)
    for key in form_data.keys():
        # Extract width data, assuming it's submitted as part of the form data
        width_key = key + '_width'  # Assuming width data is submitted with a key suffix '_width'
        width = form_data.get(width_key, '')  # Default width is an empty string if not provided

        if key.endswith('_CB'):
            value = 'on' if 'on' in form_data.getlist(key) else ''
            key_parts = key.split('_')
            if len(key_parts) >= 3:
                question_id = key_parts[0]
                answer_index = key_parts[1]
                answer_type = key_parts[2]
                if question_id not in answers:
                    answers[question_id] = []
                answers[question_id].append({'type': answer_type, 'value': value, 'width': width})
        else:
            value = form_data.get(key)
            key_parts = key.split('_')
            if len(key_parts) >= 3:
                question_id = key_parts[0]
                answer_index = key_parts[1]
                answer_type = key_parts[2]
                if question_id not in answers:
                    answers[question_id] = []
                answers[question_id].append({'type': answer_type, 'value': value, 'width': width})
            else:
                # Handle the case where there are not enough parts after splitting
                pass
    return answers


def check_existing_data(company_id, user_id, questionnaire_id):
    """
    Check if there is existing data for a given combination of company ID, user ID, and questionnaire ID.

    Args:
        company_id (int): The ID of the company.
        user_id (int): The ID of the user.
        questionnaire_id (int): The ID of the questionnaire.

    Returns:
        bool: True if existing data is found, False otherwise.
    """
    existing = Answer.query.filter_by(company_id=company_id, user_id=user_id, questionnaire_id=questionnaire_id).first()
    return existing is not None


def is_substantive(data):
    """Check if the data contains more than just whitespace or is non-empty."""
    if data and data.strip():
        return True
    return False

def save_answers(data):
    try:
        if not is_substantive(data['answer_data']):
            flash('No substantial data to save.', 'error')
            return redirect(url_for('show_survey', questionnaire_id=data['questionnaire_id']))

        action_id = data['action_id']
        company_id = data['company_id']
        user_id = data['user_id']
        questionnaire_id = data['questionnaire_id']
        answer_data = json.loads(data['answer_data'])  # This is a dictionary keyed by question IDs

        should_submit = (action_id == 'submit')
        changes_made = False  # Flag to track if any data was updated

        # Iterate over each question's answer data
        for current_question_id, question_answers in answer_data.items():
            answer = Answer.query.filter_by(
                company_id=company_id,
                user_id=user_id,
                questionnaire_id=questionnaire_id,
                question_id=current_question_id
            ).first()

            # Serialize the question's answer data for storage
            serialized_answer = json.dumps(question_answers, ensure_ascii=False)

            if answer:
                if is_substantive(serialized_answer) and serialized_answer != answer.answer_data:
                    answer.answer_data = serialized_answer
                    changes_made = True
                if answer.submitted != should_submit:
                    answer.submitted = should_submit
                    changes_made = True
            else:
                # Create new record
                answer = Answer(
                    company_id=company_id,
                    user_id=user_id,
                    questionnaire_id=questionnaire_id,
                    question_id=current_question_id,
                    answer_data=serialized_answer,
                    submitted=should_submit
                )
                db.session.add(answer)
                changes_made = True

        # Update the QuestionnaireCompanies status if the form is being submitted
        if should_submit and changes_made:
            q_company = QuestionnaireCompanies.query.filter_by(
                company_id=company_id,
                questionnaire_id=questionnaire_id
            ).first()
            if q_company:
                q_company.status_id = 10  # Set to 'submitted' status
                db.session.commit()
                flash('Form submitted and status updated.', 'success')
            else:
                flash('Questionnaire company record not found.', 'error')
        elif changes_made:
            db.session.commit()
            flash('Data saved successfully!', 'success')

        return redirect(url_for('thank_you'))
    except Exception as e:
        db.session.rollback()
        print(f"Database commit failed: {e}")
        flash(f'Error saving data: {str(e)}', 'error')
        return redirect(url_for('show_survey', questionnaire_id=questionnaire_id))


@login_required
@app.route('/load_survey', methods=['GET', 'POST'])
def load_survey():
    company_id = request.args.get('company_id')
    user_id = request.args.get('user_id')
    questionnaire_id = request.args.get('questionnaire_id')

    answer = Answer.query.filter_by(
        company_id=company_id, user_id=user_id, questionnaire_id=questionnaire_id
    ).first()

    if not answer:
        return "No data found for the given parameters.", 404

    try:
        json_data = json.loads(answer.answer_data)
    except json.JSONDecodeError:
        return "Error: Data is not in valid JSON format.", 400

    if request.method == 'POST':
        if answer.submitted:
            return jsonify({'found': True, 'submitted': True})
        return jsonify({'found': True, 'submitted': False, 'data': json_data})

    # For GET requests, render the survey with the loaded data
    return render_template('survey.html', form_data=json_data)


def validate_form_structure(form_data, json_data):
    expected_keys = form_data.keys()  # Get field names from your form class or definition
    json_keys = json_data.keys()

    if set(expected_keys) == set(json_keys):
        return True
    else:
        return False


@login_required
@app.route('/company_files/<company_id>', methods=['GET'])
def list_company_files(company_id):
    user = current_user  # Retrieve current user
    if user.company_id != company_id:  # Verify company access
        return 'Access denied!', 403

    # Retrieve file paths based on company_id (from database or folder names)
    file_paths = get_company_files(company_id)

    # Prepare file information for display
    file_info = []
    for path in file_paths:
        file_info.append({
            'filename': os.path.basename(path),
            'size': os.path.getsize(path),
            # ... other relevant information
        })

    return render_template('files_list.html', files=file_info, company_id=company_id)


@login_required
@app.route('/download_file/<company_id>/<filename>', methods=['GET'])
def download_file(company_id, filename):
    user = current_user
    if user.company_id != company_id:
        return 'Access denied!', 403

    # Verify file existence and permissions
    file_path = get_company_file_path(company_id, filename)  # Implement logic to get path
    if not file_path or not os.path.isfile(file_path):
        return 'File not found!', 404

    return send_from_directory(os.path.dirname(file_path), filename)  # Use Flask-Send


# Other functions for retrieving file paths, verifying permissions, etc.
@login_required
@app.route('/company_files/<int:company_id>/<path:filename>', methods=['GET'])
def serve_company_file(company_id, filename):
    # Construct the path to the file within the company folder
    folder_path = os.path.join(app.config['COMPANY_FILES_DIR'], f"company_id_{company_id}")
    file_path = os.path.join(folder_path, filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return "File not found", 404
    # Serve the file using Flask's send_file function
    return send_file(file_path, as_attachment=True)


def save_file_with_incremented_name(file, folder_path):
    filename = secure_filename(file.filename)
    base_name, extension = os.path.splitext(filename)
    count = 1
    while os.path.exists(os.path.join(folder_path, filename)):
        filename = f"{base_name}_{count}{extension}"
        count += 1
    file_path = os.path.join(folder_path, filename)
    file.save(file_path)
    return file_path


def apply_filters(text_filter, answer_type_filter):
    # Replace this with your actual filtering logic
    # For example, if using SQLAlchemy and you have a Question model:
    query = Question.query

    if text_filter:
        query = query.filter(Question.text.ilike(f"%{text_filter}%"))

    if answer_type_filter:
        query = query.filter(Question.answer_type.ilike(f"%{answer_type_filter}%"))

    return query.all()

'''
2-factor authentication
'''

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    form = TwoFactorForm()
    if form.validate_on_submit():
        user_otp = form.otp.data

        # user = get_user_from_session_or_db()  # Implement this function to retrieve the user object
        try:
            user = Users.query.filter_by(user_id=current_user.id).first()
        except:
            user = None
            pass

        totp = pyotp.TOTP(user.user_2fa_secret)
        url = pyotp.totp.TOTP(user_2fa_secret).provisioning_uri(name=user.email, issuer_name="ArApp")
        qr = qrcode.make(url)

        if totp.verify(user_otp):
            # User verified, proceed to log them in
            return redirect(url_for('index'))
        else:
            # Verification failed
            flash('Invalid OTP', 'danger')
    return render_template('access/verify_2fa.html', form=form)


'''
Verify TOTP Code: When the user attempts to log in, you'll need to verify the TOTP code 
they provide against the expected TOTP code generated using the user's secret key. 
You can do this using the pyotp library.
'''
def verify_totp(secret_key, token):
    totp = pyotp.TOTP(secret_key)
    return totp.verify(token)

'''
# Assuming user_secret_key and user_token are obtained from the user's input
if verify_totp(user_secret_key, user_token):
    # TOTP code is valid, proceed with authentication
else:
    # TOTP code is invalid, deny access
'''

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')


# Define a custom error handler for 404 Not Found errors
@app.errorhandler(404)
def page_not_found(error):
    # Render a custom template for the 404 error
    return render_template('error_pages/404.html'), 404


@app.errorhandler(403)
def page_forbidden(error):
    # Render a custom template for the 404 error
    return render_template('error_pages/403.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error_pages/500.html', message=str(error)), 500

@app.route('/back')
def back():
    # Add any logic you need before redirecting, if necessary
    return redirect(url_for('home'))  # Assuming 'home' is the route for your home page


@app.route('/')
def home():

    # app.logger.debug("Home route accessed")
    return render_template('index.html')  # Render your home page template


@app.route('/noticeboard', methods=['GET', 'POST'])
@login_required
def noticeboard():
    user_id = current_user.id

    if request.method == 'POST':
        message_ids = request.form.getlist('message_ids')
        if message_ids:
            messages_to_mark = Post.query.filter(Post.id.in_(message_ids)).all()
            for message in messages_to_mark:
                message.marked_as_read = True
            db.session.commit()
            flash('Selected messages marked as read.', 'success')
        else:
            flash('No messages selected.', 'warning')
        return redirect(url_for('noticeboard'))

    unmarked_messages = Post.query.filter_by(user_id=user_id, marked_as_read=False).all()
    return render_template('home/noticeboard.html', unmarked_messages=unmarked_messages)


@app.route('/auditlog')
@login_required
@roles_required('Admin')
def auditlog():
    # Retrieve unmarked messages from the database
    audit_log = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    # Pass the messages to the template for rendering
    return render_template('home/auditlog.html', audit_log=audit_log)


@app.errorhandler(Exception)
def handle_exception(e):

    # TODO restore the snippet below after debug
    '''
    :param e:
    :return:
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    # Now you're handling non-HTTP exceptions only
    return render_template("error.html", error=str(e)), 500
    '''
    # Temporarily disable login redirection during debugging
    if not app.debug:
        #app.logger.error(f"An error occurred: {e}", exc_info=True)
        return render_template('error.html', error=e), 500
    else:
        raise e  # Raise the exception in debug mode for detailed traceback


'''
@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message=str(error)), 500
'''


@app.route('/chart_form', methods=['GET', 'POST'])
def chart_form():
    areas = Area.query.all()
    subareas = Subarea.query.all()
    companies = Company.query.all()

    selected_chart_type = None
    selected_area_id = None
    selected_subarea_id = None
    selected_company_id = None
    chart_html = None

    if request.method == 'POST':
        selected_chart_type = request.form.get('chart_type')
        selected_company_id = request.form.get('company_id') if selected_chart_type == '2d' else None
        selected_area_id = request.form.get('area_id')
        selected_subarea_id = request.form.get('subarea_id')

        try:
            data = ChartService.query_data(company_id=selected_company_id, area_id=selected_area_id, subarea_id=selected_subarea_id)
            if selected_chart_type == '2d':
                chart_html = ChartService.generate_bar_chart(data)
            elif selected_chart_type == '3d':
                chart_html = ChartService.generate_3d_chart(data)
        except Exception as e:
            chart_html = f"An error occurred: {str(e)}"

        return render_template('charts/chart_form.html', areas=areas, subareas=subareas, companies=companies,
                               chart_html=chart_html, chart_type=selected_chart_type,
                               selected_area_id=int(selected_area_id), selected_subarea_id=int(selected_subarea_id),
                               selected_company_id=int(selected_company_id) if selected_company_id else None)

    return render_template('charts/chart_form.html', areas=areas, subareas=subareas, companies=companies)



@app.route('/questionnaire/<int:id>', methods=['GET'])
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def get_questionnaire(id):
    questionnaire = Questionnaire_psf.query.get(id)
    if questionnaire:
        return jsonify(questionnaire.structure)
    return jsonify({"error": "Questionnaire not found"}), 404



# STRIPE
# ======


@app.route('/create-checkout-session', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Subscription Plan',
                },
                'unit_amount': 1000,  # price in cents
            },
            'quantity': 1,
        }],
        mode='subscription',
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cancel', _external=True),
    )
    return jsonify(id=session.id)



@app.route('/success')
def success():
    return 'Payment succeeded'

@app.route('/cancel')
@login_required
@roles_required('Manager', 'Employee')
def cancel():
    return 'Payment canceled'


# **Handle Webhooks**:
# Set up a webhook endpoint to handle events from Stripe, such as payment success.

@app.route('/webhook', methods=['POST'])
@login_required
@roles_required('Manager', 'Employee')
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_ENDPOINT_SECRET']
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return '', 200


def handle_checkout_session(session):
    try:
        # Check if 'email' exists in session
        if 'email' not in session:
            flash('Email not found in session', 'error')
            return

        # Find the user by email
        user = Users.query.filter_by(email=session['email']).first()

        # If user not found, handle it appropriately
        if not user:
            flash('User not found', 'error')
            return

        # Update subscription details
        user.subscription_status = 'active'
        user.subscription_plan = 'basic'  # or other plan based on session details
        user.subscription_start_date = datetime.utcnow()
        user.subscription_end_date = datetime.utcnow() + timedelta(days=30)

        # Commit changes to the database
        db.session.commit()
        flash('Subscription updated successfully', 'success')

    except Exception as e:
        # Rollback the session in case of error
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')


@app.route('/subscriptions')
@login_required
@roles_required('Manager', 'Employee')
def subscriptions():
    try:
        email = session.get('email')
        logging.debug(f'Session email: {email}')
        user = Users.query.filter_by(email=email).first()
        logging.debug(f'User fetched: {user}')

        if user:
            subscription = Subscription.query.filter_by(user_id=user.id,
                                                        status='active').first()  # Fetch the active subscription
            if subscription:
                current_plan = Plan.query.filter_by(id=subscription.plan_id).first()
                # If subscription.end_date is None, it's considered active
                subscription_info = {
                    'id': subscription.id,  # Add the subscription ID for reference in the template
                    'plan': current_plan.name if current_plan else 'N/A',
                    'status': 'active' if subscription.end_date is None or subscription.end_date > datetime.utcnow() else 'inactive',
                    'start_date': subscription.start_date,
                    'end_date': subscription.end_date,
                    'status': subscription.status,
                }
            else:
                subscription_info = {
                    'id': None,
                    'plan': 'N/A',
                    'status': 'N/A',
                    'start_date': 'N/A',
                    'end_date': 'N/A',
                    'status': 'N/A'
                }
        else:
            subscription_info = {
                'id': None,
                'plan': 'N/A',
                'status': 'N/A',
                'start_date': 'N/A',
                'end_date': 'N/A',
                'status': 'N/A'
            }

        logging.debug(f'Subscription info: {subscription_info}')

        plans = Plan.query.all()
        additional_products = Product.query.all()

        # Add products to plans
        for plan in plans:
            plan.products = [pp.product for pp in plan.plan_products]
            plan.product_ids = [pp.product_id for pp in plan.plan_products]

        logging.debug(f'Plans fetched: {plans}')

        form = SubscriptionForm()
        return render_template('subscriptions.html', subscription_info=subscription_info, plans=plans,
                               additional_products=additional_products, form=form)
    except Exception as e:
        logging.error(f"Error in subscriptions route: {e}")
        return "An error occurred", 500



@app.route('/subscribe', methods=['POST'])
@login_required
@roles_required('Manager', 'Employee')
def subscribe():
    form = SubscriptionForm()
    logging.debug(f"Form data before validation: {form.plan_id.data}, additional_products: {request.form.getlist('additional_products')}")

    try:
        if form.validate_on_submit():
            plan_id = form.plan_id.data
            logging.debug(f"Plan ID after validation: {plan_id}")

            if not plan_id:
                logging.error("Plan ID is missing.")
                flash("Please select a plan.", "danger")
                return redirect(url_for('subscriptions'))

            plan_id = int(plan_id)
            additional_product_ids = [product_id for product_id in request.form.getlist('additional_products') if product_id]
            logging.debug(f'Form validated. Plan: {plan_id}, Additional Products: {additional_product_ids}')

            user_id = session.get('user_id')
            logging.debug(f'User ID: {user_id}')
            user = Users.query.filter_by(id=user_id).first()

            if not user:
                logging.error("User not found.")
                flash("User not found.", "danger")
                return redirect(url_for('subscriptions'))

            # Mark previous subscriptions as inactive
            active_subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            if active_subscription:
                logging.debug(f"Terminating active subscription: {active_subscription.id}")
                active_subscription.end_date = datetime.utcnow()
                active_subscription.status = 'inactive'
                db.session.add(active_subscription)

            # Create new subscription
            new_subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                start_date=datetime.utcnow(),
                additional_products=','.join(additional_product_ids),
                status='active'
            )
            db.session.add(new_subscription)

            try:
                db.session.commit()
                logging.debug(f"Subscription created successfully: {new_subscription.id}")
                flash("Subscription updated successfully.", "success")
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error committing subscription to the database: {e}")
                flash("An error occurred while updating the subscription.", "danger")

            return redirect(url_for('subscriptions'))  # Ensure updated subscription info is fetched
        else:
            logging.debug(f'Form validation failed: {form.errors}')
            flash("Invalid form submission.", "danger")
            return redirect(url_for('subscriptions'))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        flash("An unexpected error occurred.", "danger")
        return redirect(url_for('subscriptions'))


@app.route('/cancel_subscription', methods=['POST'])
@login_required
@roles_required('Manager', 'Employee')
def cancel_subscription():
    try:
        subscription_id = request.form.get('subscription_id')
        if not subscription_id:
            flash("Subscription ID not provided.", "danger")
            return redirect(url_for('subscriptions'))

        subscription = Subscription.query.filter_by(id=subscription_id, status='active').first()

        if not subscription:
            flash("No active subscription found to cancel.", "warning")
            return redirect(url_for('subscriptions'))

        # Fetch the plan associated with the subscription
        plan = Plan.query.get(subscription.plan_id)
        if not plan:
            flash("Subscription plan not found.", "danger")
            return redirect(url_for('subscriptions'))

        # Calculate end_date based on billing_cycle
        if plan.billing_cycle == 'monthly':
            subscription.end_date = datetime.utcnow() + timedelta(days=30)
        elif plan.billing_cycle == 'quarterly':
            subscription.end_date = datetime.utcnow() + timedelta(days=90)
        elif plan.billing_cycle == 'yearly':
            subscription.end_date = datetime.utcnow() + timedelta(days=365)
        else:
            subscription.end_date = datetime.utcnow() + timedelta(days=30)

        subscription.status = 'canceled'

        try:
            db.session.commit()
            flash("Subscription canceled successfully.", "success")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error committing subscription cancellation to the database: {e}")
            flash("An error occurred while canceling the subscription.", "danger")

        return redirect(url_for('subscriptions'))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        flash("An unexpected error occurred.", "danger")
        return redirect(url_for('subscriptions'))


@app.route('/subscription_report')
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def subscription_report():
    try:
        user_id = current_user.id
        user_roles = session.get('user_roles', [])
        subscriptions_query = Subscription.query

        # Admin can see all subscriptions
        if 'Admin' in user_roles:
            subscriptions = subscriptions_query.order_by(Subscription.start_date.desc()).all()

        # Manager can see subscriptions related to their company
        elif 'Manager' in user_roles:
            company_id = session.get('company_id')
            user_ids = [cu.user_id for cu in CompanyUsers.query.filter_by(company_id=company_id).all()]
            subscriptions = subscriptions_query.filter(Subscription.user_id.in_(user_ids)).order_by(Subscription.start_date.desc()).all()

        # Employee can only see their own subscriptions
        elif 'Employee' in user_roles:
            subscriptions = subscriptions_query.filter_by(user_id=user_id).order_by(Subscription.start_date.desc()).all()

        else:
            flash("You do not have permission to view this report.", "danger")
            return redirect(url_for('index'))

        # Fetch product names for additional products
        for subscription in subscriptions:
            if subscription.additional_products:
                product_ids = map(int, subscription.additional_products.split(','))
                products = Product.query.filter(Product.id.in_(product_ids)).all()
                subscription.additional_product_names = ', '.join([product.name for product in products])
            else:
                subscription.additional_product_names = 'None'

        return render_template('subscription_report.html', subscriptions=subscriptions)
    except Exception as e:
        logging.error(f"Error generating subscription report: {e}")
        flash("An error occurred while generating the report.", "danger")
        return redirect(url_for('index'))


# TODO more data_mapping us cases to be inserted here

@app.route('/generate_dashboard')
@login_required
def generate_dashboard():
    area_id = 2
    subarea_id = 11

    # Fetch the mapping configuration
    mapping = DataMapping.query.filter_by(area_id=area_id, subarea_id=subarea_id).first()

    if not mapping:
        return "No mapping found for this area and subarea.", 404

    # Extract and parse the JSON fields from the mapping
    data_key = json.loads(mapping.data_key)
    aggregation_rule = json.loads(mapping.aggregation_rule)

    # Fetch the relevant data based on year and interval conditions
    data = BaseData.query.filter_by(
        area_id=area_id,
        subarea_id=subarea_id
    ).all()

    # Organize the data by year and interval
    organized_data = {}
    for entry in data:
        year = entry.fi0  # Assuming fi0 is the year field
        interval = entry.interval_ord
        total_value = getattr(entry, data_key['total'])

        if year not in organized_data:
            organized_data[year] = {}
        if interval not in organized_data[year]:
            organized_data[year][interval] = 0

        # Sum the components based on the aggregation rule
        for field in data_key['components']:
            organized_data[year][interval] += getattr(entry, field)

    # Convert the organized data to a format suitable for the chart
    chart_data = {
        'labels': list(organized_data.keys()),  # Years
        'datasets': []
    }

    # Prepare datasets
    for interval in sorted({interval for year_data in organized_data.values() for interval in year_data}):
        dataset = {
            'label': f"Interval {interval}",
            'data': [organized_data[year].get(interval, 0) for year in chart_data['labels']],
            'backgroundColor': '#007bff'
        }
        chart_data['datasets'].append(dataset)

    return render_template('dashboard.html', chart_data=chart_data)


def process_aggregation_rule(aggregation_rule, data_list):
    result = 0

    # Process the aggregation rule
    if aggregation_rule['operation'] == 'sum':
        for data in data_list:
            for field in aggregation_rule['fields']:
                result += data[field]

    # Add more logic for different operations if necessary

    return result


def perform_data_aggregation(data_key, aggregation_rule, area_id, subarea_id, additional_info):
    logging.debug(f"Starting data aggregation for area_id={area_id}, subarea_id={subarea_id}")
    data = BaseData.query.filter_by(area_id=area_id, subarea_id=subarea_id).all()
    logging.debug(f"Fetched data: {data}")

    organized_data = {}
    for entry in data:
        year = getattr(entry, data_key['year'])
        interval = getattr(entry, data_key['interval_id'])
        interval_ord = getattr(entry, data_key['interval_ord'])

        if year not in organized_data:
            organized_data[year] = {}

        if interval not in organized_data[year]:
            organized_data[year][interval] = {}

        # Handle 'none' operation or sum operation
        if aggregation_rule['operation'] == 'none':
            for component in data_key.get('metrics', []):
                component_value = getattr(entry, component)
                if component not in organized_data[year][interval]:
                    organized_data[year][interval][component] = 0
                organized_data[year][interval][component] = component_value  # Direct assignment for 'none' operation
        else:
            for component in aggregation_rule.get('fields', []):
                component_value = getattr(entry, component)
                if component not in organized_data[year][interval]:
                    organized_data[year][interval][component] = 0
                organized_data[year][interval][component] += component_value  # Summing for other operations

    logging.debug(f"Organized Data: {organized_data}")

    # Convert the organized data into a format suitable for the chart
    chart_data = {
        'labels': [],  # List of years
        'datasets': []
    }

    component_labels = additional_info.get('data_labels', ['Component 1', 'Component 2'])
    colors = additional_info.get('colors', ['#007bff', '#28a745'])  # Default colors

    for interval in sorted({interval for year_data in organized_data.values() for interval in year_data}):
        for idx, component in enumerate(data_key.get('metrics', aggregation_rule.get('fields', []))):
            dataset = {
                'label': f"{component_labels[idx]} - Interval {interval}",
                'data': [],
                'backgroundColor': colors[idx % len(colors)]
            }
            for year in sorted(organized_data.keys()):
                if year not in chart_data['labels']:
                    chart_data['labels'].append(year)
                dataset['data'].append(organized_data[year][interval].get(component, 0))
            chart_data['datasets'].append(dataset)

    logging.debug(f"Chart Data before returning: {chart_data}")
    return chart_data




# TODO this is a general purpose area-subarea dashboard generator, linked to admin_dashboard or dashboard_template template

@app.route('/admin_dashboard/<int:area_id>/<int:subarea_id>')
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def admin_dashboard(area_id, subarea_id):
    print('admin dashboard 1')
    try:
        print('admin dashboard 2')
        logging.debug(f"Fetching data mapping for area_id={area_id} and subarea_id={subarea_id}")
        mapping = DataMapping.query.filter_by(area_id=area_id, subarea_id=subarea_id).first()

        print(f"Raw data_key: {mapping.data_key}")
        print(f"Raw aggregation_rule: {mapping.aggregation_rule}")
        print(f"Raw additional_info: {mapping.additional_info}")

        if not mapping:
            flash("No data mapping found for the specified area and subarea.", "danger")
            return redirect(url_for('index'))

        print('admin dashboard 3')

        # Since the data is already a dict, we don't need to decode it
        data_key = mapping.data_key
        aggregation_rule = mapping.aggregation_rule
        additional_info = mapping.additional_info

        print('admin dashboard 4')
        logging.debug(f"Mapping found: {mapping}")

        # Perform data aggregation based on the aggregation_rule
        logging.debug(f"Performing data aggregation")
        dashboard_data = perform_data_aggregation(data_key, aggregation_rule, area_id, subarea_id, additional_info)
        print(f"Chart Data before returning: {dashboard_data}")

        # Convert the result back to JSON strings to pass to the template
        logging.debug(f"Converting data to JSON strings")
        dashboard_data_json = json.dumps(dashboard_data)
        additional_info_json = json.dumps(additional_info)

        print('admin dashboard 9')
        return render_template('admin_dashboard.html',
                               area_id=area_id,
                               subarea_id=subarea_id,
                               dashboard_data=dashboard_data_json,
                               representation_type=mapping.representation_type,
                               additional_info=additional_info_json)
    except ValueError as ve:
        logging.error(f"ValueError in admin_dashboard route: {ve}")
        flash(f"Value error occurred: {ve}", "danger")
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error in admin_dashboard route: {e}")
        flash("An error occurred while generating the dashboard.", "danger")
        return redirect(url_for('index'))


@app.route('/questionnaire_psf')
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def questionnaire_psf():
    return render_template('dynamic_questionnaire_psf.html')


@app.route('/submit_response_psf', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def submit_response_psf():
    data = request.form
    questionnaire_id = data.get('questionnaire_id')
    user_id = data.get('user_id')
    company_id = 1  # Replace with actual company_id
    status_id = data.get('status_id')
    answers = {key: data.get(key) for key in data if key.startswith('answer_')}
    files = {key: request.files.get(key) for key in request.files if key.startswith('file_')}

    # Store answers and files appropriately
    response = Response_psf(
        questionnaire_id=questionnaire_id,
        user_id=user_id,
        company_id=company_id,
        answers=answers,
        status_id=status_id
    )

    db.session.add(response)
    db.session.commit()

    return jsonify({"message": "Response submitted successfully"})


# Route to list images
@app.route('/list_images')
def list_images():
    images_dir = os.path.join(app.static_folder, 'images')
    images = os.listdir(images_dir)
    images = [f'/static/images/{img}' for img in images if img.endswith(('png', 'jpg', 'jpeg', 'gif'))]
    return jsonify(images)

@app.route('/admin_news', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def admin_news():
    if request.method == 'POST':
        headline = request.form['headline']
        short_text = request.form['short_text']
        image_url = request.form['image_url']
        link_type = request.form['link_type']
        more_link = request.form['more_link']
        body = request.form['body'] if link_type == 'internal' else None
        page = 'home'
        company_id = 0
        user_id = current_user.id
        role_id = 1  # Admin
        area_id = None
        content_type = 'news'
        content = {
            'headline': headline,
            'short_text': short_text,
            'image_url': image_url,
            'link_type': link_type,
            'more_link': more_link,
            'body': body
        }
        new_entry = Container(
            content=content,
            content_type=content_type,
            page=page,
            company_id=company_id,
            role_id=role_id,
            area_id=area_id
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('News item created successfully!')
        return redirect(url_for('admin_news'))

    news_items = Container.query.filter_by(content_type='news').all()
    return render_template('admin_news.html', news_items=news_items)


@app.route('/edit_news/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_news(id):
    news_item = Container.query.get_or_404(id)
    if request.method == 'POST':
        headline = request.form['headline']
        short_text = request.form['short_text']
        image_url = request.form['image_url']
        link_type = request.form['link_type']
        more_link = request.form['more_link']
        body = request.form['body']

        # Update the JSONB content field explicitly
        news_item.content = {
            'headline': headline,
            'short_text': short_text,
            'image_url': image_url,
            'link_type': link_type,
            'more_link': more_link,
            'body': body
        }

        try:
            db.session.flush()  # Add this line
            db.session.commit()
            flash('News item updated successfully!')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the news item. Please try again.', 'danger')

        return redirect(url_for('admin_news'))

    return render_template('edit_news.html', news_item=news_item)


@app.route('/delete_news/<int:id>')
@login_required
@roles_required('Admin')
def delete_news(id):
    news_item = Container.query.get_or_404(id)
    db.session.delete(news_item)
    db.session.commit()
    flash('News item deleted successfully!')
    return redirect(url_for('admin_news'))


@app.route('/public_news')
@login_required
@roles_required('Admin', 'Authority', 'Manager', 'Employee', 'Provider')
def public_news():
    news_items = Container.query.filter_by(content_type='news').all()
    return render_template('public_news.html', news_items=news_items)


@app.route('/news/<int:id>')
@login_required
@roles_required('Admin', 'Authority', 'Manager', 'Employee', 'Provider')
def detailed_news(id):
    news_item = Container.query.get_or_404(id)
    return render_template('detailed_news.html', news_item=news_item)


@app.route('/create_ticket', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Authority', 'Manager', 'Employee', 'Provider')
def create_ticket():
    form = TicketForm()
    form.subject.choices = [(s.id, s.name) for s in Subject.query.filter_by(tier_1='Tickets').all()]
    if form.validate_on_submit():
        new_ticket = Ticket(
            user_id=current_user.id,
            subject_id=form.subject.data,
            description=form.description.data,
            status_id=2  # Default status "Open"
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash('Ticket created successfully!')
        return redirect(url_for('view_tickets'))
    return render_template('create_ticket.html', form=form)

@app.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id:
        flash('You do not have permission to edit this ticket.')
        return redirect(url_for('view_tickets'))
    form = TicketForm(obj=ticket)
    form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        ticket.subject_id = form.subject.data
        ticket.description = form.description.data
        db.session.commit()
        flash('Ticket updated successfully!')
        return redirect(url_for('view_tickets'))
    return render_template('edit_ticket.html', form=form, ticket=ticket)

@app.route('/view_tickets')
@login_required
def view_tickets():
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('view_tickets.html', tickets=tickets)


@app.route('/admin_tickets')
@login_required
@roles_required('Admin')
def admin_tickets():
    if 'Admin' not in [role.name for role in current_user.roles]:
        flash('You do not have permission to view this page.')
        return redirect(url_for('index'))
    tickets = Ticket.query.all()
    return render_template('admin_tickets.html', tickets=tickets)

@app.route('/respond_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def respond_ticket(ticket_id):
    if 'Admin' not in [role.name for role in current_user.roles]:
        flash('You do not have permission to respond to tickets.')
        return redirect(url_for('index'))
    ticket = Ticket.query.get_or_404(ticket_id)
    form = ResponseForm()
    form.status.choices = [(s.id, s.name) for s in Status.query.all()]
    if form.validate_on_submit():
        ticket.response = form.response.data
        ticket.status_id = form.status.data
        db.session.commit()
        flash('Response sent successfully!')
        return redirect(url_for('admin_tickets'))
    return render_template('respond_ticket.html', form=form, ticket=ticket)


@app.route('/update_account', methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.mid_name = form.mid_name.data
        current_user.last_name = form.last_name.data
        current_user.title = form.title.data
        current_user.address = form.address.data
        current_user.address1 = form.address1.data
        current_user.city = form.city.data
        current_user.province = form.province.data
        current_user.region = form.region.data
        current_user.zip_code = form.zip_code.data
        current_user.country = form.country.data
        current_user.tax_code = form.tax_code.data
        current_user.mobile_phone = form.mobile_phone.data
        current_user.work_phone = form.work_phone.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('home'))  # Redirect to home page or another page
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.mid_name.data = current_user.mid_name
        form.last_name.data = current_user.last_name
        form.title.data = current_user.title
        form.address.data = current_user.address
        form.address1.data = current_user.address1
        form.city.data = current_user.city
        form.province.data = current_user.province
        form.region.data = current_user.region
        form.zip_code.data = current_user.zip_code
        form.country.data = current_user.country
        form.tax_code.data = current_user.tax_code
        form.mobile_phone.data = current_user.mobile_phone
        form.work_phone.data = current_user.work_phone
    return render_template('account.html', title='Account', form=form)


@app.route('/set_cookies', methods=['POST'])
def set_cookies():
    response = make_response(redirect(url_for('index')))
    consent = request.form.get('consent')

    if consent == 'allow_all':
        response.set_cookie('analytics', 'true', max_age=60 * 60 * 24 * 30)  # 30 days
        response.set_cookie('marketing', 'true', max_age=60 * 60 * 24 * 30)
    elif consent == 'reject_all':
        response.set_cookie('analytics', 'false', max_age=60 * 60 * 24 * 30)
        response.set_cookie('marketing', 'false', max_age=60 * 60 * 24 * 30)
    elif consent == 'customize':
        analytics = request.form.get('analytics', 'false')
        marketing = request.form.get('marketing', 'false')
        response.set_cookie('analytics', analytics, max_age=60 * 60 * 24 * 30)
        response.set_cookie('marketing', marketing, max_age=60 * 60 * 24 * 30)

    # Set a cookie to indicate that the user has made a choice regarding cookies
    response.set_cookie('cookies_accepted', 'true', max_age=60 * 60 * 24 * 30)

    # Update the user's cookies_accepted field in the database
    if current_user.is_authenticated:
        user = Users.query.get(current_user.id)
        user.cookies_accepted = True
        db.session.commit()

    current_app.logger.debug("Set cookies accepted to true in both cookie and database")

    return response



def generate_event_instances(event):
    instances = []
    if event.recurrence and event.recurrence_end:
        start_date = event.start
        end_date = datetime.combine(event.recurrence_end, datetime.min.time())  # Convert date to datetime
        duration = event.end - event.start

        if event.recurrence == 'daily':
            freq = rrule.DAILY
        elif event.recurrence == 'weekly':
            freq = rrule.WEEKLY
        elif event.recurrence == 'monthly':
            freq = rrule.MONTHLY
        elif event.recurrence == 'quarterly':
            freq = rrule.MONTHLY
            interval = 3
        else:
            return instances

        rr = rrule.rrule(freq, dtstart=start_date, until=end_date, interval=interval)

        for dt in rr.between(start_date, end_date, inc=True):
            instance_start = datetime(dt.year, dt.month, dt.day, event.start.hour, event.start.minute)
            instance_end = instance_start + duration  # Adjust end time as needed
            instances.append({
                'title': event.title,
                'start': instance_start.isoformat(),
                'end': instance_end.isoformat(),
                'description': event.description,
                'all_day': event.all_day,
                'location': event.location,
                'color': event.color,
                'recurrence': event.recurrence,
                'recurrence_end': event.recurrence_end.isoformat() if event.recurrence_end else None
            })

    return instances


@app.route('/api/events')
@login_required
def get_events():
    try:
        start_date = request.args.get('start', default=None)
        end_date = request.args.get('end', default=None)

        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)

        if current_user and current_user.is_authenticated:
            user_id = current_user.id
            company_id = current_user.company_id
            is_manager = Role.query.join(UserRoles).filter(UserRoles.user_id == user_id, Role.name == 'Manager').count() > 0
        else:
            return jsonify({'error': 'User not authenticated'}), 401

        if start_date and end_date:
            if is_manager:
                events = Event.query.filter(Event.company_id == company_id, Event.start >= start_date, Event.end <= end_date).all()
            else:
                events = Event.query.filter(Event.user_id == user_id, Event.start >= start_date, Event.end <= end_date).all()
        else:
            if is_manager:
                events = Event.query.filter_by(company_id=company_id).all()
            else:
                events = Event.query.filter_by(user_id=user_id).all()

        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        app.logger.error(f"Error fetching events: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/add-event', methods=['GET', 'POST'])
@login_required
def add_event():
    date = request.args.get('date')
    time = request.args.get('time', '00:00:00')

    app.logger.info(f"Received date: {date}")
    app.logger.info(f"Received time: {time}")

    try:
        # Combine date and time strings and convert to datetime object
        if date and time:
            datetime_str = f"{date} {time}"
            app.logger.info(f"Combined datetime string: {datetime_str}")
            default_start = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            default_end = default_start + timedelta(hours=1)
            app.logger.info(f"Parsed default start: {default_start}, Parsed default end: {default_end}")
        else:
            now = datetime.now()
            default_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            default_end = default_start + timedelta(hours=1)
            app.logger.info(f"Generated default start: {default_start}, Generated default end: {default_end}")

        form = EventForm()

        # Use datetime objects for the form fields
        if request.method == 'GET':
            form.start.data = default_start
            form.end.data = default_end
            form.recurrence_end.data = default_end.date()

        if request.method == 'POST':
            app.logger.info(f"Form data received: {request.form}")

            if not form.validate():
                app.logger.warning('Form validation failed (POST)')
                for fieldName, errorMessages in form.errors.items():
                    for err in errorMessages:
                        app.logger.warning(f"Error in {fieldName}: {err}")
                app.logger.warning(f"Form errors: {form.errors}")
            else:
                app.logger.info(f"Form validation succeeded: {form.data}")

        print('validation check')
        if form.validate_on_submit():
            print('valid!')
            app.logger.info(f"Form validated: {form.data}")
            app.logger.info(f"Start: {form.start.data}, End: {form.end.data}, Recurrence End: {form.recurrence_end.data}")

            if current_user and current_user.is_authenticated:
                user_id = current_user.id
                company_id = session.get('company_id')
                app.logger.info(f"Current user: {current_user}, User ID: {user_id}, Company ID: {company_id}")

                event = Event(
                    title=form.title.data,
                    start=form.start.data,
                    end=form.end.data,
                    description=form.description.data,
                    all_day=form.all_day.data,
                    location=form.location.data,
                    user_id=user_id,
                    company_id=company_id,
                    color=form.color.data,
                    recurrence=form.recurrence.data,
                    recurrence_end=form.recurrence_end.data if form.recurrence_end.data else None
                )

                if event.recurrence:
                    instances = generate_event_instances(event)  # Call your function to generate instances
                    for instance_data in instances:
                        new_event = Event(
                            title=instance_data['title'],
                            start=datetime.fromisoformat(instance_data['start']),
                            end=datetime.fromisoformat(instance_data['end']),
                            description=instance_data['description'],
                            all_day=instance_data['all_day'],
                            location=instance_data['location'],
                            color=instance_data['color'],
                            recurrence=instance_data['recurrence'],
                            recurrence_end=instance_data['recurrence_end'],
                            user_id=user_id,
                            company_id=company_id,
                        )

                        print('added branch 1')
                        db.session.add(new_event)
                else:
                    print('added branch 2')
                    db.session.add(event)

                db.session.commit()

                print('committed')
                flash('Event added successfully!', 'success')
                app.logger.info('Event added successfully!')
                return redirect(url_for('calendar'))
            else:
                flash('User not logged in', 'warning')
                app.logger.warning('User not logged in')
                return redirect(url_for('login'))
        else:
            app.logger.warning('Form validation failed on submit')
            app.logger.warning(f"Form errors on submit: {form.errors}")

        return render_template('add_event.html', form=form)

    except ValueError as e:
        app.logger.error(f"ValueError: {e}")
        flash('Error processing date and time. Please try again.', 'danger')
        return redirect(url_for('calendar'))
    except Exception as e:
        app.logger.error(f"Exception: {e}")
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('calendar'))


@app.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if not current_user or not current_user.is_authenticated:
        flash('User not authenticated', 'warning')
        return redirect(url_for('login'))

    is_manager = Role.query.join(UserRoles).filter(UserRoles.user_id == current_user.id, Role.name == 'Manager').count() > 0

    if not is_manager and event.user_id != current_user.id:
        flash('Permission denied', 'danger')
        return redirect(url_for('calendar'))

    form = EventForm(obj=event)

    if request.method == 'POST':
        app.logger.info(f"Form data received: {request.form}")
        if form.validate_on_submit():
            try:
                event.title = form.title.data
                event.start = form.start.data
                event.end = form.end.data
                event.description = form.description.data
                event.all_day = form.all_day.data
                event.location = form.location.data
                event.color = form.color.data
                event.recurrence = form.recurrence.data

                if form.recurrence.data:
                    event.recurrence_end = form.recurrence_end.data
                else:
                    event.recurrence_end = None

                db.session.commit()
                flash('Event updated successfully!', 'success')
                return redirect(url_for('calendar'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error updating event: {e}")
                flash('An error occurred while updating the event. Please try again.', 'danger')
        else:
            app.logger.warning('Form validation failed')
            app.logger.warning(f"Form errors 1: {form.errors}")

    return render_template('edit_event.html', form=form, event=event)


@app.route('/delete-event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    if not current_user or not current_user.is_authenticated:
        flash('User not authenticated', 'warning')
        return redirect(url_for('login'))

    is_manager = Role.query.join(UserRoles).filter(UserRoles.user_id == current_user.id, Role.name == 'Manager').count() > 0

    if not is_manager and event.user_id != current_user.id:
        flash('Permission denied', 'danger')
        return redirect(url_for('calendar'))

    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('calendar'))

@app.route('/update-event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)

    if not current_user or not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated'}), 401

    is_manager = Role.query.join(UserRoles).filter(UserRoles.user_id == current_user.id, Role.name == 'Manager').count() > 0

    if not is_manager and event.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    try:
        new_start = datetime.fromisoformat(request.form.get('start'))
        new_end = datetime.fromisoformat(request.form.get('end'))
        event.start = new_start
        event.end = new_end
        db.session.commit()
        return jsonify({'success': 'Event updated successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error updating event: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')


@app.route('/cookie-settings')
def cookie_settings():
    return render_template('cookie_settings.html')


@app.route('/update_cookies', methods=['POST'])
def update_cookies():
    response = make_response(redirect(url_for('cookie_settings')))
    analytics = 'true' if request.form.get('analytics') == 'true' else 'false'
    marketing = 'true' if request.form.get('marketing') == 'true' else 'false'

    response.set_cookie('analytics', analytics, max_age=60 * 60 * 24 * 30)  # 30 days
    response.set_cookie('marketing', marketing, max_age=60 * 60 * 24 * 30)

    # Update the user's cookie preferences in the database if necessary
    user = Users.query.get(current_user.id)
    user.analytics = analytics == 'true'
    user.marketing = marketing == 'true'
    db.session.commit()

    current_app.logger.debug("Updated cookie preferences: Analytics - {}, Marketing - {}".format(analytics, marketing))

    return response


@app.route('/products_page')
@login_required
def products_page():
    products = Product.query.all()
    form = AddProductToCartForm()
    return render_template('products.html', products=products, form=form)

@app.route('/plans_page')
@login_required
def plans_page():
    form = AddPlanToCartForm()
    try:
        plans = Plan.query.all()
        return render_template('plans.html', plans=plans, form=form)
    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while fetching plans", 500

@app.route('/add_plan_to_cart/<int:plan_id>', methods=['POST'])
@login_required
def add_plan_to_cart(plan_id):
    # Logic to add the plan to the cart
    flash('Plan added to cart successfully!', 'success')
    return redirect(url_for('plans_page'))


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    print('add to cart 1')
    try:
        quantity = int(request.form.get('quantity', 1))
        print(f'Received quantity: {quantity}')
        product_to_add = Product.query.get(product_id)
        print('add to cart 2', product_to_add)
        user_id = current_user.id
        company_id = session.get('company_id')
        print(f'user_id: {user_id}, company_id: {company_id}')

        if product_to_add:
            print('add to cart 3', product_to_add)
            cart_item = Cart.query.filter_by(product_id=product_id, user_id=user_id, company_id=company_id).first()
            if cart_item:
                print('add to cart 4', cart_item)
                cart_item.quantity += quantity
            else:
                print('add to cart 5', product_to_add)
                new_cart_item = Cart(
                    product_id=product_to_add.id,
                    user_id=user_id,
                    company_id=company_id,
                    quantity=quantity,
                    price=product_to_add.price
                )
                db.session.add(new_cart_item)
            db.session.commit()
            print('added to cart (', product_to_add.id, ')')
            flash('Product added to cart successfully!', 'success')
        else:
            print('add to cart 7 no prod')
            flash('Product not found.', 'error')
        return redirect(url_for('products_page'))
    except Exception as e:
        print(f'add to cart 8 other errors: {e}')
        db.session.rollback()
        flash('An error occurred while adding to cart.', 'error')
        return redirect(url_for('products_page'))


def get_cart_items(user_id, company_id, role):
    print('getting items')
    if 'Manager' in role:
        cart_items = Cart.query.filter_by(company_id=company_id).all()
    else:
        cart_items = Cart.query.filter_by(user_id=user_id).all()

    product_ids = [item.product_id for item in cart_items]
    products = Product.query.filter(product.id.in_(product_ids)).all()

    items = []
    for item in cart_items:
        product = next((p for p in products if p.id == item.product_id), None)
        if product:
            items.append({
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': item.quantity
            })
    return items


@app.route('/cart')
@login_required
def cart():
    try:
        # Fetch user and company details from session
        company_id = session.get('company_id', -1)
        user_id = current_user.id
        logging.debug(f'Cart route accessed by user: {user_id}, company: {company_id}')

        # Determine the correct cart items based on user role
        if 'Manager' in [role.name for role in current_user.roles]:
            cart_items = Cart.query.filter_by(company_id=company_id).all()
        else:
            cart_items = Cart.query.filter_by(user_id=user_id).all()

        logging.debug(f"Cart items from DB: {cart_items}")

        # Fetch product details for items in the cart
        product_ids = [item.product_id for item in cart_items]
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        product_dict = {product.id: product for product in products}

        # Prepare items for rendering
        filtered_cart_items = []
        for item in cart_items:
            product = product_dict.get(item.product_id)
            if product:
                filtered_cart_items.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': item.quantity
                })

        # Calculate the total price of the cart items
        total_price = sum(item['price'] * item['quantity'] for item in filtered_cart_items)

        form = UpdateCartItemForm()

        return render_template('cart.html', cart=filtered_cart_items, total_price=total_price, form=form)
    except Exception as e:
        logging.error(f"Error fetching cart items: {e}")
        return "An error occurred", 500


@app.route('/update_cart_item/<int:product_id>', methods=['POST'])
@login_required
def update_cart_item(product_id):
    try:
        quantity = int(request.form.get('quantity', 1))
        user_id = current_user.id
        company_id = session.get('company_id')

        cart_item = Cart.query.filter_by(product_id=product_id, user_id=user_id, company_id=company_id).first()
        if cart_item:
            cart_item.quantity = quantity
            db.session.commit()
            flash('Cart updated successfully!', 'success')
        else:
            flash('Cart item not found.', 'error')
        return redirect(url_for('cart'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the cart.', 'error')
        return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>', methods=['GET'])
@login_required
def remove_from_cart(product_id):
    try:
        user_id = current_user.id
        company_id = session.get('company_id')

        cart_item = Cart.query.filter_by(product_id=product_id, user_id=user_id, company_id=company_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart successfully!', 'success')
        else:
            flash('Cart item not found.', 'error')
        return redirect(url_for('cart'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while removing the item from cart.', 'error')
        return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    try:
        user_id = current_user.id
        company_id = session.get('company_id')

        if request.method == 'POST':
            # Handle payment and order creation logic here

            # For simplicity, let's just clear the cart after "checkout"
            Cart.query.filter_by(user_id=user_id, company_id=company_id).delete()
            db.session.commit()
            flash('Checkout successful! Your order has been placed.', 'success')
            return redirect(url_for('products_page'))

        # For GET request, render the checkout page
        cart_items = Cart.query.filter_by(user_id=user_id, company_id=company_id).all()
        total_price = sum(item.price * item.quantity for item in cart_items)
        return render_template('checkout.html', cart=cart_items, total_price=total_price)

    except Exception as e:
        db.session.rollback()
        flash('An error occurred during checkout.', 'error')
        return redirect(url_for('cart'))


@app.route('/checkout_success')
def checkout_success():
    Cart.query.delete()
    db.session.commit()
    return render_template('checkout_success.html')


if __name__ == '__main__':
    # Load menu items from JSON file
    current_dir = get_current_directory()
    json_file_path = os.path.join(current_dir, 'static', 'js', 'menuStructure101.json')
    with open(Path(json_file_path), 'r') as file:
        main_menu_items = json.load(file)

    # Create a MenuBuilder instance for the "Guest" role
    guest_menu_builder = MenuBuilder(main_menu_items, ["guest"])
    guest_menu_data = guest_menu_builder.parse_menu_data(user_roles=["guest"],
                                                         is_authenticated=False, include_protected=False)
    # Pass the "Guest" menu data to the template
    additional_data = {
        "username": "Guest",
        "is_authenticated": False,
        "public_menu": guest_menu_data
    }

    port = int(os.environ.get('PORT', 5000))

    # TODO DEBUG
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0', port=port, extra_files=['./static/js/menuStructure101.json'])