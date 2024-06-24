
# DEBUG LOGGING LOGGER TOOLBAR: see app_factory.py

# app.py (or run.py)
import re

# import logging
# from logging import FileHandler, Formatter
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_, and_, desc, func, not_, null, exists, extract, select
from sqlalchemy import distinct
from sqlalchemy.orm import sessionmaker

from sqlalchemy.exc import OperationalError
from db import db
from flask import g
from flask import flash
import datetime

from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange

from flask_session import Session
from wtforms import SubmitField
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from userManager101 import UserManager
from workflow_manager import (add_transition_log, create_card,
                              get_model_statistics, create_deadline_card,
                              create_model_card, deadline_approaching)

from app_defs import get_user_roles, create_message, generate_menu_tree
from models.user import (Users, UserRoles, Role, Container, Questionnaire, Question,
        QuestionnaireQuestions,
        Answer, Company, Area, Subarea, AreaSubareas,
        QuestionnaireCompanies, CompanyUsers, Status, Lexic,
        Interval, Subject,
        AuditLog, Post, Ticket, StepQuestionnaire,
        Workflow, Step, BaseData, Container, WorkflowSteps, WorkflowBaseData,
                         StepBaseData, Config, get_config_values)

from master_password_reset import admin_reset_password, AdminResetPasswordForm

from forms.forms import (LoginForm, ForgotPasswordForm, ResetPasswordForm101, RegistrationForm,
                         QuestionnaireCompanyForm, CustomBaseDataForm,
        QuestionnaireQuestionForm, WorkflowStepForm, WorkflowBaseDataForm,
                         BaseDataWorkflowStepForm,
        UserRoleForm, CompanyUserForm, UserDocumentsForm, StepBaseDataInlineForm,
        create_dynamic_form, CustomFileLoaderForm,
        CustomSubjectAjaxLoader, BaseSurveyForm)

from flask_mail import Mail, Message
from flask_babel import lazy_gettext as _  # Import lazy_gettext and alias it as _

from app_factory import create_app

from config.config import (extract_year_from_fy, get_current_interval, get_current_intervals,
        get_subarea_interval_type, generate_company_questionnaire_report_data, generate_area_subarea_report_data,
        check_status, check_status_limited, check_status_extended, generate_html_cards, get_session_workflows,
        generate_html_cards_progression_with_progress_bars111, generate_html_cards_progression_with_progress_bars_in_short,
        get_subarea_name, get_pd_report_from_base_data_wtq, get_if_active, get_areas, create_notification,
        get_subareas, generate_company_user_report_data, generate_user_role_report_data, create_audit_log,
        generate_questionnaire_question_report_data, generate_workflow_step_report_data, get_company_id,
        generate_workflow_document_report_data, generate_document_step_report_data, get_cet_time, remove_duplicates,
        normalize_structure, compare_structures, some_keys)

from admin_views import (ContainerAdmin, CompanyView, QuestionnaireView, QuestionView,
                         StatusView, LexicView, AreaView, StepQuestionnaireView,
        SubareaView, SubjectView, PostView, TicketView, WorkflowView, StepView, AuditLogView,
        QuestionnaireQuestionsView, WorkflowStepsView, QuestionnaireCompaniesView,
                         OpenQuestionnairesView, BaseDataView, UsersView)

from mail_service import send_simple_message, send_simple_message333
from wtforms import Form

from utils.utils import get_current_directory
from wtforms import (SelectField, BooleanField, ValidationError, EmailField)
from flask_login import login_required, LoginManager
from flask_login import login_user, current_user
from flask_cors import CORS

from flask import flash, current_app, get_flashed_messages
# from flask_admin.exceptions import ValidationError

from flask_bcrypt import Bcrypt
from flask import abort
from functools import wraps

from wtforms import IntegerField
from wtforms.fields import DateField
from crud_blueprint import create_crud_blueprint

from menu_builder import MenuBuilder

from flask_bootstrap import Bootstrap

import datetime
from datetime import datetime, timedelta
from jinja2 import Undefined

from flask_admin.form import FileUploadField
from flask import session
from flask_admin import Admin, expose, expose_plugview
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

# for graphical representation of workflows
# Additional libraries for visualization (choose one)
# Option 1: Flask-Vis (lightweight)
#from flask_wtf import FlaskForm
#from wtforms import SelectField, SubmitField

# Option 2: Plotly (more powerful)
# import plotly.graph_objects as go

import plotly.graph_objects as go

print('1')
app = create_app()
print('app created')

# Setup Mail
mail = Mail(app)
print('mail server active')

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
print('login manager active')

# Register the password reset route
app.add_url_rule('/admin_reset_password', 'admin_reset_password', admin_reset_password, methods=['GET', 'POST'])
print('url rule set')

@app.route('/set_session')
def set_session():
    session['key'] = 'value'
    return 'Session set'


@app.route('/get_session')
def get_session():
    value = session.get('key')
    return f'Session value: {value}'


@login_manager.user_loader
def load_user(user_id):
    user = user_manager.load_user(user_id)
    # print('user loaded', user)
    # print_routes()

    # clear_flashed_messages()
    if user:
        # Store user roles in the session
        session['user_roles'] = [role.name for role in user.roles] if user.roles else []
        #print('roles', session['user_roles'])
    return user


@app.before_request
def before_request():
    if current_user.is_authenticated:
        session['session_workflows'] = get_session_workflows(db.session, current_user)
        # print('session w', session['session_workflows'])
    g.current_user = current_user
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

'''
# TODO (de)activate LOGGER here
logging.basicConfig(level=logging.DEBUG)
# Set up file handler
file_handler = FileHandler('error.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(file_handler)
'''

current_interval = get_current_interval(1) #year

print('Current periods:', get_current_interval(1),
      get_current_interval(2), get_current_interval(3),
      get_current_interval(4), get_current_interval(12))

with app.app_context():
    if get_areas():
        app.config['AREAS'] = get_areas()

    for i in range(len(get_areas())):
        if get_subareas(i):
            app.config['SUBAREAS_' + str(i)] = get_subareas(i)

    intervals = get_current_intervals(db.session)
    app.config['CURRENT_INTERVALS'] = intervals

# Serializer for generating tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# TODO - eliminati tutti i blueprint per i quali c'è Admin?
# pyobjc
with app.app_context():
    # db.create_all()

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


def is_user_role(session, user_id, role_name):
    # Get user roles for the specified user ID
    user_roles = get_user_roles(session, user_id)
    # Check if the specified role name (in lowercase) is in the user's roles
    return role_name in user_roles


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


@app.errorhandler(SMTPAuthenticationError)
def handle_smtp_authentication_error(error):
    # Handle SMTP authentication errors gracefully
    return "SMTP Authentication Error: Failed to authenticate with the SMTP server.", 500


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


@app.errorhandler(OperationalError)
def handle_db_error(error):
   return render_template('db_error.html'), 500


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
    try:
        folder_path = None
        folder_name = f"company_id_{company_id}/{subfolder}"
        folder_path = os.path.join(app.config['COMPANY_FILES_DIR'], folder_name)
        print('folder_path', folder_path)
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


@app.route('/forgot_password', methods=['GET', 'POST'])
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

                flash(_('An email has been sent with instructions to reset your password.'), 'success')
            else:
                flash(_('No user found with that email address.'), 'danger')
            return redirect(url_for('forgot_password'))
        except Exception as e:
            print(f"Error: {e}")  # Log the error for debugging purposes
            flash(_('An error occurred while processing your request. Please try again later.'), 'danger')
            return render_template('access/forgot_password.html', form=form)
    return render_template('access/forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
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


@app.route("/send_email222")
def send_email222():
    mail = Mail(app)
    msg = Message("Hello from ILM",
                  sender="amarad21@gmail.com",
                  recipients=["astridel.radulescu1@gmail.com"])
    msg.body = "This is a test email sent from my App using Postfix."
    mail.send(msg)
    return "Email sent successfully!"


@app.route("/send_email")
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

            user_roles = session.get('user_roles', [])

            # Check if the lists intersect
            intersection = set(user_roles) & set(["Employee", "Manager", "Authority", "Admin"])
            allowed_roles = []
            left_menu_items = {}
            if intersection:
                left_menu_items = get_left_menu_items(list(intersection))
                allowed_roles = list(intersection)
                # prova left menu
                #left_menu_items = ["Area 1", "Area 2", "Area 3", "Item 4", "Item 5", "Item 6"]
            else:
                allowed_roles= ["Guest"]

            menu_builder_instance = MenuBuilder(main_menu_items, allowed_roles=allowed_roles)

            if limited_menu:
                menu_data = menu_builder_instance.parse_menu_data(user_roles=user_roles,
                                        is_authenticated=False, include_protected=False)
            else:
                menu_data = menu_builder_instance.parse_menu_data(user_roles=user_roles,
                                        is_authenticated=is_authenticated, include_protected=include_protected)

            buttons = []
            '''for company, records in companyRecords.items():
                buttons.append(CompanyButton(companyName=company, companyRecords=records))'''

            # Example: Generate dynamic URL for 'admin_2.admin_blueprint.index'
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

            # Check for unread notices
            if is_authenticated:
                unread_notices_count = Post.query.filter_by(user_id=current_user.id, marked_as_read=False).count()

            else:
                unread_notices_count = 0

            # TODO select containers by role, company etc!
            containers = Container.query.filter_by(page='1').all()

            # Iterate over the containers and print the 'container' field
            for container in containers:
                print('container:', container.page, container.content_type, container.content)

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
                "limited_menu": limited_menu,  # Added this line
                "left_menu_items": left_menu_items,
                "buttons": buttons,
                "admin_url": admin_url,
                "admin_2_url": admin_2_url,
                "admin_3_url": admin_3_url,
                "admin_4_url": admin_4_url,
                "admin_10_url": admin_10_url,
                "unread_notices_count": unread_notices_count,
                "containers": containers
            }

            return render_template(template, **additional_data)

        return wrapper

    return decorator



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


from sqlalchemy.exc import OperationalError

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
                    if not current_user.is_authenticated:
                        login_user(user)
                        flash('Login Successful')
                        cet_time = get_cet_time()
                        try:
                            create_message(db.session, user_id=user.id, message_type='email', subject='Security check',
                                           body='È stato rilevato un nuovo accesso al tuo account il ' +
                                                cet_time.strftime('%Y-%m-%d') + '. Se eri tu, non devi fare nulla. ' +
                                                'In caso contrario, ti aiuteremo a proteggere il tuo account; ' +
                                                "non rispondere a questa mail e contatta l'amministratore del sistema.",
                                           sender='System', company_id=None,
                                           lifespan='one-off', allow_overwrite=True)
                        except Exception as e:
                            print('Error creating logon message:', e)

                        session['user_roles'] = [role.name for role in user.roles] if user.roles else []
                        session['user_id'] = user.id
                        session['username'] = username

                        try:
                            company_user = CompanyUsers.query.filter_by(user_id=user.id).first()
                            company_id = company_user.company_id if company_user else None
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


@app.route('/access/login___', methods=['GET', 'POST'])
@limiter.limit("200/day;96/hour;12/minute")
def login___():
    form = LoginForm()
    if form.validate_on_submit() and request.method == 'POST':
        # Verify CAPTCHA
        user_captcha = request.form['captcha']
        if 'captcha' in session and session['captcha'] == user_captcha:
            # CAPTCHA entered correctly
            username = form.username.data
            password = form.password.data
            user = user_manager.authenticate_user(username, password)
            if user:
                if not current_user.is_authenticated:
                    login_user(user)
                    flash('Login Successful')
                    cet_time = get_cet_time()
                    try:
                        create_message(db.session, user_id=user.id, message_type='email', subject='Security check',
                                       body='È stato rilevato un nuovo accesso al tuo account il ' +
                                            cet_time.strftime('%Y-%m-%d') + '. Se eri tu, non devi fare nulla. ' +
                                            'In caso contrario, ti aiuteremo a proteggere il tuo account; ' +
                                            "non rispondere a questa mail e contatta l'amministratore del sistema.",
                                       sender='System', company_id=None,
                                       lifespan='one-off', allow_overwrite=True)
                    except Exception as e:
                        print('Error creating logon message:', e)

                    session['user_roles'] = [role.name for role in user.roles] if user.roles else []
                    session['user_id'] = user.id
                    session['username'] = username

                    try:
                        company_user = CompanyUsers.query.filter_by(user_id=user.id).first()
                        company_id = company_user.company_id if company_user else None
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



@app.route('/left_menu', methods=['GET', 'POST'])
@generate_route_and_menu('/home', allowed_roles=["Employee"], template='home/left_menu.html')
def left_menu():
    #app.logger.debug("Home route accessed")

    username = current_user.username if current_user.is_authenticated else "Guest"
    if callable(getattr(current_user, 'is_authenticated', None)):
        is_authenticated = current_user.is_authenticated()
    else:
        is_authenticated = current_user.is_authenticated
    user_roles = session.get('user_roles', [])
    allowed_roles = ["Employee", "Manager", "Authority", "Admin", "Provider"]
    #menu_builder_instance = MenuBuilder(main_menu_items, allowed_roles=allowed_roles)

    # TODO select containers by role, company etc!
    containers = Container.query.filter_by(page='1').all()

    print('containers 3', containers)

    # Check if the lists intersect
    intersection = set(user_roles) & set(allowed_roles)

    left_menu_items = []
    if intersection:
        left_menu_items = get_left_menu_items(list(intersection))
    else:
        pass

    # Check for unread notices
    if is_authenticated:
        unread_notices_count = Post.query.filter_by(user_id=current_user.id, marked_as_read=False).count()

    else:
        unread_notices_count = 0

    additional_data = {
        "username": current_user.username,
        "is_authenticated": current_user.is_authenticated,
        "user_roles": user_roles,
        "unread_notices_count": unread_notices_count,
        "main_menu_items": None,
        "admin_menu_data": None,
        "authority_menu_data": None,
        "manager_menu_data": None,
        "employee_menu_data": None,
        "guest_menu_data": None,
        "allowed_roles": allowed_roles,
        "limited_menu": limited_menu,
        "left_menu_items": left_menu_items,
        "containers": containers,
    }
    print('additional data', additional_data)
    return render_template('home/home.html', **additional_data)


@app.route('/')
@generate_route_and_menu('/', allowed_roles=["Guest"], template='home/home.html', include_protected=False,
                         limited_menu=True)
def index():

    # app.logger.debug("Home route accessed")
    user_id = session.get('user_id')
    user_roles = session.get('user_roles', [])
    #user_roles = ['Guest']

    # Create MenuBuilder with user roles
    menu_builder = MenuBuilder(main_menu_items, allowed_roles=user_roles)
    # Generate menu for the current user
    generated_menu = menu_builder.generate_menu(user_roles=user_roles, is_authenticated=True,
                                                include_protected=False)
    pass
    # return render_template('home/home.html', **additional_data)


@app.route('/access/logout', methods=['GET'])
def logout():

    # Clear the user session
    # session.clear()
    # Clear the user roles from the session
    # session.pop('user_roles', None)

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



# TODO add Home and Back buttons
@app.route('/document_workflow_visualization_d3js')
def workflow_visualization():
    return render_template('document_workflow_visualization_d3js.html')


@app.route('/custom_base_atti')
def custom_base_atti_index():
    form = CustomFileLoaderForm()  # Instantiate your form object here
    return render_template('custom_file_loader.html', form=form)


@app.route('/user_documents_d3')
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


@app.route('/user_documents')
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

                print('no workflow data for first document')
                #app.logger.info("No workflow data found for the first document")
                #return render_template('workflow/no_workflow_data.html')  # Handle case where no workflow data exists
                pass

        else:
            print('no docs for current user')
            #app.logger.info("No documents found for the current user")
            #return render_template('workflow/no_documents.html')  # Handle the case where no documents exist

    except Exception as e:
        #app.logger.error("An error occurred: %s", e)
        return render_template('error.html', error_message=str(e))  # Render a generic error page



# Document workflow view route (using Plotly)
@app.route('/documents/<int:company_id>/<int:base_data_id>/<int:workflow_id>', methods=['GET', 'POST'])
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


class CustomStepQuestionnaireForm(Form):
    inline_form = None

