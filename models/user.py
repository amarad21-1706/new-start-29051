import json
from db import db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_security import RoleMixin, UserMixin
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey,
                        LargeBinary, Numeric, func, TIMESTAMP, DATE, Sequence, Boolean)

from wtforms.widgets import DateTimeInput
from wtforms.validators import DataRequired, Regexp, EqualTo, Email, Length

from sqlalchemy import or_, and_, Enum, event

from sqlalchemy.orm import object_session, validates
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from sqlalchemy.ext.mutable import MutableDict
from wtforms.fields import StringField, TextAreaField, DateTimeField, SelectField, BooleanField, SubmitField
from datetime import datetime

from sqlalchemy.exc import IntegrityError
# OR
# from sqlalchemy.dialects.mysql import JSON  # for MySQL
# OR
from sqlalchemy.dialects.sqlite import JSON # for SQLite
# OR
# from sqlalchemy.dialects.oracle import JSON  # for Oracle
# OR
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt


class CheckboxField(BooleanField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = True
        else:
            self.data = False
    def populate_obj(self, obj, name):
        setattr(obj, name, "Yes" if self.data else "No")  # Customize as per your model


# TODO create ContainerCompanies and ContainerRoles?
class Container(db.Model):
    __tablename__ = 'container'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255))
    content_type = db.Column(db.String(50), nullable=False)
    content = db.Column(MutableDict.as_mutable(JSONB))

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255))
    action_type = db.Column(db.String(255), nullable=True)
    action_url = db.Column(db.String(255), nullable=True)
    container_order = db.Column(db.Integer, nullable=True)

    def __init__(self, page, content_type, content, company_id, role_id, area_id, position=None, description=None,
                 action_type=None, action_url=None, image=None, container_order=None):
        self.page = page
        self.position = position
        self.content_type = content_type
        self.content = content
        self.company_id = company_id
        self.role_id = role_id
        self.area_id = area_id
        self.description = description
        self.action_type = action_type
        self.action_url = action_url
        self.image = image
        self.container_order = container_order

    def __repr__(self):
        return f"Container: {self.page} ({self.position}, {self.content_type}, {self.description}, {self.action_type}, {self.action_url})"


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_2fa_secret = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(12), nullable=True)
    first_name = db.Column(db.String(128), nullable=False)
    mid_name = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    company = db.Column(db.String(128), nullable=True)
    address = db.Column(db.String(128), nullable=False)
    address1 = db.Column(db.String(128), nullable=True)
    city = db.Column(db.String(128), nullable=True)
    province = db.Column(db.String(64), nullable=True)
    region = db.Column(db.String(64), nullable=True)
    zip_code = db.Column(db.String(24), nullable=True)
    country = db.Column(db.String(64), nullable=False)
    tax_code = db.Column(db.String(128), nullable=True)
    phone_prefix = db.Column(db.String(15), nullable=False)
    mobile_phone = db.Column(db.String(15), nullable=False)
    work_phone = db.Column(db.String(15), nullable=True)
    street = db.Column(db.String(128), nullable=True)
    subscription_plan = db.Column(db.String(20), default='free')
    subscription_status = db.Column(db.String(20), default='inactive')
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    created_on = db.Column(db.DateTime, nullable=False)
    updated_on = db.Column(db.DateTime, nullable=True, onupdate=db.func.now())
    end_of_registration = db.Column(db.Date)
    cookies_accepted = db.Column(db.Boolean, default=False)
    analytics = db.Column(db.Boolean, default=False)
    marketing = db.Column(db.Boolean, default=False)
    terms_accepted = db.Column(db.Boolean, nullable=False, default=False)
    accepted_terms_date = db.Column(db.DateTime, nullable=True)

    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'),
                            primaryjoin='UserRoles.user_id == Users.id',
                            secondaryjoin='UserRoles.role_id == Role.id')

    user_plans = db.relationship('UserPlans', back_populates='user', uselist=False)
    subscriptions = db.relationship('Subscription', back_populates='user')

    #def get_reset_token(self, expires_sec=1800):
    #    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    #    return s.dumps({'user_id': self.id}).decode('utf-8')

    #user_roles_as_role = relationship('UserRoles', back_populates='users')
    #user_roles = relationship('UserRoles', back_populates='users')
    #roles = relationship('Role', secondary='user_roles_as_role', back_populates='users')


    # Add constructor to set the primary key
    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')
        self.subscription_plan = kwargs.get('subscription_plan', 'free')
        self.subscription_status = kwargs.get('subscription_status', 'inactive')
        self.subscription_start_date = kwargs.get('subscription_start_date')
        self.subscription_end_date = kwargs.get('subscription_end_date')

    def set_password(self, password):
        # Use bcrypt to hash the password
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        # Check if the hash is PBKDF2
        if self.password_hash.startswith("pbkdf2:sha256:"):
            return check_password_hash(self.password_hash, password)

        # Otherwise, assume it's bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def is_active(self):
        # Implement the logic to check if the user is active
        return True  # Modify this based on your requirements

    def get_id(self):
        # Implement the logic to get the user's ID
        return str(self.id)  # Modify this based on your requirements

    def is_authenticated(self):
        return True  # Modify based on your authentication logic

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.get(int(user_id))

    def is_admin(self):
        # Check if the user has an admin role
        return 'admin' in [role.name for role in self.roles]

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def __repr__(self):
        return f"{self.username} {self.last_name}"


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer)
    name = db.Column(String(80), unique=True)
    description = db.Column(String(255))

    def __repr__(self):
        return (f"{self.name} ({self.description})")

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)
    end_of_registration = Column(DateTime, nullable=True)
    #user = relationship('Users', backref='user_roles')
    #role = relationship('Role', backref='user_roles')


