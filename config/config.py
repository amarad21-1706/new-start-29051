
import secrets
import os
from db import db

from models.user import (Company, CompanyUsers, Users, Role, UserRoles,
                         Area, Subarea, AreaSubareas, Deadline, Interval,
                         QuestionnaireCompanies, Questionnaire, Question, QuestionnaireQuestions,
                         get_config_values, Workflow, Step, BaseData, WorkflowSteps,
                         WorkflowBaseData, StepBaseData, Post, AuditLog)

# from sqlalchemy import or_, and_, desc, func, null
# import pandas as pd
# from sqlalchemy.orm import subqueryload
# from flask import Flask, session, redirect, url_for

from dateutil.relativedelta import relativedelta

import pandas as pd

from flask_login import current_user
import json
import pytz

import os
from dotenv import load_dotenv
import redis

load_dotenv()  # Load environment variables from .env file if present

def user_has_edit_workflow_permission(current_user):
    # Replace this with your logic to check user roles or permissions
    return current_user.role in ['Admin', 'Authority']  # Example based on user roles

def user_has_edit_step_permission(current_user):
    # Replace this with your logic to check user roles or permissions
    return current_user.role in ['Admin', 'Authority']  # Example based on user roles

def get_cet_time():
    # Get the current time in UTC
    utc_now = datetime.utcnow()

    # Convert UTC time to CET
    utc_timezone = pytz.timezone('UTC')
    cet_timezone = pytz.timezone('CET')
    utc_now = utc_timezone.localize(utc_now)
    cet_now = utc_now.astimezone(cet_timezone)

    return cet_now

class Config:
    def __init__(self):
        # Get the absolute path to the directory of the current script
        self.current_directory = os.getcwd()

        # Extract /config part
        self.config_directory = os.path.normpath(os.path.join(self.current_directory, 'config'))
        # Other configurations

        # SQLite
        '''
        self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{self.current_directory}/database/sysconfig.db"
        self.SQLALCHEMY_BINDS = {
            "db1": f"sqlite:///{self.current_directory}/database/sysconfig.db",
        }
        '''

        self.SECRET_KEY = os.environ.get('SECRET_KEY_2')
        self.SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT_')

        # PostgreSQL
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        self.SQLALCHEMY_BINDS = {
            'db1': os.environ.get('DATABASE_URL_DB1')
        }
        # TODO DEBUG deactivate in prod or after first debug row
        # self.DEBUG = True
        self.SQLALCHEMY_ECHO = False  # This will log all or none of the SQL queries
        self.SQLALCHEMY_TRACK_MODIFICATIONS = True
        # self.DEBUG_TB_INTERCEPT_REDIRECTS = False

        self.BOOTSTRAP_USE_MINIFIED = False
        self.BOOTSTRAP_SERVE_LOCAL = True
        self.EXCEPT_FIELDS = ["id", "email", "user_id", "role_id", "created_on", "updated_on",
                              "end_of_registration", "password", "company_id", "company"]
        self.CURRENT_DIRECTORY = self.current_directory
        self.UPLOAD_FOLDER = f"/{self.current_directory}/static/docs"
        self.COMPANY_FILES_DIR =f"/{self.current_directory}/static/docs/company_files/"
        self.CRUD_ADD_TEMPLATE = f"/{self.current_directory}/templates/crud_add_template.html"

        self.STATIC_FOLDER = 'static'
        self.ASSETS_FOLDER = 'assets'
        self.MAX_RECURSION_DEPTH = 1000
        self.TEMPLATES_AUTO_RELOAD = True
        self.SQLALCHEMY_COMMIT_ON_TEARDOWN = True
        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)  # Set session to expire in 5 minutes
        self.SEND_FILE_MAX_AGE_DEFAULT = 0  # Disable caching for development

        # self.SESSION_TYPE = 'filesystem'
        self.SESSION_TYPE = 'redis'
        self.SESSION_REDIS = redis.StrictRedis(host='localhost', port=6379)

        self.SEND_FILE_MAX_AGE_DEFAULT = 0  # Disable caching for development

        self.RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
        self.RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

        # CAPTCHA
        # selfRECAPTCHA_PUBLIC_KEY = some_keys['recaptcha_public_key']
        # selfRECAPTCHA_PRIVATE_KEY = some_keys['recaptcha_private_key']
        self.WTF_CSRF_ENABLED = False  # Disable CSRF protection for local development

        '''
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {
                'options': '-c statement_timeout=60000',  # Set timeout to 60 seconds
                'connect_timeout': 30  # Set connection timeout to 30 seconds
            }
        }
        '''

        self.SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,  # Recycle connections after 30 minutes
            'pool_pre_ping': True,  # Check connections before using them
            'connect_args': {
                'options': '-c statement_timeout=60000',  # Set timeout to 60 seconds
                'connect_timeout': 30  # Set connection timeout to 30 seconds
            }
        }

        self.TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
        self.TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
        self.TWILIO_AUTHY_API_KEY = os.environ.get('TWILIO_AUTHY_API_KEY')

        #self.SESSION_COOKIE_HTTPONLY = True
        #self.SESSION_COOKIE_SECURE = True  # Only set to True if using HTTPS

        # Emailing
        '''
        self.MAIL_SERVER = 'localhost'
        self.MAIL_PORT = 25
        self.MAIL_USERNAME = None
        self.MAIL_PASSWORD = None
        self.MAIL_USE_TLS = False
        self.MAIL_USE_SSL = False
        '''

        self.MAIL_SERVER = 'smtp.gmail.com'
        self.MAIL_PORT = 587
        self.MAIL_USERNAME = 'arad.mara@gmail.com'
        self.MAIL_PASSWORD = ' *******'
        self.MAIL_USE_TLS = True
        self.MAIL_USE_SSL = False

        self.STRIPE_API_KEY = 'your_stripe_api_key'
        self.STRIPE_PUBLISHABLE_KEY = 'your_stripe_publishable_key'


# Define a custom JSON encoder class to handle datetime serialization
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

some_keys = {

    "secret_key_2": secrets.token_hex(16),
}
# "recaptcha_public_key": '6LdcYnkpAAAAADpQdytwQVK7UtxeJJ0C_nHsPc8R',
# "recaptcha_private_key": '6LdcYnkpAAAAAKOWGB7_cEBlY-3UlBGZY9KS6zH9',
# "security_password_salt": '329d29b7bedc86e66ea3456b3a49ff9328b082649a1bc3b02ecb6f5881d2a380',
#    "secret_key_1": 'see .env',

sample_answer = {
    "questionnaire_id": None,  # Initialize with appropriate values
    "question_id": None,
    "company_id": None,
    "user_id": None,
    "text": "",  # Initialize with appropriate values
    "score": 0,  # Initialize with appropriate values
    "file": None,  # Initialize with appropriate values
    "comment": "",  # Initialize with appropriate values
    "date": None  # Initialize with appropriate values
}

encoding_scheme = {
  'TST': {'type': 'Text', 'characteristic': 'Short Text'},
  'TLT': {'type': 'Text', 'characteristic': 'Long Text'},
  'NI': {'type': 'Number', 'characteristic': 'Integer'},
  'NI(0-10)': {'type': 'Number', 'characteristic': 'Integer', 'min': 0, 'max': 10, 'step': None},
  'ND': {'type': 'Number', 'characteristic': 'Decimal'},
  'NF': {'type': 'Number', 'characteristic': 'Float'},
  'FILE': {'type': 'File', 'characteristic': 'Any'},
  'DD': {'type': 'Date', 'characteristic': 'Date Only'},
  'DT': {'type': 'Date', 'characteristic': 'Time Only'},
  'DDT': {'type': 'Date', 'characteristic': 'Date and Time'},
  'BYN': {'type': 'Boolean', 'characteristic': 'Yes/No'},
}


def decode_question_type(code, encoding_scheme):

    if '(' in code and ')' in code:
        base_code, extra_info = code.split('(')

        if extra_info.endswith(')'):
            extra_info = extra_info[:-1]  # Remove the closing parenthesis

            if '-' in extra_info:
                min_value, max_value = extra_info.split('-')

                if min_value.isdigit() and max_value.isdigit():
                    min_value = int(min_value)
                    max_value = int(max_value)
                    base_code_with_parentheses = f"{base_code}({extra_info})"

                    if base_code_with_parentheses in encoding_scheme:
                        decoded = encoding_scheme[base_code_with_parentheses]
                        decoded['min'] = min_value
                        decoded['max'] = max_value

                        if decoded['type'] == 'Number' and decoded[
                            'characteristic'] == 'Integer' and min_value == 0 and max_value == 10:
                            return f"Type: {decoded['type']}, Characteristic: {decoded['characteristic']} (0-10)"
                        else:
                            return f"Type: {decoded['type']}, Characteristic: {decoded['characteristic']}, Min: {decoded['min']}, Max: {decoded['max']}"
                    else:
                        return "Invalid code"
                else:
                    return "Invalid code (Non-numeric min or max value)"
            else:
                return "Invalid code (Missing '-' between min and max)"
        else:
            return "Invalid code (Unmatched parentheses)"
    else:
        adjusted_code = code.upper() if 'FILE' in encoding_scheme.keys() else code

        if adjusted_code in encoding_scheme:
            decoded = encoding_scheme[adjusted_code]

            if 'min' in decoded and 'max' in decoded:
                return f"Type: {decoded['type']}, Characteristic: {decoded['characteristic']}, Min: {decoded['min']}, Max: {decoded['max']}"
            else:
                return f"Type: {decoded['type']}, Characteristic: {decoded['characteristic']}"
        else:
            return "Invalid code"


