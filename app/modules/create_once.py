from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config

import os

# Get the absolute path to the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

appa = Flask(__name__)
appa.config.from_object(Config)
SQLALCHEMY_DATABASE_URI = f"sqlite:///{current_directory}/database/sysconfig.dba"
print('uri is', SQLALCHEMY_DATABASE_URI)
dba = SQLAlchemy(appa)
#dba.init_appa(appa)


#from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(dba.Model, UserMixin):
    extend_existing = False
    id = dba.Column(dba.Integer, primary_key=True)
    username = dba.Column(dba.String(80), unique=True, nullable=False)
    email = dba.Column(dba.String(120), unique=True, nullable=False)
    password = dba.Column(dba.String(60), nullable=False)
    first_name = dba.Column(dba.String(128), nullable=True)
    mid_name = dba.Column(dba.String(128), nullable=True)
    last_name = dba.Column(dba.String(128), nullable=True)
    company_id = dba.Column(dba.Integer, dba.ForeignKey('company.id'),
                            backref=db.backref('employees', lazy=True),
                            nullable=True),
    company = dba.Column(dba.String(128), nullable=True)
    address = dba.Column(dba.String(128), nullable=False)
    address1 = dba.Column(dba.String(128), nullable=True)
    city = dba.Column(dba.String(128), nullable=False)
    province = dba.Column(dba.String(64), nullable=False)
    region = dba.Column(dba.String(64), nullable=False)
    zip_code = dba.Column(dba.String(24), nullable=True)
    country = dba.Column(dba.String(64), nullable=False)
    tax_code = dba.Column(dba.String(128), nullable=True)
    mobile_phone = dba.Column(dba.Integer, nullable=False)
    work_phone = dba.Column(dba.Integer, nullable=True)
    registration_date = dba.Column(dba.DateTime, nullable=False, default=datetime.utcnow)

class Company(dba.Model):
    extend_existing = False
    id = dba.Column(dba.Integer, primary_key=True)
    name = dba.Column(dba.String(100), nullable=False)
    description = dba.Column(dba.Text)
    address = dba.Column(dba.String(255))
    phone_number = dba.Column(dba.String(20))
    email = dba.Column(dba.String(100))
    website = dba.Column(dba.String(100))
    tax_code = dba.Column(dba.String(24), nullable=True)
    employees = dba.relationship('Employee', backref='company', lazy=True)

class Employee(dba.Model):
    extend_existing = False
    id = dba.Column(dba.Integer, primary_key=True)
    name = dba.Column(dba.String(100), nullable=False)
    position = dba.Column(dba.String(100))
    company_id = dba.Column(dba.Integer, dba.ForeignKey('company.id'), backref=db.backref('employees', lazy=True), nullable=False)

# Define the Question model
class Question(dba.Model):
    extend_existing = False
    id = dba.Column(dba.Integer, primary_key=True)
    text = dba.Column(dba.String(255), nullable=False)

# Define the Questionnaire model
class Questionnaire(dba.Model):
    extend_existing = False
    id = dba.Column(dba.Integer, primary_key=True)
    user_id = dba.Column(dba.Integer, dba.ForeignKey('user.id'), nullable=False)
    creation_date = dba.Column(dba.DateTime, default=datetime.utcnow, nullable=False)
    last_update_date = dba.Column(dba.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = dba.Column(dba.String(20), default='created', nullable=False)  # created, pending, submitted
    # Other questionnaire fields...

    # Define the relationship with questions
    questions = dba.relationship('Question', secondary='questionnaire_questions', lazy='dynamic')

# Define the association table for the many-to-many relationship
questionnaire_questions = dba.Table(
    'questionnaire_questions',
    dba.Column('questionnaire_id', dba.Integer, dba.ForeignKey('questionnaire.id')),
    dba.Column('question_id', dba.Integer, dba.ForeignKey('question.id'))
)


class Table(dba.Model):
    extend_existing = True
    id = dba.Column(dba.Integer, primary_key=True)
    name = dba.Column(dba.String(255), nullable=False)
    description = dba.Column(dba.Text)
    user_id = dba.Column(dba.Integer, dba.ForeignKey('user.id'), nullable=False)

    # Define additional columns as needed
    column1 = dba.Column(dba.String(255), nullable=True)
    column2 = dba.Column(dba.Integer, nullable=True)
    # Add more columns as necessary

    creation_date = dba.Column(dba.DateTime, default=datetime.utcnow, nullable=False)
    # Add more columns as necessary

    # Define relationships if needed
    user = dba.relationship('User', backref=dba.backref('tables', lazy=True))

    def __repr__(self):
        return f"<Table {self.name} - {self.user.username}>"


if __name__ == '__main__':
    with appa.app_context():
        print('Creating the database tables')
        dba.create_all()
        print('Done')

        for i in range(10):
            # Example usage
            new_record = Table(
                name="Tabella 1",
                description="Description of table 1",
                user_id=9,
                column1=f"ABC {i}",
                column2=i * 14 + i ** 3,
                creation_date=datetime.strptime("24/12/2023", "%d/%m/%Y")
            )

            # Add the new record to the session and commit the changes
            dba.session.add(new_record)

        dba.session.commit()

    # Run the Flask appa only if the script is the main entry point
    appa.run(debug=True)