class CompanyUsers(db.Model):
    __tablename__ = 'company_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)
    end_of_registration = db.Column(db.DateTime, nullable=True)

    company = relationship('Company', backref='company_users')
    user = relationship('Users', backref='company_users')

    def readable_format(self):
        company_name = self.company.name if self.company else "N/A"
        user_name = self.user.username if self.user else "N/A"
        return f"ID: {self.id}, Company: {company_name}, User: {user_name}"

        #return self
    def __str__(self):
        return self.readable_format()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), unique=True)
    description = db.Column(String)
    address = db.Column(String(255))
    phone_number = db.Column(String(20))
    email = db.Column(String(100))
    website = db.Column(String(100))
    tax_code = db.Column(String(24), nullable=True)
    employees = db.relationship('Employee', backref='company', lazy=True)
    created_on = db.Column(db.DateTime)
    updated_on = db.Column(db.DateTime, default=datetime.utcnow)
    end_of_registration = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return (f"{self.name}")



class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), nullable=False)
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')])
    position = db.Column(String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)


class PossibleAnswer(db.Model):
    __tablename__ = 'possible_answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    text = db.Column(String(255))
    next_question_id = db.Column(db.Integer, db.ForeignKey('question.id'))


class Questionnaire(db.Model):
    __tablename__ = 'questionnaire'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    questionnaire_id = db.Column(db.String(64), unique=True, nullable=False)
    questionnaire_type = db.Column(db.String(24), nullable=True, default='Questionnaire')
    name = db.Column(db.String(128), unique=True, nullable=False)
    interval = db.Column(db.String(12))  # If this represents a numeric interval, consider using Integer
    deadline_date = db.Column(db.DateTime)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)
    headers = db.Column(db.JSON)

    steps_questionnaires_relationship = db.relationship("StepQuestionnaire", back_populates="questionnaire")

    def __init__(self, questionnaire_id: str, questionnaire_type: str, name: str, interval: str, deadline_date: datetime, status_id: int, headers: dict):
        self.questionnaire_id = questionnaire_id
        self.questionnaire_type = questionnaire_type
        self.name = name
        self.interval = interval
        self.deadline_date = deadline_date
        self.status_id = status_id
        self.headers = headers

    def __repr__(self):
        return (f"{self.name}")

    def to_json(self):
        return json.dumps({
            "answer_data": self.headers  # Assuming answer_data is already JSON
        })

    def set_headers(self, data: dict):
        try:
            self.headers = data
        except (TypeError, json.JSONDecodeError) as e:
            print(f"Error setting headers: {e}")

    def get_headers(self) -> dict:
        try:
            return self.headers or {}
        except json.JSONDecodeError as e:
            print(f"Error getting headers: {e}")
            return {}


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(String(64))
    text = db.Column(db.String(4000))
    answer_type = db.Column(db.String(312), default = 'TLT')
    answer_width = db.Column(db.String(500))
    answer_fields = db.Column(db.JSON)  # Store complex answers as JSON

    # Forward reference to Question (replace 'InlineField' with your actual class name)
    #inline_fields: db.relationship('InlineField', backref='question')  # Example relationship
    #inline_fields: Mapped[list[InlineField]] = db.relationship('InlineField', backref='question')

    def __repr__(self):
        return (f"Question: {self.question_id} (answer type={self.answer_type})")

    def to_json(self):
        return json.dumps({
            "answer_data": self.answer_data  # Assuming answer_data is already JSON
        })

    def set_answer_fields(self, data):
        try:
            self.answer_fields = json.dumps(data)
        except (TypeError, json.JSONDecodeError) as e:
            # Handle error: data is not serializable or invalid JSON
            print(f"Error setting answer data: {e}")

    def get_answer_fields(self):
        try:
            if self.answer_fields:
                return json.loads(self.answer_fields)
            else:
                # Handle the case when answer_data is empty
                return None
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            return None



class QuestionnaireQuestions(db.Model):
    __tablename__ = 'questionnaire_questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    extra_data = db.Column(db.String(600))
    # Define the relationships
    questionnaire = relationship('Questionnaire', backref='questionnaire_questions')
    question = relationship('Question', backref='questionnaire_questions')

    def readable_format(self):
        if self.questionnaire:
            questionnaire_name = self.questionnaire.name
        else:
            questionnaire_name = "N/A"

        if self.question:
            question_text = self.question.text
        else:
            question_text = "N/A"
        return f"ID: {self.id}, Questionnaire: {questionnaire_name}, Question: {question_text}, Extra Data: {self.extra_data}"

        #return self
    def __str__(self):
        return self.readable_format()