def decode_answer_types(answer_type_list, encoding_scheme):
    """
    This function decodes a list of answer type codes using the provided encoding scheme.

    Args:
        answer_type_list: A string containing comma-separated answer type codes.
        encoding_scheme: A dictionary containing mappings between answer type codes and their characteristics.

    Returns:
        A list of control types or "Invalid" for malformed codes.
    """
    control_types = []
    for code in answer_type_list.split(','):
        decoded_answer = decode_question_type(code.strip(), encoding_scheme)  # Remove leading/trailing whitespace
        # Extract only the control type from the decoded info
        if len(decoded_answer.split(', ')) >= 2:
            control_types.append(decoded_answer.split(', ')[0].split(': ')[1])
        else:
            control_types.append("Invalid")  # Add "Invalid" for malformed codes
    return control_types



# COMPARE STRUCTURES
def normalize_structure(obj):
   if isinstance(obj, dict):
       # For dictionaries, replace each value with its type
       return {k: normalize_structure(v) for k, v in obj.items()}
   elif isinstance(obj, list):
       # For lists, apply normalization to each element
       return [normalize_structure(v) for v in obj]
   else:
       # Replace values with their type names
       return type(obj).__name__

def compare_structures(json1, json2):
   # Normalize both JSON structures
   norm_json1 = normalize_structure(json1)
   norm_json2 = normalize_structure(json2)

   # Compare normalized structures
   return norm_json1 == norm_json2


def generate_answer_controls(decoded_answers):
    # Initialize an empty string to store the generated HTML
    answer_controls_html = ""

    # Iterate over each decoded answer type
    for decoded_answer in decoded_answers:
        # Parse the decoded answer type
        answer_type_info = decoded_answer.split(', ')

        # Check if the answer type info has the expected format
        if len(answer_type_info) >= 2:
            answer_type = answer_type_info[0].split(': ')[1]  # Extract the answer type
            characteristic = answer_type_info[1].split(': ')[1]  # Extract the characteristic

            # Generate the HTML form element based on the answer type
            if answer_type == 'Text':
                if characteristic == 'Short Text':
                    # Generate a short text input field
                    answer_controls_html += '<input type="text" class="form-control">'
                elif characteristic == 'Long Text':
                    # Generate a long text input field (textarea)
                    answer_controls_html += '<textarea class="form-control"></textarea>'
            elif answer_type == 'Number':
                # Generate a number input field
                answer_controls_html += '<input type="number" class="form-control">'
            elif answer_type == 'File':
                # Generate a file input field
                answer_controls_html += '<input type="file" class="form-control-file">'
            elif answer_type == 'Date':
                if characteristic == 'Date Only':
                    # Generate a date picker input field
                    answer_controls_html += '<input type="date" class="form-control">'
                elif characteristic == 'Time Only':
                    # Generate a time picker input field
                    answer_controls_html += '<input type="time" class="form-control">'
                elif characteristic == 'Date and Time':
                    # Generate a date and time picker input field
                    answer_controls_html += '<input type="datetime-local" class="form-control">'
            elif answer_type == 'Boolean':
                # Generate a dropdown for Yes/No/N/A selection
                answer_controls_html += '''
                    <select class="form-control">
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                        <option value="N/A">N/A</option>
                    </select>
                '''
            else:
                # Generate a long text input field (textarea) as default
                answer_controls_html += '<textarea class="form-control"></textarea>'
        else:
            # If the answer type info does not have the expected format, add a placeholder input field
            answer_controls_html += '<input type="text" class="form-control" placeholder="Invalid answer type">'

    # Return the generated HTML for the answer controls
    return answer_controls_html



'''
codes = ['TST', 'NI', 'FIMG', 'DDT', 'BYN']
for code in codes:
  print(decode_question_type(code))

  encoding_scheme['NI'] = {
    'type': 'Number',
    'characteristic': 'Integer',
    'min': 0,
    'max': 100,
    'step': 1
}
'''

# Example usage
'''
answer_type = 'TLT, NI(0-10), FPDF/FDOC/FXLS, TLT'
decoded_answers = decode_answer_types(answer_type)
for decoded_answer in decoded_answers:
    print(decoded_answer)
'''




def prepare_questions_by_answer_type(answer_type):
    # Retrieve questions based on the provided answer_type
    questions = Question.query.filter_by(answer_type=answer_type).all()

    for question in questions:
        answer_fields_json = None  # Initialize to None

        if question.answer_type == 'complex':
            # Prepare the JSON structure only for complex questions (using sample_answer as a base)
            answer_fields_dict = sample_answer.copy()  # Create a copy to potentially modify

            # Modify answer_fields_dict for complex fields based on your needs (optional)
            # ... (your logic for modifying answer_fields_dict for complex questions)

            # Convert to JSON format
            answer_fields_json = json.dumps(answer_fields_dict)

        # Update the answer_fields attribute of the Question object (if applicable)
        question.answer_fields = answer_fields_json

    # Commit the changes to the database
    db.session.commit()


# TODO ******* molto importante: la struttura è scritta sul db, quindi se voglio preparare i camppi per l'utente
# CORRENTE, allora devo trovare un modo per metterla in memora, con user, comopany, questionnaire, data etc
# aggiornate SOLO per l'utente corrente - questo per evitare problemi di concorrenza sulle risorse
def prepare_questions_by_answer_type222(answer_type):
    # Retrieve questions based on the provided answer_type
    questions = Question.query.filter_by(answer_type=answer_type).all()

    for question in questions:
        answer_fields_dict = None  # Initialize to None

        if question.answer_type == 'complex':
            # Check for data before assigning (assuming answer_fields should be a dictionary)
            if question.answer_fields:
                try:
                    answer_fields_dict = json.loads(question.answer_fields)
                except json.JSONDecodeError:
                    # Handle potential JSON parsing errors
                    print(f"Error parsing JSON for question {question.id}: {question.answer_fields}")
            else:
                # If no data available, use an empty dictionary
                answer_fields_dict = {}
        else:
            # Use sample_answer structure for other answer types
            answer_fields_dict = sample_answer.copy()  # Create a copy to avoid modifying the original

        # Convert to JSON format
        answer_fields_json = json.dumps(answer_fields_dict)

        # Update the answer_fields attribute of the Question object
        question.answer_fields = answer_fields_json

    # Commit the changes to the database
    db.session.commit()



def get_company_id(user_id):
    if user_id:
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None
    else:
        company_id = None
    return company_id

def extract_year_from_fy(fy_string):
    parts = fy_string.split()  # Split the string into parts based on spaces
    return parts[-1]  # Return the last part, which should be the year


from datetime import datetime
def get_current_interval(interval):
    now = datetime.now()

    if interval == 1:
        return f'FY {now.year}'
    elif interval == 4:
        quarter = (now.month - 1) // 3 + 1
        return f'T{quarter} {now.year}'
    elif interval == 12:
        return f'M{now.month} {now.year}'
    elif interval == 52:
        week_number = now.strftime('%U')
        return f'W{week_number} {now.year}'
    elif interval == 2:
        semester = 'H1' if now.month <= 6 else 'H2'
        return f'{semester} {now.year}'
    elif interval == 3:
        if now.month in [1, 2, 3, 4]:
            quadrimester = 'Q1'
        elif now.month in [5, 6, 7, 8]:
            quadrimester = 'Q2'
        elif now.month in [9, 10, 11, 12]:
            quadrimester = 'Q3'
        return f'{quadrimester} {now.year}'
    else:
        raise ValueError(f"Unsupported interval: {interval}")

from datetime import datetime, timedelta

from datetime import datetime, timedelta

def set_to_first_day(date, interval_ord, interval_id):
    if interval_id == 1:
        return datetime(date.year, 1, 1)
    elif interval_id == 4:
        month = (interval_ord - 1) * 3 + 1
        return datetime(date.year, month, 1)
    elif interval_id == 12:
        return datetime(date.year, interval_ord, 1)
    elif interval_id == 3:
        month = (interval_ord - 1) * 4 + 1
        return datetime(date.year, month, 1)
    elif interval_id == 2:
        month = 1 if interval_ord == 1 else 7
        return datetime(date.year, month, 1)
    elif interval_id == 26:
        return datetime(date.year, 1, 1) + timedelta(days=(interval_ord - 1) * 14)
    elif interval_id == 52:
        # Assuming the week starts on Monday
        return datetime.fromisocalendar(date.year, interval_ord, 1)
    else:
        return None


def set_to_last_day(date, interval_ord, interval_id):
    if interval_id == 1:
        return datetime(date.year, 12, 31)
    elif interval_id == 4:
        start_month = (interval_ord - 1) * 3 + 1
        end_month = start_month + 2
        end_date = (datetime(date.year, end_month, 1) + relativedelta(months=1)) - timedelta(days=1)
        return end_date if end_date.month == end_month else end_date.replace(day=30)
    elif interval_id == 12:
        return (datetime(date.year, interval_ord, 1) + relativedelta(months=1)) - timedelta(days=1)
    elif interval_id == 3:
        start_month = (interval_ord - 1) * 4 + 1
        end_month = start_month + 3
        end_date = (datetime(date.year, end_month, 1) + relativedelta(months=1)) - timedelta(days=1)
        return end_date if end_date.month == end_month else end_date.replace(day=30)
    elif interval_id == 2:
        start_month = 1 if interval_ord == 1 else 7
        end_month = start_month + 5
        end_date = (datetime(date.year, end_month, 1) + relativedelta(months=1)) - timedelta(days=1)
        return end_date if end_date.month == end_month else end_date.replace(day=30)
    elif interval_id == 26:
        start_date = datetime(date.year, 1, 1) + timedelta(days=(interval_ord - 1) * 14)
        return start_date + timedelta(days=13)
    elif interval_id == 52:
        # Assuming the week ends on Sunday
        start_date = datetime.fromisocalendar(date.year, interval_ord, 1)
        return start_date + timedelta(days=6)
    else:
        return None


