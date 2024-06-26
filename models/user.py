
from db import db
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_security import RoleMixin, UserMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Numeric, func
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy import or_, and_, Enum

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, DATE, func

from wtforms.fields import StringField, TextAreaField, DateTimeField, SelectField, BooleanField, SubmitField
from datetime import datetime

from sqlalchemy.exc import IntegrityError
# OR
# from sqlalchemy.dialects.mysql import JSON  # for MySQL
# OR
from sqlalchemy.dialects.sqlite import JSON  # for SQLite
# OR
# from sqlalchemy.dialects.oracle import JSON  # for Oracle
import json


class CheckboxField(BooleanField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = True
        else:
            self.data = False
    def populate_obj(self, obj, name):
        setattr(obj, name, "Yes" if self.data else "No")  # Customize as per your model


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(String(80), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)
    user_2fa_secret = db.Column(String(32), nullable=False)
    title = db.Column(String(12), nullable=True)
    first_name = db.Column(String(128), nullable=True)
    mid_name = db.Column(String(128), nullable=True)
    last_name = db.Column(String(128), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    company = db.Column(String(128), nullable=True)
    address = db.Column(String(128), nullable=False)
    address1 = db.Column(String(128), nullable=True)
    city = db.Column(String(128), nullable=False)
    province = db.Column(String(64), nullable=False)
    region = db.Column(String(64), nullable=False)
    zip_code = db.Column(String(24), nullable=True)
    country = db.Column(String(64), nullable=False)
    tax_code = db.Column(String(128), nullable=True)
    mobile_phone = db.Column(db.Integer, nullable=False)
    work_phone = db.Column(db.Integer, nullable=True)

    #password_hash = db.Column(db.String(128))
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    end_of_registration = db.Column(DATE)

    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('user', lazy='dynamic'),
                            primaryjoin='UserRoles.user_id == Users.id',
                            secondaryjoin='UserRoles.role_id == Role.id')

    #def get_reset_token(self, expires_sec=1800):
    #    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    #    return s.dumps({'user_id': self.id}).decode('utf-8')

    #user_roles_as_role = relationship('UserRoles', back_populates='user')
    #user_roles = relationship('UserRoles', back_populates='user')
    #roles = relationship('Role', secondary='user_roles_as_role', back_populates='users')


    # Add constructor to set the primary key
    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
        self.id = kwargs.get('id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

        # Implement your password checking logic here
        #return bcrypt.check_password_hash(self.password, password.encode('utf-8'))

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

    def __repr__(self):
        return f"<User {self.username} {self.last_name}>"


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(80), unique=True)
    description = db.Column(String(255))

    def __repr__(self):
        return (f"Role #{self.id}: {self.name} ({self.description})")

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    #user = relationship('Users', backref='user_roles')
    #role = relationship('Role', backref='user_roles')


class CompanyUsers(db.Model):
    __tablename__ = 'company_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
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
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    end_of_registration = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return (f"Company ID {self.id}: {self.name}")



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

    id = Column(Integer, primary_key=True, autoincrement=True)
    questionnaire_id = db.Column(String(64), unique=True, nullable=False)
    questionnaire_type = db.Column(db.String(24), nullable=True, default='Questionnaire')
    name = db.Column(String(128), unique=True)
    interval = db.Column(String(12))
    deadline_date = db.Column(DateTime)
    status_id = db.Column(Integer, ForeignKey('status.id'))
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    # TODO json?
    headers = db.Column(db.JSON)

    steps_questionnaires_relationship = relationship("StepQuestionnaire", back_populates="questionnaire")

    def __repr__(self):
        return (f"Questionnaire #{self.id}: {self.questionnaire_id} ({self.name})")


    def to_json(self):
        return json.dumps({
            "answer_data": self.headers  # Assuming answer_data is already JSON
        })

    def set_headers(self, data):
        try:
            self.headers = json.dumps(data)
        except (TypeError, json.JSONDecodeError) as e:
            # Handle error: data is not serializable or invalid JSON
            print(f"Error setting headers: {e}")

    def get_headers(self):
        try:
            if self.headers:
                return json.loads(self.headers)
            else:
                # Handle the case when answer_data is empty
                return None
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            return None


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
        return (f"Question #{self.id}: {self.question_id} (answer type={self.answer_type})")

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
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())

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
        return (f"<Answer(id={self.id}, company_id={self.company_id}, user_id={self.user_id}, "
                f"questionnaire_id={self.questionnaire_id}, "
                f"timestamp={self.timestamp}, submitted={self.submitted}, answer_data={self.answer_data})>")

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

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)


    def __repr__(self):
        return (f"Status #{self.id}: {self.name} ({self.description})")