class CheckboxField(BooleanField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = True
        else:
            self.data = False
    def populate_obj(self, obj, name):
        setattr(obj, name, "Yes" if self.data else "No")  # Customize as per your model


# admin -  f l u s s i  precomplaint
class Flussi_dataView(ModelView):
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 1  # Define subarea_id as a class attribute
    area_id = 1

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Flussi_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Flussi_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = (
    'interval_ord', 'fi0', 'lexic', 'subject', 'fi1', 'fi2', 'fi3', 'fc1')  # Add 'lexic_id' to column_list

    form_columns = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fc1')  # Remove 'lexic_id' from form_columns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Totale',
                     'fi2': 'IVI',
                     'fi3': 'Altri',
                     'fc1': 'Nome venditore'}

    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)',
                           'fi1': 'Inserisci numero totale di casi registrati',
                           'fi2': 'di cui IVI',
                           'fi3': 'altri (IVI+Altri=Totale)',
                           'fc1': "Nome dell'utente venditore"}

    # Customize inlist for the View class
    column_default_sort = ('subject_id', True)
    column_searchable_list = (
    'lexic.name', 'subject.name', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fc1')  # Adjust based on your model structure
    column_filters = ('lexic.name', 'subject.name', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fc1')

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    def _lexic_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.lexic:
            if isinstance(model.lexic, Lexic):  # Check if the subject is an instance of Subject
                return model.lexic.name
            else:
                return Lexic.query.get(model.lexic).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter,
        'lexic': _lexic_formatter
    }

    def scaffold_form(self):
        form_class = super(Flussi_dataView, self).scaffold_form()
        # Set default values for specific fields

        # Get the current year
        current_year = datetime.now().year
        # Generate choices for the year field from current_year - 5 to current_year + 1
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        # Set the default value to the current year
        default_year = str(current_year)
        # Dynamically determine interval_ord options based on subject_id
        form_class.fi0 = SelectField(
            'Anno',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        form_class.subject_id = SelectField(
            'Oggetto',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Utenti").all()]
        )

        form_class.lexic_id = SelectField(
            'Tipo pre-complaint',
            validators=[InputRequired()],
            coerce=int,
            choices=[(lexic.id, lexic.name) for lexic in Lexic.query.filter_by(category="Precomplaint").all()]
        )

        return form_class

    def create_model(self, form):
        model = super(Flussi_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.subject_id = form.subject.data.id  # Set the subject_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')


    def get_query(self):

        #query = self.session.query(self.model).filter_by(data_type=self.subarea_name)
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)


    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False


    def on_model_change(self, form, model, is_created):

        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        subarea_name = self.subarea_name
        status_id = 1

        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=self.subarea_id)

        interval_id = config_values[0]
        interval_ord = form.interval_ord.data
        year_id = form.fi0.data
        # Get the lexic_id value from the form
        lexic_id = form.lexic_id.data
        subject_id = form.subject_id.data

        record_type = 'control_area'
        data_type = self.subarea_name

        legal_document_id = None

        if form.fi2.data is None or form.fi3.data is None:
            raise ValidationError("Please enter all required data.")

        if (form.fi1.data + form.fi2.data + form.fi3.data == 0) or \
            (form.fi1.data < 0 or form.fi2.data < 0 or form.fi3.data < 0) or \
            (form.fi1.data != form.fi2.data + form.fi3.data):
            raise ValidationError("Please check the values you entered.")

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null")

        # - Validate data and Save the model
        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        # no "attached file missing check" here
        # perform actions relevant to both creation and edit:
        with app.app_context():

            # include fi1-3, fn1-3, fc1-3 AS NEEDED
            # interval_id = 1
            result, message = check_status_extended(is_created, company_id,
                                                    lexic_id, subject_id, legal_document_id, interval_ord,
                                                    interval_id, year_id, area_id, subarea_id,
                                                    form.fi1.data, None, None,
                                                    None, None, None,
                                                    form.fc1.data, None, None,
                                                    datetime.today(), db.session)

        if result == False:
            raise ValidationError(message)
            pass

        # Assign the value to the model
        model.lexic_id = lexic_id
        model.updated_on = datetime.now()  # Set the created_on
        model.user_id = user_id
        model.company_id = company_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.fi0 = year_id
        model.interval_id = interval_id
        model.interval_ord = interval_ord
        model.status_id = status_id
        model.subject_id = subject_id
        model.legal_document_id = legal_document_id

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model


class MyStringField(StringField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, default='Inserire commento', **kwargs)
        self.help_text = 'Click to edit'  # Store help text separately


class MyIntegerField(IntegerField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, default=datetime.now().year, **kwargs)


class MyIntegerIntervalField(IntegerField):
    """Custom field for selecting an interval based on area and subarea IDs.

    - Leverages Flask's app context for database access.
    - Validates user-selected interval against available options.
    - Provides flexibility for customization and error handling.

    Args:
        area_id (int): Area ID.
        subarea_id (int): Subarea ID.
        get_current_intervals (callable): Function to retrieve current intervals.
        get_subarea_name (callable): Function to retrieve subarea name.
        get_subarea_interval_type (callable): Function to determine interval type.
        default (int, optional): Default interval if no selection is made.

    Raises:
        ValidationError: If the selected interval is invalid.
    """

    def __init__(self, *args, area_id, subarea_id,
                 get_current_intervals, get_subarea_name, get_subarea_interval_type,
                 default=None, **kwargs):
        super().__init__(*args, default=default, **kwargs)
        self.area_id = area_id
        self.subarea_id = subarea_id
        self.get_current_intervals = get_current_intervals
        self.get_subarea_name = get_subarea_name
        self.get_subarea_interval_type = get_subarea_interval_type

# TODO *** salva file (attachment) in folder company (dove si trova? perché non funziona più?)

@app.route('/file-upload', methods=['POST'])
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


def generate_new_id(model):
    # Get the maximum ID from the database
    max_id = db.session.query(db.func.max(model.id)).scalar()
    # If there are no records in the table, start with ID 1
    if max_id is None:
        return 1
    else:
        # Otherwise, increment the maximum ID by one
        return max_id + 1


# qui base
class Atti_BaseView(BaseView):
    subarea_id = 2  # Define subarea_id as a class attribute
    area_id = 1

    def __init__(self, name='Base View Atti', category='Base Views', endpoint='custom_base_atti'):
        super(Atti_BaseView, self).__init__(name, category, endpoint)

    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        fi0 = request.args.get('fi0')
        interval_id = request.args.get('interval_id')
        interval_ord = request.args.get('interval_ord')

        # Access the form object passed from the ModelView
        form = request.args.get('form')

        # Set a simple key-value pair in the session to test session functionality
        session['key'] = 'value'
        return render_template('custom_file_loader.html', form=form)


# 1001
# TODO **** sistemare la doppia creazione di record in inline - the action template looks good
# otherwise Contingencies is better -

class Atti_dataView(ModelView):

    can_export = True  # Default to enabled

    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # inline_models = [(StepBaseDataInlineForm, StepBaseData, 'ONE_TO_MANY')]  # Assuming a one-to-one relationship
    form_base_class = CustomBaseDataForm  # Use our custom form class
    create_template = 'admin/area_1/create_base_data_2.html'
    subarea_id = 2
    area_id = 1

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc2']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc2': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Atti_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Atti_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    '''
    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False
    '''

    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # Specify the columns to display in the edit view
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    #'interval_ord', 'fi0', 'subject_id', 'fc2',
    # Replace the StringField with FileUploadField

    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati', 'no_action': 'Dichiarazione di assenza di documenti (1)'}

    form_extra_fields = {
        'file_path': FileUploadField('File', base_path=app.config['UPLOAD_FOLDER'])
    }

    form_overrides = {
        'no_action': CheckboxField
    }

    column_filters = ('subject', 'fc2', 'no_action')  # Adjust based on your model structure
    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        # Fetch StepBaseData records related to the provided model IDs
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()

        # Fetch model records related to the provided model IDs
        model_records = BaseData.query.filter(BaseData.id.in_(ids)).all()

        # Render the template to display the records
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records, model_records=model_records)


    # TODO ***** Implement Next Step Action
    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        print('Implement next step action')
        pass


    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter
    }

    def scaffold_form(self):
        form_class = super(Atti_dataView, self).scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )
        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        current_interval = [t[2] for t in intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        # Remove 'subject_id' field from the form
        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Legale").all()]
        )
        #delattr(form_class, 'subject_id')
        form_class.no_action = CheckboxField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        return form_class #ExtendedForm


    def _validate_no_action(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is None and not no_action_value:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is not None and no_action_value:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)


    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)

        # Reset form data
        form.populate_obj(model)

        # Get the inline form data
        # TODO eliminated on 26Mar to cope with duplicated records in the INLINE
        # inline_form_data = form.inline_form  # Assuming 'inline_form' is the attribute holding the inline form data

        uploaded_file = form.file_path.data
        print('1 - uploaded file', uploaded_file)

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)
        interval_id = nr_intervals
        status_id = 1
        record_type = 'control_area'

        year_id = form.fi0.data
        interval_ord = form.interval_ord.data
        subject_id = form.subject_id.data

        if form.date_of_doc.data > datetime.now():
            raise ValidationError(f"Date of document cannot be a future date.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError(f"Date of document must be consistent with the reporting year.")

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null.")

        if form.subject_id.data == None:
            raise ValidationError(f"Document type can not be null.")

        # - Validate data - Save the model
        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass


        # Perform actions relevant to both creation and edit:
        with app.app_context():
            result, message = check_status_limited(is_created, company_id,
                                subject_id, None, year_id, interval_ord,
                                    interval_id, area_id, subarea_id, datetime.today(), db.session)

        if result == False:
            raise ValidationError(message)
            pass

        model.updated_on = datetime.now()  # Set the created_on
        model.user_id = user_id
        model.company_id = company_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.fi0 = year_id
        model.interval_id = interval_id
        model.interval_ord = interval_ord
        model.status_id = status_id
        model.subject_id = subject_id
        model.legal_document_id = None
        # for upload actions
        # model.file_path = form.file_path.data

        # workflow_controls = f"{dropdown_html}<br>{date_picker_html}<br>{checkbox_html}"  # Adjusted variable name
        # Determine if workflow controls need to be generated
        # Save the model to the database
        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        # Return the model after saving
          # Replace 'YourModelBase' with the base class of your models if different
        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        # Accessing inline form data directly from the main form object
        inline_form_data = form.data.get('steps_relationship', [])
        inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
        inline_data_string += f"was created by the user {user_id} ({company_id}. "
        inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        # Initialize an empty string to hold the inline form data
        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"  # Append field name and value to the string

        # Now you have the inline form data as a string, you can use it to create a system message
        # For example, you can use it to create a message using your `create_notification` function

        create_notification(
            self.session,
            company_id=company_id,
            user_id=user_id,
            sender="System",
            message_type="noticeboard",
            subject="Document and Workflow Created",
            body=inline_data_string,
            lifespan='one-off'
        )
        #except:
        #    print('Error adding inline data')

        # TODO create ADMIN message too

        action_type = 'update'
        if is_created:
            action_type = 'create'

        create_audit_log(
            self.session,
            company_id=company_id,
            user_id=user_id,
            base_data_id=None,
            workflow_id=None,
            step_id=None,
            action='create',
            details=inline_data_string
        )

        return model


@app.route('/custom_action/', methods=['GET', 'POST'])
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


# 1001
def perform_complex_operations(form_data):
    # This function might modify related models based on the new MainModel instance
    # For example, create a new RelatedModel instance linked to the MainModel

    print('*****')
    '''
    Base_data
    :param form_data: 
    :return: 
    if action == 'create':
        print('create', model)


        new_related_record = RelatedModel(main_model_id=main_model_instance.id, detail="Some detail")
        db.session.add(new_related_record)
        db.session.commit()
        # You could also call a BaseView method or redirect to a BaseView's page for further actions


    elif action == 'edit':
        print('create', model)

    else:
        print('none of the two', model)
        for item in model:
            print('item', item)
    '''
    pass


class Contingencies_dataView(ModelView):

    can_export = True  # Default to enabled

    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # inline_models = [(StepBaseDataInlineForm, StepBaseData, 'ONE_TO_MANY')]  # Assuming a one-to-one relationship
    form_base_class = CustomBaseDataForm  # Use our custom form class
    create_template = 'admin/area_1/create_base_data_3.html'
    subarea_id = 3
    area_id = 1

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc2']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc2': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Contingencies_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Contingencies_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)


    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # Specify the columns to display in the edit view
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    #'interval_ord', 'fi0', 'subject_id', 'fc2',
    # Replace the StringField with FileUploadField

    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati', 'no_action': 'Dichiarazione di assenza di documenti (1)'}

    form_extra_fields = {
        'file_path': FileUploadField('File', base_path=app.config['UPLOAD_FOLDER'])
    }

    form_overrides = {
        'no_action': CheckboxField
    }

    column_filters = ('subject', 'fc2', 'no_action')  # Adjust based on your model structure
    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        # Fetch StepBaseData records related to the provided model IDs
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()

        # Fetch model records related to the provided model IDs
        model_records = BaseData.query.filter(BaseData.id.in_(ids)).all()

        # Render the template to display the records
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records, model_records=model_records)


    # TODO ***** Implement Next Step Action
    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        print('Implement next step action')
        pass


    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter
    }

    def scaffold_form(self):
        form_class = super(Contingencies_dataView, self).scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )
        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        current_interval = [t[2] for t in intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        # Remove 'subject_id' field from the form
        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Legale").all()]
        )
        #delattr(form_class, 'subject_id')
        form_class.no_action = CheckboxField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        return form_class #ExtendedForm


    def _validate_no_action(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is None and not no_action_value:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is not None and no_action_value:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)


    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)

        # Reset form data
        form.populate_obj(model)

        uploaded_file = form.file_path.data
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)
        interval_id = nr_intervals
        status_id = 1
        record_type = 'control_area'

        year_id = form.fi0.data
        interval_ord = form.interval_ord.data
        subject_id = form.subject_id.data

        if form.date_of_doc.data > datetime.now():
            raise ValidationError(f"Date of document cannot be a future date.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError(f"Date of document must be consistent with the reporting year.")

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null.")

        if form.subject_id.data == None:
            raise ValidationError(f"Document type can not be null.")

        # - Validate data - Save the model
        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass

        # Perform actions relevant to both creation and edit:
        with app.app_context():
            result, message = check_status_limited(is_created, company_id,
                                subject_id, None, year_id, interval_ord,
                                    interval_id, area_id, subarea_id, datetime.today(), db.session)

        if result == False:
            raise ValidationError(message)
            pass

        model.updated_on = datetime.now()  # Set the created_on
        model.user_id = user_id
        model.company_id = company_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.fi0 = year_id
        model.interval_id = interval_id
        model.interval_ord = interval_ord
        model.status_id = status_id
        model.subject_id = subject_id
        model.legal_document_id = None
        # for upload actions
        # model.file_path = form.file_path.data

        # workflow_controls = f"{dropdown_html}<br>{date_picker_html}<br>{checkbox_html}"  # Adjusted variable name
        # Determine if workflow controls need to be generated
        # Save the model to the database

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        # Return the model after saving
          # Replace 'YourModelBase' with the base class of your models if different
        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        # Accessing inline form data directly from the main form object
        inline_form_data = form.data.get('steps_relationship', [])
        inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
        inline_data_string += f"was created by the user {user_id} ({company_id}. "
        inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        # Initialize an empty string to hold the inline form data
        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"  # Append field name and value to the string

        # Now you have the inline form data as a string, you can use it to create a system message
        # For example, you can use it to create a message using your `create_notification` function

        create_notification(
            self.session,
            company_id=company_id,
            user_id=user_id,
            sender="System",
            message_type="noticeboard",
            subject="Document and Workflow Created",
            body=inline_data_string,
            lifespan='one-off'
        )
        #except:
        #    print('Error adding inline data')

        # TODO create ADMIN message too

        action_type = 'update'
        if is_created:
            action_type = 'create'

        create_audit_log(
            self.session,
            company_id=company_id,
            user_id=user_id,
            base_data_id=None,
            workflow_id=None,
            step_id=None,
            action=action_type,
            details=inline_data_string
        )

        return model


class Contenziosi_dataView(ModelView):

    create_template = 'admin/area_1/create_base_data_4.html'
    subarea_id = 4  # Define subarea_id as a class attribute
    area_id = 1
    can_export = True  # Default to enabled
    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # inline_models = [(StepBaseDataInlineForm, StepBaseData, 'ONE_TO_MANY')]  # Assuming a one-to-one relationship
    form_base_class = CustomBaseDataForm  # Use our custom form class

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc2']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc2': {'widget': XEditableWidget()},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Contenziosi_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Contenziosi_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    '''
    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False
    '''

    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # Specify the columns to display in the edit view
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    #'interval_ord', 'fi0', 'subject_id', 'fc2',
    # Replace the StringField with FileUploadField

    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati', 'no_action': 'Dichiarazione di assenza di documenti (1)'}

    form_extra_fields = {
        'file_path': FileUploadField('File', base_path=app.config['UPLOAD_FOLDER'])
    }

    form_overrides = {
        'no_action': CheckboxField
    }

    column_filters = ('subject', 'fc2', 'no_action')  # Adjust based on your model structure
    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        # Fetch StepBaseData records related to the provided model IDs
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()

        # Fetch model records related to the provided model IDs
        model_records = BaseData.query.filter(BaseData.id.in_(ids)).all()

        # Render the template to display the records
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records, model_records=model_records)


    # TODO ***** Implement Next Step Action
    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        pass


    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter
    }

    def scaffold_form(self):
        form_class = super(Contenziosi_dataView, self).scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )
        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        current_interval = [t[2] for t in intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        # Remove 'subject_id' field from the form
        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Legale").all()]
        )
        #delattr(form_class, 'subject_id')
        form_class.no_action = CheckboxField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        return form_class #ExtendedForm


    def _validate_no_action(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is None and not no_action_value:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is not None and no_action_value:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)


    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)

        # Reset form data
        form.populate_obj(model)

        # Get the inline form data
        # TODO eliminated on 26Mar to cope with duplicated records in the INLINE
        # inline_form_data = form.inline_form  # Assuming 'inline_form' is the attribute holding the inline form data

        uploaded_file = form.file_path.data
        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)
        interval_id = nr_intervals
        status_id = 1
        record_type = 'control_area'

        year_id = form.fi0.data
        interval_ord = form.interval_ord.data
        subject_id = form.subject_id.data

        if form.date_of_doc.data > datetime.now():
            raise ValidationError(f"Date of document cannot be a future date.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError(f"Date of document must be consistent with the reporting year.")

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null.")

        if form.subject_id.data == None:
            raise ValidationError(f"Document type can not be null.")

        # - Validate data - Save the model
        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass


        # Perform actions relevant to both creation and edit:
        with app.app_context():
            result, message = check_status_limited(is_created, company_id,
                                subject_id, None, year_id, interval_ord,
                                    interval_id, area_id, subarea_id, datetime.today(), db.session)

        if result == False:
            raise ValidationError(message)
            pass

        model.updated_on = datetime.now()  # Set the created_on
        model.user_id = user_id
        model.company_id = company_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.fi0 = year_id
        model.interval_id = interval_id
        model.interval_ord = interval_ord
        model.status_id = status_id
        model.subject_id = subject_id
        model.legal_document_id = None
        # for upload actions
        # model.file_path = form.file_path.data
        # workflow_controls = f"{dropdown_html}<br>{date_picker_html}<br>{checkbox_html}"  # Adjusted variable name
        # Determine if workflow controls need to be generated
        # Save the model to the database
        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        # Return the model after saving
          # Replace 'YourModelBase' with the base class of your models if different
        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        # Accessing inline form data directly from the main form object
        inline_form_data = form.data.get('steps_relationship', [])
        inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
        inline_data_string += f"was created by the user {user_id} ({company_id}. "
        inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        # Initialize an empty string to hold the inline form data
        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"  # Append field name and value to the string

        # Now you have the inline form data as a string, you can use it to create a system message
        # For example, you can use it to create a message using your `create_notification` function

        create_notification(
            self.session,
            company_id=company_id,
            user_id=user_id,
            sender="System",
            message_type="noticeboard",
            subject="Document and Workflow Created",
            body=inline_data_string,
            lifespan='one-off'
        )
        #except:
        #    print('Error adding inline data')

        # TODO create ADMIN message too

        action_type = 'update'
        if is_created:
            action_type = 'create'

        create_audit_log(
            self.session,
            company_id=company_id,
            user_id=user_id,
            base_data_id=None,
            workflow_id=None,
            step_id=None,
            action='create',
            details=inline_data_string
        )

        return model


class Iniziative_dso_as_dataView(ModelView):

    create_template = 'admin/area_1/create_base_data_6.html'
    subarea_id = 6  # Define subarea_id as a class attribute
    area_id = 1

    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # inline_models = [(StepBaseDataInlineForm, StepBaseData, 'ONE_TO_MANY')]  # Assuming a one-to-one relationship
    form_base_class = CustomBaseDataForm  # Use our custom form class

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc2']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc2': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Iniziative_dso_as_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Iniziative_dso_as_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # Specify the columns to display in the edit view
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # 'interval_ord', 'fi0', 'subject_id', 'fc2',
    # Replace the StringField with FileUploadField

    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati',
                           'no_action': 'Dichiarazione di assenza di documenti (1)'}

    form_extra_fields = {
        'file_path': FileUploadField('File', base_path=app.config['UPLOAD_FOLDER'])
    }

    form_overrides = {
        'no_action': CheckboxField
    }

    column_filters = ('subject', 'fc2', 'no_action')  # Adjust based on your model structure
    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        # Fetch StepBaseData records related to the provided model IDs
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()

        # Fetch model records related to the provided model IDs
        model_records = BaseData.query.filter(BaseData.id.in_(ids)).all()

        # Render the template to display the records
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records,
                           model_records=model_records)

    # TODO ***** Implement Next Step Action
    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        print('Implement next step action')
        pass

    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter
    }

    def scaffold_form(self):
        form_class = super(Iniziative_dso_as_dataView, self).scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )
        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        # Remove 'subject_id' field from the form
        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Legale").all()]
        )
        # delattr(form_class, 'subject_id')
        form_class.no_action = CheckboxField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        return form_class  # ExtendedForm

    def _validate_no_action(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is None and not no_action_value:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is not None and no_action_value:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)

        # Reset form data
        form.populate_obj(model)

        # Get the inline form data
        # TODO eliminated on 26Mar to cope with duplicated records in the INLINE
        # inline_form_data = form.inline_form  # Assuming 'inline_form' is the attribute holding the inline form data

        uploaded_file = form.file_path.data
        print('1 - uploaded file', uploaded_file)

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)
        interval_id = nr_intervals
        status_id = 1
        record_type = 'control_area'

        year_id = form.fi0.data
        interval_ord = form.interval_ord.data
        subject_id = form.subject_id.data

        if form.date_of_doc.data > datetime.now():
            raise ValidationError(f"Date of document cannot be a future date.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError(f"Date of document must be consistent with the reporting year.")

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null.")

        if form.subject_id.data == None:
            raise ValidationError(f"Document type can not be null.")

        # - Validate data - Save the model
        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass

        # Perform actions relevant to both creation and edit:
        with app.app_context():
            result, message = check_status_limited(is_created, company_id,
                                                   subject_id, None, year_id, interval_ord,
                                                   interval_id, area_id, subarea_id, datetime.today(), db.session)

        if result == False:
            raise ValidationError(message)
            pass

        model.updated_on = datetime.now()  # Set the created_on
        model.user_id = user_id
        model.company_id = company_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.fi0 = year_id
        model.interval_id = interval_id
        model.interval_ord = interval_ord
        model.status_id = status_id
        model.subject_id = subject_id
        model.legal_document_id = None
        # for upload actions
        # model.file_path = form.file_path.data
        # workflow_controls = f"{dropdown_html}<br>{date_picker_html}<br>{checkbox_html}"  # Adjusted variable name
        # Determine if workflow controls need to be generated
        # Save the model to the database
        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        # Return the model after saving
        # Replace 'YourModelBase' with the base class of your models if different
        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        # Accessing inline form data directly from the main form object
        inline_form_data = form.data.get('steps_relationship', [])
        inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
        inline_data_string += f"was created by the user {user_id} ({company_id}. "
        inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        # Initialize an empty string to hold the inline form data
        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"  # Append field name and value to the string

        # Now you have the inline form data as a string, you can use it to create a system message
        # For example, you can use it to create a message using your `create_notification` function

        create_notification(
            self.session,
            company_id=company_id,
            user_id=user_id,
            sender="System",
            message_type="noticeboard",
            subject="Document and Workflow Created",
            body=inline_data_string,
            lifespan='one-off'
        )
        # except:
        #    print('Error adding inline data')

        # TODO create ADMIN message too

        action_type = 'update'
        if is_created:
            action_type = 'create'

        create_audit_log(
            self.session,
            company_id=company_id,
            user_id=user_id,
            base_data_id=None,
            workflow_id=None,
            step_id=None,
            action='create',
            details=inline_data_string
        )

        return model



class Iniziative_as_dso_dataView(ModelView):

    create_template = 'admin/area_1/create_base_data_7.html'
    subarea_id = 7  # Define subarea_id as a class attribute
    area_id = 1

    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # inline_models = [(StepBaseDataInlineForm, StepBaseData, 'ONE_TO_MANY')]  # Assuming a one-to-one relationship
    form_base_class = CustomBaseDataForm  # Use our custom form class

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc2']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc2': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Iniziative_as_dso_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Iniziative_as_dso_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # Specify the columns to display in the edit view
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # 'interval_ord', 'fi0', 'subject_id', 'fc2',
    # Replace the StringField with FileUploadField

    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati',
                           'no_action': 'Dichiarazione di assenza di documenti (1)'}

    form_extra_fields = {
        'file_path': FileUploadField('File', base_path=app.config['UPLOAD_FOLDER'])
    }

    form_overrides = {
        'no_action': CheckboxField
    }

    column_filters = ('subject', 'fc2', 'no_action')  # Adjust based on your model structure
    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        # Fetch StepBaseData records related to the provided model IDs
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()

        # Fetch model records related to the provided model IDs
        model_records = BaseData.query.filter(BaseData.id.in_(ids)).all()

        # Render the template to display the records
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records,
                           model_records=model_records)

    # TODO ***** Implement Next Step Action
    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        print('Implement next step action')
        pass

    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter
    }

    def scaffold_form(self):
        form_class = super(Iniziative_as_dso_dataView, self).scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )
        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        # Remove 'subject_id' field from the form
        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Legale").all()]
        )
        # delattr(form_class, 'subject_id')
        form_class.no_action = CheckboxField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        return form_class  # ExtendedForm

    def _validate_no_action(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is None and not no_action_value:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is not None and no_action_value:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)

        # Reset form data
        form.populate_obj(model)

        # Get the inline form data
        # TODO eliminated on 26Mar to cope with duplicated records in the INLINE
        # inline_form_data = form.inline_form  # Assuming 'inline_form' is the attribute holding the inline form data

        uploaded_file = form.file_path.data
        print('1 - uploaded file', uploaded_file)

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)
        interval_id = nr_intervals
        status_id = 1
        record_type = 'control_area'

        year_id = form.fi0.data
        interval_ord = form.interval_ord.data
        subject_id = form.subject_id.data

        if form.date_of_doc.data > datetime.now():
            raise ValidationError(f"Date of document cannot be a future date.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError(f"Date of document must be consistent with the reporting year.")

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null.")

        if form.subject_id.data == None:
            raise ValidationError(f"Document type can not be null.")

        # - Validate data - Save the model
        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass

        # Perform actions relevant to both creation and edit:
        with app.app_context():
            result, message = check_status_limited(is_created, company_id,
                                                   subject_id, None, year_id, interval_ord,
                                                   interval_id, area_id, subarea_id, datetime.today(), db.session)

        if result == False:
            raise ValidationError(message)
            pass

        model.updated_on = datetime.now()  # Set the created_on
        model.user_id = user_id
        model.company_id = company_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.fi0 = year_id
        model.interval_id = interval_id
        model.interval_ord = interval_ord
        model.status_id = status_id
        model.subject_id = subject_id
        model.legal_document_id = None
        # for upload actions
        # model.file_path = form.file_path.data
        # workflow_controls = f"{dropdown_html}<br>{date_picker_html}<br>{checkbox_html}"  # Adjusted variable name
        # Determine if workflow controls need to be generated
        # Save the model to the database
        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        # Return the model after saving
        # Replace 'YourModelBase' with the base class of your models if different
        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        # Accessing inline form data directly from the main form object
        inline_form_data = form.data.get('steps_relationship', [])
        inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
        inline_data_string += f"was created by the user {user_id} ({company_id}. "
        inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        # Initialize an empty string to hold the inline form data
        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"  # Append field name and value to the string

        # Now you have the inline form data as a string, you can use it to create a system message
        # For example, you can use it to create a message using your `create_notification` function

        create_notification(
            self.session,
            company_id=company_id,
            user_id=user_id,
            sender="System",
            message_type="noticeboard",
            subject="Document and Workflow Created",
            body=inline_data_string,
            lifespan='one-off'
        )
        # except:
        #    print('Error adding inline data')

        # TODO create ADMIN message too

        action_type = 'update'
        if is_created:
            action_type = 'create'

        create_audit_log(
            self.session,
            company_id=company_id,
            user_id=user_id,
            base_data_id=None,
            workflow_id=None,
            step_id=None,
            action='create',
            details=inline_data_string
        )

        return model



class Iniziative_dso_dso_dataView(ModelView):

    create_template = 'admin/area_1/create_base_data_8.html'
    subarea_id = 8  # Define subarea_id as a class attribute
    area_id = 1

    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # inline_models = [(StepBaseDataInlineForm, StepBaseData, 'ONE_TO_MANY')]  # Assuming a one-to-one relationship
    form_base_class = CustomBaseDataForm  # Use our custom form class

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc2']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc2': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Iniziative_dso_dso_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Iniziative_dso_dso_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # Specify the columns to display in the edit view
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    # 'interval_ord', 'fi0', 'subject_id', 'fc2',
    # Replace the StringField with FileUploadField

    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati',
                           'no_action': 'Dichiarazione di assenza di documenti (1)'}

    form_extra_fields = {
        'file_path': FileUploadField('File', base_path=app.config['UPLOAD_FOLDER'])
    }

    form_overrides = {
        'no_action': CheckboxField
    }

    column_filters = ('subject', 'fc2', 'no_action')  # Adjust based on your model structure
    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        # Fetch StepBaseData records related to the provided model IDs
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()

        # Fetch model records related to the provided model IDs
        model_records = BaseData.query.filter(BaseData.id.in_(ids)).all()

        # Render the template to display the records
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records,
                           model_records=model_records)

    # TODO ***** Implement Next Step Action
    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        print('Implement next step action')
        pass

    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter
    }

    def scaffold_form(self):
        form_class = super(Iniziative_dso_dso_dataView, self).scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )
        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        # Remove 'subject_id' field from the form
        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Legale").all()]
        )
        # delattr(form_class, 'subject_id')
        form_class.no_action = CheckboxField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        return form_class  # ExtendedForm

    def _validate_no_action(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is None and not no_action_value:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        no_action_value = form.no_action.data
        if model.file_path is not None and no_action_value:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)

        # Reset form data
        form.populate_obj(model)

        # Get the inline form data
        # TODO eliminated on 26Mar to cope with duplicated records in the INLINE
        # inline_form_data = form.inline_form  # Assuming 'inline_form' is the attribute holding the inline form data

        uploaded_file = form.file_path.data
        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)
        interval_id = nr_intervals
        status_id = 1
        record_type = 'control_area'

        year_id = form.fi0.data
        interval_ord = form.interval_ord.data
        subject_id = form.subject_id.data

        if form.date_of_doc.data > datetime.now():
            raise ValidationError(f"Date of document cannot be a future date.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError(f"Date of document must be consistent with the reporting year.")

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null.")

        if form.subject_id.data == None:
            raise ValidationError(f"Document type can not be null.")

        # - Validate data - Save the model
        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass

        # Perform actions relevant to both creation and edit:
        with app.app_context():
            result, message = check_status_limited(is_created, company_id,
                                                   subject_id, None, year_id, interval_ord,
                                                   interval_id, area_id, subarea_id, datetime.today(), db.session)

        if result == False:
            raise ValidationError(message)
            pass

        model.updated_on = datetime.now()  # Set the created_on
        model.user_id = user_id
        model.company_id = company_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.fi0 = year_id
        model.interval_id = interval_id
        model.interval_ord = interval_ord
        model.status_id = status_id
        model.subject_id = subject_id
        model.legal_document_id = None
        # for upload actions
        # model.file_path = form.file_path.data

        # workflow_controls = f"{dropdown_html}<br>{date_picker_html}<br>{checkbox_html}"  # Adjusted variable name
        # Determine if workflow controls need to be generated
        # Save the model to the database
        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        # Return the model after saving
        # Replace 'YourModelBase' with the base class of your models if different
        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        # Accessing inline form data directly from the main form object
        inline_form_data = form.data.get('steps_relationship', [])
        inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
        inline_data_string += f"was created by the user {user_id} ({company_id}. "
        inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        # Initialize an empty string to hold the inline form data
        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"  # Append field name and value to the string

        print('create msg', company_id, user_id, inline_data_string)
        # Now you have the inline form data as a string, you can use it to create a system message
        # For example, you can use it to create a message using your `create_notification` function

        create_notification(
            self.session,
            company_id=company_id,
            user_id=user_id,
            sender="System",
            message_type="noticeboard",
            subject="Document and Workflow Created",
            body=inline_data_string,
            lifespan='one-off'
        )
        # except:
        #    print('Error adding inline data')

        # TODO create ADMIN message too

        action_type = 'update'
        if is_created:
            action_type = 'create'

        create_audit_log(
            self.session,
            company_id=company_id,
            user_id=user_id,
            base_data_id=None,
            workflow_id=None,
            step_id=None,
            action='create',
            details=inline_data_string
        )

        return model


class Tabella21_dataView(ModelView):
    create_template = 'admin/create_base_data.html'
    subarea_id = 9  # Define subarea_id as a class attribute
    area_id = 2

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fi1', 'fi2', 'fc1']

    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        'interval_ord': {'widget': XEditableWidget()},
        'fi1': {'widget': XEditableWidget()},
        'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella21_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella21_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')
    form_columns = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Specify form columns with dropdowns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'UDD', 'fi2': 'PdR',
                     'fc1': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)',
                    'fi1': 'Numero UDD', 'fi2': 'Numero PdR',
                    'fc1': 'Note (opzionale)'}

    # Customize inlist for the View class
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Adjust based on your model structure

    # Specify fields to be excluded from the form
    #form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    def scaffold_form(self):
        form_class = super(Tabella21_dataView, self).scaffold_form()

        # Use the custom form class instead of the default form class
        # Define a custom form class with the desired date format
        '''class CustomForm(form_class):
            date_of_doc = DateField('Document date', format='%d-%m-%Y')

        # Use the custom form class instead of the default form class
        form_class = CustomForm'''

        # form_class.fi0 = MyIntegerField('Anno', validators=[InputRequired()])
        # Get the current year
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        return form_class

    # Use the custom loader with 'Servizi' as a filter criteria
    filter_criteria = None
    form_ajax_refs = {
        'name': CustomSubjectAjaxLoader(
            name='Interval',
            session=db.session,
            model=Interval,
            fields=['name'],
            filter_criteria=filter_criteria,
        ),
    }

    def create_model(self, form):
        model = super(Tabella21_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')

    def get_query(self):
        query = super(Tabella21_dataView, self).get_query().filter_by(data_type=self.subarea_name)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        # Reset form data

        form.populate_obj(model)  # This resets the form data to its default values

        fi0_value = model.fi0
        interval_ord_value = model.interval_ord
        fi1_value = model.fi1
        fi2_value = model.fi2
        fc1_value = model.fc1

        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass
        area_id = self.area_id
        subarea_id = self.subarea_id
        status_id = 1
        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=self.subarea_id)
        interval_id = config_values[0]

        subject_id = None
        lexic_id = None
        legal_document_id = None
        record_type = 'control_area'
        data_type = self.subarea_name

        # Get the name of the edited field
        edited_field_name = next(iter(form._fields))

        # Validate only the edited field
        edited_field = getattr(form, edited_field_name)
        if edited_field.data is None:
            raise ValidationError(f"{edited_field.label.text} field cannot be null")

        if edited_field_name == 'interval_ord':
            if edited_field.data > 52 or edited_field.data < 0:
                raise ValidationError(
                    "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            else:
                interval_ord_value = edited_field.data
            pass

        elif edited_field_name == 'fi0':
            if edited_field.data < 2000 or edited_field.data > 2099:
                raise ValidationError("Please check the year")
            else:
                fi0_value = edited_field.data
            pass

        elif edited_field_name == 'fi1':
            if edited_field.data < 0:
                raise ValidationError("Please enter valid values.")
            else:
                fi1_value = edited_field.data
            pass

        elif edited_field_name == 'fi2':
            if edited_field.data < 0:
                raise ValidationError("Please enter valid values.")
            else:
                fi2_value = edited_field.data
            pass

        else:
            fc1_value = edited_field.data
            pass

        if edited_field_name == 'fi1' or edited_field_name == 'fi2':
            # Check if fi1 and fi2 values are provided even though interval_ord is edited
            if fi1_value is not None and fi2_value is not None:
                # Perform validation or logic specific to fi1 and fi2
                if fi1_value + fi2_value == 0:
                    raise ValidationError("Please enter non-zero values for the fields.")
                # ... other logic based on fi1 and fi2 ...
        else:
            # User might be editing a different field (e.g., fi0)
            # You might not need to do anything specific here
            pass

        model.user_id = user_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.interval_id = interval_id
        model.status_id = status_id

        model.legal_document_id = legal_document_id
        model.subject_id = subject_id
        model.interval_ord = interval_ord_value
        model.fi0 = fi0_value
        model.fi1 = fi1_value
        model.fi2 = fi2_value
        model.updated_on = datetime.now()  # Set the created_on
        model.company_id = company_id
        model.fc1 = fc1_value

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model


class Tabella22_dataView(ModelView):
    create_template = 'admin/create_base_data.html'
    subarea_id = 10  # Define subarea_id as a class attribute
    area_id = 2

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fi1', 'fi2', 'fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        'fi1': {'widget': XEditableWidget()},
        'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella22_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella22_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')
    form_columns = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Specify form columns with dropdowns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'UDD', 'fi2': 'PdR',
                     'fc1': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)',
                    'fi1': 'Numero UDD', 'fi2': 'Numero PdR',
                    'fc1': 'Note (opzionale)'}

    # Customize inlist for the View class
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Adjust based on your model structure

    # Specify fields to be excluded from the form
    #form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    def scaffold_form(self):
        form_class = super(Tabella22_dataView, self).scaffold_form()

        # Use the custom form class instead of the default form class
        # Define a custom form class with the desired date format

        # form_class.fi0 = MyIntegerField('Anno', validators=[InputRequired()])
        # Get the current year
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        return form_class

    # Use the custom loader with 'Servizi' as a filter criteria
    filter_criteria = None
    form_ajax_refs = {
        'name': CustomSubjectAjaxLoader(
            name='Interval',
            session=db.session,
            model=Interval,
            fields=['name'],
            filter_criteria=filter_criteria,
        ),
    }

    def create_model(self, form):
        model = super(Tabella22_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')

    def get_query(self):
        query = super(Tabella22_dataView, self).get_query().filter_by(data_type=self.subarea_name)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def on_model_change(self, form, model, is_created):
        super(Tabella22_dataView, self).on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        #print('method is', form.get('_method'), form.get('_method') in ['PUT', 'PATCH'])
        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        area_id = self.area_id
        subarea_id = self.subarea_id
        status_id = 1
        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=self.subarea_id)
        interval_id = config_values[0]
        subject_id = None
        lexic_id = None
        legal_document_id = None
        record_type = 'control_area'
        data_type = self.subarea_name

        result, message = check_status(is_created, company_id,
                                   None, None, form.fi0.data, form.interval_ord.data,
                                       interval_id, area_id, subarea_id, datetime.today(), db.session)

        # - Validate data
        # - Save the model
        fields_to_check = ['fi0',
                           'fi1', 'fi2', 'interval_ord']

        for field_name in fields_to_check:
            if form[field_name].data is None:
                raise ValidationError(f"Field {field_name} cannot be null")

        if form.interval_ord.data > 52 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")

        if form.fi0.data < 2000 or form.fi0.data > 2199:
            raise ValidationError(
                "Please check the year")

        if form.fi1.data * form.fi2.data == 0:
            raise ValidationError("Please enter non-zero values for the fields.")

        model.user_id = user_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.interval_id = interval_id
        model.status_id = status_id

        model.legal_document_id = legal_document_id
        model.subject_id = subject_id
        model.interval_ord = form.interval_ord.data
        model.fi0 = form.fi0.data
        model.updated_on = datetime.now()  # Set the created_on
        model.company_id = company_id

        if result == False:
            raise ValidationError(message)
        else:
            pass

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model