def calculate_interval_dates(year_id, interval_ord, interval_id):

    if interval_id == 1:
        start_date = datetime(year_id, 1, 1)
        end_date = datetime(year_id, 12, 31)
    elif interval_id == 4:
        month = (interval_ord - 1) * 3 + 1
        start_date = datetime(year_id, month, 1)
        end_date = (start_date + relativedelta(months=3)) - timedelta(days=1)
    elif interval_id == 12:
        start_date = datetime(year_id, interval_ord, 1)
        end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
    elif interval_id == 3:
        month = (interval_ord - 1) * 4 + 1
        start_date = datetime(year_id, month, 1)
        end_date = (start_date + relativedelta(months=4)) - timedelta(days=1)
    elif interval_id == 2:
        month = 1 if interval_ord == 1 else 7
        start_date = datetime(year_id, month, 1)
        end_date = (start_date + relativedelta(months=6)) - timedelta(days=1)
    elif interval_id == 26:
        start_date = datetime(year_id, 1, 1) + timedelta(days=(interval_ord - 1) * 14)
        end_date = start_date + timedelta(days=13)
    elif interval_id == 52:
        # Assuming the week starts on Monday
        start_date = datetime.fromisocalendar(year_id, interval_ord, 1)
        end_date = start_date + timedelta(days=6)
    else:
        start_date = None
        end_date = None

    config_values = get_config_values(config_type='extra_time', company_id=None, area_id=None, subarea_id=None)

    if config_values[0] < 0:
        start_date = start_date + timedelta(days=config_values[0])
    elif config_values[0] > 0:
        end_date = end_date + timedelta(days=config_values[0])

    return start_date, end_date


# interval_id: 1 year, 2 'semester', 3 quadrimenter, 4 quarter, 12 month, 26 fortnight, 52 week
def check_status(is_created, company_id, subject_id, legal_document_id,
                 year_id, interval_ord, interval_id,
                 area_id, subarea_id, current_date, session):

    # Calculate the start and end dates for the interval
    interval_start_date, interval_end_date = calculate_interval_dates(year_id, interval_ord, interval_id)

    if interval_start_date is None:
        # Handle the case where interval_start_date is None
        return False, "Interval start date is not available"

    # Case 1: The current date is before the interval
    if current_date < interval_start_date:
        return False, "Data can not be entered for a future interval."

    # Case 2: The current date is within the interval
    elif interval_start_date <= current_date <= interval_end_date:
        query = session.query(BaseData)
        # Filter based on non-None parameters (adjust based on your needs):
        if company_id is not None:
            query = query.filter(BaseData.company_id == company_id)

        if subject_id is not None:
            query = query.filter(BaseData.subject_id == subject_id)  # Exact match (can be adjusted)
        if legal_document_id is not None:
            query = query.filter(BaseData.legal_document_id == legal_document_id)  # Exact match  (can be adjusted)
        if year_id is not None:
            query = query.filter(BaseData.fi0 == year_id)
        if interval_ord is not None:
            query = query.filter(BaseData.interval_ord == interval_ord)
        if interval_id is not None:
            query = query.filter(BaseData.interval_id == interval_id)
        if area_id is not None:
            query = query.filter(BaseData.area_id == area_id)
        if subarea_id is not None:
            query = query.filter(BaseData.subarea_id == subarea_id)
        existing_data = query.first()

        # If the data already exists in BaseData, return False
        if existing_data:
            if is_created:
                return False, "Data for this period already exists. Please edit the existing record if needed."
            else:
                return True, "Please edit the existing record if needed."
        else:
            return True, "Data can be registered."

    # Case 3: The current date is after the interval
    else:

        query = session.query(BaseData)

        # Filter based on non-None parameters (adjust based on your needs):
        if company_id is not None:
            query = query.filter(BaseData.company_id == company_id)
        if subject_id is not None:
            query = query.filter(BaseData.subject_id == subject_id)  # Exact match for subject_id (can be adjusted)
        if legal_document_id is not None:
            query = query.filter(BaseData.legal_document_id == legal_document_id)  # Exact match  (can be adjusted)
        if year_id is not None:
            query = query.filter(BaseData.fi0 == year_id)
        if interval_ord is not None:
            query = query.filter(BaseData.interval_ord == interval_ord)
        if interval_id is not None:
            query = query.filter(BaseData.interval_id == interval_id)
        if area_id is not None:
            query = query.filter(BaseData.area_id == area_id)
        if subarea_id is not None:
            query = query.filter(BaseData.subarea_id == subarea_id)
        existing_data = query.first()

        # If the data already exists in BaseData, return False
        if existing_data:
            return False, "Data for this period already exists and cannot be modified."
        else:
            return True, "Data can be added or edited."



# interval_id: 1 year, 2 'semester', 3 quadrimenter, 4 quarter, 12 month, 26 fortnight, 52 week
def check_status_limited(is_created, company_id, subject_id, legal_document_id, year_id, interval_ord, interval_id,
                 area_id, subarea_id, current_date, session):
    # Calculate the start and end dates for the interval
    interval_start_date, interval_end_date = calculate_interval_dates(year_id, interval_ord, interval_id)

    if interval_start_date is None:
        # Handle the case where interval_start_date is None
        return False, "Interval start date is not available"

    # Case 1: The current date is before the interval
    if current_date < interval_start_date:
        return False, "Data can not be entered for a future interval."

    # Case 2: The current date is within the interval
    elif interval_start_date <= current_date <= interval_end_date:
        query = session.query(BaseData)

        # Filter based on non-None parameters (adjust based on your needs):
        if company_id is not None:
            query = query.filter(BaseData.company_id == company_id)
        if subject_id is not None:
            query = query.filter(BaseData.subject_id == subject_id)  # Exact match (can be adjusted)
        if legal_document_id is not None:
            query = query.filter(BaseData.legal_document_id == legal_document_id)  # Exact match  (can be adjusted)
        if year_id is not None:
            query = query.filter(BaseData.fi0 == year_id)
        if interval_ord is not None:
            query = query.filter(BaseData.interval_ord == interval_ord)
        if interval_id is not None:
            query = query.filter(BaseData.interval_id == interval_id)
        if area_id is not None:
            query = query.filter(BaseData.area_id == area_id)
        if subarea_id is not None:
            query = query.filter(BaseData.subarea_id == subarea_id)
        existing_data = query.first()

        # If the data already exists in BaseData, return False
        if existing_data:
            #if is_created:
            #    return False, "Data for this period already exists. Please edit the existing record if needed."
            #else:
            return True, "Please edit the existing record if needed."
        else:
            return True, "Data can be registered."

    # Case 3: The current date is after the interval
    else:

        query = session.query(BaseData)

        # Filter based on non-None parameters (adjust based on your needs):
        if company_id is not None:
            query = query.filter(BaseData.company_id == company_id)
        if subject_id is not None:
            query = query.filter(BaseData.subject_id == subject_id)  # Exact match for subject_id (can be adjusted)
        if legal_document_id is not None:
            query = query.filter(BaseData.legal_document_id == legal_document_id)  # Exact match  (can be adjusted)
        if year_id is not None:
            query = query.filter(BaseData.fi0 == year_id)
        if interval_ord is not None:
            query = query.filter(BaseData.interval_ord == interval_ord)
        if interval_id is not None:
            query = query.filter(BaseData.interval_id == interval_id)
        if area_id is not None:
            query = query.filter(BaseData.area_id == area_id)
        if subarea_id is not None:
            query = query.filter(BaseData.subarea_id == subarea_id)
        existing_data = query.first()

        # If the data already exists in BaseData, return False
        if existing_data:
            return True, "Data for this period already exists."
        else:
            return True, "Data for this period was not found."




# interval_id: 1 year, 2 'semester', 3 quadrimenter, 4 quarter, 12 month, 26 fortnight, 52 week
def check_status_extended(is_created, company_id, lexic_id, subject_id, legal_document_id, interval_ord, interval_id, year_id,
                 area_id, subarea_id, fi1, fi2, fi3, fn1, fn2, fn3, fc1, fc2, fc3, current_date, session):
    # Calculate the start and end dates for the interval
    interval_start_date, interval_end_date = calculate_interval_dates(year_id, interval_ord, interval_id)

    if interval_start_date is None:
        # Handle the case where interval_start_date is None
        return False, "Interval start date is not available"

    # Case 1: The current date is before the interval
    if current_date < interval_start_date:
        return False, "Data can not be entered for a future interval."

    # Case 2: The current date is within the interval
    elif interval_start_date <= current_date <= interval_end_date:
        query = session.query(BaseData)

        # Filter based on non-None parameters (adjust based on your needs):
        if company_id is not None:
            query = query.filter(BaseData.company_id == company_id)
        if subject_id is not None:
            query = query.filter(BaseData.subject_id == subject_id)  # Exact match (can be adjusted)
        if lexic_id is not None:
            query = query.filter(BaseData.lexic_id == lexic_id)  # Exact match (can be adjusted)
        if legal_document_id is not None:
            query = query.filter(BaseData.legal_document_id == legal_document_id)  # Exact match  (can be adjusted)
        if year_id is not None:
            query = query.filter(BaseData.fi0 == year_id)
        if interval_ord is not None:
            query = query.filter(BaseData.interval_ord == interval_ord)
        if interval_id is not None:
            query = query.filter(BaseData.interval_id == interval_id)
        if area_id is not None:
            query = query.filter(BaseData.area_id == area_id)
        if subarea_id is not None:
            query = query.filter(BaseData.subarea_id == subarea_id)
        if fi1 is not None:
            query = query.filter(BaseData.fi1 == fi1)
        if fi2 is not None:
            query = query.filter(BaseData.fi2 == fi2)
        if fi3 is not None:
            query = query.filter(BaseData.fi3 == fi3)
        if fn1 is not None:
            query = query.filter(BaseData.fn1 == fn1)
        if fn2 is not None:
            query = query.filter(BaseData.fn2 == fn2)
        if fn3 is not None:
            query = query.filter(BaseData.fn3 == fn3)
        if fc1 is not None:
            query = query.filter(BaseData.fc1 == fc1)
        if fc2 is not None:
            query = query.filter(BaseData.fc2 == fc2)
        if fc3 is not None:
            query = query.filter(BaseData.fc3 == fc3)
        existing_data = query.first()

        # If the data already exists in BaseData, return False
        if existing_data:
            if is_created:
                return False, "Data for this period already exists. Please edit the existing record if needed."
            else:
                return True, "Please edit the existing record if needed."
        else:
            return True, "Data can be registered."

    # Case 3: The current date is after the interval
    else:

        query = session.query(BaseData)

        # Filter based on non-None parameters (adjust based on your needs):
        if company_id is not None:
            query = query.filter(BaseData.company_id == company_id)
        if subject_id is not None:
            query = query.filter(BaseData.subject_id == subject_id)  # Exact match for subject_id (can be adjusted)
        if lexic_id is not None:
            query = query.filter(BaseData.lexic_id == lexic_id)  # Exact match for subject_id (can be adjusted)
        if legal_document_id is not None:
            query = query.filter(BaseData.legal_document_id == legal_document_id)  # Exact match  (can be adjusted)
        if year_id is not None:
            query = query.filter(BaseData.fi0 == year_id)
        if interval_ord is not None:
            query = query.filter(BaseData.interval_ord == interval_ord)
        if interval_id is not None:
            query = query.filter(BaseData.interval_id == interval_id)
        if area_id is not None:
            query = query.filter(BaseData.area_id == area_id)
        if subarea_id is not None:
            query = query.filter(BaseData.subarea_id == subarea_id)
        existing_data = query.first()

        # If the data already exists in BaseData, return False
        if existing_data:
            return True, "Data for this period already exists."
        else:
            return True, "Data for this period was not found."