class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), nullable=False)
    description = db.Column(String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)

    column1 = db.Column(String(100))
    column2 = db.Column(String(100))
    created_on = Column(DateTime, nullable=False)

    # Define relationships if needed
    user = db.relationship('Users', backref=db.backref('tables', lazy=True))

    def __init__(self, name, description, user_id, column1, column2, creation_date=None):
        self.name = name
        self.description = description
        self.user_id = user_id
        self.column1 = column1
        self.column2 = column2
        self.creation_date = creation_date
        # Add other initialization logic as needed

# Define the association table for the many-to-many relationship


class QuestionnaireCompanies(db.Model):
    __tablename__ = 'questionnaire_companies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    status_id = db.Column(Integer, ForeignKey('status.id'))

    # Define relationships
    questionnaire = db.relationship('Questionnaire', backref='companies')
    company = db.relationship('Company', backref='questionnaires')


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'))
    question_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    submitted = db.Column(db.Boolean, default=False)
    answer_data = db.Column(db.JSON)  # Serialized JSON

    def __repr__(self):
        return (f"<Answer: company {self.company_id}, user {self.user_id}, "
                f"questionnaire {self.questionnaire_id}, answer={self.answer_data})>")

    def to_json(self):
        return json.dumps({
            "answer_data": self.answer_data  # Assuming answer_data is already JSON
        })

    def set_answer_data(self, data):
        try:
            self.answer_data = json.dumps(data)
        except (TypeError, json.JSONDecodeError) as e:
            # Handle error: data is not serializable or invalid JSON
            print(f"Error setting answer data: {e}")

    def get_answer_data(self):
        try:
            if self.answer_data:
                return json.loads(self.answer_data)
            else:
                # Handle the case when answer_data is empty
                return None
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            return None

    company = db.relationship('Company', backref='answers')
    user = db.relationship('Users', backref='answers')
    questionnaire = db.relationship('Questionnaire', backref='answers')


    # question = db.relationship('Question', backref='answers')


class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String, unique=True, nullable=False)
    description = db.Column(String)


    def __repr__(self):
        return (f"{self.name} ({self.description})")

class Interval(db.Model):
    __tablename__ = 'interval'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text)
    interval_id = db.Column(db.Integer)

    def __repr__(self):
        return (f"{self.name} ({self.description})")


class Deadline(db.Model):
    __tablename__ = 'deadline'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(Integer, ForeignKey('company.id'))
    area_id = db.Column(Integer, ForeignKey('area.id'))
    subarea_id = db.Column(Integer, ForeignKey('subarea.id'))
    interval_id = db.Column(Integer, ForeignKey('interval.interval_id'))
    status_id = db.Column(Integer, ForeignKey('status.id'))
    status_start = db.Column(String)
    status_end = db.Column(String)

    # Define relationships
    '''company = relationship("Company", back_populates="deadline")
    area = relationship("Area", back_populates="deadline")
    subarea = relationship("SubArea", back_populates="deadline")
    interval = relationship("Interval", back_populates="deadline")
    status = relationship("Status", back_populates="deadline")'''

class Lexic(db.Model):
    __tablename__ = 'lexic'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self, category=None, name=None):
        self.category = category
        self.name = name

    def __repr__(self):
        return f"{self.name}"


class Area(db.Model):
    __tablename__ = 'area'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"{self.name} ({self.description})"


class Subarea(db.Model):
    __tablename__ = 'subarea'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    data_type = db.Column(db.String(64))

    def __init__(self, name=None, description=None, data_type=None):
        self.name = name
        self.description = description
        self.data_type = data_type

    def __repr__(self):
        return f"{self.name} ({self.description})"



class AreaSubareas(db.Model):
    __tablename__ = 'area_subareas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    subarea_id = db.Column(db.Integer, db.ForeignKey('subarea.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    interval_id = db.Column(db.Integer, db.ForeignKey('interval.id'))
    caption = db.Column(db.Text(255))

    def __repr__(self):
        return (f"Area={self.area_id}, subarea={self.subarea_id}, "
                f"status={self.status_id}, interval={self.interval_id}")

class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    tier_1 = db.Column(db.String(50), nullable=False)
    tier_2 = db.Column(db.String(50), nullable=True)
    tier_3 = db.Column(db.String(50), nullable=True)

    def __init__(self, name=None, tier_1=None, tier_2=None, tier_3=None):
        self.name = name
        self.tier_1 = tier_1
        self.tier_2 = tier_2
        self.tier_3 = tier_3

    def __repr__(self):
        return (f"{self.name} ({self.tier_1})")


class LegalDocument(db.Model):
    __tablename__ = 'legal_document'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    tier_1 = db.Column(db.String(50), nullable=False)
    tier_2 = db.Column(db.String(50), nullable=False)
    tier_3 = db.Column(db.String(50), nullable=False)

    def __init__(self, name, tier_1, tier_2, tier_3):
        self.id = id
        self.name = name
        self.tier_1 = tier_1
        self.tier_2 = tier_2
        self.tier_3 = tier_3

    def __repr__(self):
        return (f"{self.name} ({self.tier_1})")