class Tabella23_dataView(ModelView):

    create_template = 'admin/create_base_data.html'
    subarea_id = 11  # Define subarea_id as a class attribute
    area_id = 2

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella23_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella23_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
    form_columns = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
    # Specify form columns with dropdowns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Totale', 'fi2': '', 'fi3': '',
                     'fn1': 'Tasso Switching (%)', 'fn2': '',
                     'fc1': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                        'fi0': 'Inserire anno (es. 2024)',
                        'fi1': '(numero)', 'fi2': 'di cui: PdR domestico', 'fi3': 'PdR non domestico',
                        'fn1': ', di cui % domestico', 'fn2': '% non domestico',
        'fc1': '(opzionale)'}

    # Customize inlist for the class
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
    # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
        'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,
    }
    def scaffold_form(self):
        form_class = super(Tabella23_dataView, self).scaffold_form()

        # Use the custom form class instead of the default form class
        # Define a custom form class with the desired date format

        # form_class.fi0 = MyIntegerField('Anno', validators=[InputRequired()])
        # Get the current year
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        return form_class

    # Use the custom loader with 'Servizi' as a filter criteria
    filter_criteria = None
    form_ajax_refs = {
        'name': CustomSubjectAjaxLoader(
            name='Interval',
            session=db.session,
            model=Interval,
            fields=['name'],
            filter_criteria=filter_criteria,
        ),
    }

    def create_model(self, form):
        model = super(Tabella23_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')


    def get_query(self):
        query = super(Tabella23_dataView, self).get_query().filter_by(data_type=self.subarea_name)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def all_not_none_validator(self, form, field):
        if any(getattr(form, field_name).data is None for field_name in field.args):
            raise ValidationError("Some fields are null")


    def on_model_change(self, form, model, is_created):

        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        #print('method is', form.get('_method'), form.get('_method') in ['PUT', 'PATCH'])
        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass
        area_id = self.area_id
        subarea_id = self.subarea_id
        status_id = 1
        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=self.subarea_id)
        interval_id = config_values[0]
        subject_id = None
        legal_document_id = None
        record_type = 'control_area'
        data_type = self.subarea_name

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null")

        with app.app_context():
            result, message = check_status(is_created, company_id,
                                       None, None, form.fi0.data, form.interval_ord.data,
                                        interval_id, area_id, subarea_id, datetime.today(), db.session)

        # - Validate data
        # - Save the model
        fields_to_check = ['fi0',
                           'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1', 'interval_ord']

        for field_name in fields_to_check:
            if form[field_name].data is None:
                raise ValidationError(f"Field {field_name} cannot be null")
        if form.interval_ord.data > 52 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            pass
        if form.fi0.data < 2000 or form.fi0.data > 2199:
            raise ValidationError(
                "Please check the year")
            pass

        if (form.fi1.data is None or form.fi2.data is None or form.fi3.data is None):
            raise ValidationError("Please enter all required data.")

        if form.fi1.data * form.fi2.data * form.fi3.data == 0:
            raise ValidationError("Please enter non-zero values for the fields.")
        else:
            if form.fi1.data != form.fi2.data + form.fi3.data:
                raise ValidationError("Please check the total.")

        model.user_id = user_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.interval_id = interval_id
        model.status_id = status_id

        model.legal_document_id = legal_document_id
        model.subject_id = subject_id
        model.interval_ord = form.interval_ord.data
        model.fi0 = form.fi0.data
        model.updated_on = datetime.now()  # Set the created_on
        model.company_id = company_id

        if result == False:
            raise ValidationError(message)
        else:
            pass

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model