# Define the function to get the current interval for each interval_id
def get_current_intervals(session):
    current_date = datetime.now()
    current_year = current_date.year
    intervals = session.query(Interval).all()
    current_intervals = []
    for interval in intervals:
        if interval.id == 1:  # year
            current_interval_ord = int(current_year / current_year)
        elif interval.id == 2:  # semester
            current_interval_ord = (current_date.month + 5) // 6
        elif interval.id == 3:  # quadrimester
            current_interval_ord = (current_date.month + 3) // 4
        elif interval.id == 4:  # quarter
            current_interval_ord = (current_date.month + 2) // 3
        elif interval.id == 5:  # month
            current_interval_ord = current_date.month
        elif interval.id == 6:  # fortnight
            current_interval_ord = int(current_date.strftime('%W')) // 2
        elif interval.id == 7:  # week
            current_interval_ord = int(current_date.strftime('%W'))
        current_intervals.append((interval.id, current_year, current_interval_ord))
    return current_intervals


def get_record_counts(session):
    current_intervals = get_current_intervals(session)

    current_interval_ids = [interval[0] for interval in current_intervals]
    past_interval_ids = [interval[0] for interval in current_intervals if interval[0] != 1]
    current_interval_ords = [interval[1] for interval in current_intervals]
    current_years = [interval[2] for interval in current_intervals]

    company_records = session.query(BaseData.company_id, BaseData.interval_id, BaseData.interval_ord, BaseData.fi0, func.count(BaseData.id)).\
        filter(BaseData.interval_id.in_(current_interval_ids)).\
        filter(BaseData.interval_ord.in_(current_interval_ords)).\
        filter(BaseData.fi0.in_(current_years)).\
        group_by(BaseData.company_id, BaseData.interval_id, BaseData.interval_ord, BaseData.fi0).all()

    past_records = session.query(BaseData.company_id, BaseData.interval_id, BaseData.interval_ord, BaseData.fi0, func.count(BaseData.id)).\
        filter(BaseData.interval_id.in_(past_interval_ids)).\
        filter(BaseData.interval_ord.in_(current_interval_ords)).\
        filter(BaseData.fi0.in_(current_years)).\
        group_by(BaseData.company_id, BaseData.interval_id, BaseData.interval_ord, BaseData.fi0).all()

    return company_records, past_records


from datetime import datetime

import pandas as pd
from datetime import datetime


def get_time_qualifier(interval_id, interval_ord, year):
    current_date = datetime.now()
    current_year = current_date.year

    if year < current_year:
        result = "past"
    elif year > current_year:
        result = "future"
    else:  # Same year as current year
        if interval_id == 1:  # year
            result = "current"
        elif interval_id == 2:  # semester
            current_interval_ord = (current_date.month + 5) // 6
        elif interval_id == 3:  # quadrimester
            current_interval_ord = (current_date.month + 3) // 4
        elif interval_id == 4:  # quarter
            current_interval_ord = (current_date.month + 2) // 3
        elif interval_id == 5:  # month
            current_interval_ord = current_date.month
        elif interval_id == 6:  # fortnight
            current_interval_ord = int(current_date.strftime('%W')) // 2
        elif interval_id == 7:  # week
            current_interval_ord = int(current_date.strftime('%W'))

        if interval_ord < current_interval_ord:
            result = "past"
        elif interval_ord > current_interval_ord:
            result = "future"
        else:  # Same interval order as current interval order
            result = "current"

    return result


def get_time_qualifier222(interval_id, interval_ord, year):
    current_date = datetime.now()
    current_year = current_date.year

    if year < current_year:
        return "past"
    elif year > current_year:
        return "future"
    else:  # Same year as current year
        if interval_id == 1:  # year
            return "current"
        elif interval_id == 2:  # semester
            current_interval_ord = (current_date.month + 5) // 6
        elif interval_id == 3:  # quadrimester
            current_interval_ord = (current_date.month + 3) // 4
        elif interval_id == 4:  # quarter
            current_interval_ord = (current_date.month + 2) // 3
        elif interval_id == 5:  # month
            current_interval_ord = current_date.month
        elif interval_id == 6:  # fortnight
            current_interval_ord = int(current_date.strftime('%W')) // 2
        elif interval_id == 7:  # week
            current_interval_ord = int(current_date.strftime('%W'))

        if interval_ord < current_interval_ord:
            return "past"
        elif interval_ord > current_interval_ord:
            return "future"
        else:  # Same interval order as current interval order
            return "current"


def get_subarea_description(subarea_id):
    # Query the database to get the subarea description
    subarea = Subarea.query.filter_by(id=subarea_id).first()
    if subarea:
        return subarea.description
    else:
        return "Unknown"


def get_session_workflows(session, current_user):

    serialized_workflows = []

    if current_user and current_user.is_authenticated and current_user.is_admin:
        # Inside your view function or wherever you're retrieving workflows
        workflows = session.query(Workflow).all()
        # Convert Workflow objects to dictionaries
        serialized_workflows = [workflow.to_dict() for workflow in workflows]
        # Pass the serialized workflows to your template or serialize as JSON
    else:
        workflows = Workflow.query.filter_by(restricted=0).all()  # Return restricted workflows for non-admin users
        # Convert Workflow objects to dictionaries
        serialized_workflows = [workflow.to_dict() for workflow in workflows]

    return serialized_workflows



def get_pd_report_from_base_data(session):
    # Get the records without the time qualifier
    query = session.query(
        BaseData.company_id,
        Company.name.label('company_name'),  # Add the company name to the query
        BaseData.area_id,
        BaseData.subarea_id,
        BaseData.interval_id,
        BaseData.interval_ord,
        BaseData.fi0,
        func.count().label('record_count')
    ).join(
        Company, BaseData.company_id == Company.id  # Join with Company model to get company name
    ).group_by(
        BaseData.company_id,
        Company.name,
        BaseData.area_id,
        BaseData.subarea_id,
        BaseData.interval_id,
        BaseData.interval_ord,
        BaseData.fi0
    )

    # Fetch query results into DataFrame
    compiled_query = query.statement.compile(session.bind)

    df = pd.read_sql(str(compiled_query), session.bind)

    # Apply the same logic as the loop for assigning time qualifier to each record
    df['time_qualifier'] = df.apply(lambda row: get_time_qualifier(row['interval_id'], row['interval_ord'], row['fi0']), axis=1)
    # Print the updated DataFrame

    # (debugging an error): Assuming df is your DataFrame
    #df['time_qualifier'] = df.apply(lambda row: get_time_qualifier(row['interval_id'], row['interval_ord'], row['fi0']),
    #                                axis=1)
    # Sort the DataFrame by time_qualifier, area_id, subarea_id, interval_ord, and year
    sorted_df = df.sort_values(by=['time_qualifier', 'area_id', 'subarea_id', 'interval_ord', 'fi0'], ascending=[False, True, True, True, True])

    # To drop a single column without returning a new df
    sorted_df.drop('interval_id', axis=1, inplace=True)

    # Convert DataFrame to list of dictionaries
    sorted_records = sorted_df.to_dict(orient='records')

    return sorted_records