class BaseData(db.Model):
    __tablename__ = 'base_data'

    # id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id = db.Column(Integer, Sequence('base_data_id_seq'), primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    interval_id = db.Column(db.Integer, db.ForeignKey('interval.interval_id'))
    interval_ord = db.Column(db.Integer)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    legal_document_id = db.Column(db.Integer, db.ForeignKey('legal_document.id'), nullable=True)
    record_type = db.Column(db.String(64))
    data_type = db.Column(db.String(128))
    created_on = db.Column(DateTime, nullable=False)
    updated_on = db.Column(DateTime, nullable=True, onupdate=datetime.now)
    deadline = db.Column(DATE)
    created_by = db.Column(db.String(128))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    subarea_id = db.Column(db.Integer, db.ForeignKey('subarea.id'))
    lexic_id = db.Column(db.Integer, db.ForeignKey('lexic.id'))
    number_of_doc = db.Column(db.String(64))
    date_of_doc = db.Column(DATE)
    fc1 = db.Column(db.String)
    fc2 = db.Column(db.String)
    fc3 = db.Column(db.String)
    fc4 = db.Column(db.String)
    fc5 = db.Column(db.String)
    fc6 = db.Column(db.String)
    ft1 = db.Column(db.String)
    fb1 = db.Column(db.LargeBinary)
    fi0 = db.Column(db.Integer)
    fi1 = db.Column(db.Integer)
    fi2 = db.Column(db.Integer)
    fi3 = db.Column(db.Integer)
    fi4 = db.Column(db.Integer)
    fi5 = db.Column(db.Integer)
    fi6 = db.Column(db.Integer)
    fi7 = db.Column(db.Integer)
    fi8 = db.Column(db.Integer)
    fi9 = db.Column(db.Integer)
    fi10 = db.Column(db.Integer)
    fi11 = db.Column(db.Integer)
    fi12 = db.Column(db.Integer)
    fi13 = db.Column(db.Integer)
    fi14 = db.Column(db.Integer)
    fi15 = db.Column(db.Integer)
    fi16 = db.Column(db.Integer)
    fn0 = db.Column(db.Numeric)
    fn1 = db.Column(db.Numeric)
    fn2 = db.Column(db.Numeric)
    fn3 = db.Column(db.Numeric)
    fn4 = db.Column(db.Numeric)
    fn5 = db.Column(db.Numeric)
    fn6 = db.Column(db.Numeric)
    fn7 = db.Column(db.Numeric)
    fn8 = db.Column(db.Numeric)
    fn9 = db.Column(db.Numeric)
    file_path = db.Column(db.String(255))
    no_action = db.Column(db.Boolean, default=False)  # Change to BOOLEAN type

    user = db.relationship('Users', foreign_keys=[user_id])
    company = db.relationship('Company', foreign_keys=[company_id])
    interval = db.relationship('Interval', foreign_keys=[interval_id])
    status = db.relationship('Status', foreign_keys=[status_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    legal_document = db.relationship('LegalDocument', foreign_keys=[legal_document_id])
    area = db.relationship('Area', foreign_keys=[area_id])
    subarea = db.relationship('Subarea', foreign_keys=[subarea_id])
    lexic = db.relationship('Lexic', foreign_keys=[lexic_id])

    # Define relationship with StepBaseData
    steps_relationship = relationship("StepBaseData", back_populates="base_data")

    # Relationship with BaseDataInline
    # base_data_inlines = db.relationship('BaseDataInline', backref='base_data', lazy=True, cascade="all, delete-orphan")
    base_data_inlines = db.relationship('BaseDataInline', backref='parent_base_data', lazy=True, cascade="all, delete-orphan")
    # Define the relationship
    # base_data_inlines = db.relationship('BaseDataInline', back_populates='base_data', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Data ID: {self.id}>'

    @classmethod
    def get_documents(cls):
        """
        Get documents where file_path is not null.

        :return: A SQLAlchemy query object filtering BaseData instances where file_path is not null.
        """
        return cls.query.filter(cls.file_path.isnot(None))

    def serialize_for_area21(self):
        return {
            'company_id': self.company_id,
            'user_id': self.user_id,
            'area_id': self.area_id,
            'subarea_id': self.subarea_id,
            'record_type': self.record_type,
            'data_type': self.data_type,
            'status_id': self.status_id,
            'interval_ord': self.interval_ord,
            'interval_id': self.interval_id,
            'fi1': self.fi1,
            'fi2': self.fi2,
            'fi3': self.fi3,
            'fc2': self.fc2

            # Add more fields as needed for the API view
        }


    def serialize_for_area22(self):
        return {
            'company_id': self.company_id,
            'user_id': self.user_id,
            'area_id': self.area_id,
            'subarea_id': self.subarea_id,
            'record_type': self.record_type,
            'data_type': self.data_type,
            'status_id': self.status_id,
            'interval_ord': self.interval_ord,
            'interval_id': self.interval_id,
            'fi1': self.fi1,
            'fi2': self.fi2,
            'fi3': self.fi3,
            'fc2': self.fc2

            # Add more fields as needed for the API view
        }


    def serialize_for_area23(self):
        return {
            'company_id': self.company_id,
            'user_id': self.user_id,
            'area_id': self.area_id,
            'subarea_id': self.subarea_id,
            'record_type': self.record_type,
            'data_type': self.data_type,
            'status_id': self.status_id,
            'interval_ord': self.interval_ord,
            'interval_id': self.interval_id,
            'fi1': self.fi1,
            'fi2': self.fi2,
            'fi3': self.fi3,
            'fn1': self.fn1,
            'fn2': self.fn2,
            'fc1': self.fc1,
            # Add more fields as needed for the API view
        }

    def serialize_for_area24(self):
        return {
            'company_id': self.company_id,
            'user_id': self.user_id,
            'area_id': self.area_id,
            'subarea_id': self.subarea_id,
            'record_type': self.record_type,
            'data_type': self.data_type,
            'status_id': self.status_id,
            'interval_ord': self.interval_ord,
            'interval_id': self.interval_id,
            'fi1': self.fi1,
            'fi2': self.fi2,
            'fi3': self.fi3,
            'fi4': self.fi4,
            'fi5': self.fi5,
            'fc1': self.fc1

            # Add more fields as needed for the API view
        }

    def workflow(self):
        workflows = []  # List to store workflow attributes of each element
        for step_relationship in self.steps_relationship:
            if step_relationship:  # Ensure the step_rel object exists
                workflow = step_relationship.workflow
                workflows.append(workflow)  # Append the workflow attribute to the list
        return workflows


    '''

    @property
    def workflow(self):
        if self.steps_relationship:
            print('self_rel workflow', self.steps_relationship)
            return self.steps_relationship.workflow
        else:
            return None  # Handle cases where there's no related step_base_data

    @property
    def workflow(self):
        workflows = [step.workflow for step in self.steps_relationship if step.workflow]
        return workflows[0] if workflows else None
    '''

    def step(self):
        steps = []  # List to store 'step' attributes of each element
        for step_relationship in self.steps_relationship:
            if step_relationship:  # Ensure the step_rel object exists
                step = step_relationship.step
                steps.append(step)  # Append the 'step' attribute to the list
        return steps

    '''
    @property
    def step(self):
        if self.steps_relationship:
            return self.steps_relationship.step
        else:
            return None  # Handle cases where there's no related step_base_data



    @property
    def step(self):
        steps = [step.step for step in self.steps_relationship if step.step]
        return steps[0] if steps else None
    '''

    from sqlalchemy.orm import aliased
    @classmethod
    def get_combined_subset(cls, lexic_id=None, area_id_list=None, subarea_id_list=None,
                            company_id=None, user_id=None, user_role=None,
                            status_id_list=None,
                            filter_file_path=True):
        """
        Get a combined subset of BaseData based on multiple criteria.

        :param lexic_id: Filter by lexic_id.
        :param company_id: Filter by company_id.
        :param user_id: Filter by user_id.
        :param user_role: Users role for condition checks.
        :param filter_file_path: Boolean flag indicating whether to filter records based on file_path.
        :return: A SQLAlchemy query object for the combined subset of BaseData instances.
        """
        query = cls.query

        # Condition for record_type
        # query = query.filter(cls.record_type == 'table')

        if filter_file_path:
            # Add condition for non-null file_path
            query = query.filter(cls.file_path != None)

        if status_id_list:
            query = query.filter(cls.status_id.in_(status_id_list))

        if area_id_list:
            query = query.filter(cls.area_id.in_(area_id_list))

        if subarea_id_list:
            query = query.filter(cls.subarea_id.in_(subarea_id_list))


        if user_role in ['Admin', 'Authority']:
            # Admin or Authority can see all records
            pass  # no additional filter needed
        elif user_role == 'Employee':
            # Employee can only see their own records
            query = query.filter(cls.user_id == user_id)
        elif user_role == 'Manager':
            # Manager can see all records related to their company
            # Get all user_ids for the given company
            manager_company_users = (
                Companys.query.filter_by(company_id=company_id)
                .with_entities(CompanyUsers.user_id)
            )
            # Filter records where user_id is in the set of company users
            query = query.filter(cls.user_id.in_(manager_company_users.subquery()))
        else:
            # For other roles, no records are visible
            return query.filter(False)  # Return an empty query

        # Condition related to lexic
        if lexic_id is not None:
            query = query.filter(cls.lexic_id == lexic_id)

        # List to store results
        results = []
        for base_data_object in query.all():
            results.append({
                'base_data': base_data_object,
                'workflow': base_data_object.workflow,  # Use the property
                'step': base_data_object.step  # Use the property
            })

        return results


class BaseDataInline(db.Model):
   __tablename__ = 'basedata_inline'
   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   base_data_id = db.Column(db.Integer, db.ForeignKey('base_data.id'), nullable=False)
   name = db.Column(db.String(100), nullable=False)
   type = db.Column(db.String(100), nullable=False)
   value = db.Column(db.Integer, nullable=False)
   record_type = db.Column(db.String(64), nullable=False)

   # Relationship with BaseData
   #parent_base_data = db.relationship('BaseData', backref=db.backref('base_data_inlines', lazy=True, cascade="all, delete-orphan"))

def after_flush_listener(session, flush_context):
    updates = []
    for instance in session.new:
        if isinstance(instance, BaseData):
            total_value = sum(inline.value for inline in instance.base_data_inlines)
            updates.append((instance.id, total_value))

    for instance in session.dirty:
        if isinstance(instance, BaseData):
            total_value = sum(inline.value for inline in instance.base_data_inlines)
            updates.append((instance.id, total_value))

    session.info['fi16_updates'] = updates

def after_flush_postexec_listener(session, flush_context):
    updates = session.info.get('fi16_updates', [])
    for base_data_id, total_value in updates:
        session.query(BaseData).filter(BaseData.id == base_data_id).update({'fi16': total_value})

event.listen(db.session, 'after_flush', after_flush_listener)
event.listen(db.session, 'after_flush_postexec', after_flush_postexec_listener)


class StepBaseData(db.Model):
    __tablename__ = 'step_base_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_data_id = db.Column(db.Integer, db.ForeignKey('base_data.id'))
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    start_date = db.Column(db.DateTime, default=func.current_timestamp())
    deadline_date = db.Column(db.DateTime)
    auto_move = db.Column(db.Integer, default=0)
    end_date = db.Column(db.DateTime)
    hidden_data = db.Column(db.String(255))
    start_recall = db.Column(db.Integer, default=0)
    deadline_recall = db.Column(db.Integer, default=0)
    end_recall = db.Column(db.Integer, default=0)
    recall_unit = db.Column(db.String(24), default='day')

    open_action = db.Column(db.Integer, default=1)

    # Define relationship with BaseData
    base_data = relationship("BaseData", back_populates="steps_relationship")
    workflow = relationship("Workflow", foreign_keys=[workflow_id])
    step = relationship("Step", foreign_keys=[step_id])
    status = relationship("Status", foreign_keys=[status_id])


    @validates('auto_move')
    def validate_auto_move(self, key, value):
        return int(value)


    # Define unique constraint
    #__table_args__ = (
    #    UniqueConstraint('base_data_id', 'workflow_id', 'step_id', 'status_id', name='unique_step_base_data'),
    #)

    def __repr__(self):
        return f"Workflow ID {self.id}: doc {self.base_data_id} in wf {self.workflow_id}, step {self.step_id}, status {self.status_id}"

    @classmethod
    def create(cls, **kwargs):
        try:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance
        except IntegrityError as e:
            db.session.rollback()
            # Handle constraint violation error
            print("Constraint violation error:", e)
            return None




class StepQuestionnaire(db.Model):
    __tablename__ = 'step_questionnaire'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'))
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    start_date = db.Column(db.DateTime, default=func.current_timestamp())
    deadline_date = db.Column(db.DateTime)
    auto_move = db.Column(db.Boolean, default=False)
    end_date = db.Column(db.DateTime)
    hidden_data = db.Column(db.String(255))
    start_recall = db.Column(db.Integer, default=0)
    deadline_recall = db.Column(db.Integer, default=0)
    end_recall = db.Column(db.Integer, default=0)
    recall_unit = db.Column(db.String(24), default='day')

    open_action = db.Column(db.Integer, default=1)

    # Define relationship with BaseData

    questionnaire = relationship("Questionnaire", back_populates="steps_questionnaires_relationship")

    workflow = relationship("Workflow", foreign_keys=[workflow_id])
    step = relationship("Step", foreign_keys=[step_id])
    status = relationship("Status", foreign_keys=[status_id])

    # Define unique constraint
    #__table_args__ = (
    #    UniqueConstraint('base_data_id', 'workflow_id', 'step_id', 'status_id', name='unique_step_base_data'),
    #)

    def __repr__(self):
        return f"Quesionnaire ID {self.id}: quest {self.questionnaire_id} in wf {self.workflow_id}, step {self.step_id}, status {self.status_id}"

    @classmethod
    def create(cls, **kwargs):
        try:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance
        except IntegrityError as e:
            db.session.rollback()
            # Handle constraint violation error
            print("Constraint violation error:", e)
            return None


class Workflow(db.Model):
    __tablename__ = 'workflow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20))
    restricted = db.Column(db.Boolean, default=True)
    deadline_date = db.Column(db.DateTime, nullable=True)

    # Define the relationship with WorkflowBaseData
    # workflow_base_data = db.relationship("WorkflowBaseData", back_populates="workflow")

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    def __repr__(self):
        return f"{self.name} ({self.description})"


class Step(db.Model):
    __tablename__ = 'step'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200))
    action = db.Column(db.String(50))
    order = db.Column(db.Integer)
    next_step_id = db.Column(db.Integer, db.ForeignKey('step.id'))
    deadline_date = db.Column(db.DateTime, nullable=True)
    reminder_date = db.Column(db.DateTime, nullable=True)

    def __init__(self, base_data_id=None, step_id=None, hidden_data=None, workflow_id=None, start_date=None,
                 deadline_date=None, auto_move=False, end_date=None, start_recall=None,
                 deadline_recall=None, end_recall=None, recall_unit=None, open_action=None,
                 name=None, description=None, action=None, order=None):
        self.base_data_id = base_data_id
        self.workflow_id = workflow_id
        self.step_id = step_id
        self.start_date = start_date
        self.deadline_date = deadline_date
        self.auto_move = auto_move
        self.end_date = end_date
        self.hidden_data = hidden_data
        self.start_recall = start_recall
        self.deadline_recall = deadline_recall
        self.end_recall = end_recall
        self.recall_unit = recall_unit
        self.open_action = open_action
        self.name = name
        self.description = description
        self.action = action
        self.order = order

    def step_transition(self, workflow_id, step_offset):
        """Moves the document by step_offset within the constraints of the workflow."""
        # Query the steps for the given workflow
        workflow_steps = WorkflowSteps.query.filter_by(workflow_id=workflow_id).all()

        # Extract step ids
        step_ids = [step.step_id for step in workflow_steps]

        # Query the steps details
        steps_for_transition = Step.query.filter(Step.id.in_(step_ids)).order_by(Step.order).all()

        # Find the current step index
        current_step_index = step_ids.index(self.step_id)
        print('current step is', current_step_index)

        # Calculate the new step index
        new_step_index = current_step_index + step_offset

        print('next step is', new_step_index)

        # Check if the new step index is within bounds
        if new_step_index < 0 or new_step_index >= len(steps_for_transition):
            return  # Do not move if out of bounds

        # Get the new step
        new_step = steps_for_transition[new_step_index]

        # Update the current step
        if new_step.next_step_id is not None:
            # If the new step has a next step defined, move to that instead
            new_step = Step.query.get(new_step.next_step_id)

        self.step_id = new_step.id
        db.session.commit()

    def status_change(self, to_status):
        """Changes the status of the document."""
        self.status_id = to_status
        db.session.commit()

    def __repr__(self):
        return f"{self.name} ({self.description})"