class Tabella24_dataView(ModelView):

    create_template = 'admin/create_base_data.html'
    subarea_id = 12  # Define subarea_id as a class attribute
    area_id = 2

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella24_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella24_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    form_columns = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    # Specify form columns with dropdowns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Totale', 'fi2': 'IVI', 'fi3': 'Altri',
                     'fi4': 'Lavori semplici', 'fi5': 'Lavori complessi',
                     'fc1': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                        'fi0': 'Inserire anno (es. 2024)',
                        'fi1': 'Totale', 'fi2': 'di cui: IVI', 'fi3': 'altri',
                        'fi4': 'Lavori semplici', 'fi5': 'Lavori complessi',
        'fc1': 'Inserire commento'}

    # Customize inlist for class dataView
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    def scaffold_form(self):
        form_class = super(Tabella24_dataView, self).scaffold_form()

        # form_class.fi0 = MyIntegerField('Anno', validators=[InputRequired()])
        # Get the current year
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)

        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        return form_class

    # Use the custom loader with 'Servizi' as a filter criteria
    filter_criteria = None
    form_ajax_refs = {
        'name': CustomSubjectAjaxLoader(
            name='Interval',
            session=db.session,
            model=Interval,
            fields=['name'],
            filter_criteria=filter_criteria,
        ),
    }

    def create_model(self, form):
        model = super(Tabella24_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')


    def get_query(self):
        #query = super(Tabella24_dataView, self).get_query().filter_by(data_type=self.subarea_name)
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def all_not_none_validator(self, form, field):
        if any(getattr(form, field_name).data is None for field_name in field.args):
            raise ValidationError("Some fields are null")


    def on_model_change(self, form, model, is_created):

        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        #print('method is', form.get('_method'), form.get('_method') in ['PUT', 'PATCH'])
        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass
        area_id = self.area_id
        subarea_id = self.subarea_id
        status_id = 1
        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=self.subarea_id)
        interval_id = config_values[0]
        subject_id = None
        legal_document_id = None
        record_type = 'control_area'
        data_type = self.subarea_name

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null")

        # - Validate data
        # - Save the model
        fields_to_check = ['fi0',
                           'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1', 'interval_ord']

        with app.app_context():
            result, message = check_status(is_created, company_id,
                                       None, None, form.fi0.data, form.interval_ord.data,
                                        interval_id, area_id, subarea_id, datetime.today(), db.session)

        for field_name in fields_to_check:
            if form[field_name].data is None:
                raise ValidationError(f"Field {field_name} cannot be null")
        if form.interval_ord.data > 52 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            pass
        if form.fi0.data < 2000 or form.fi0.data > 2199:
            raise ValidationError(
                "Please check the year")
            pass

        if (form.fi1.data is None or form.fi2.data is None or form.fi3.data is None
                or form.fi4.data is None or form.fi5.data is None):
            raise ValidationError("Please enter all required data.")

        if form.fi1.data + form.fi2.data + form.fi3.data + form.fi4.data + form.fi5.data == 0:
            raise ValidationError("Please enter non-zero values for the fields.")
        else:
            if form.fi1.data != form.fi2.data + form.fi3.data:
                raise ValidationError("Please check the total.")

        model.user_id = user_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.interval_id = interval_id
        model.status_id = status_id

        model.legal_document_id = legal_document_id
        model.subject_id = subject_id
        model.interval_ord = form.interval_ord.data
        model.fi0 = form.fi0.data
        model.updated_on = datetime.now()  # Set the created_on
        model.company_id = company_id

        if result == False:
            raise ValidationError(message)
        else:
            pass

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model