from sqlalchemy import func
def get_pd_report_from_base_data_wtq(engine):
    try:
        # Assuming BaseData and Company are your SQLAlchemy models
        connection = engine.connect()

        query = db.session.query(
            BaseData.company_id,
            Company.name.label('company_name'),  # Add the company name to the query
            BaseData.area_id,
            BaseData.subarea_id,
            BaseData.interval_id,
            BaseData.interval_ord,
            BaseData.fi0,
            func.count().label('record_count')
        ).join(
            Company, BaseData.company_id == Company.id  # Join with Company model to get company name
        ).group_by(
            BaseData.company_id,
            Company.name,
            BaseData.area_id,
            BaseData.subarea_id,
            BaseData.interval_id,
            BaseData.interval_ord,
            BaseData.fi0
        )

        # Fetch query results into DataFrame
        df = pd.read_sql(query.statement, connection)  # Use query.statement

        # Debugging: Print the DataFrame structure

        # Check if the DataFrame is empty
        if df.empty:
            print("No data returned.")
            return []

        # Apply the logic for assigning time qualifier to each record
        df['time_qualifier'] = df.apply(
            lambda row: get_time_qualifier(row['interval_id'], row['interval_ord'], row['fi0']), axis=1)

        # Sort the DataFrame by time_qualifier, area_id, subarea_id, interval_ord, and year
        sorted_df = df.sort_values(by=['fi0', 'interval_ord', 'area_id', 'subarea_id'],
                                   ascending=[False, True, True, True])

        # To drop a single column without returning a new df
        sorted_df.drop('interval_id', axis=1, inplace=True)

        # Convert DataFrame to list of dictionaries
        sorted_records = sorted_df.to_dict(orient='records')

        return sorted_records

    except Exception as e:
        print(f"Error in get_pd_report_from_base_data_wtq: {e}")
        raise

    finally:
        connection.close()


def generate_html_cards(sorted_values, all_companies):
    html_code = ""

    # Group items by company_name and then by time_qualifier
    grouped_items = {}
    for item in sorted_values:
        company_name = item['company_name']
        time_qualifier = item['time_qualifier']
        if company_name not in grouped_items:
            grouped_items[company_name] = {}
        if time_qualifier not in grouped_items[company_name]:
            grouped_items[company_name][time_qualifier] = []
        grouped_items[company_name][time_qualifier].append(item)

    # Iterate over all companies
    for company in all_companies:
        company_name = company.name

        html_code += f"<div class='card'>"
        html_code += f"<div class='card-header'>Company: {company_name}</div>"
        html_code += "<div class='card-body'>"

        # If there are records for the company
        if company_name in grouped_items:
            time_qualifiers = grouped_items[company_name]
            # Iterate over time_qualifiers
            for time_qualifier, items in time_qualifiers.items():
                html_code += "<div class='nested-card'>"
                html_code += f"<div class='card-header'>{time_qualifier.capitalize()} Record</div>"
                html_code += "<div class='card-body'>"

                # Start table for record details with table styling
                html_code += "<table class='record-table'>"
                html_code += "<tr><th>Area di controllo; sub-area</th><th>Intervallo/Anno</th><th>Record</th></tr>"

                # Add rows for record details
                for item in items:
                    area_id = item['area_id']
                    subarea_id = item['subarea_id']
                    fi0 = item['fi0']
                    interval_ord = item['interval_ord']
                    record_count = item['record_count']
                    html_code += f"<tr><td>{area_id}; {subarea_id}</td><td>{interval_ord}/{fi0}</td><td>{record_count}</td></tr>"

                # End table
                html_code += "</table>"

                html_code += "</div></div>"
        else:
            # No data found for this company
            html_code += "<p>No data</p>"

        html_code += "</div></div>"

    return html_code


def get_areas_with_subareas(session):
    areas_with_subareas = []

    # Query all distinct areas
    distinct_areas = session.query(Area).all()

    for area in distinct_areas:
        # Query subareas for the current area using the relationship table
        subareas = session.query(Subarea).join(AreaSubareas).filter(AreaSubareas.area_id == area.id).all()
        areas_with_subareas.append((area, subareas))

    return areas_with_subareas


def generate_html_cards_progression_with_progress_bars111(sorted_values, current_time_qualifier, session, company_id=None):
    html_code = ""

    areas_with_subareas = get_areas_with_subareas(session)

    # If current_time_qualifier is None, set it to an empty dictionary
    current_time_qualifier = current_time_qualifier or {}

    # If company_id is None, get all companies
    companies = session.query(Company).all() if company_id is None else [session.query(Company).get(company_id)]

    # Loop through each company
    for company in companies:
        # Get company name and ID
        company_name = company.name
        company_id = company.id

        # Initialize counter for cards in the row
        cards_in_row = 0

        # Start the row for the current company
        html_code += "<div class='row'>"

        # Loop through each area with its subareas
        for area, subareas in areas_with_subareas:
            # Filter sorted_values to include only items for the current area, company, and time qualifier
            filtered_values_area = [item for item in sorted_values if
                                    item['area_id'] == area.id and
                                    item['time_qualifier'] == current_time_qualifier and
                                    item['company_id'] == company_id]

            # Initialize dictionary to store record counts for subareas
            subarea_record_counts = {subarea.id: 0 for subarea in subareas}

            # Update record counts for subareas with non-zero counts
            last_fi0 = None
            last_interval_ord = None

            for item in filtered_values_area:
                subarea_id = item.get('subarea_id')
                if subarea_id is not None and subarea_id in subarea_record_counts:
                    subarea_record_counts[subarea_id] += 1
                else:
                    print(f"Subarea ID {subarea_id} not found or invalid.")

                # Store the last fi0 and interval_ord before the loop ends
                last_fi0 = item.get('fi0', '')
                last_interval_ord = item.get('interval_ord', '')

            # Start card body using the stored last values
            html_code += f"<div class='col-md-4'>"  # Bootstrap column to contain the card
            html_code += f"<div class='card' style='width: 22rem;'>"
            # print('area id hyperlink and other values 1)', area.id, '2)', company_name, '3)', area.name, '4)', last_fi0, '5)', last_interval_ord)
            # print(f'Route is open_admin_app_{area.id}')
            html_code += f"<div class='card-header'><h5 class='card-title' style='font-size: 1rem;'><a href='/open_admin_app_{area.id}'>\
            {company_name} - {area.name}</a> - {last_fi0} / {last_interval_ord}</h5></div>"

            html_code += "<div class='card-body'>"
            html_code += "<table class='table table-sm'>"
            html_code += "<thead><tr><th style='font-size: 0.8rem;'>Subarea</th><th style='font-size: 0.8rem;'>Records</th></tr></thead>"
            html_code += "<tbody>"

            # Display subarea details
            for subarea in subareas:
                subarea_description = get_subarea_description(subarea.id)
                record_count = subarea_record_counts.get(subarea.id, 0)
                # Add different background color for rows with zero records
                row_style = ""
                if record_count == 0:
                    row_style = "background-color: #ffccaa;"  # Light orange
                elif record_count > 2:
                    row_style = "background-color: #add8e6;"  # trq?
                html_code += f"<tr style='{row_style}'><td style='font-size: 0.8rem;'>\
                {subarea_description}</td><td style='font-size: 0.8rem; text-align: center;'>{record_count}</td></tr>"
            # End table body and card body
            html_code += "</tbody>"
            html_code += "</table>"
            html_code += "</div>"

            # Calculate progress based on the total number of subareas
            total_subareas_with_records = sum(1 for count in subarea_record_counts.values() if count > 0)
            divisor = len(subareas) if len(subareas) > 0 else 1
            percentage = (total_subareas_with_records / divisor) * 100
            percentage = min(percentage, 100)

            # Create a progress bar based on the calculated percentage
            progress_bar = f"<a href='/open_admin_app_{area.id}'>\
               <div class='progress' style='font-size: 10px;'>" \
               f"<div class='progress-bar' role='progressbar' style='width: {percentage}%;\
               ' aria-valuenow='{percentage}' aria-valuemin='0' aria-valuemax='100'>\
               {percentage:.2f}%</div></div></a>"

            # Card footer with the progress bar
            html_code += f"<div class='card-footer'>{progress_bar}</div>"

            # Close the card
            html_code += "</div>"
            html_code += "</div>"  # Close Bootstrap column

            # Increment the counter for cards in the row
            cards_in_row += 1

            # If three cards are already in the row, close the row and start a new one
            if cards_in_row == 3:
                html_code += "</div>"  # Close the row
                html_code += "<div class='row'>"  # Start a new row
                cards_in_row = 0

        # Close the row for the current company
        html_code += "</div>"

    return html_code



def generate_html_cards_progression_with_progress_bars_in_short(sorted_values, current_time_qualifier, session,
                                                          company_id=None):
    html_code = ""

    areas_with_subareas = get_areas_with_subareas(session)

    # If current_time_qualifier is None, set it to an empty dictionary
    current_time_qualifier = current_time_qualifier or {}

    # If company_id is None, get all companies
    companies = session.query(Company).all() if company_id is None else [session.query(Company).get(company_id)]

    # Loop through each company
    for company in companies:
        # Get company name and ID
        company_name = company.name
        company_id = company.id

        # Initialize counter for cards in the row
        cards_in_row = 0

        # Start the row for the current company
        html_code += "<div class='row'>"

        # Loop through each area with its subareas
        for area, subareas in areas_with_subareas:
            # Filter sorted_values to include only items for the current area, company, and time qualifier
            filtered_values_area = [item for item in sorted_values if
                                    item['area_id'] == area.id and
                                    item['time_qualifier'] == current_time_qualifier and
                                    item['company_id'] == company_id]

            # Placeholder for the removed card body
            # html_code += "<div class='col-md-4'>"  # Bootstrap column to contain the card
            # html_code += f"<div class='card' style='width: 22rem;'>"
            # html_code += f"<div class='card-header'><h5 class='card-title' style='font-size: 1rem;'>{company_name} - {area.name}</h5></div>"  # Card header with company name and area name

            # Placeholder for the removed card body
            # html_code += "<div class='card-body'>"
            # html_code += "<table class='table table-sm'>"
            # html_code += "<thead><tr><th style='font-size: 0.8rem;'>Subarea</th><th style='font-size: 0.8rem;'>Records</th></tr></thead>"
            # html_code += "<tbody>"

            # Placeholder for the removed card body
            # html_code += "</tbody>"
            # html_code += "</table>" # synthetic format
            # html_code += "</div>"

            # Calculate progress based on the total number of subareas
            total_subareas = len(subareas)
            total_records = len(filtered_values_area)  # Total records count for all subareas
            progress_percentage = (total_records / total_subareas) * 100 if total_subareas != 0 else 0

            # Generate progress bar

            html_code += f"<div class='col-md-4'>"  # Bootstrap column to contain the card
            html_code += f"<div class='card' style='width: 22rem;'>"
            html_code += f"<div class='card-header' style='background-color: #00008B; color: #ffffff;'><h5 class='card-title' style='font-size: 1rem;'>\
            {company_name} - {area.name}</h5></div>"  # Card header with company name and area name

            #html_code += f"<div class='col-md-4'>"  # Bootstrap column to contain the card
            #html_code += f"<div class='card' style='width: 22rem;'>"
            #html_code += f"<div class='card-header'><h5 class='card-title' style='font-size: 1rem;'>{company_name} - {area.name}</h5></div>"  # Card header with company name and area name

            html_code += f"<div class='card-footer'><div class='progress' style='font-size: 10px;'><div class='progress-bar' role='progressbar' style='width: {progress_percentage}%;' aria-valuenow='{progress_percentage}' aria-valuemin='0' aria-valuemax='100'>{progress_percentage:.2f}%</div></div></div>"
            html_code += "</div>"
            html_code += "</div>"  # Close Bootstrap column

            # Increment the counter for cards in the row
            cards_in_row += 1

            # If three cards are already in the row, close the row and start a new one
            if cards_in_row == 3:
                html_code += "</div>"  # Close the row
                html_code += "<div class='row'>"  # Start a new row
                cards_in_row = 0

        # Close the row for the current company
        html_code += "</div>"
    return html_code