class WorkflowSteps(db.Model):
    __tablename__ = 'workflow_steps'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))

    workflow = db.relationship("Workflow", backref="workflow_steps")
    step = db.relationship("Step", backref="workflow_steps")

    def __repr__(self):
        return f"{self.workflow_id}, step {self.step_id}"


class WorkflowBaseData(db.Model):
    __tablename__ = 'workflow_base_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    base_data_id = db.Column(db.Integer, db.ForeignKey('base_data.id'))
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)
    end_of_registration = db.Column(db.DateTime)

    workflow = db.relationship("Workflow", backref="workflow_base_data")
    base_data = db.relationship("BaseData", backref="workflow_base_data")
    # Define the relationship with Workflow model
    #workflow_data_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    #workflow_data = relationship('Workflow', backref='base_data_workflows')
    # Assuming there's a foreign key to BaseData_Workflow
    #workflow_data_id = db.Column(db.Integer, db.ForeignKey('base_data_workflow.id'))

    # Define the relationship with BaseData_Workflow
    #workflow_data = relationship('BaseData_Workflow', foreign_keys=[workflow_data_id], backref='workflow_base_data')

    def __repr__(self):
        return f"Docs workflow: doc {self.base_data_id}, wf {self.workflow_id}"



class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_type = db.Column(db.String(64))
    company_id = db.Column(db.Integer)
    area_id = db.Column(db.Integer)
    subarea_id = db.Column(db.Integer)
    config_integer = db.Column(db.Integer)
    config_number = db.Column(db.Numeric)
    config_text = db.Column(db.String(255))
    config_date = db.Column(db.String)

    def __repr__(self):
        return (f"Config: type={self.config_type}, company={self.company_id}, "
                f"area={self.area_id}, subarea={self.subarea_id}")