class Tabella25_dataView(ModelView):

    create_template = 'admin/create_base_data.html'
    page_title = 'Secondo livello: Quote di mercato della IVI nel settore vendita del SMR'

    subarea_id = 13  # Define subarea_id as a class attribute
    area_id = 2

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella25_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella25_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('interval_ord', 'fi0', 'fi1', 'fn1', 'fi2', 'fn2', 'fi3', 'fc1')
    form_columns = ('interval_ord', 'fi0', 'fi1', 'fn1', 'fi2', 'fn2', 'fi3', 'fc1')  # Specify form columns with dropdowns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Numero', 'fn1': '%',
                     'fi2': 'Altri', 'fn2': '%',
                     'fi3': 'Totale',
                     'fc1': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)',
                           'fi1': 'Numero IVI nel settore di vendita del SMR',
                           'fn1': 'quota di mercato IVI',
                           'fi2': 'Numero altri nel settore di vendita del SMR',
                           'fn2': 'quota di altri',
                           'fi3': '(numero)',
                           'fc1': 'Inserire commento'}

    # Customize inlist for the View class
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'subject.name', 'fi3', 'fn1','fi4', 'fn2', 'fi5', 'fc1', 'fc2')
    # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'subject.name', 'fi3', 'fi4', 'fi5', 'fc1')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')
    def _subject_formatter(view, context, model, name):
        # This function will be used to format the 'subject' column
        if model.subject:
            if isinstance(model.subject, Subject):  # Check if the subject is an instance of Subject
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name  # If not, query the subject object
        return ''

    column_formatters = {
        'subject': _subject_formatter,
        'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
        'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,

    }

    def scaffold_form(self):
        form_class = super(Tabella25_dataView, self).scaffold_form()
        # Set default values for specific fields

        form_class.subject_id = SelectField(
            'Oggetto',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Utenti").all()]
        )

        # Get the current year
        current_year = datetime.now().year
        # Generate choices for the year field from current_year - 5 to current_year + 1
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        # Set the default value to the current year
        default_year = str(current_year)
        # Dynamically determine interval_ord options based on subject_id
        form_class.fi0 = SelectField(
            'Anno',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )
        return form_class

    def create_model(self, form):
        model = super(Tabella25_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')

    def get_query(self):
        #query = super(Tabella25_dataView, self).get_query().filter_by(data_type=self.subarea_name)
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def on_model_change(self, form, model, is_created):

        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        #print('method is', form.get('_method'), form.get('_method') in ['PUT', 'PATCH'])
        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass
        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        status_id = 1
        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=self.subarea_id)
        interval_id = config_values[0]
        subject_id = form.subject_id.data
        legal_document_id = None
        record_type = 'control_area'

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null")

        with app.app_context():
            result, message = check_status(is_created, company_id, None,
                                       None, form.fi0.data, form.interval_ord.data,
                                        interval_id, area_id, subarea_id, datetime.today(), db.session)

        # - Validate data
        # - Save the model
        fields_to_check = ['fi0',
                           'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'interval_ord']

        for field_name in fields_to_check:
            if form[field_name].data is None:
                raise ValidationError(f"Field {field_name} cannot be null")
        if form.interval_ord.data > 52 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            pass
        if form.fi0.data < 2000 or form.fi0.data > 2199:
            raise ValidationError(
                "Please check the year")
            pass

        if (form.fi1.data is None or form.fi2.data is None or form.fi3.data is None):
            raise ValidationError("Please enter all required data.")

        if form.fi1.data + form.fi2.data + form.fi3.data == 0:
            raise ValidationError("Please enter non-zero values for the fields.")
        else:
            if form.fi3.data != form.fi1.data + form.fi2.data:
                raise ValidationError("Please check the total.")

        model.user_id = user_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.data_type = self.subarea_name
        model.interval_id = interval_id
        model.status_id = status_id

        model.legal_document_id = legal_document_id
        model.subject_id = subject_id
        model.interval_ord = form.interval_ord.data
        model.fi0 = form.fi0.data
        model.updated_on = datetime.now()  # Set the created_on
        model.company_id = company_id

        if result == False:
            raise ValidationError(message)
        else:
            pass

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model


class Tabella26_dataView(ModelView):
    page_title = "Switching rate (trattamento della vendita dell'IVI rispetto agli altri operatori)"

    create_template = 'admin/create_base_data.html'
    area_id = 2
    subarea_id = 14

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella26_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella26_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('interval_ord', 'fi0',
                   'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4',
                   'fi6', 'fn5', 'fi7', 'fn6', 'fi8', 'fi9', 'fn7', 'fi10', 'fi11', 'fn8',
                   'fc1')
    form_columns = ('interval_ord', 'fi0',
                   'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4',
                   'fi6', 'fn5', 'fi7', 'fn6', 'fi8', 'fi9', 'fn7', 'fi10', 'fi11', 'fn8',
                   'fc1')
    # Specify form columns with dropdowns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                    'fi1': 'Totale rich. (a)', 'fi2': 'IVI (b)', 'fn1': '% (c)', 'fi3': 'Esito positivo (d)',
                     'fn2': '% (e)', 'fi4': 'Esito negativo (f)', 'fn3': '% (g)',
                     'fi5': 'ALTRI (h)', 'fn4': '% (i)',
                    'fi6': 'Esito pos. (j)', 'fn5': '% (k)', 'fi7': 'Esito neg. (l)', 'fn6': '% (m)',
                     'fi8': 'Rich. altri su PdR altri (n)', 'fi9': 'Esito neg. (p)', 'fn7': '% (q)',
                     'fi10': 'Rich altri su PdR IVI (r)', 'fi11': 'Esito neg. (s)', 'fn8': '% (t)',
                    'fc1': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                   'fi0': 'Inserire anno (es. 2024)',
                   'fi1': 'Totale richieste presentate', 'fi2': 'di cui IVI', 'fn1': 'Percentuale richieste IVI (=b/a)',
                           'fi3': 'Richieste con esito positivo',
                           'fn2': 'Percentuale delle richieste IVI con esito positivo (=d/b)',
                           'fi4': 'Richieste con esito negativo (=b-d)',
                           'fn3': 'Percentuale delle richieste IVI con esito negativo (=f/b)',
                           'fi5': 'Richieste ALTRI operatori (=a-b)',
                   'fn4': 'Percentuale ALTRI sul totale (=h/a)',
                   'fi6': 'Richieste ALTRI con esito positivo', 'fn5': 'Percentuale di richieste ALTRI con esito positivo (=j/h)',
                           'fi7': 'Richieste ALTRI con esito negativo (=h-j)', 'fn6': 'Percentuale richieste ALTRI con esito negativo (=l/h)',
                           'fi8': 'Richieste ALTRI su PdR altri', 'fi9': 'di cui con esito negativo',
                           'fn7': 'Percentuale di richieste ALTRI con esito negativo (=p/n)',
                           'fi10': 'Richieste ALTRI su PdR IVI',
                   'fi11': 'di cui con esito negativo', 'fn8': 'Percentuale di richieste ALTRI su PdR IVI con esito negativo (=s/r)',
                   'fc1': '(opzionale)'}

    # Customize inlist for tabella26
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5',
                              'fi6', 'fi7', 'fi8', 'fi9' ,'fi10', 'fi11', 'fc1')
    # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5',
                              'fi6', 'fi7', 'fi8', 'fi9' ,'fi10', 'fi11', 'fc1')

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
        'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,
        'fn3': lambda view, context, model, name: "%.2f" % model.fn3 if model.fn3 is not None else None,
        'fn4': lambda view, context, model, name: "%.2f" % model.fn4 if model.fn4 is not None else None,
        'fn5': lambda view, context, model, name: "%.2f" % model.fn5 if model.fn5 is not None else None,
        'fn6': lambda view, context, model, name: "%.2f" % model.fn6 if model.fn6 is not None else None,
        'fn7': lambda view, context, model, name: "%.2f" % model.fn7 if model.fn7 is not None else None,
        'fn8': lambda view, context, model, name: "%.2f" % model.fn8 if model.fn8 is not None else None,
    }

    def scaffold_form(self):
        form_class = super(Tabella26_dataView, self).scaffold_form()
        # Set default values for specific fields

        '''
        form_class.subject_id = SelectField(
            'Oggetto',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Utenti").all()]
        )
        '''

        # Get the current year
        current_year = datetime.now().year
        # Generate choices for the year field from current_year - 5 to current_year + 1
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        # Set the default value to the current year
        default_year = str(current_year)
        # Dynamically determine interval_ord options based on subject_id
        form_class.fi0 = SelectField(
            'Anno',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )

        return form_class

    def get_query(self):
        #query = super(Tabella26_dataView, self).get_query().filter_by(data_type=self.subarea_name)
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def create_model(self, form):
        model = super(Tabella26_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')

    def on_model_change(self, form, model, is_created):

        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        # print('method is', form.get('_method'), form.get('_method') in ['PUT', 'PATCH'])
        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass
        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        status_id = 1
        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=subarea_id)
        interval_id = config_values[0]
        subject_id = None
        legal_document_id = None
        record_type = 'control_area'

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null")

        # - Validate data
        # - Save the model
        fields_to_check_not_null = ['fi0', 'interval_ord',
                           'fi1', 'fi2', 'fi5', 'fi8', 'fi10']

        fields_to_check = ['fi0', 'interval_ord',
                           'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fi6', 'fi7', 'fi8', 'fi9', 'fi10', 'fi11',
                           'fn1', 'fn2', 'fn3', 'fn4', 'fn5', 'fn6', 'fn7', 'fn8',
                           'fc1']

        with app.app_context():
            result, message = check_status(is_created, company_id,
                                       None, None, form.fi0.data, form.interval_ord.data,
                                        interval_id, area_id, subarea_id, datetime.today(), db.session)

        for field_name in fields_to_check_not_null:
            if form[field_name].data is None:
                raise ValidationError(f"Field {field_name} cannot be null")

        if form.interval_ord.data > 52 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError(
                "Please check the year")
            pass

        if (form.fi1.data is None or form.fi2.data is None or form.fi5.data is None
                or form.fi8.data is None or form.fi10.data is None):
            raise ValidationError("Please enter all required integers.")
        else:
            if form.fi1.data + form.fi2.data + form.fi5.data + form.fi8.data + form.fi10.data == 0:
                raise ValidationError("Please enter at least one non-zero values for the integer number.")
            pass
            if form.fi1.data != form.fi2.data + form.fi5.data:
                raise ValidationError("Please check total, 'IVI' and 'Altri'.")
            pass
            if form.fi2.data != form.fi3.data + form.fi4.data:
                raise ValidationError("Please check 'totale IVI', 'esito positivo' and 'esito negativo'.")
            pass
            if form.fi5.data != form.fi6.data + form.fi7.data:
                raise ValidationError("Please check 'totale altri', 'esito positivo' and 'esito negativo'.")
            pass

            if form.fi1.data is not None and form.fi1.data != 0:
                form.fn1.data = round(100*(form.fi2.data / form.fi1.data), 2) #IVI/tot
                form.fn4.data = round(100*(form.fi5.data / form.fi1.data), 2) #altri/TOT
            if form.fi2.data is not None and form.fi2.data != 0:
                form.fn2.data = round(100*(form.fi3.data / form.fi2.data), 2) #pct IVI pos
                form.fn3.data = round(100*(form.fi4.data / form.fi2.data), 2) #PCT IVI neg
            if form.fi5.data is not None and form.fi5.data != 0:
                form.fn5.data = round(100*(form.fi6.data / form.fi5.data), 2) #PCT POS altri
                form.fn6.data = round(100*(form.fi7.data / form.fi5.data), 2) #PCT NEG altri

        if form.fn1.data is None or form.fn1.data == 0:
            if form.fi1.data != 0:
                form.fn1.data = round(form.fi2.data / form.fi1.data, 2)
        else:
            if form.fi1.data != 0:
                form.fi2.data = int(form.fi1.data * float(form.fn1.data) * 0.01)

        model.user_id = user_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.interval_id = interval_id
        model.status_id = status_id

        model.fn1 = form.fn1.data
        model.fn2 = form.fn2.data
        model.fn3 = form.fn3.data
        model.fn4 = form.fn4.data
        model.fn5 = form.fn5.data
        model.fn6 = form.fn6.data

        model.legal_document_id = legal_document_id
        model.subject_id = subject_id
        model.interval_ord = form.interval_ord.data
        model.fi0 = form.fi0.data
        model.updated_on = datetime.now()  # Set the created_on
        model.company_id = company_id

        if result == False:
            raise ValidationError(message)
        else:
            pass

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model


class Tabella27_dataView(ModelView):

    create_template = 'admin/create_base_data.html'
    subarea_id = 15  # Define subarea_id as a class attribute
    area_id = 2

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        # 'fi0': {'widget': XEditableWidget()},
        # 'interval_ord': {'widget': XEditableWidget()},
        # 'fi1': {'widget': XEditableWidget()},
        # 'fi2': {'widget': XEditableWidget()},
        'fc1': {'widget': XEditableWidget()},
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella27_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella27_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    form_columns = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    # Specify form columns with dropdowns

    column_labels = {'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Totale', 'fi2': 'domestico', 'fn1': '%',
                     'fi3': 'IVI', 'fn2': '%',
                     'fi4': 'altri', 'fn3': '%',
                     'fi5': 'PdR', 'fn4':'Tasso switching PdR',
                     'fc1': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)',
                           'fi1': 'Totale', 'fi2': 'di cui: domestico', 'fn1': 'domestico, in percentuale',
                           'fi3': 'di cui IVI', 'fn2': 'IVI, in percentuale',
                           'fi4': 'altri', 'fn3': 'altri, in percentuale',
                           'fi5': 'PdR', 'fn4': 'Tasso switching PdR (percentuale)',
                           'fc1': 'Inserire commento'}

    # Customize inlist for the View class
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
        'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,
        'fn3': lambda view, context, model, name: "%.2f" % model.fn3 if model.fn3 is not None else None,
        'fn4': lambda view, context, model, name: "%.2f" % model.fn4 if model.fn4 is not None else None,
    }

    def scaffold_form(self):
        form_class = super(Tabella27_dataView, self).scaffold_form()

        # form_class.fi0 = MyIntegerField('Anno', validators=[InputRequired()])
        # Get the current year
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        # NEW
        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        # OLD
        # nr_intervals = get_subarea_interval_type(self.area_id, self.subarea_id)

        current_interval = [t[2] for t in intervals if
                            t[0] == nr_intervals]  # int(get_current_interval(3))  # quadriester
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,  # Example choices, replace with your logic
            default=first_element
        )
        return form_class

    def create_model(self, form):
        model = super(Tabella27_dataView, self).create_model(form)
        if current_user.is_authenticated:
            try:
                model.user_id = current_user.id  # Set the user_id
                model.company_id = current_user.company_id  # Set the company_id
                model.data_type = self.subarea_name
                created_by = current_user.username  # Set the created_by
                user_id = current_user.id
                model.user_id = user_id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass
                model.company_id = company_id  # Set the company_id
                model.created_by = created_by  # Set the cr by
                model.created_on = datetime.now()  # Set the created_on
            except AttributeError:
                pass
            return model
        else:
            # Handle the case where the user is not authenticated
            raise ValidationError('User not authenticated.')

    def get_query(self):
        #query = super(Tabella27_dataView, self).get_query().filter_by(data_type=self.subarea_name)
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()

                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                # Employee can only see their own records
                query = query.filter(self.model.user_id == current_user.id)
                return query

        # For other roles or anonymous users, return an empty query
        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def all_not_none_validator(self, form, field):
        if any(getattr(form, field_name).data is None for field_name in field.args):
            raise ValidationError("Some fields are null")

    def on_model_change(self, form, model, is_created):

        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values
        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass
        area_id = self.area_id
        subarea_id = self.subarea_id
        data_type = self.subarea_name
        status_id = 1
        config_values = get_config_values(config_type='area_interval', company_id=company_id, area_id=self.area_id,
                                          subarea_id=self.subarea_id)
        interval_id = config_values[0]
        subject_id = None
        legal_document_id = None
        record_type = 'control_area'

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null")

        # - Validate data
        # - Save the model
        fields_to_check = ['fi0', 'interval_ord',
                           'fi1', 'fi2', 'fi3', 'fi4', 'fi5',
                           'fn1', 'fn2', 'fn3', 'fn4',
                           'fc1']

        with app.app_context():
            result, message = check_status(is_created, company_id,
                                       None, None, form.fi0.data, form.interval_ord.data,
                                        interval_id, area_id, subarea_id, datetime.today(), db.session)

        for field_name in fields_to_check:
            if form[field_name].data is None:
                raise ValidationError(f"Field {field_name} cannot be null")

        if form.interval_ord.data > 52 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            pass

        if form.fi0.data < 2000 or form.fi0.data > 2199:
            raise ValidationError(
                "Please check the year")
            pass

        if (form.fi1.data is None or form.fi2.data is None or form.fi3.data is None
                or form.fi4.data is None or form.fi5.data is None):
            raise ValidationError("Please enter all required integers.")
        else:
            if form.fi1.data + form.fi2.data + form.fi3.data + form.fi4.data + form.fi5.data == 0:
                raise ValidationError("Please enter at least one non-zero values for the integer fields.")
            pass
            if form.fi1.data != form.fi2.data + form.fi3.data + form.fi4.data:
                raise ValidationError("Please check the total.")
            pass

        if (form.fn1.data is None or form.fn2.data is None or form.fn3.data is None
                or form.fn4.data is None):
            raise ValidationError("Please enter all required % data.")
            pass
        else:
            if form.fn1.data + form.fn2.data + form.fn3.data + form.fn4.data == 0:
                raise ValidationError("Please enter at least one non-zero value for the % fields.")
            pass

        model.user_id = user_id
        model.data_type = data_type
        model.record_type = record_type
        model.area_id = area_id
        model.subarea_id = subarea_id
        model.interval_id = interval_id
        model.status_id = status_id

        model.legal_document_id = legal_document_id
        model.subject_id = subject_id
        model.interval_ord = form.interval_ord.data
        model.fi0 = form.fi0.data
        model.updated_on = datetime.now()  # Set the created_on
        model.company_id = company_id

        if result == False:
            raise ValidationError(message)
        else:
            pass

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        return model