'''
Functions generate_...
-are used to generate the reports under System Setup
-all are linked to routes starting with /dashboard_setup etc
'''

def generate_company_user_report_data(session):
    report_data = []

    # Fetch company_users relationship data
    company_users = session.query(CompanyUsers).all()

    # Iterate over company_users
    for cu in company_users:
        user = cu.user
        company = cu.company

        if user and company:  # Check if both user and company exist
            company_name = company.name  # Get company name from Company model
            user_first_name = user.first_name  # Get user first name from User model
            user_last_name = user.last_name  # Get user last name from User model
            # Append user and company names to the report data
            report_data.append([company_name, user_first_name, user_last_name])

        elif user:  # If user exists but not assigned to a company
            user_first_name = user.first_name  # Get user first name from User model
            user_last_name = user.last_name  # Get user last name from User model

            # Append user name and placeholder for company name to the report data
            report_data.append(["Not assigned to a company", user_first_name, user_last_name])
        elif company:  # If company exists but no user assigned
            company_name = company.name  # Get company name from Company model
            # Append placeholder for user name and company name to the report data
            report_data.append([company_name, "No user assigned", ""])

        else:  # If neither user nor company exists
            # Append placeholders for user and company names to the report data
            report_data.append(["No company assigned", "No user assigned", ""])

    # Sort the report data by company name (third element in each row)
    report_data.sort(key=lambda x: x[0])

    return report_data


def generate_user_role_report_data(session):
    report_data = []

    # Query users and roles directly
    users_and_roles = session.query(Users, Role).select_from(Users).join(UserRoles).join(Role).all()

    # Iterate over user-role pairs
    for user, role in users_and_roles:
        user_first_name = user.first_name if user else "No user assigned"
        user_last_name = user.last_name if user else ""
        role_name = role.name if role else "No role created"

        report_data.append([user_first_name, user_last_name, role_name])

    # Sort the report data by company name (third element in each row)
    report_data.sort(key=lambda x: x[1])

    return report_data


def generate_company_questionnaire_report_data(session):
    report_data = []

    # Query users and roles directly
    companies_and_questionnaires = session.query(Questionnaire, Company).select_from(Questionnaire).join(QuestionnaireCompanies).join(Company).all()

    # Iterate over user-role pairs
    for questionnaire, company in companies_and_questionnaires:
        company_name = company.name if company else "No company assigned"
        questionnaire_name = questionnaire.name if questionnaire else ""
        questionnaire_id = questionnaire.questionnaire_id if questionnaire else "No questionnaire created"

        report_data.append([company_name, questionnaire_name, questionnaire_id])

    # Sort the report data by company name (third element in each row)
    report_data.sort(key=lambda x: x[2])

    return report_data


def generate_area_subarea_report_data(session):
    report_data = []

    # Query users and roles directly
    areas_and_subareas = session.query(Area, Subarea).select_from(Area).join(AreaSubareas).join(Subarea).all()

    # Iterate over user-role pairs
    for area, subarea in areas_and_subareas:
        area_name = area.description if area else "No area assigned"
        subarea_name = subarea.description if subarea else ""
        subarea_type = subarea.data_type if subarea else "No subarea created"

        report_data.append([area_name, subarea_name, subarea_type])

    # Sort the report data by company name (third element in each row)
    report_data.sort(key=lambda x: x[0])

    return report_data


def generate_questionnaire_question_report_data(session):
    report_data = []

    # Fetch company_questionnaires relationship data
    questionnaire_questions = session.query(QuestionnaireQuestions).all()

    # Iterate over questionnaire_questionnaires
    for cu in questionnaire_questions:
        questionnaire = cu.questionnaire
        question = cu.question

        if questionnaire and question:  # Check if both questionnaire and role exist
            question_name = question.text  # Get questionnaire name from role model
            questionnaire_id = questionnaire.id  # Get questionnaire first name from questionnaire model
            questionnaire_name = questionnaire.name  # Get user last name from User model
            # Append user and company names to the report data
            report_data.append([questionnaire_id, questionnaire_name, question_name])

        elif questionnaire:  # If user exists but not assigned to a role
            questionnaire_id = questionnaire.id  # Get user first name from User model
            questionnaire_name = questionnaire.name  # Get user last name from User model
            # Append user name and placeholder for company name to the report data
            report_data.append([ questionnaire_id, questionnaire_name, "No questions assigned"])

        elif question:  # If company exists but no user assigned
            question_name = question.text  # Get role name from Role model
            # Append placeholder for user name and company name to the report data
            report_data.append(["No questionnaire assigned", "", question_name])

        else:  # If neither user nor company exists
            # Append placeholders for user and company names to the report data
            report_data.append(["No questionnaire assigned", "", "No question created"])

    # Sort the report data by company name (third element in each row)
    report_data.sort(key=lambda x: x[0])

    return report_data

'''
workflows and their steps
'''
def generate_workflow_step_report_data(session):
    report_data = []

    # Fetch company_questionnaires relationship data
    workflow_steps = session.query(WorkflowSteps).all()

    # Iterate over workflow_workflows
    for cu in workflow_steps:
        workflow = cu.workflow
        step = cu.step

        if workflow and step:  # Check if both workflow and step exist

            step_id = step.id  # Get workflow name from step model
            step_name = step.name  # Get workflow name from step model
            workflow_id = workflow.id  # Get workflow first name from workflow model
            workflow_name = workflow.name  # Get user last name from User model
            # Append user and company names to the report data
            report_data.append([workflow_id, workflow_name, step_id, step_name])

        elif workflow:  # If user exists but not assigned to a step
            workflow_id = workflow.id  # Get user first name from User model
            workflow_name = workflow.name  # Get user last name from User model
            # Append user name and placeholder for company name to the report data
            report_data.append([workflow_id, workflow_name, "", "No steps assigned"])

        elif step:  # If company exists but no user assigned
            step_id = step.id  # Get workflow name from step model
            step_name = step.name  # Get step name from step model
            # Append placeholder for user name and company name to the report data
            report_data.append(["No workflow assigned", "", step_id, step_name])

        else:  # If neither user nor company exists
            # Append placeholders for user and company names to the report data
            report_data.append(["No workflow assigned", "", "No step created"])

    # Sort the report data by company name (third element in each row)
    report_data.sort(key=lambda x: x[0])

    return report_data


'''
this is the function listing the documents assigned to workflows
'''
def generate_workflow_document_report_data(session):
    report_data = []

    # Query workflows and base data
    workflows_and_base_data = session.query(Workflow, BaseData).select_from(Workflow).join(WorkflowBaseData).join(BaseData).all()

    # Iterate over workflow-base data pairs
    for workflow, base_data in workflows_and_base_data:
        workflow_name = workflow.name if workflow else "No workflow assigned"
        base_data_name = base_data.file_path if base_data else None  # Set to None if base_data is None
        report_data.append([base_data_name, workflow_name])

    # Sort the report data by base data name (first element in each row)
    report_data.sort(key=lambda x: x[0] if x[0] is not None else '')  # Use empty string as default if base_data_name is None

    return report_data