def get_config_values(config_type, company_id=None, area_id=None, subarea_id=None):
    my_config = Config()
    query = my_config.query.filter(Config.config_type == config_type)
    if company_id is not None:
        query = query.filter(or_(Config.company_id == company_id, Config.company_id == None))
    if area_id is not None:
        query = query.filter(or_(Config.area_id == area_id, Config.area_id == None))
    if subarea_id is not None:
        query = query.filter(or_(Config.subarea_id == subarea_id, Config.subarea_id == None))

    config = query.first()

    if config:
        config_integer = config.config_integer if isinstance(config.config_integer, int) else None
        config_number = config.config_number if isinstance(config.config_number, (int, float)) else None
        config_text = config.config_text if isinstance(config.config_text, str) else None
        config_date = config.config_date if isinstance(config.config_date, str) else None
        return config_integer, config_number, config_text, config_date
    else:
        return None, None, None, None


class AuditLog(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    base_data_id = db.Column(db.Integer, db.ForeignKey('base_data.id'))
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'), nullable=True)
    action = db.Column(db.String(256))
    details = db.Column(db.Text)

    # Relationships (optional, define as needed)
    base_data = relationship('BaseData', backref='audit_log')
    # company_id = relationship('Company', backref='audit_log')
    # user_id = relationship('Users', backref='audit_log')
    # workflow_id = relationship('Workflow', backref='audit_log')
    # step_id = relationship('Step', backref='audit_log')
    def __repr__(self):
        # Print each attribute individually
        '''

        :return:
        print(f"id={self.id}")
        print(f"user_id={self.user_id}")
        print(f"company_id={self.company_id}")
        print(f"base_data_id={self.base_data_id}")
        print(f"workflow_id={self.workflow_id}")
        print(f"step_id={self.step_id}")
        print(f"action={self.action}")

        '''
        # Return the string representation
        return (f"Audit log: {self.id}, user {self.user_id}, company {self.company_id}, "
                f"doc {self.base_data_id}, workflow {self.workflow_id}, step {self.step_id}, "
                f"action {self.action}, details ...")


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, ForeignKey('company.id'))  # If messages are specific to a company
    user_id = db.Column(db.Integer, ForeignKey('users.id'))  # If messages are targeted at specific users
    sender = db.Column(db.String(255))  # Information about the sender
    message_type = db.Column(Enum('noticeboard', 'email', 'service_message', name='message_types'))
    subject = db.Column(db.String(255))
    body = db.Column(db.String)
    created_at =  db.Column(db.DateTime)
    marked_as_read = db.Column(db.Boolean, default=False)
    lifespan = db.Column(Enum('one-off', 'persistent', name='lifespan_types'), default='one-off')

    # Define relationships
    company = relationship("Company")  # If using company_id
    user = relationship("Users")  # If using user_id

    def __repr__(self):
        return f"{self.message_type}, {self.subject}"