class Interval(db.Model):
    __tablename__ = 'interval'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text)
    interval_id = db.Column(db.Integer)

    def __repr__(self):
        return (f"Interval # {self.id}: {self.name} ({self.description}, "
                f"{self.interval_id})")


class Deadline(db.Model):
    __tablename__ = 'deadline'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('company.id'))
    area_id = Column(Integer, ForeignKey('area.id'))
    subarea_id = Column(Integer, ForeignKey('subarea.id'))
    interval_id = Column(Integer, ForeignKey('interval.interval_id'))
    status_id = Column(Integer, ForeignKey('status.id'))
    status_start = Column(String)
    status_end = Column(String)

    # Define relationships
    '''company = relationship("Company", back_populates="deadline")
    area = relationship("Area", back_populates="deadline")
    subarea = relationship("SubArea", back_populates="deadline")
    interval = relationship("Interval", back_populates="deadline")
    status = relationship("Status", back_populates="deadline")'''

class Lexic(db.Model):
    __tablename__ = 'lexic'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), unique=True)
    def __repr__(self):
        return f"Dictionary entry {self.id}: {self.name} ({self.category})"


class Area(db.Model):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    def __repr__(self):
        return f"Area{self.id}: {self.name} ({self.description})"


class Subarea(db.Model):
    __tablename__ = 'subarea'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    data_type = Column(String)

    def __repr__(self):
        return f"Subarea {self.id}: {self.name} ({self.description}, {self.data_type})"