'''
FUNCTION to determine STEP(s) each DOCUMENT belongs to currently
'''
def generate_document_step_report_data(session):
    report_data = []

    # Fetch all BaseData records
    base_data_records = session.query(BaseData).all()

    # Iterate over BaseData records
    for base_data in base_data_records:
        document_name = base_data.file_path  # Use file_path instead of name

        if document_name and document_name != None:
            document_id = base_data.id

            company_query = session.query(Company).filter(Company.id == base_data.company_id).first()
            if company_query:
                company_name = company_query.name
            else:
                company_name = "Unknown"

            area_query = session.query(Area).filter(Area.id == base_data.area_id).first()
            if area_query:
                area_name = area_query.name
            else:
                area_name = "Unknown"

            # Fetch associated Subarea for the current BaseData
            subarea_query = session.query(Subarea).filter(Subarea.id == base_data.subarea_id).first()
            if subarea_query:
                subarea_name = subarea_query.name
            else:
                subarea_name = "Unknown"

            # Fetch associated StepBaseData for the current BaseData
            step_base_data_records = session.query(StepBaseData).filter_by(base_data_id=base_data.id).all()

            for step_base_data in step_base_data_records:
                base_data_id = base_data.id
                step = step_base_data.step
                step_start = step_base_data.start_date if step_base_data else ""
                step_deadline = step_base_data.deadline_date if step_base_data else ""
                step_end = step_base_data.end_date if step_base_data else ""
                auto_move = step_base_data.auto_move if step_base_data else False

                workflow_id = None
                workflow_base_data_query = session.query(WorkflowBaseData).filter(
                    WorkflowBaseData.id == step_base_data.base_data_id).first()
                if workflow_base_data_query:
                    workflow_id = workflow_base_data_query.workflow_id

                step_id = step.id if step else ""
                step_name = step.name if step else ""

                # Append data to report
                report_data.append([document_id, document_name, area_name, subarea_name, company_name, workflow_id, step_id, step_name, step_start, step_deadline, step_end, auto_move])

            if not step_base_data_records:  # If no StepBaseData records found for the current BaseData
                # Append data to report with placeholders for step and workflow information
                report_data.append([document_id, document_name, area_name, subarea_name, company_name, "", "", "No step created", "", "", "", False])

    return report_data



'''
function(s) to generate generic templates for cards
'''
def generate_html_cards_with_year_period_interval(sorted_values, current_time_qualifier, session, company_id):
    html_code = ""

    areas_with_subareas = get_areas_with_subareas(session)

    # Get company name from company_id
    company_name = session.query(Company).filter(Company.id == company_id).first().name

    # Initialize counter for cards in the row
    cards_in_row = 0

    # Start the row
    html_code += "<div class='row'>"

    # Loop through each area with its subareas
    for area, subareas in areas_with_subareas:

        # Group items by area_id, year_id, and interval_ord for the current area
        grouped_items = {}
        for item in sorted_values:
            key = (item['area_id'], item['fi0'], item['interval_ord'])
            if key not in grouped_items:
                grouped_items[key] = []
            grouped_items[key].append(item)

        # Filter items for the current area, year, and interval
        for key, items_for_area_year_interval in grouped_items.items():
            area_id, year_id, interval_ord = key

            if area_id == area.id:
                # Start building the HTML code for the card
                html_code += f"<div class='col-md-4'>"  # Bootstrap column to contain the card
                html_code += f"<div class='card' style='width: 22rem;'>"
                html_code += f"<div class='card-header'><h5 class='card-title'><a href='/open_admin_app_{area.id}'>\
                {company_name} - {area.name}</a> - {year_id}/ {interval_ord}</h5></div>"
                # Card header with company name, area name, year, and interval details
                html_code += "<div class='card-body'>"
                html_code += "<table class='table table-sm'>"
                html_code += "<thead><tr><th>Subarea</th><th>Records</th></tr></thead>"
                html_code += "<tbody>"

                # Filter items for the current area, year, and interval
                filtered_items = [item for item in items_for_area_year_interval if
                                  item['company_id'] == company_id and
                                  item['fi0'] == year_id and
                                  item['interval_ord'] == interval_ord]

                # Initialize dictionary to store record counts for subareas
                subarea_record_counts = {subarea.id: 0 for subarea in subareas}

                # Update record counts for subareas with non-zero counts
                for item in filtered_items:
                    subarea_id = item.get('subarea_id')  # Get subarea_id from item
                    if subarea_id is not None:  # Check if subarea_id exists
                        subarea_record_counts[subarea_id] += 1

                # Display subarea details
                for subarea in subareas:
                    subarea_description = get_subarea_description(subarea.id)
                    record_count = subarea_record_counts.get(subarea.id, 0)
                    html_code += f"<tr><td>{subarea_description}</td><td>{record_count}</td></tr>"

                # End table body and card body
                html_code += "</tbody>"
                html_code += "</table>"
                html_code += "</div>"

                # Calculate progress based on the total number of subareas
                total_subareas_with_records = sum(1 for count in subarea_record_counts.values() if count > 0)
                divisor = max(len(subareas), 1)  # Ensure divisor is at least 1 to avoid division by zero
                percentage = (total_subareas_with_records / divisor) * 100
                percentage = min(percentage, 100)

                # Create a progress bar based on the calculated percentage
                progress_bar = f"<a href='/open_admin_app_{area_id}'><div class='progress' style='font-size: 10px;'>" \
                               f"<div class='progress-bar progress-bar-sm' style='width: {percentage}%; font-size: 10px;'>" \
                               f"{percentage:.2f}%</div></div></a>"

                # Card footer with the progress bar
                html_code += f"<div class='card-footer'>{progress_bar}</div>"

                # Close the card
                html_code += "</div>"
                html_code += "</div>"  # Close Bootstrap column

                # Increment the counter for cards in the row
                cards_in_row += 1

                # If three cards are already in the row, close the row and start a new one
                if cards_in_row == 3:
                    html_code += "</div>"  # Close the row
                    html_code += "<div class='row'>"  # Start a new row
                    cards_in_row = 0

    # Close the last row if it's not already closed
    if cards_in_row != 0:
        html_code += "</div>"

    return html_code


def generate_company_cards(filtered_values):
    html_code = ""

    # Group items by area_id
    grouped_items = {}
    for item in filtered_values:
        area_id = item['area_id']
        year_id = item['fi0']
        interval_ord = item['interval_ord']

        key = (area_id, year_id, interval_ord)
        if key not in grouped_items:
            grouped_items[key] = []
        grouped_items[key].append(item)

    # Iterate over distinct area_ids
    for (area_id, year_id, interval_ord), items in grouped_items.items():
        html_code += f"<div class='card'>"
        company_name = items[0]['company_name']  # Get company name from the first item
        html_code += f"<a href='/control_area_{area_id}'><div class='card-header'>Area ID: {area_id} - Company: {company_name}; \
        Interval: {interval_ord}/{year_id}</div></a>"  # Add anchor tag and display company_name

        html_code += "<div class='card-body'>"

        # Start table for record details with table styling
        html_code += "<table class='record-table'>"
        html_code += "<tr><th>Subarea</th><th>Records</th></tr>"

        # Get distinct subarea_ids for the current area_id
        distinct_subarea_ids = set(item['subarea_id'] for item in items)
        subarea_record_counts = {item['subarea_id']: item['record_count'] for item in items}

        # Display subarea details
        for subarea_id in distinct_subarea_ids:
            subarea_description = get_subarea_description(subarea_id)
            record_count = subarea_record_counts.get(subarea_id, 0)
            html_code += f"<tr><td>{subarea_description}</td><td>{record_count}</td></tr>"

        # End table
        html_code += "</table>"
        html_code += "</div>"  # End card body

        # Calculate progress based on the total number of subareas and display a single progress bar
        total_subareas = len(distinct_subarea_ids)
        divisor = 7 if area_id == 1 else 8
        percentage = (total_subareas / divisor) * 100
        percentage = min(percentage, 100)

        # Create a progress bar based on the calculated percentage
        progress_bar = f"<div class='progress'>" \
                       f"<div class='progress-bar' style='width: {percentage}%;'>" \
                       f"{percentage:.2f}%</div></div>"

        # Card footer with the progress bar
        html_code += f"<div class='card-footer'>{progress_bar}</div>"

        html_code += "</div>"  # End card

    return html_code


def generate_area_cards(filtered_values):
    html_code = ""

    # Group items by area_id
    grouped_items = {}
    for item in filtered_values:
        area_id = item['area_id']
        year_id = item['fi0']
        interval_ord = item['interval_ord']

        key = (area_id, year_id, interval_ord)
        if key not in grouped_items:
            grouped_items[key] = []
        grouped_items[key].append(item)

    # Iterate over distinct area_ids
    for (area_id, year_id, interval_ord), items in grouped_items.items():
        html_code += f"<div class='card'>"
        company_name = items[0]['company_name']  # Get company name from the first item
        html_code += f"<a href='/control_area_{area_id}'><div class='card-header'>Area ID: {area_id} - Company: {company_name}; \
        Interval: {interval_ord}/{year_id}</div></a>"  # Add anchor tag and display company_name

        html_code += "<div class='card-body'>"

        # Start table for record details with table styling
        html_code += "<table class='record-table'>"
        html_code += "<tr><th>Subarea</th><th>Records</th></tr>"

        # Get distinct subarea_ids for the current area_id
        distinct_subarea_ids = set(item['subarea_id'] for item in items)
        subarea_record_counts = {item['subarea_id']: item['record_count'] for item in items}

        # Display subarea details
        for subarea_id in distinct_subarea_ids:
            subarea_description = get_subarea_description(subarea_id)
            record_count = subarea_record_counts.get(subarea_id, 0)
            html_code += f"<tr><td>{subarea_description}</td><td>{record_count}</td></tr>"

        # End table
        html_code += "</table>"

        html_code += "</div>"  # End card body

        # Calculate progress based on the total number of subareas and display a single progress bar
        total_subareas = len(distinct_subarea_ids)
        divisor = 7 if area_id == 1 else 8
        percentage = (total_subareas / divisor) * 100
        percentage = min(percentage, 100)

        # Create a progress bar based on the calculated percentage
        progress_bar = f"<div class='progress'>" \
                       f"<div class='progress-bar' style='width: {percentage}%;'>" \
                       f"{percentage:.2f}%</div></div>"

        # Card footer with the progress bar
        html_code += f"<div class='card-footer'>{progress_bar}</div>"

        html_code += "</div>"  # End card

    return html_code