class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False, default=2)  # Default status "Open"
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    marked_as_read = db.Column(db.Boolean, default=False)
    lifespan = db.Column(Enum('one-off', 'persistent', name='lifespan_types'), default='one-off')

    # users = db.relationship('Users', backref='tickets')
    user = db.relationship('Users', foreign_keys=[user_id], backref='tickets')
    subject = db.relationship('Subject', foreign_keys=[subject_id], backref='tickets')
    status = db.relationship('Status', foreign_keys=[status_id], backref='tickets')


class Questionnaire_psf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    structure = db.Column(db.JSON, nullable=False)

class Response_psf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)

    interval_id = db.Column(db.Integer, db.ForeignKey('interval.interval_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    record_type = db.Column(db.String(64))
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)
    deadline = db.Column(DATE)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    subarea_id = db.Column(db.Integer, db.ForeignKey('subarea.id'))
    number_of_doc = db.Column(db.String(64))
    date_of_doc = db.Column(DATE)
    file_path = db.Column(db.String(255))


class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    stripe_plan_id = db.Column(db.String(128), nullable=False)
    stripe_price_id = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    billing_cycle = db.Column(db.String(50), nullable=False, default='monthly')  # e.g., 'monthly', 'yearly', 'one-off'

    plan_products = db.relationship('PlanProducts', back_populates='plan')
    user_plans = db.relationship('UserPlans', back_populates='plan')
    subscriptions = db.relationship('Subscription', back_populates='plan')

    # products = db.relationship('Product', secondary='plan_products', backref=db.backref('plan', lazy='dynamic'),
    #                         primaryjoin='PlanProducts.plan_id == Plan.id',
    #                         secondaryjoin='PlanProducts.product_id == Product.id')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Plan(id={self.id}, name={self.name})>"

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    stripe_product_id = db.Column(db.String(128), nullable=False)
    stripe_price_id = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='EUR')
    path = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(128), nullable=True)
    plan_products = db.relationship('PlanProducts', back_populates='product')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"