#===================================================
# Use app context for creating Flask-Admin instances
with app.app_context():
    # Define the first custom index view class

    class CustomAdminIndexView1(BaseData):
        default_view = 'flussi_data_view'  # Or any other valid view name
        def index(self):
            # Customize the index view here for the first custom index view
            return self.render('open_admin.html')
            #return 'Hello From first admin :{}.'.format(self)

    # Define the second custom index view class
    class CustomAdminIndexView2(BaseData):
        default_view = 'view_struttura_offerta'  # Or the intended first view for "Area 2"
        def index(self):
            # Customize the index view here for the second custom index view
            return self.render('open_admin_2.html')  # Adjust template path if needed


    # Define custom form for CustomAdminIndexView1
    class CustomForm1(FlaskForm): #was BaseForm
        fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2199)]) #anno
        interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)]) #periodo

        fi1 = IntegerField('fi1', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

        fi2 = IntegerField('fi2', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
        fi3 = IntegerField('fi3', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
        fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
        fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
        fi6 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

        fn1 = IntegerField('fn1', validators=[InputRequired(), NumberRange(min=0.00, max=100.00)])
        fn2 = IntegerField('fn2', validators=[InputRequired(), NumberRange(min=0.00, max=100.00)])
        fn3 = IntegerField('fn3', validators=[InputRequired(), NumberRange(min=0.00, max=100.00)])

        fc1 = StringField('fc1')
        fc2 = StringField('fc2')

        number_of_doc = StringField('number_of_doc')
        date_of_doc = DateField('date_of_doc')

    class CustomFlussiDataView(Flussi_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomAttiBaseView(Atti_BaseView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomFileLoaderForm

    class CustomAttiDataView(Atti_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1


    class CustomContenziosiDataView(Contenziosi_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1


    class CustomIniziative_dso_asDataView(Iniziative_dso_as_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomIniziative_as_dsoDataView(Iniziative_as_dso_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomIniziative_dso_dsoDataView(Iniziative_dso_dso_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1



    # =================================================================================================================
    # Define custom form for CustomAdminIndexView2
    # =================================================================================================================
    #class CustomForm2(BaseData):
    class CustomForm2(FlaskForm):
        fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2199)])
        interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])
        fi3 = IntegerField('fi3', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
        fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
        fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

        fn1 = IntegerField('fn1', validators=[InputRequired(), NumberRange(min=0.00, max=100.00)])
        fn2 = IntegerField('fn2', validators=[InputRequired(), NumberRange(min=0.00, max=100.00)])
        fn3 = IntegerField('fn3', validators=[InputRequired(), NumberRange(min=0.00, max=100.00)])

        fc1 = StringField('fc1')
        fc2 = StringField('fc2', validators=[InputRequired()])


    class CustomTabella21DataView(Tabella21_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

    class CustomTabella22DataView(Tabella22_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

        '''
        def on_model_change(self, form, model, is_created):
            try:
                super().on_model_change(form, model, is_created)
            except ValidationError as e:
                flash(str(e) + '2', 'error')
                raise e  # Reraise the exception if you want Flask-Admin to handle it further or stop the execution
        '''

    class CustomTabella23DataView(Tabella23_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

    class CustomTabella24DataView(Tabella24_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

    class CustomTabella25DataView(Tabella25_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

    class CustomTabella26DataView(Tabella26_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

    class CustomTabella27DataView(Tabella27_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

    admins_off_set = 0

    # First Flask-Admin instance with the first custom index view
    admin_app1 = Admin(app,
       name='Area di controllo 1 - Documenti e atti',
       url='/open_admin',
       template_mode='bootstrap3',
       endpoint='open_admin',
   )

    # Add views to admin_app1
    admins_off_set += 1
    sub_off_set = 0

    sub_off_set += 1
    if get_if_active(admins_off_set, sub_off_set):
        admin_app1.add_view(CustomFlussiDataView(BaseData, db.session,
                                             name="Flussi pre-complaint", endpoint='flussi_data_view'))

    sub_off_set += 1
    if get_if_active(admins_off_set, sub_off_set):
    # Register the view with Flask Admin
        #admin_app1.add_view(CustomAttiBaseView(name='Workflow Manager (Atti complaint)',
        #                    endpoint='custom_base_atti'))
        admin_app1.add_view(CustomAttiDataView(BaseData, db.session,
                                           name='Atti di complaint', endpoint='atti_data_view'))

    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app1.add_view(Contingencies_dataView(BaseData, db.session,
                                                   name='Contingencies', endpoint='contingencies_data_view'))

    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app1.add_view(CustomContenziosiDataView(BaseData, db.session,
                                                  name='Contenziosi', endpoint='contenziosi_data_view'))

    sub_off_set += 1
    sub_off_set += 1 # questionnaire here

    if get_if_active(admins_off_set,sub_off_set):
        admin_app1.add_view(CustomIniziative_dso_asDataView(BaseData, db.session,
                                                        name='Iniziative DSO vs amministrazioni',
                                                   endpoint='iniziative_dso_as_data_view'))

    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app1.add_view(CustomIniziative_as_dsoDataView(BaseData, db.session,
                                                        name='Amministrazioni vs DSO',
                                                   endpoint='iniziative_as_dso_data_view'))

    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app1.add_view(CustomIniziative_dso_dsoDataView(BaseData, db.session,
                                                         name='DSO vs DSO/TSO',
                                                    endpoint='iniziative_dso_dso_data_view'))

    # Second Flask-Admin instance with the second custom index view

    admin_app2 = Admin(app,
                       name='Area di controllo 2 - Elementi quantitativi',
                       url='/open_admin_2',
                       template_mode='bootstrap4',
                       endpoint='open_admin_2',
                       )

    # Add views to admin_app2
    admins_off_set += 1
    sub_off_set = len(app.config['SUBAREAS_1'])

    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app2.add_view(CustomTabella21DataView(BaseData, db.session, name="Struttura offerta",
                                               endpoint='view_struttura_offerta'))
    sub_off_set += 1
    if get_if_active(admins_off_set, sub_off_set):
        admin_app2.add_view(CustomTabella22DataView(BaseData, db.session, name="Area di contendibilita'",
                                      endpoint="view_area_contendibilita'"))
    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app2.add_view(CustomTabella23DataView(BaseData, db.session, name="Grado di contendibilita'",
                                                endpoint="view_grado_contendibilita'"))
    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app2.add_view(CustomTabella24DataView(BaseData, db.session, name='Accesso venditori a DSO',
                                      endpoint='view_accesso_venditori'))
    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app2.add_view(CustomTabella25DataView(BaseData, db.session, name='Quote mercato IVI',
                                      endpoint='view_quote_mercato_ivi'))
    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app2.add_view(CustomTabella26DataView(BaseData, db.session, name='Trattamento switching',
                                      endpoint='view_trattamento_switching'))
    sub_off_set += 1
    if get_if_active(admins_off_set,sub_off_set):
        admin_app2.add_view(CustomTabella27DataView(BaseData, db.session, name="Livello di contendibilta'",
                                      endpoint="view_livello_contendibilita'"))


# Initialize Flask-Admin
#admin_app4 = Admin(app, name='Setup', url = '/open_setup_basic', template_mode='bootstrap4', endpoint = 'setup_basic')

admin_app4 = Admin(app, name='System Setup', url='/open_admin_4', template_mode='bootstrap4', endpoint='open_admin_4')
# Add your ModelViews to Flask-Admin
admin_app4.add_view(CompanyView(Company, db.session, name='Companies', endpoint='companies_data_view'))
admin_app4.add_view(UsersView(Users, db.session, name='Users', endpoint='users_data_view'))
admin_app4.add_view(QuestionnaireView(Questionnaire, db.session, name='Questionnaires', endpoint='questionnaires_data_view'))
admin_app4.add_view(QuestionView(Question, db.session, name='Questions', endpoint='questions_data_view'))
admin_app4.add_view(StatusView(Status, db.session, name='Status', endpoint='status_data_view'))
admin_app4.add_view(LexicView(Lexic, db.session, name='Dictionary', endpoint='dictionary_data_view'))
admin_app4.add_view(AreaView(Area, db.session, name='Areas', endpoint='areas_data_view'))
admin_app4.add_view(SubareaView(Subarea, db.session, name='Subareas', endpoint='subareas_data_view'))
admin_app4.add_view(SubjectView(Subject, db.session, name='Subjects', endpoint='subjects_data_view'))
admin_app4.add_view(WorkflowView(Workflow, db.session, name='Workflows', endpoint='workflows_data_view'))
admin_app4.add_view(StepView(Step, db.session, name='Steps', endpoint='steps_data_view'))
admin_app4.add_view(AuditLogView(AuditLog, db.session, name='Audit Log', endpoint='audit_data_view'))
admin_app4.add_view(PostView(Post, db.session, name='Posts', endpoint='posts_data_view'))
admin_app4.add_view(TicketView(Ticket, db.session, name='Tickets', endpoint='tickets_data_view'))
admin_app4.add_view(BaseDataView(BaseData, db.session, name='Data', endpoint='base_data_view'))
admin_app4.add_view(BaseDataView(Container, db.session, name='Container', endpoint='container_view'))

# Add other ModelViews as needed...

# TODO ***** copy Contingencies "structure" of main and inline forms
#  - in modo che ogni soc gestisca il suo, con le fasi etc.
# EXISTA O DIFERENTA: in BaseData exista comp_id si user_id, in QUEST, nu!
# asa ca probabil ca e mai bine sa fac cum e scris mai jos
# quindi il form per l'inserimento del quest deve essere più scarno, con inline del (o dei) workflow in cui si vuole inserire
'''
probabil ca e mai potrivit sa folosesc asta:
                                                                    DocumentsAssignedBaseDataView
        pentru ca get_query e bazata pe mai multe Model decat ModelView!

selectionarea elementelor listei va trebui facuta pt acele
    Questionnaire cu 
        scadenta si Status compatibile,
        si 
    unde, prin intermediul StepQuestionnaire,
        questionnaire_id (se gaseste in relatia questionnaire-companies)
        
SAU user is_admin!
'''

# TOD how to eliminate relationship fields in the Question and workflow CREATE templates?

# TODO Associazione di 1->m da non consentire qui (can_create = False) , in quanto già fatta (con controllo IF EXISTS) altrove

# TODO ***** le risposte ai questionnari *** - answer - sono da STORE non in Answer, ma in BaseData (cu data_type='answer')!

admin_app10 = Admin(app, name='Surveys & Questionnaires Workflow',
                    url='/open_admin_10', template_mode='bootstrap4',
                    endpoint='open_admin_10')
# Add your ModelViews to Flask-Admin
admin_app10.add_view(OpenQuestionnairesView(name='Open Questionnaires', endpoint='open_questionnaires'))

admin_app10.add_view(StepQuestionnaireView(StepQuestionnaire, db.session,
                                           name='A. Questionnaires & Surveys (Q&S) Workflow',
                                           endpoint='stepquestionnaire_questionnaire_view'))
admin_app10.add_view(QuestionnaireView(Questionnaire, db.session, name='B.1 Q&S Repository',
                                       endpoint='questionnaire_questionnaire_view'))
admin_app10.add_view(QuestionView(Question, db.session, name='B.2 Questions Repository',
                                  endpoint='question_questionnaire_view'))
admin_app10.add_view(QuestionnaireQuestionsView(QuestionnaireQuestions, db.session,
                                                name='B.3 Association of Questions to Q&S',
                                                endpoint='questionnaire_questions_questionnaire_view'))
admin_app10.add_view(CompanyView(Company, db.session, name='C.1 Company List',
                                 endpoint='company_questionnaire_view'))
# TODO decode/dropdown lists here
admin_app10.add_view(QuestionnaireCompaniesView(QuestionnaireCompanies, db.session,
                                name='C.2 Association of Questionnaires to Companies',
                                endpoint='questionnaire_companies_questionnaire_view'))
admin_app10.add_view(WorkflowView(Workflow, db.session, name='D.1 List of Workflows',
                                  endpoint='workflow_questionnaire_view'))
admin_app10.add_view(StepView(Step, db.session, name='D.2 List of Steps',
                              endpoint='step_questionnaire_view'))
admin_app10.add_view(WorkflowStepsView(WorkflowSteps, db.session,
                                       name='C.3 Association of Steps to Workflows',
                                       endpoint='workflow_steps_questionnaire_view'))

admin_app10.add_view(ContainerAdmin(Container, db.session, name='Containers'))
#admin_app10.add_view(StatusView(Status, db.session, name='E. Dictionary of Status',
#                                endpoint='status_questionnaire_view'))

@login_required
@role_required('Admin')
# Define the index route
@app.route('/open_admin_app_4')
def open_admin_app_4():
    user_id = current_user.id
    return redirect(url_for('open_admin_4.index'))


@login_required
@role_required('Admin')
@app.route('/master_reset_password')
def master_reset_password():
    return redirect(url_for('admin_reset_password'))


# Route to open F l a s k -Admin
@app.route('/open_admin_app_1')
def open_admin_app_1():
    user_id = current_user.id

    company_row = db.session.query(Company.name) \
        .join(CompanyUsers, CompanyUsers.company_id == Company.id) \
        .filter(CompanyUsers.user_id == user_id) \
        .first()

    company_name = company_row[0] if company_row else None  # Extracting the name attribute

    template = "Area di controllo 1 - Atti, iniziative, documenti"
    placeholder_value = company_name if company_name else None
    formatted_string = template.format(placeholder_value) if placeholder_value else template

    admin_app1.name = formatted_string
    print('*** admin_app1.name', admin_app1.name)

    return redirect(url_for('open_admin.index'))


@app.route('/open_admin_app_2')
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

    print('*** admin_app2.name', admin_app2.name)
    return redirect(url_for('open_admin_2.index'))

# Define the index route
@app.route('/open_admin_app_3')
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

    print('*** admin_app3.name', admin_app3.name)
    return redirect(url_for('open_admin_3.index'))


@login_required
@role_required('Admin')
# Define the index route
@app.route('/open_admin_app_10')
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

    print('*** admin_app10.name', admin_app3.name)

    return redirect(url_for('open_admin_10.index'))


# ADMIN
# unassigned documents (all), to be distributed to workflows and steps
# ====================================================================

class DocumentsNewBaseDataView(ModelView):
    can_create = False  # Optionally disable creation
    can_edit = True  # Optionally disable editing
    can_delete = True  # Optionally disable deletion
    name = 'Documents'
    menu_icon_type = 'glyph'  # You can also use 'fa' for Font Awesome icons
    menu_icon_value = 'glyphicon-list-alt'  # Icon class for the menu item

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name = self.__class__.__name__  # Store the class name

    column_list = [
        'id', 'company_name', 'user_name',
        'interval_name', 'interval_ord', 'fi0',
        'record_type', 'area_name', 'subarea_name',
        'data_type', 'subject_name', 'legal_name',
        'file_path', 'created_on', 'number_of_doc',
        'fc1', 'no_action'
    ]

    column_labels = {'id': 'Document ID', 'company_name': 'Company', 'user_name': 'User',
                     'interval_name': 'Interval', 'interval_ord': 'Interv.#', 'fi0': 'Year',
                     'record_type': 'Type', 'area_name': 'Area', 'subarea_name': 'Subarea',
                     'data_type': 'Data Type', 'subject_name': 'Subject', 'legal_name': 'Doc Type',
                     'file_path': 'File', 'created_on':'Date created', 'number_of_doc': 'Doc. #',
                     'fc1': 'Note', 'no_action': 'No doc.'}
    # column_descriptions

    # Customize inlist for the View class
    column_default_sort = ('created_on', True)
    column_searchable_list = ('company_id', 'user_id', 'fi0', 'subject_id', 'legal_document_id', 'file_path')
    # Adjust based on your model structure
    column_filters = ('company_id', 'user_id', 'fi0', 'subject_id', 'legal_document_id', 'file_path')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('company_id', 'status_id', 'created_by', 'updated_on')

    def get_query(self):
        # Assuming `db` is your SQLAlchemy instance
        query = db.session.query(BaseData)

        # Apply any necessary filters or conditions here
        query = query.filter(BaseData.file_path != None)
        query = query.filter(BaseData.fi0 > (int(get_current_interval(1)[3:]) - 2))  # Filter by year

        # Filter out BaseData records without related StepBaseData records
        subquery = db.session.query(distinct(StepBaseData.base_data_id)).subquery()

        # Assign the subquery result to a variable (alias)
        unrelated_data_ids = subquery

        # Use the alias in the filter clause
        query = query.filter(BaseData.id.notin_(unrelated_data_ids))

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
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


    def get_count_query(self):
        # Return count query for pagination
        return None  # Disable pagination count query

    def get_list(self, page, sort_column, sort_desc, search, filters, page_size=None):

        count, data = super().get_list(page, sort_column, sort_desc, search, filters, page_size)

        # Fetch company and user names for each record
        for item in data:
            if item.company:
                company_name = item.company.name
            else:
                company_name = 'n.a.'

            if item.user:
                user_name = item.user.last_name  # Use the correct attribute for the user's name
            else:
                user_name = 'n.a.'

            if item.interval:
                interval_name = item.interval.description  # Access the name of the Step object
            else:
                interval_name = 'n.a.'

            if item.area:
                area_name = item.area.name  # Access the name of the Step object
            else:
                area_name = 'n.a.'

            if item.subarea:
                subarea_name = item.subarea.name
            else:
                subarea_name = 'n.a.'

            if item.subject:
                subject_name = item.subject.name
            else:
                subject_name = 'n.a.'

            if item.subject:
                legal_name = item.subject.name
            else:
                legal_name = 'n.a.'

            item.company_name = company_name
            item.user_name = user_name
            item.interval_name = interval_name
            item.area_name = area_name
            item.subarea_name = subarea_name
            item.subject_name = subject_name
            item.legal_name = legal_name

        return count, data

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        return model


    # Common action to Flask Admin 'Documents' (attach/detach documents to/from W-S)
    @action('action_manage_workflow_step', 'Workflow Management',
            'Are you sure you want to change documents workflow?')
    def action_manage_workflow_step(self, ids):
        # Parse the list of IDs
        id_list = [int(id) for id in ids]

        # Define the selected columns you want to retrieve
        selected_columns = [BaseData.id, BaseData.user_id, BaseData.company_id,
                            BaseData.interval_id, BaseData.interval_ord, BaseData.fi0,
                            BaseData.record_type, BaseData.area_id, BaseData.subarea_id,
                            BaseData.data_type, BaseData.subject_id, BaseData.legal_document_id,
                            BaseData.file_path, BaseData.created_on, BaseData.number_of_doc,
                            BaseData.fc1, BaseData.no_action]  # Add or remove columns as needed

        # Select specific columns
        selected_documents = BaseData.query.with_entities(*selected_columns).filter(BaseData.id.in_(id_list)).all()

        # Retrieve lists of workflows and steps from your database or any other source
        workflows = Workflow.query.all()
        steps = Step.query.all()

        # Pass the lists of workflows, steps, and selected documents to the template
        return render_template('admin/attach_to_workflow_step.html',
                               workflows=workflows, steps=steps,
                               selected_documents=selected_documents)



class DocumentsAssignedBaseDataView(ModelView):
    can_create = False  # Optionally disable creation
    can_edit = True  # Optionally disable editing
    can_delete = True  # Optionally disable deletion
    name = 'Documents'
    menu_icon_type = 'glyph'  # You can also use 'fa' for Font Awesome icons
    menu_icon_value = 'glyphicon-list-alt'  # Icon class for the menu item

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name = self.__class__.__name__  # Store the class name

    column_list = [
        'id', 'company_name', 'user_name',
        'interval_name', 'interval_ord', 'fi0',
        'record_type', 'area_name', 'subarea_name',
        'data_type', 'subject_name', 'legal_name',
        'file_path', 'created_on', 'number_of_doc',
        'fc1', 'no_action'
    ]

    column_labels = {'id': 'Document ID', 'company_name': 'Company', 'user_name': 'User',
                     'interval_name': 'Interval', 'interval_ord': 'Interv.#', 'fi0': 'Year',
                     'record_type': 'Type', 'area_name': 'Area', 'subarea_name': 'Subarea',
                     'data_type': 'Data Type', 'subject_name': 'Subject', 'legal_name': 'Doc Type',
                     'file_path': 'File', 'created_on':'Date created', 'number_of_doc': 'Doc. #',
                     'fc1': 'Note', 'no_action': 'No doc.'}
    # column_descriptions

    # Customize inlist for the View class
    column_default_sort = ('created_on', True)
    column_searchable_list = ('company_id', 'user_id', 'fi0', 'subject_id', 'legal_document_id', 'file_path')
    # Adjust based on your model structure
    column_filters = ('company_id', 'user_id', 'fi0', 'subject_id', 'legal_document_id', 'file_path')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('company_id', 'status_id', 'created_by', 'updated_on')

    def get_query(self):
        # Assuming `db` is your SQLAlchemy instance
        query = db.session.query(BaseData)

        # Apply any necessary filters or conditions here
        query = query.filter(BaseData.file_path != None)
        query = query.filter(BaseData.fi0 > (int(get_current_interval(1)[3:]) - 2))  # Filter by year

        # Filter out BaseData records without related StepBaseData records
        subquery = db.session.query(distinct(StepBaseData.base_data_id)).subquery()

        # Assign the subquery result to a variable (alias)
        unrelated_data_ids = subquery

        # Use the alias in the filter clause
        query = query.filter(BaseData.id.in_(unrelated_data_ids))

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                # Manager can only see records related to their company_users
                # Assuming you have a relationship named 'user_companies' between User and CompanyUsers models
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


    def get_count_query(self):
        # Return count query for pagination
        return None  # Disable pagination count query

    def get_list(self, page, sort_column, sort_desc, search, filters, page_size=None):

        count, data = super().get_list(page, sort_column, sort_desc, search, filters, page_size)

        # Fetch company and user names for each record
        for item in data:
            if item.company:
                company_name = item.company.name
            else:
                company_name = 'n.a.'

            if item.user:
                user_name = item.user.last_name  # Use the correct attribute for the user's name
            else:
                user_name = 'n.a.'

            if item.interval:
                interval_name = item.interval.description  # Access the name of the Step object
            else:
                interval_name = 'n.a.'

            if item.area:
                area_name = item.area.name  # Access the name of the Step object
            else:
                area_name = 'n.a.'

            if item.subarea:
                subarea_name = item.subarea.name
            else:
                subarea_name = 'n.a.'

            if item.subject:
                subject_name = item.subject.name
            else:
                subject_name = 'n.a.'

            if item.subject:
                legal_name = item.subject.name
            else:
                legal_name = 'n.a.'

            item.company_name = company_name
            item.user_name = user_name
            item.interval_name = interval_name
            item.area_name = area_name
            item.subarea_name = subarea_name
            item.subject_name = subject_name
            item.legal_name = legal_name

        return count, data

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        # Perform actions relevant to both creation and edit:
        user_id = current_user.id  # Get the current user's ID or any other criteria
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
            pass

        return model


    # Common action to Flask Admin 'Documents' (attach/detach documents to/from W-S)
    # TODO sostituire/complement action_manage_workflow_step con action_one_step_forward (to be built) - incuding MESSAGE etc etc
    @action('action_manage_workflow_step', 'Workflow Management',
            'Are you sure you want to change documents workflow?')
    def action_manage_workflow_step(self, ids):
        # Parse the list of IDs
        id_list = [int(id) for id in ids]

        # Define the selected columns you want to retrieve
        selected_columns = [BaseData.id, BaseData.user_id, BaseData.company_id,
                            BaseData.interval_id, BaseData.interval_ord, BaseData.fi0,
                            BaseData.record_type, BaseData.area_id, BaseData.subarea_id,
                            BaseData.data_type, BaseData.subject_id, BaseData.legal_document_id,
                            BaseData.file_path, BaseData.created_on, BaseData.number_of_doc,
                            BaseData.fc1, BaseData.no_action]  # Add or remove columns as needed

        # Select specific columns
        selected_documents = BaseData.query.with_entities(*selected_columns).filter(BaseData.id.in_(id_list)).all()

        # Retrieve lists of workflows and steps from your database or any other source
        workflows = Workflow.query.all()
        steps = Step.query.all()

        # Pass the lists of workflows, steps, and selected documents to the template
        return render_template('admin/attach_to_workflow_step.html',
                               workflows=workflows, steps=steps,
                               selected_documents=selected_documents)



# TODO: ***** inserire come action: move one step forward!

@app.route('/detach_documents_from_workflow_step', methods=['POST'])
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


@app.route('/attach_documents_to_workflow_step', methods=['POST'])
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
                auto_move=0 # Include start_recall in the initialization
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


# for document workflow management (forward, backward, deadlines etc) - for already distributed documents
class DocumentsBaseDataDetails(ModelView):
    can_create = True  # Optionally disable creation
    can_edit = True  # Optionally disable editing
    can_delete = True  # Optionally disable deletion

    can_view_details = True

    name = 'Manage Document Flow'
    menu_icon_type = 'glyph'  # You can also use 'fa' for Font Awesome icons
    menu_icon_value = 'glyphicon-list-alt'  # Icon class for the menu item


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name = self.__class__.__name__  # Store the class name

    column_list = [
        'id', 'base_data.file_path', 'base_data.created_on', 'company_name', 'user_name',
        'workflow.name', 'step.name', 'status_id', 'auto_move',
        'start_date', 'deadline_date', 'end_date', 'start_recall', 'deadline_recall',
        'end_recall', 'recall_unit', 'hidden_data'
    ]

    column_labels = {
        'id': 'ID',
        'base_data.file_path': 'Document Name', 'base_data.created_on': 'Created',
        'company_name': 'Company', 'user_name': 'User',
        'workflow_id': 'Workflow', 'step_id': 'Phase',
        'status_id': 'Status', 'auto_move': 'Auto transition',
        'start_date': 'Start', 'deadline_date': 'Deadline', 'end_date': 'End',
        'start_recall': 'Start Recall', 'deadline_recall': 'Deadline Recall',
        'end_recall': 'End Recall', 'recall_unit': 'Recall Unit', 'hidden_data': 'Miscellanea'
    }
    # column_descriptions

    # Customize inlist for the View class
    column_default_sort = ('base_data.created_on', True)
    column_searchable_list = ('base_data.file_path', 'workflow_id', 'step_id', 'start_date', 'deadline_date')
    # Adjust based on your model structure
    column_filters = ('base_data.file_path', 'workflow_id', 'step_id', 'start_date', 'deadline_date')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('base_data.id')

    def get_query(self):
        query = super().get_query()
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                company_ids = [base_data.company_id for base_data in query.join('base_data').all()]
                query = query.filter(StepBaseData.company_id.in_(company_ids))
            elif current_user.has_role('Employee'):
                base_data_query = query.join('base_data').filter(BaseData.user_id == current_user.id)
                company_ids = [base_data.company_id for base_data in base_data_query]
                query = query.filter(StepBaseData.company_id.in_(company_ids))

        # Modify the query to join Company and User tables to access their names
        query = query.join(StepBaseData.base_data).join(BaseData.company).join(BaseData.user)

        return query

    def get_list(self, page, sort_column, sort_desc, search, filters, page_size=None):
        # Define a custom get_list method to fetch company and user names
        count, data = super().get_list(page, sort_column, sort_desc, search, filters, page_size)

        # Fetch company and user names for each record
        for item in data:
            if item.base_data and item.base_data.company:
                company_name = item.base_data.company.name
            else:
                company_name = "N/A"  # Or any default value
            if item.base_data and item.base_data.user:
                user_name = item.base_data.user.last_name  # Use the correct attribute for the user's name
            else:
                user_name = "N/A"
            if item.base_data and item.base_data:
                created_on = item.base_data.created_on  # Use the correct attribute for the user's name
            else:
                created_on = "N/A"

            if item.base_data and item.workflow:  # Access the ID of the Workflow object
                workflow_id =  item.workflow.id
            else:
                workflow_id = "N/A"
            if item.base_data and item.step:
                step_name = item.step.name  # Access the name of the Step object
            else:
                step_name = "N/A"

            item.company_name = company_name
            item.user_name = user_name
            item.workflow_id = workflow_id
            item.step_name = step_name
            item.created_on = created_on

        return count, data


    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True

        return False

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        # Reset form data
        form.populate_obj(model)  # This resets the form data to its default values

        # print('method is', form.get('_method'), form.get('_method') in ['PUT', 'PATCH'])

        if is_created:
            # Handle new model creation:
            # - Set default values
            # - Send notification
            # Apply your custom logic to set data_type
            model.created_on = datetime.now()  # Set the created_on
            pass
        else:
            # Handle existing model edit:
            # - Compare previous and updated values
            # - Trigger specific actions based on changes
            pass

        return model


    # Common action to Flask Admin 'Documents' (attach/detach documents to/from W-S)
    @action('action_manage_dws_deadline', 'Deadline Setting',
            'Are you sure you want to change documents deadline?')
    def action_manage_dws_deadline(self, ids):
        # Parse the list of IDs
        id_list = [int(id) for id in ids]

        # Define the selected columns you want to retrieve
        '''
        # 23Mar
        column_list = [StepBaseData.id, StepBaseData.base_data_id, StepBaseData.workflow_id,
                       StepBaseData.step_id, StepBaseData.status_id, StepBaseData.auto_move,
                       StepBaseData.start_date, StepBaseData.deadline_date, StepBaseData.end_date,
                       StepBaseData.hidden_data, StepBaseData.start_recall, StepBaseData.deadline_recall,
                       StepBaseData.end_recall, StepBaseData.recall_unit]  # Add or remove columns as needed
        '''
        column_list = [StepBaseData.base_data_id, StepBaseData.workflow_id,
                       StepBaseData.step_id, StepBaseData.status_id, StepBaseData.auto_move,
                       StepBaseData.start_date, StepBaseData.deadline_date, StepBaseData.end_date,
                       StepBaseData.hidden_data, StepBaseData.start_recall, StepBaseData.deadline_recall,
                       StepBaseData.end_recall, StepBaseData.recall_unit]  # Add or remove columns as needed
        # Select specific columns
        #23Mar
        # selected_documents = StepBaseData.query.with_entities(*column_list).filter(StepBaseData.id.in_(id_list)).all()
        selected_documents = StepBaseData.query.with_entities(*column_list).filter(StepBaseData.base_data_id.in_(id_list)).all()

        # Pass the lists of workflows, steps, and selected documents to the template
        return render_template('admin/set_documents_deadline.html',
                               selected_documents=selected_documents)


@app.route('/action_manage_dws_deadline', methods=['POST'])
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



from custom_encoder import CustomJSONEncoder
# Use the custom JSON encoder
app.json_encoder = CustomJSONEncoder

admin_app3 = Admin(app,
                   name='Documents Workflow',
                   url='/open_admin_3',
                   template_mode='bootstrap4',
                   endpoint='open_admin_3',
                   )


admin_app3.add_view(ModelView(name='Workflows Dictionary', model=Workflow, session=db.session))
admin_app3.add_view(ModelView(name='Steps Dictionary', model=Step, session=db.session))
admin_app3.add_view(DocumentsAssignedBaseDataView(name='Documents Assigned to Workflows', model=BaseData, session=db.session,
                                          endpoint='assigned_documents'))
admin_app3.add_view(DocumentsNewBaseDataView(name='New Unassigned Documents', model=BaseData, session=db.session,
                                                    endpoint='new_documents'))
admin_app3.add_view(DocumentsBaseDataDetails(name='Documents Workflow Management', model=StepBaseData, session=db.session))



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
def get_subject_name(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()

    if subject:
        return jsonify({'name': subject.name})
    else:
        return jsonify({'name': 'Not Found'})

@app.route('/handle_dynamic_url/<endpoint>')
def handle_dynamic_url(endpoint):
    # You can handle the dynamic URL here, for example, redirect to a default view
    return redirect(url_for('index'))


# Define the custom Jinja2 filter
def list_intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

# Create a custom filter to replace Undefined with None
def replace_undefined(value):
    return None if value is Undefined else value


# Load menu items from JSON file
json_file_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'menuStructure101.json')
# json_file_path = get_current_directory() + "/static/js/menuStructure101.json"
with open(Path(json_file_path), 'r') as file:
    main_menu_items = json.load(file)


# Create an instance of MenuBuilder
menu_builder = MenuBuilder(main_menu_items, ["Guest"])
parsed_menu_data = menu_builder.parse_menu_data(user_roles=["Guest"], is_authenticated=False, include_protected=False)

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
    print("employee route")
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
    # print('guest page')
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
@app.route('/access/signup', methods=['GET', 'POST'])
def signup():
    # Setup logging
    #logging.debug('Signup route accessed')

    clear_flashed_messages()
    form = RegistrationForm()
    print('signup1')
    if form.validate_on_submit():
        print('signup1 2')
        new_user = Users(
            username=form.username.data,
            email=form.email.data,
            user_2fa_secret=pyotp.random_base32(),
            first_name=form.first_name.data,
            mid_name=form.mid_name.data,
            last_name=form.last_name.data,
            address=form.address.data,
            address1=form.address1.data,
            city=form.city.data,
            province=form.province.data,
            region=form.region.data,
            zip_code=form.zip_code.data,
            country=form.country.data,
            tax_code=form.tax_code.data,
            mobile_phone=form.mobile_phone.data,
            work_phone=form.work_phone.data,
            created_on=datetime.now(),
            updated_on=datetime.now()

            # Add other fields from the form as needed
        )

        try:
            # Set the hashed password
            new_user.set_password(form.password.data)

            db.session.add(new_user)

            try:
                db.session.commit()

            except Exception as commit_error:
                # logging.error(f'Error committing to the database: {commit_error}')
                db.session.rollback()
                flash('An error occurred during signup', 'error')
                return render_template('access/signup.html', title='Sign Up', form=form)

            # Retrieve the newly assigned user ID

            new_user_id = new_user.id

            # Create a new record in UserRoles table
            # user_role_employee = UserRoles(user_id=new_user_id, role_id=4)
            # db.session.add(user_role_employee)

            # Create a new record in UserRoles table for role ID 5 (Guest)

            user_role_guest = UserRoles(user_id=new_user_id, role_id=5)

            db.session.add(user_role_guest)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))

        except IntegrityError as e:
            print('signup 11', e)
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('access/signup.html', form=form)

    return render_template('access/signup.html', title='Sign Up', form=form)


# TODO this is a test route. TB cancelled
@app.route('/create_step', methods=['GET', 'POST'])
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


@app.route('/home/contact/email',  methods=['GET', 'POST'])
def contact_email():
    return render_template('home/contact.html')

@app.route('/home/contact/phone',  methods=['GET', 'POST'])
def contact_phone():
    return render_template('home/contact.html')


@app.route('/home/privacy_policy',  methods=['GET', 'POST'])
def privacy_policy():
    return render_template('home/privacy_policy.html')


@app.route('/home/mission',  methods=['GET', 'POST'])
def mission():
    return render_template('home/mission.html')

@app.route('/home/services',  methods=['GET', 'POST'])
def services():
    return render_template('home/services.html')

@app.route('/home/history',  methods=['GET', 'POST'])
def history():
    return render_template('home/history.html')


@app.route('/workflow/control_areas/area_1', methods=['GET', 'POST'])
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
        print(e)
        return jsonify({"message": "Error saving card content"})


@app.route('/workflow/control_areas/area_3',  methods=['GET', 'POST'])
def area_3():
    # Assuming user_id is available, adjust the query accordingly
    user_id = current_user.id  # Implement your user authentication logic
    specific_table = Table.query.filter_by(user_id=user_id, name='Tabella 3').first()
    # Replace 1 with the actual ID of the table you want to display
    tables = Table.query.filter_by(user_id=user_id, name='Tabella 3').all()

    return render_template('workflow/control_areas/area_3.html',
                           specific_table=specific_table, tables=tables)


@app.route('/update_cell', methods=['POST'])
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
def dashboard_company():
    # Your view logic goes here
    return render_template('dashboard/company.html')


@app.route('/overview_statistics_1')
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
    return render_template('base_cards_template.html', cards=card_data, create_card=create_card)

@app.route('/deadlines_1')
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
    print(cards)
    return render_template('base_cards_deadlines_template.html', cards=cards)


@app.route('/dashboard_company_audit')
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
def handle_card_click():
    card_id = request.args.get('id')
    # Handle the card click action here, if needed
    return redirect(url_for('open_admin', card_id=card_id))


''' 
System setup, admin: Company->User(s)
'''
@app.route('/dashboard_setup_companies_users')
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
def dashboard_setup_user_roles():

    # Generate HTML report
    report_data = generate_user_role_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="User-Role Relationship Report", columns=["User", "Last Name", "Role"], rows=report_data)


''' 
System setup, admin: Questionnaire->Question(s)
'''

@app.route('/dashboard_setup_questionnaire_questions')
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
def generate_setup_company_questionnaire():
    # Generate HTML report
    report_data = generate_company_questionnaire_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="Questionnaires and Companies", columns=["Company", "Questionnaire name", "Questionnaire id"], rows=report_data)


@app.route('/dashboard_setup_workflow_steps')
def dashboard_setup_workflow_steps():
    # Generate HTML report
    report_data = generate_workflow_step_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="Workflows and Steps", columns=["Workflow id", "Workflow name", "Step id", "Step name"], rows=report_data)

'''
report of workflow of documents
'''
@app.route('/dashboard_setup_workflow_base_data')
def dashboard_setup_workflow_base_data():

    # Generate HTML report
    report_data_raw = generate_workflow_document_report_data(db.session)
    report_data = []
    for data in report_data_raw:
        file_name, file_extension = extract_filename_and_extension(data[0])
        #print(f"{file_name}{file_extension}")
        report_data.append([f"{file_name}{file_extension}", data[1]])

    # Render the template with the report data
    return render_template('generic_report.html', title="Workflow of Documents", columns=["Document", "Workflow"], rows=report_data)

'''
Route to manage trilateral link document/workflow/step
'''
@app.route('/dashboard_setup_step_base_data')
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
        #print(f"{file_name}{file_extension}")
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
def dashboard_setup_area_subareas():
    # Generate HTML report
    report_data = generate_area_subarea_report_data(db.session)

    # Render the template with the report data
    return render_template('generic_report.html', title="Control Areas and Subareas", columns=["Area", "Subarea", "Data Type"], rows=report_data)


@app.route('/dashboard_company_audit_progression')
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

    sorted_values_raw = get_pd_report_from_base_data_wtq(engine)
    # Example usage to filter 'current' records
    sorted_values = filter_records_by_time_qualifier(sorted_values_raw, time_scope)

    if is_user_role(session, current_user.id, 'Admin'):
        company_id = None  # will list all companies' cards
    else:
        company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id

    html_cards = generate_html_cards_progression_with_progress_bars_in_short(sorted_values, time_scope or {}, session,
                                                                       company_id)

    # Write HTML code to a file
    with open('report_cards1.html', 'w') as f:
        f.write(html_cards)

    return render_template('admin_cards_progression.html', html_cards=html_cards, user_roles=user_roles)


@app.route('/company_overview_current')
def company_overview_current():
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

        sorted_values_raw = get_pd_report_from_base_data_wtq(engine)
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



@app.route('/company_overview_historical')
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

    # Example usage to filter 'current' records
    sorted_values = filter_records_by_time_qualifier(sorted_values_raw, time_scope)

    if is_user_role(db.session, current_user.id, 'Admin'):
        company_id = None # will list all companies' cards
    else:
        company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id

    html_cards = generate_html_cards_progression_with_progress_bars111(sorted_values, time_scope, db.session, company_id)

    # Write HTML code to a file
    with open('report_cards1.html', 'w') as f:
        f.write(html_cards)

    return render_template('admin_cards_progression.html', html_cards=html_cards, user_roles=user_roles)


@app.route('/control_area_1')
def control_area_1():
    # Get the current route from the request object
    current_route = request.url_rule
    user_roles = session.get('user_roles', [])

    # Your view logic goes here
    current_route_url = current_app.url_for('control_area_1')

    if "area_1" in current_route_url:
        left_menu_items = get_left_menu_items_limited(user_roles, 'area_1')
        # Render the template using the current route information and left menu items
        return render_template('control_area_1.html',
                               current_route=current_route, left_menu_items=left_menu_items)

    # If the condition is not met, you should still return a response
    return render_template('control_area_1.html',
                           current_route=current_route, left_menu_items=None)

@app.route('/control_area_2')
def control_area_2():
    # Get the current route from the request object
    current_route = request.url_rule
    user_roles = session.get('user_roles', [])

    # Your view logic goes here
    current_route_url = current_app.url_for('control_area_2')

    if "area_2" in current_route_url:
        left_menu_items = get_left_menu_items_limited(user_roles, 'area_2')

        # Render the template using the current route information and left menu items
        return render_template('control_area_2.html',
                               current_route=current_route, left_menu_items=left_menu_items)

    # If the condition is not met, you should still return a response
    return render_template('control_area_2.html',
                           current_route=current_route)


@app.route('/control_area_3')
def control_area_3():
    # Get the current route from the request object
    current_route = request.url_rule
    user_roles = session.get('user_roles', [])

    # Your view logic goes here
    current_route_url = current_app.url_for('control_area_3')

    if "area_3" in current_route_url:
        left_menu_items = get_left_menu_items_limited(user_roles, 'area_3')

        # Render the template using the current route information and left menu items
        return render_template('control_area_3.html',
                               current_route=current_route, left_menu_items=left_menu_items)

    # If the condition is not met, you should still return a response
    return render_template('control_area_3.html',
                           current_route=current_route_url)



@app.route('/home/site_map',  methods=['GET', 'POST'])
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
@role_required('Admin')
def manage_user_roles():
    form = UserRoleForm()
    message = None

    # Populate choices for users and roles
    form.user.choices = [(user.id, user.username) for user in Users.query.all()]
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]

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
                #flash('User-role association already exists', 'warning')

            else:
                # Add logic to associate the user with the selected role
                new_user_role = UserRoles(user_id=user_id, role_id=role_id)
                db.session.add(new_user_role)
                db.session.commit()
                # Set a success message
                message = "User role added successfully."
                #flash('User-role association added successfully', 'success')

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
                #flash('User-role association deleted successfully', 'success')        # Set a success message

            else:
                message = "User role not found."
                #flash('User-role association not found', 'warning')

    return render_template('manage_user_roles.html', form=form, message=message)


@app.route('/manage_workflow_steps', methods=['GET', 'POST'])
@role_required('Admin')
def manage_workflow_steps():
    form = WorkflowStepForm()
    message = None

    # Populate choices for workflows and steps
    form.workflow.choices = [(workflow.id, workflow.name) for workflow in Workflow.query.all()]
    form.step.choices = [(step.id, step.name) for step in Step.query.all()]

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

    return render_template('manage_workflow_steps.html', form=form, message=message)


@app.route('/manage_workflow_base_data', methods=['GET', 'POST'])
@role_required('Admin')
def manage_workflow_base_data():
    form = WorkflowBaseDataForm()
    message = None

    # Populate choices for workflows and steps
    form.workflow.choices = [(workflow.id, workflow.name) for workflow in Workflow.query.all()]
    form.base_data.choices = [(base_data.id, base_data.file_path) for base_data in
                              BaseData.query.filter(BaseData.file_path.isnot(None)).all()]

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

            # Find and delete the wkf-base_data association
            workflow_base_data_to_delete = WorkflowBaseData.query.filter_by(workflow_id=workflow_id, base_data_id=base_data_id).first()

            if workflow_base_data_to_delete:
                db.session.delete(workflow_base_data_to_delete)
                db.session.commit()
                message = f"Document link to <{workflow_name}> deleted successfully."
            else:
                message = "Workflow-document link not found."

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
@role_required('Admin')
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



@app.route('/show_survey/<int:questionnaire_id>', methods=['GET', 'POST'])
@login_required  # This decorator ensures that the route is only accessible to authenticated users
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
            # print('existing answer found', existing_answer.answer_data)
            merged_fields = merge_answer_fields(question.answer_fields, existing_answer.answer_data)  # Make sure this function is set to merge JSON fields correctly
            form_data[str(question.id)] = merged_fields
        else:
            # print('no existing data found')
            form_data[str(question.id)] = question.answer_fields

        questions.append({
            'id': question.id,
            'question_id': question.question_id,
            'text': question.text,
            'answer_type': question.answer_type,
            'answer_width': question.answer_width,
            'answer_fields': form_data[str(question.id)]
        })
    # print('questions list', questions)
    dynamic_html = create_dynamic_form(form, {'questions': questions, 'form_data': form_data}, company_id, horizontal)  # Adjust this function to accept horizontal flag
    return render_template('survey.html', form=form, headers=headers, dynamic_html=dynamic_html, questionnaire_name=selected_questionnaire.name, today=datetime.now().date())


# Example use within the Flask view function
@app.route('/show_survey_sqlite/<int:questionnaire_id>', methods=['GET', 'POST'])
@login_required  # This decorator ensures that the route is only accessible to authenticated users
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
        print('serialize answers, key:', key)
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


@app.route('/company_files/<company_id>', methods=['GET'])
@login_required  # Ensure user is logged in
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


@app.route('/download_file/<company_id>/<filename>', methods=['GET'])
@login_required
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


@app.route('/back')
def back():
    # Add any logic you need before redirecting, if necessary
    return redirect(url_for('home'))  # Assuming 'home' is the route for your home page


@app.route('/')
def home():

    # app.logger.debug("Home route accessed")
    return render_template('index.html')  # Render your home page template


@app.route('/noticeboard')
@login_required  # Ensure user is logged in
def noticeboard():
    # Retrieve unmarked messages from the database
    user_id = current_user.id
    unmarked_messages = Post.query.filter_by(user_id=user_id, marked_as_read=False).all()

    # Pass the messages to the template for rendering
    return render_template('home/noticeboard.html', unmarked_messages=unmarked_messages)


@app.route('/auditlog')
@login_required  # Ensure user is logged in
@role_required('Admin') # only for the admin
def auditlog():
    # Retrieve unmarked messages from the database
    audit_log = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    # Pass the messages to the template for rendering
    return render_template('home/auditlog.html', audit_log=audit_log)


def print_routes():
    with current_app.test_request_context():
        print(current_app.url_map)



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

    # Start the application
    # app.run(debug=False, port=5000, host='localhost', extra_files=['./static/js/menuStructure101.json'])
    # Change the port number

    ''' 25May2024
    port = int(os.environ.get('PORT', 5000)) # 5000
    app.run(debug=True, host='0.0.0.0', port=port, extra_files=['./static/js/menuStructure101.json'])
    '''
    #port = int(os.environ.get('PORT', 5000))

    port = int(os.environ.get('PORT', 5000))
    #logging.basicConfig(level=logging.DEBUG)
    # logging.debug(f"Starting app on port {port}")
    # TODO DEBUG
    app.run(debug=False, host='0.0.0.0', port=port, extra_files=['./static/js/menuStructure101.json'])