def generate_html_cards_progression_one_company(sorted_values, current_time_qualifier, company_id):
    html_code = ""

    # Get the current user's company ID
    current_company_id = company_id

    # Filter sorted_values to include only items with the current_time_qualifier and current_company_id
    filtered_values = [item for item in sorted_values if item['company_id'] == current_company_id and item.get('time_qualifier') == current_time_qualifier]

    # Get distinct area_id values for the current company_id
    distinct_area_ids = set(item['area_id'] for item in filtered_values)

    # If no records are present for the current user's company and time qualifier
    if not distinct_area_ids:
        html_code += "<p>No records found for your company and time qualifier.</p>"
        return html_code

    # Group items by area_id
    grouped_items = {}
    for item in filtered_values:
        area_id = item['area_id']
        if area_id not in grouped_items:
            grouped_items[area_id] = []
        grouped_items[area_id].append(item)

    # Iterate over distinct area_ids
    for area_id in distinct_area_ids:
        html_code += f"<div class='card'>"
        #html_code += f"<a href='/control_area_{area_id}'><div class='card-header'>Area ID: {area_id}</div></a>"  # Add anchor tag
        html_code += f"<a href='/control_area_{area_id}'><div class='card-header'>Area ID: {area_id} - Company: {filtered_values[0]['company_name']}</div></a>"  # Add anchor tag and display company_name

        html_code += "<div class='card-body'>"

        # If there are records for the area_id
        if area_id in grouped_items:
            items = grouped_items[area_id]

            # Start table for record details with table styling
            html_code += "<table class='record-table'>"
            html_code += "<tr><th>Subarea ID</th><th>Progress:</th></tr>"

            # Get distinct subarea_ids for the current area_id
            distinct_subarea_ids = set(item['subarea_id'] for item in grouped_items[area_id])

            subarea_record_counts = {item['subarea_id']: item['record_count'] for item in grouped_items[area_id]}

            # Iterate over distinct subarea_ids
            for subarea_id in distinct_subarea_ids:
                # Get the record count for the current subarea_id from the dictionary
                record_count = subarea_record_counts.get(subarea_id, 0)


            # Calculate progress based on the number of distinct subarea_ids
            progress_value = len(distinct_subarea_ids)

            divisor = 7 if area_id == 1 else 8
            percentage = (progress_value / divisor) * 100
            percentage = min(percentage, 100)

            # Create a progress bar based on the calculated percentage
            progress_bar = f"<div class='progress'>" \
                           f"<div class='progress-bar' style='width: {percentage}%;'>" \
                           f"{percentage:.2f}%</div></div>"

            # Display distinct subarea_ids and progress bar
            html_code += f"<tr><td>Subarea, records found:{subarea_record_counts}</td><td>{progress_bar}</td></tr>"

            # End table
            html_code += "</table>"
        else:
            # No data found for this area_id
            html_code += "<p>No data</p>"

        html_code += "</div></div>"

    return html_code


def get_record_counts_by_time(session, company_id=None):
    # Get the records without the time qualifier
    query = session.query(
        BaseData.company_id,
        BaseData.area_id,
        BaseData.subarea_id,
        BaseData.interval_id,
        BaseData.interval_ord,
        BaseData.fi0,
        func.count().label('record_count')
    ).group_by(
        BaseData.company_id,
        BaseData.area_id,
        BaseData.subarea_id,
        BaseData.interval_id,
        BaseData.interval_ord,
        BaseData.fi0
    )

    # If company_id is provided, filter the records by company_id
    if company_id is not None:
        query = query.filter(BaseData.company_id == company_id)

    records_without_qualifier = query.all()

    # Create a list to hold records with the time qualifier included
    records_with_qualifier = []

    # Assign the time qualifier to each record
    for record in records_without_qualifier:
        time_qualifier = get_time_qualifier(record.interval_id, record.interval_ord, record.fi0)
        '''record_dict = {
            "company_id": record.company_id,
            "area_id": record.area_id,
            "subarea_id": record.subarea_id,
            "interval_id": record.interval_id,
            "interval_ord": record.interval_ord,
            "year": record.fi0,
            "record_count": record.record_count,
            "time_qualifier": time_qualifier
        }'''
        record_dict = {
            "area_id": record.area_id,
            "subarea_id": record.subarea_id,
            "interval_ord": record.interval_ord,
            "year": record.fi0,
            "record_count": record.record_count,
            "time_qualifier": time_qualifier
        }

        records_with_qualifier.append(record_dict)

    # Sort the records by company_id, area_id, subarea_id, interval_id, interval_ord, and year
    '''sorted_records = sorted(records_with_qualifier, key=lambda x: (
        x["time_qualifier"],  # Sort time_qualifier in descending order
    ), reverse=True) + sorted(records_with_qualifier, key=lambda x: (
        x["company_id"],
        x["area_id"],
        x["subarea_id"],
        x["interval_id"],
        x["interval_ord"],
        x["year"]
    ))'''

    sorted_records = sorted(records_with_qualifier, key=lambda x: (
        x["time_qualifier"],  # Sort time_qualifier in descending order
    ), reverse=True) + sorted(records_with_qualifier, key=lambda x: (
        x["area_id"],
        x["subarea_id"],
        x["interval_ord"],
        x["year"]
    ))
    return sorted_records



def is_questionnaire_editable(questionnaire):
    """
    Check if the questionnaire is editable based on the deadline.

    :param questionnaire: Questionnaire instance
    :return: True if editable, False otherwise
    """
    return db.or_(
        questionnaire.deadline_date.is_(None),
        questionnaire.deadline_date >= datetime.now().date()
    )


def normalize_value(value):
    if value is None:
        return ''
    elif value == '':
        return ''
    else:
        return value


def custom_compare(elem1, elem2):
    return (elem1 == '' or elem1 is None) and (elem2 == '' or elem2.lower() == 'none')

def form_has_changes(rendered_form, initial_data):
    initials = []
    currents = []

    for field_name, initial_value in initial_data.items():
        initials.append(normalize_value(initial_value))

        if field_name in rendered_form:
            current_value = rendered_form[field_name]
            current_value_normalized = normalize_value(current_value)
            currents.append(current_value_normalized)

    # Check if lists are different

    if any(not custom_compare(elem1, elem2) for elem1, elem2 in zip(initials, currents)):
        return True
    else:
        pass

    return False

def get_pd_report_from_base_data_2(session, report_name):
    query_result = session.query(BaseData).all()

    # Convert query result to DataFrame
    df = pd.DataFrame([vars(row) for row in query_result])

    print(df.head())


def get_subarea_name(area_id, subarea_id):
    # Query the association table to fetch the Subarea ID associated with the given area_id and subarea_id
    association_record = AreaSubareas.query.filter_by(area_id=area_id, subarea_id=subarea_id).first()
    if association_record:
        subarea_id = association_record.subarea_id
        # Query the Subarea table to fetch the name based on the obtained subarea_id
        subarea = Subarea.query.get(subarea_id)
        if subarea:
            return subarea.name
    return None

def get_subarea_interval_type(area_id, subarea_id):
    # Query the association table to fetch the Subarea ID associated with the given area_id and subarea_id
    association_record = AreaSubareas.query.filter_by(area_id=area_id, subarea_id=subarea_id).first()
    if association_record:
        interval_id = association_record.interval_id
        if interval_id:
            return interval_id
        else:
            return None

def get_areas() -> list[Area]:
    return Area.query.all()


def get_subareas(area_id):

    # Query subareas based on area_id
    subareas = Subarea.query.join(AreaSubareas).filter(AreaSubareas.area_id == area_id).all()

    # Convert the list of SQLAlchemy objects to a list of Subarea instances
    subareas_list = [subarea for subarea in subareas]

    return subareas_list

def get_if_active(area_id, subarea_id):
    # Query the association table to fetch the Subarea ID associated with the given area_id and subarea_id
    association_record = AreaSubareas.query.filter_by(area_id=area_id, subarea_id=subarea_id).first()
    if association_record:
        subarea_id = association_record.status_id
        if subarea_id:
            if subarea_id == 1:
                return True
            else:
                return False
    return False


from sqlalchemy import func

def remove_duplicates(session, model_class, keys):
    # Find duplicates
    key_columns = [getattr(model_class, key) for key in keys]
    duplicates = session.query(*key_columns, func.count('*').label('count')).group_by(*key_columns).having(func.count('*') > 1).all()

    # For each group of duplicates, keep the one with the lowest id and delete the rest
    for dup in duplicates:
        # This query fetches all but the first (lowest id) record for each set of duplicates
        filter_args = {keys[i]: getattr(dup, keys[i]) for i in range(len(keys))}
        duplicates_to_delete = session.query(model_class).filter_by(**filter_args).order_by(
            model_class.id  # Orders the records by id
        ).offset(1).all()  # Skips the first record

        # Delete the selected duplicates
        for item in duplicates_to_delete:
            session.delete(item)

        # Commit the changes
        session.commit()


def create_notification(session, **kwargs):
    notification = Post(
        created_at=datetime.now(),
        **kwargs
    )
    session.add(notification)
    session.commit()

    '''
    use example
    
    create_notification(
    session,
    company_id=1,
    user_id=1,
    sender="System",
    message_type="noticeboard",
    subject="Important Notice",
    body="This is an important notice for all users.",
    lifespan='persistent'
    )

    '''


from datetime import datetime


def create_audit_log(session, **kwargs):
    """
    Create an audit log entry.

    Args:
        session: SQLAlchemy session object.
        **kwargs: Additional keyword arguments to construct the AuditLog object.
                  Expected keys: 'user_id', 'company_id', 'base_data_id', 'workflow_id', 'step_id', 'action', 'details'.
    """
    audit_log = AuditLog(
        timestamp=datetime.utcnow(),
        **kwargs
    )
    session.add(audit_log)
    session.commit()

    '''
    example
    create_audit_log(
    session,
    user_id=1,
    company_id=2,
    base_data_id=3,
    workflow_id=4,
    step_id=5,
    action='create',
    details='New entry created.'
    )
    '''