class PlanProducts(db.Model):
    __tablename__ = 'plan_products'
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    created_on = Column(DateTime, nullable=True)
    updated_on = Column(DateTime, nullable=True, onupdate=datetime.now)
    end_of_registration = Column(DateTime, nullable=True)
    plan = db.relationship('Plan', back_populates='plan_products')
    product = db.relationship('Product', back_populates='plan_products')

    def __init__(self, plan_id, product_id, created_on=None, updated_on=None, end_of_registration=None):
        self.plan_id = plan_id
        self.product_id = product_id
        self.created_on = created_on or datetime.utcnow()
        self.updated_on = updated_on
        self.end_of_registration = end_of_registration

    def __repr__(self):
        return f"<PlanProducts(plan_id={self.plan_id}, product_id={self.product_id})>"



class UserPlans(db.Model):
    __tablename__ = 'user_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    activation_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    stripe_subscription_id = db.Column(db.String(255), nullable=True)

    user = db.relationship('Users', back_populates='user_plans')
    plan = db.relationship('Plan', back_populates='user_plans')


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    title = db.Column(String(255), nullable=False)
    start = db.Column(DateTime, nullable=False)
    end = db.Column(DateTime, nullable=False)
    description = db.Column(String)
    all_day = db.Column(Boolean, default=False)
    location = Column(String(255))
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = db.Column(Integer, ForeignKey('company.id'), nullable=False)
    color = db.Column(String(7))
    recurrence = db.Column(String(255), nullable=True)
    recurrence_end = db.Column(db.Date, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    user = relationship('Users', backref='events')
    company = relationship('Company', backref='events')

    def __repr__(self):
        return f'<Event {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'description': self.description,
            'all_day': self.all_day,
            'location': self.location,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'color': self.color,
            'recurrence': self.recurrence,
            'recurrence_end': self.recurrence_end.isoformat() if self.recurrence_end else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }



class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    # plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Ensure the price field is properly defined
    currency = db.Column(db.String(3), nullable=False, default='EUR')

    product = db.relationship('Product', backref=db.backref('cart', lazy=True))
    # plan = db.relationship('Plan', backref=db.backref('cart', lazy=True))
    user = db.relationship('Users', backref=db.backref('cart', lazy=True))
    company = db.relationship('Company', backref=db.backref('cart', lazy=True))


class Subscription(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
   start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   end_date = db.Column(db.DateTime, nullable=True)
   user = db.relationship('Users', back_populates='subscriptions')
   plan = db.relationship('Plan', back_populates='subscriptions')