class AreaSubareas(db.Model):
    __tablename__ = 'area_subareas'
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    subarea_id = db.Column(db.Integer, db.ForeignKey('subarea.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    interval_id = db.Column(db.Integer, db.ForeignKey('interval.id'))
    caption = db.Column(db.Text(255))

    def __repr__(self):
        return (f"<AreaSubareas(id={self.id}, area_id={self.area_id}, subarea_id={self.subarea_id}, "
                f"status_id={self.status_id}, interval_id={self.interval_id}, caption='{self.caption}')>")


class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tier_1 = db.Column(db.String(50), nullable=False)
    tier_2 = db.Column(db.String(50), nullable=True)
    tier_3 = db.Column(db.String(50), nullable=True)

    def __init__(self, name, tier):
        self.id = id
        self.name = name
        self.tier_1 = tier_1

    def __repr__(self):
        return (f"Items dictionary # {self.id}: {self.name} ({self.tier_1}, "
                f"{self.tier_2}, {self.tier_3})")


class LegalDocument(db.Model):
    __tablename__ = 'legal_document'

    id = db.Column(db.Integer, primary_key=True)
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
        return (f"Documents dictionary {self.id}: {self.name} ({self.tier_1}, "
                f"{self.tier_2}, {self.tier_3})")


class BaseData(db.Model):
    __tablename__ = 'base_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    interval_id = db.Column(db.Integer, db.ForeignKey('interval.interval_id'))
    interval_ord = db.Column(db.Integer)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    legal_document_id = db.Column(db.Integer, db.ForeignKey('legal_document.id'), nullable=True)
    record_type = db.Column(db.String(64))
    data_type = db.Column(db.String(128))
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    deadline = Column(DATE)
    created_by = db.Column(db.String(128))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    subarea_id = db.Column(db.Integer, db.ForeignKey('subarea.id'))
    lexic_id = db.Column(db.Integer, db.ForeignKey('lexic.id'))
    number_of_doc = db.Column(db.String(64))
    date_of_doc = Column(DATE)
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
    no_action = db.Column(db.Integer, default=0)

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

    def __repr__(self):
        return f'<BaseData {self.id}>'

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
            'fi4': self.fi4,
            'fi5': self.fi5,
            'fn1': self.fn1,
            'fn2': self.fn2,
            'fc1': self.fc1,
            'fc2': self.fc2,
            'fc3': self.fc3,
            'fc4': self.fc4,
            'fc5': self.fc5,
            'fc6': self.fc6

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


class StepBaseData(db.Model):
    __tablename__ = 'step_base_data'

    id = db.Column(db.Integer, primary_key=True)
    base_data_id = db.Column(db.Integer, db.ForeignKey('base_data.id'))
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
    base_data = relationship("BaseData", back_populates="steps_relationship")
    workflow = relationship("Workflow", foreign_keys=[workflow_id])
    step = relationship("Step", foreign_keys=[step_id])
    status = relationship("Status", foreign_keys=[status_id])

    # Define unique constraint
    #__table_args__ = (
    #    UniqueConstraint('base_data_id', 'workflow_id', 'step_id', 'status_id', name='unique_step_base_data'),
    #)

    def __repr__(self):
        return f"Doc WF {self.id}: doc {self.base_data_id} in wf {self.workflow_id}, step {self.step_id}, status {self.status_id}"

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

    id = db.Column(db.Integer, primary_key=True)
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
        return f"Quest WF {self.id}: quest {self.questionnaire_id} in wf {self.workflow_id}, step {self.step_id}, status {self.status_id}"

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

    id = db.Column(db.Integer, primary_key=True)
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
        return f"Workflow {self.id}, {self.name} ({self.description})"


class Step(db.Model):
    __tablename__ = 'step'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200))
    action = db.Column(db.String(50))
    order = db.Column(db.Integer)
    next_step_id = db.Column(db.Integer, db.ForeignKey('step.id'))
    deadline_date = db.Column(db.DateTime, nullable=True)
    reminder_date = db.Column(db.DateTime, nullable=True)


    def __init__(self, base_data_id, step_id, hidden_data, workflow_id, start_date=None,
                 deadline_date=None, auto_move=False, end_date=None, start_recall=None,
                 deadline_recall=None, end_recall=None, recall_unit=None, open_action=None):
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
        return f"Step {self.id}: {self.name} ({self.description})"


class WorkflowSteps(db.Model):
    __tablename__ = 'workflow_steps'

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))

    workflow = db.relationship("Workflow", backref="workflow_steps")
    step = db.relationship("Step", backref="workflow_steps")

    def __repr__(self):
        return f"WF {self.id} {self.workflow_id}, step {self.step_id}"


class WorkflowBaseData(db.Model):
    __tablename__ = 'workflow_base_data'

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    base_data_id = db.Column(db.Integer, db.ForeignKey('base_data.id'))
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
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
        return f"Docs WF {self.id}: doc {self.base_data_id}, wf {self.workflow_id}"



class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_type = db.Column(db.String(64))
    company_id = db.Column(db.Integer)
    area_id = db.Column(db.Integer)
    subarea_id = db.Column(db.Integer)
    config_integer = db.Column(db.Integer)
    config_number = db.Column(db.Numeric)
    config_text = db.Column(db.String(255))
    config_date = db.Column(db.String)

    def __repr__(self):
        return (f"Config id={self.id}, type={self.config_type}, company_id={self.company_id}, "
                f"area_id={self.area_id}, subarea_id={self.subarea_id}")



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

    id = db.Column(db.Integer, primary_key=True)
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
    # user_id = relationship('User', backref='audit_log')
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
        return (f"Audit log id={self.id}, user {self.user_id}, company {self.company_id}, "
                f"doc {self.base_data_id}, workflow {self.workflow_id}, step {self.step_id}, "
                f"action {self.action}, details ...")


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
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
        return f"Message id={self.id}, type={self.message_type}, subject={self.subject}"



class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    marked_as_read = db.Column(db.Boolean, default=False)
    lifespan = db.Column(Enum('one-off', 'persistent', name='lifespan_types'), default='')
