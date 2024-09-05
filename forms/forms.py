
# Create a dynamic form based on questions
from db import db

from datetime import datetime
from wtforms import (DecimalField, StringField, BooleanField, FloatField, FileField, DateField, TimeField,
                    DateTimeLocalField, ValidationError,
                     SelectField, SelectMultipleField, FloatField, IntegerField, IntegerField,
                     DateTimeField, FileField,
                     Form, FormField, IntegerField, HiddenField, DateTimeField, MonthField,
                     TimeField, FileField, TextAreaField, PasswordField, SubmitField, EmailField,
                     RadioField, validators
                     )
# Import ColorField
from wtforms.fields import ColorField  # Correct import
from wtforms import FieldList

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, BooleanField, SubmitField, SelectField, TextAreaField, FieldList
from wtforms.validators import DataRequired

from flask_admin.form import rules
from flask_admin.form.rules import FieldSet
from wtforms.validators import (DataRequired, Length, Email, EqualTo, Optional, NumberRange, Regexp, URL,
                                ValidationError)
import re
from datetime import datetime

from wtforms_sqlalchemy.fields import QuerySelectField
from models.user import (Users, Company, Event, Subject, Step, Workflow, StepBaseData, WorkflowSteps, BaseData, BaseDataInline,
                         Question, Questionnaire, QuestionnaireQuestions, Status, LegalDocument,
                         Area, Subarea, Lexic, Workflow, Interval, Step,
                         Contract, ContractParty, ContractTerm, ContractDocument,
                         ContractStatusHistory, ContractArticle, Party
                         )
from flask_admin.model.form import InlineFormAdmin
from enum import Enum
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_babel import lazy_gettext as _  # Import lazy_gettext and alias it as _
# from werkzeug.security import generate_password_hash, check_password_hash



class TeamForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Create Team')

class ManagePlanForm(FlaskForm):
    id = HiddenField()
    name = StringField('Plan Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    billing_cycle = SelectField('Billing Cycle', choices=[('none', 'None'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly'), ('one-off', 'One-off')], validators=[DataRequired()])
    submit = SubmitField('Save Plan')


class ManageProductForm(FlaskForm):
    id = HiddenField()
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    stripe_product_id = StringField('Stripe Product ID', validators=[DataRequired()])
    stripe_price_id = StringField('Stripe Price ID', validators=[DataRequired()])
    price = IntegerField('Price (in cents)', validators=[DataRequired()])
    currency = StringField('Currency', validators=[DataRequired()])
    path = StringField('Product Path', validators=[DataRequired()])
    icon = StringField('Product Icon (URL or internal path)', validators=[URL(require_tld=False)])
    submit = SubmitField('Save Product')

class AddPlanToCartForm(FlaskForm):
    submit = SubmitField('Add to Cart')

class UpdateCartItemForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Update')

class AddProductToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Cart')

class PlanProductsForm(FlaskForm):
    id = HiddenField()
    plan_id = SelectField('Plan', coerce=int, validators=[DataRequired()])
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()], choices=[], render_kw={'multiple': False})
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class SubscriptionForm(FlaskForm):
    plan_id = HiddenField('Plan ID', validators=[DataRequired()])
    additional_products = HiddenField('Additional Products')
    submit = SubmitField('Subscribe')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=24)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=128)])
    mid_name = StringField('Middle Name', validators=[Optional(), Length(max=128)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=128)])
    title = StringField('Title', validators=[DataRequired(), Length(max=12)])
    address = StringField('Address', validators=[DataRequired(), Length(max=128)])
    address1 = StringField('Address 1', validators=[Optional(), Length(max=128)])
    city = StringField('City', validators=[DataRequired(), Length(max=128)])
    province = StringField('Province', validators=[DataRequired(), Length(max=64)])
    region = StringField('Region', validators=[DataRequired(), Length(max=64)])
    zip_code = StringField('Zip Code', validators=[Optional(), Length(max=24)])
    country = StringField('Country', validators=[DataRequired(), Length(max=64)])
    tax_code = StringField('Tax Code', validators=[Optional(), Length(max=128)])
    mobile_phone = StringField('Mobile Phone', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ])
    work_phone = StringField('Work Phone', validators=[
        Optional(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ])
    submit = SubmitField('Update')


class ColorField(StringField):
    pass  # Define or import ColorField appropriately


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    start = DateTimeField('Start', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    end = DateTimeField('End', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    description = TextAreaField('Description')
    all_day = BooleanField('All Day')
    location = StringField('Location')
    color = ColorField('Color')  # Ensure ColorField is defined or imported
    recurrence = SelectField('Recurrence', choices=[
        ('', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
    ])
    recurrence_end = DateField('Recurrence End', format='%Y-%m-%d')
    submit = SubmitField('Submit')

    def validate_end(self, end):
        if self.start.data >= end.data:
            raise ValidationError('End time must be after start time.')

    def validate_recurrence_end(self, recurrence_end):
        if self.recurrence.data not in [None, ''] and self.recurrence_end.data:
            end_date = self.end.data.date() if isinstance(self.end.data, datetime) else self.end.data
            if end_date >= self.recurrence_end.data:
                raise ValidationError('Recurrence end date must be after event end date.')


class TicketForm(FlaskForm):
    subject = SelectField('Subject', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ResponseForm(FlaskForm):
    response = TextAreaField('Response', validators=[DataRequired()])
    status = SelectField('Status', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class BaseDataInlineModelForm(InlineFormAdmin):
    form_columns = ['name', 'type', 'value', 'record_type']
    form_label = 'Vendor Data'
    form_extra_fields = {
        'id': HiddenField('ID'),
        'record_type': HiddenField('Record Type')
    }

    form_edit_rules = ('id', rules.FieldSet(('name', 'type', 'value', 'record_type'), 'Vendor Data'))

    def postprocess_form(self, form_class):
        form_class.id = HiddenField()
        form_class.record_type = HiddenField(default='pre-complaint')  # Set the default value directly here

        # Query the Subject table
        subjects = db.session.query(Subject).filter_by(tier_1='Oggetto').order_by(Subject.tier_2, Subject.tier_3).all()

        # Create choices for the SelectField
        subject_choices = [(subject.id, f"{subject.tier_2} {subject.tier_3} - {subject.name}") for subject in subjects]

        # Add the SelectField to the form_class
        form_class.type = SelectField('Type', choices=subject_choices)

        return form_class

class ContractArticleInlineModelForm(InlineFormAdmin):
    form_columns = ['article_title', 'article_body', 'article_order']
    form_label = 'Contract Article'

    def on_model_change(self, form, model, is_created):
        # Ensure article_order is set to 0 if not provided
        if form.article_order.data == '':
            model.article_order = 0
        else:
            model.article_order = int(form.article_order.data)

        super(ContractArticleInlineModelForm, self).on_model_change(form, model, is_created)


class ContractArticleInlineModelForm222(InlineFormAdmin):
    form_columns = ['article_title', 'article_body', 'article_order', 'parent_article']
    form_label = 'Contract Article'

    form_extra_fields = {
        'article_id': HiddenField('Article ID'),
        'article_order': HiddenField('Order')
    }

    form_edit_rules = (
        'article_id',
        rules.FieldSet(
            ('article_title', 'article_body', 'article_order', 'parent_article'),
            'Contract Article Details'
        )
    )

    def postprocess_form(self, form_class):
        form_class.article_id = HiddenField()
        form_class.article_order = HiddenField()

        if hasattr(form_class, 'contract_id'):
            contract_id = form_class.contract_id.data
            parent_articles = db.session.query(ContractArticle).filter_by(contract_id=contract_id).order_by(
                ContractArticle.article_order).all()
        else:
            parent_articles = []

        parent_choices = [(str(article.article_id), f"{article.article_order} - {article.article_title}") for article in parent_articles]
        parent_choices.insert(0, ('', 'No Parent'))  # Add 'No Parent' option

        form_class.parent_article = SelectField('Parent Article', choices=parent_choices, default='', validators=[Optional()])

        return form_class

    def on_form_prefill(self, form, id):
        if form.parent_article.data:
            form.parent_article.data = str(form.parent_article.data.article_id)


class ContractArticleInlineModelForm333(InlineFormAdmin):
    form_columns = ['article_title', 'article_body', 'article_order', 'parent_article']
    form_label = 'Contract Article'

    form_extra_fields = {
        'article_id': HiddenField('Article ID'),
        'article_order': HiddenField('Order')
    }

    form_edit_rules = (
        'article_id',
        rules.FieldSet(
            ('article_title', 'article_body', 'article_order', 'parent_article'),
            'Contract Article Details'
        )
    )

    def postprocess_form(self, form_class):
        form_class.article_id = HiddenField()
        form_class.article_order = HiddenField()

        if hasattr(form_class, 'contract_id'):
            contract_id = form_class.contract_id.data
            parent_articles = db.session.query(ContractArticle).filter_by(contract_id=contract_id).order_by(
                ContractArticle.article_order).all()
        else:
            parent_articles = []

        parent_choices = [(None, 'No Parent')] + [
            (str(article.article_id), f"{article.article_order} - {article.article_title}") for article in parent_articles]

        form_class.parent_article = SelectField('Parent Article', choices=parent_choices, default=None,
                                                validators=[Optional()])

        return form_class

    def on_form_prefill(self, form, id):
        if form.parent_article.data:
            form.parent_article.data = str(form.parent_article.data.article_id)


class ForgotPasswordForm(FlaskForm):
    email = EmailField(_('Email Address'), validators=[DataRequired(), Email()])
    # Other form fields, if needed
    submit = SubmitField(_('Reset Password'))

class ResetPasswordForm101(FlaskForm):
    password = PasswordField(_('New Password'), validators=[DataRequired()])
    confirm_password = PasswordField(_('Confirm New Password'),
                                     validators=[DataRequired(), EqualTo('password', message=_('Passwords must match'))])
    submit = SubmitField(_('Reset Password'))


class CustomSubjectAjaxLoader(QueryAjaxModelLoader):
    def __init__(self, name, session, model=None, fields=None, filter_criteria=None):
        super(CustomSubjectAjaxLoader, self).__init__(name, session, model=model, fields=fields)
        self.filter_criteria = filter_criteria

    def get_list(self, term, offset=0, limit=10):
        # Start with a basic query
        query = self.session.query(self.model)

        # Apply the filtering criteria if provided
        if self.filter_criteria:
            query = query.filter(self.filter_criteria)

        # Apply the term-based search if needed
        if term:
            query = query.filter(self.model.name.ilike(f"%{term}%"))

        # Apply offset and limit to the query
        query = query.offset(offset).limit(limit)

        # Execute the query and return the results
        return query.all()



class StepBaseDataInlineForm(InlineFormAdmin):

    def __init__(self, model, form_data=None, **kwargs):
        super(StepBaseDataInlineForm, self).__init__(model, **kwargs)
        self.form_data = form_data  # Store the form data

    form_columns = ('id', 'workflow', 'step', 'status', 'deadline_date', 'auto_move')
    column_labels = {'id': 'ID', 'workflow': 'Workflow the document is to be assigned to', 'step': 'Step within the Workflow',
    'status': 'Initial Status', 'deadline_date': 'Deadline of the Step', 'auto_move': 'Automatic transition to next Step'}
    # Define the primary key field
    id = IntegerField('ID')  # Assuming the primary key is an IntegerField
    # Define form fields as SelectFields
    workflow_id = SelectField('Workflow', coerce=int)  # Assuming 'workflow_id' is the field for selecting workflows
    step_id = SelectField('Step', coerce=int)  # Assuming 'step_id' is the field for selecting steps
    status_id = SelectField('Status', coerce=int)  # Assuming 'status_id' is the field for selecting statuses

    @property
    def form(self):
        form = super().form
        # Print the values of the form fields
        for field in form:
            print(f"Field: {field.name}, Value: {field.data}")
        return form

    # Method to populate form with data from StepBaseData instance
    def populate_form(self, form):
        super().populate_form(form)

        # Get all StepBaseData instances related to the current main model

        step_base_data_list = self.get_query(StepBaseData).filter_by(main_model_id=form.object_data.id).all()
        # Retrieve options for dropdowns

        workflow_options = [(workflow.id, workflow.name) for workflow in Workflow.query.all()]
        step_options = [(step.id, step.name) for step in Step.query.all()]
        status_options = [(status.id, status.name) for status in Status.query.all()]

        # Update dropdown choices based on StepBaseData instances
        if step_base_data_list:
            step_ids = [data.step_id for data in step_base_data_list]
            workflow_ids = [data.workflow_id for data in step_base_data_list]
            status_ids = [data.status_id for data in step_base_data_list]

            # Filter out unique IDs and retrieve corresponding names

            workflow_options = [(workflow.id, workflow.name) for workflow in Workflow.query.filter(Workflow.id.in_(workflow_ids)).all()]
            step_options = [(step.id, step.name) for step in Step.query.filter(Step.id.in_(step_ids)).all()]
            status_options = [(status.id, status.name) for status in Status.query.filter(Status.id.in_(status_ids)).all()]

        # Populate dropdowns and other fields

        form.workflow_id.choices = workflow_options
        form.step_id.choices = step_options
        form.status_id.choices = status_options

        # Populate other fields with data from the first StepBaseData instance (if any)
        if step_base_data_list:
            first_data = step_base_data_list[0]
            form.deadline_date.data = first_data.deadline_date
            form.auto_move.data = first_data.auto_move
            form.open_action.data = 1  # Assuming this is a predefined value
        else:
            # Populate with default or null values if no related instances
            form.deadline_date.data = None
            form.auto_move.data = None
            form.open_action.data = None



class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')])
    title = SelectField('Title', choices=[('', ''), ('Mr.', 'Mr.'), ('Mrs.', 'Mrs.')], validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    mid_name = StringField('Middle Name')
    last_name = StringField('Last Name', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    region = StringField('Region', validators=[DataRequired()])
    province = StringField('Province')
    zip_code = StringField('Zip Code')
    city = StringField('City')
    street = StringField('Street')
    address = StringField('Address', validators=[DataRequired()])
    address1 = StringField('Address 1')
    phone_prefix = StringField('Phone Prefix', validators=[DataRequired()])
    mobile_phone = StringField('Mobile Phone', validators=[DataRequired()])
    work_phone = StringField('Work Phone')
    tax_code = StringField('Tax Code')
    terms_accepted = BooleanField('I accept the Terms of Use', validators=[DataRequired()])
    privacy_policy_accepted = BooleanField('I accept the Privacy Policy', validators=[DataRequired()])

    submit = SubmitField('Sign Up')

class InlineSurveyForm(InlineFormAdmin):
    def __init__(self, model=None, form_data=None, **kwargs):
        super(InlineSurveyForm, self).__init__(model, **kwargs)
        self.form_data = form_data  # Store the form data
        # Set the model attribute
        self.model = model

    form_columns = (
        'answer_text', 'answer_comment', 'answer_conclusion',
        'answer_integer', 'answer_number',
        'timestamp'
    )

    column_labels = {
        'answer_text': 'Text',
        'answer_comment': 'Comment',
        'answer_conclusion': 'Conclusion',
        'answer_integer': 'Integer',
        'answer_number': 'Number',
        'timestamp': 'Timestamp'
    }

    def populate_form(self, form):
        super().populate_form(form)

        # Populate form fields with data from the Answer model
        answer_data = self.get_query(self.model).filter_by(question_id=form.object_data.id).first()

        if answer_data:
            form.answer_text.data = answer_data.answer_text
            form.answer_comment.data = answer_data.answer_comment
            form.answer_conclusion.data = answer_data.answer_conclusion
            form.answer_integer.data = answer_data.answer_integer
            form.answer_number.data = answer_data.answer_number
            form.timestamp.data = answer_data.timestamp
        else:
            # Populate with default or null values if no answer data found
            form.answer_text.data = "Default answer"
            form.answer_comment.data = "Default comment"
            form.answer_conclusion.data = "Conclusion"
            form.answer_integer.data = 0
            form.answer_number.data = 0.0
            form.timestamp.data = datetime.now()

class QuestionnaireForm(FlaskForm):
    inline_answers = FieldList(InlineSurveyForm)


class CustomBaseDataForm(FlaskForm):
    user_id = QuerySelectField('Users', query_factory=lambda: Users.query.all(), get_label='username', allow_blank=True, validators=[Optional()])
    company_id = QuerySelectField('Company', query_factory=lambda: Company.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    interval_id = QuerySelectField('Interval', query_factory=lambda: Interval.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    interval_ord = IntegerField('Interval Ord', validators=[Optional()])
    status_id = QuerySelectField('Status', query_factory=lambda: Status.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    subject_id = QuerySelectField('Subject', query_factory=lambda: Subject.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    legal_document_id = QuerySelectField('Legal Document', query_factory=lambda: LegalDocument.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    record_type = StringField('Record Type', validators=[Optional()])
    data_type = StringField('Data Type', validators=[Optional()])
    created_on = DateTimeField('Created On', validators=[Optional()])
    updated_on = DateTimeField('Updated On', validators=[Optional()])
    deadline = DateTimeField('Deadline', validators=[Optional()])
    created_by = StringField('Created By', validators=[Optional()])
    area_id = QuerySelectField('Area', query_factory=lambda: Area.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    subarea_id = QuerySelectField('Subarea', query_factory=lambda: Subarea.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    lexic_id = QuerySelectField('Lexic', query_factory=lambda: Lexic.query.all(), get_label='name', allow_blank=True, validators=[Optional()])
    number_of_doc = StringField('Number of Document', validators=[Optional()])
    date_of_doc = DateTimeField('Date of Document', validators=[Optional()])
    fc1 = StringField('FC1', validators=[Optional()])
    fc2 = StringField('FC2', validators=[Optional()])
    fc3 = StringField('FC3', validators=[Optional()])
    fc4 = StringField('FC4', validators=[Optional()])
    fc5 = StringField('FC5', validators=[Optional()])
    fc6 = StringField('FC6', validators=[Optional()])
    ft1 = StringField('FT1', validators=[Optional()])
    fb1 = FileField('FB1', validators=[Optional()])
    fi0 = IntegerField('FI0', validators=[Optional()])
    fi1 = IntegerField('FI1', validators=[Optional()])
    fi2 = IntegerField('FI2', validators=[Optional()])
    fi3 = IntegerField('FI3', validators=[Optional()])
    fi4 = IntegerField('FI4', validators=[Optional()])
    fi5 = IntegerField('FI5', validators=[Optional()])
    fi6 = IntegerField('FI6', validators=[Optional()])
    fi7 = IntegerField('FI7', validators=[Optional()])
    fi8 = IntegerField('FI8', validators=[Optional()])
    fi9 = IntegerField('FI9', validators=[Optional()])
    fi10 = IntegerField('FI10', validators=[Optional()])
    fi11 = IntegerField('FI11', validators=[Optional()])
    fi12 = IntegerField('FI12', validators=[Optional()])
    fi13 = IntegerField('FI13', validators=[Optional()])
    fi14 = IntegerField('FI14', validators=[Optional()])
    fi15 = IntegerField('FI15', validators=[Optional()])
    fi16 = IntegerField('FI16', validators=[Optional()])
    fn0 = StringField('FN0', validators=[Optional()])
    fn1 = StringField('FN1', validators=[Optional()])
    fn2 = StringField('FN2', validators=[Optional()])
    fn3 = StringField('FN3', validators=[Optional()])
    fn4 = StringField('FN4', validators=[Optional()])
    fn5 = StringField('FN5', validators=[Optional()])
    fn6 = StringField('FN6', validators=[Optional()])
    fn7 = StringField('FN7', validators=[Optional()])
    fn8 = StringField('FN8', validators=[Optional()])
    fn9 = StringField('FN9', validators=[Optional()])
    file_path = StringField('File Path', validators=[Optional()])
    no_action = IntegerField('No Action', validators=[Optional()])


# Define the UserForm class
class UserForm(FlaskForm):
    existing_user = SelectField('Select Existing User', coerce=int)
    user_id = HiddenField('User ID')
    username = StringField('Username', validators=[DataRequired()])
    title = StringField('Title')
    first_name = StringField('First Name')
    mid_name = StringField('Mid Name')
    last_name = StringField('Last Name')
    address = StringField('Address')
    address1 = StringField('Address1')
    city = StringField('City')
    province = StringField('Province')
    region = StringField('Region')
    zip_code = StringField('Zip Code')
    country = StringField('Country')
    tax_code = StringField('Tax code')
    mobile_phone = StringField('Mobile phone')
    work_phone = StringField('Work phone')
    registration_date = StringField('Last Update')
    add = SubmitField('Add', render_kw={'class': 'btn btn-primary'})
    edit = SubmitField('Edit', render_kw={'class': 'btn btn-warning'})
    cancel = SubmitField('Cancel', render_kw={'class': 'btn btn-secondary'})
    delete = SubmitField('Delete', render_kw={'class': 'btn btn-danger'})

    '''def validate(self):
        # Skip validation for certain fields when the delete action is detected
        if self.form_action.data == 'delete':
            for field_name in ['username', 'user_id', 'id', 'first_name', 'last_name', 'email', 'password', 'title']:
                field = getattr(self, field_name)
                try:
                    field.validators.remove(StopValidation)
                except ValueError:
                    pass

        # Perform the default validation
        return super().validate()'''

'''
# Validator example
def not_admin(form, field):
   if field.data.lower() == "admin":
       raise ValidationError("The value 'admin' is not allowed.")

# usage example: in the Form,
   name = StringField('Name', [validators.InputRequired(), not_admin])
'''


'''
Total Validator Example

class MyForm(FlaskForm):
   number1 = IntegerField('Number 1', [validators.InputRequired()])
   number2 = IntegerField('Number 2', [validators.InputRequired()])
   number3 = IntegerField('Number 3', [validators.InputRequired()])
   total = IntegerField('Total', [validators.InputRequired()])

   def validate_total(form, field):
       expected_total = form.number1.data + form.number2.data + form.number3.data
       if field.data != expected_total:
           raise ValidationError(f"Total must be the sum of the numbers ({expected_total}).")

# Example usage in Flask-Admin view is similar to the previous example.



from wtforms import Form, IntegerField, validators
from wtforms.validators import ValidationError

class MyForm(Form):
    number1 = IntegerField('Number 1', [validators.InputRequired()])
    number2 = IntegerField('Number 2', [validators.InputRequired()])
    number3 = IntegerField('Number 3', [validators.InputRequired()])
    total = IntegerField('Total', [validators.InputRequired()])

    def validate_total(form, field):
        expected_total = form.number1.data + form.number2.data + form.number3.data
        if field.data != expected_total:
            raise ValidationError(f"Total must be the sum of the numbers ({expected_total}).")

# Usage
form = MyForm()
form.number1.data = 2
form.number2.data = 3
form.number3.data = 4
form.total.data = 9

# Validate the form
if form.validate():
    print("Form is valid")
else:
    print("Form is invalid:", form.errors)

# Output:
# Form is valid

'''


class DynamicForm(FlaskForm):
    answer = SelectField('Answer', choices=[], coerce=int)  # Use coerce=int for integer values
    text_answer = StringField('String Answer')
    file_attachment = FileField('File Attachment')
    submit = SubmitField('Submit')



class CustomFileLoaderForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(CustomFileLoaderForm, self).__init__(*args, **kwargs)
        # Populate choices for fields
        self.document_type.choices = [(item.id, item.name) for item in Subject.query.filter_by(tier_1='Legale').order_by('name').all()]
        self.current_year = datetime.now().year
        self.document_year.choices = [(str(year), str(year)) for year in range(self.current_year - 10, self.current_year + 101)]
        self.workflow.choices = [(item.id, item.name) for item in Workflow.query.order_by('name').all()]
        self.step.choices = [(item.id, item.name) for item in Step.query.all()]

    id = HiddenField('id')
    area_id = HiddenField('area_id')
    subarea_id = HiddenField('subarea_id')
    user_id = HiddenField('user_id')
    company_id = HiddenField('company_id')

    lexic_id = 7 # ---
    status_id = 1

    document_type = SelectField('Document Type', coerce=int)
    document_number = StringField('Document Number')
    document_date = DateField('Date of document', format='%Y-%m-%d', validators=[validators.DataRequired()])
    document_title = StringField('Title/Subject')
    document_origin = StringField('Origin')
    document_receiver = StringField('Receiver')
    document_year = SelectField('Year of reference',  default=datetime.now().year,
                                coerce=int)
    document_reference_interval = SelectField('Period type', choices=[('1', 'Year'), ('2', 'Semester'),
                                            ('3', 'Quadrimester'), ('4', 'Quarter'), ('6', 'Bimester'),
                                            ('12', 'Month'), ('52', 'Week')],
                                              coerce=int)
    document_interval = SelectField('Period of reference', choices=[('1', 'First'), ('2', 'Second'), ('3', '3rd'),
                                            ('4', '4th'), ('5', '5th'), ('6', '6th'), ('7', '7th'), ('8', '8th'),
                                            ('9', '9th'), ('10', '10th'), ('11', '11th'), ('12', '12th')],
                                    coerce=int)

    file_upload = FileField('Attach File')
    no_attachment = BooleanField('Confirm there are no documents to be attached')

    workflow = SelectField('Document Workflow', coerce=int)
    step = SelectField('Workflow Starting Phase', coerce=int)
    deadline_date = DateField('Deadline of the Phase', format='%Y-%m-%d', validators=[validators.DataRequired()])
    auto_move = BooleanField('Automatic Transition to Next Phase')

    reminder_units = SelectField('Send reminder before deadline', choices=[('0', 'No reminder'),
                                            ('1', '1'), ('2', '2'), ('3', '3'), ('5', '5'), ('6', '6'),
                                            ('7', '7'), ('9', '9'), ('10', '10'), ('15', '15'),
                                            ('30', '30')],
                                 coerce=int)
    reminder_unit = SelectField('Reminder unit', choices=[('1', 'hour'), ('2', 'day'), ('3', 'week'),
                                            ('4', 'month')])

    def save_file(self, upload_folder):
        uploaded_file = self.file_upload.data
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(upload_folder, filename)
            uploaded_file.save(filepath)
            # Assuming file_path is an attribute of the form
            self.file_path.data = filepath

class UserDocumentsForm(FlaskForm):
    document_selector = SelectField('Select Document', validators=[DataRequired()])
    next_step = StringField('Next Step')  # Define next_step attribute here if needed

    submit = SubmitField('Go to Workflow')

    def __init__(self, documents=None, *args, **kwargs):
        super(UserDocumentsForm, self).__init__(*args, **kwargs)
        self.documents = documents
        # Additional initialization code if needed

class TwoFactorForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired()])
    submit = SubmitField('Verify')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Additional fields
    first_name = StringField('First Name', validators=[Length(max=128)])
    mid_name = StringField('Middle Name', validators=[Length(max=128)])
    last_name = StringField('Last Name')
    address = StringField('Address', validators=[Length(max=128)])
    address1 = StringField('Address 1', validators=[Length(max=128)])
    city = StringField('City', validators=[Length(max=128)])
    province = StringField('Province', validators=[Length(max=64)])
    region = StringField('Region', validators=[Length(max=128)])
    zip_code = StringField('Zip Code', validators=[Length(max=24)])
    country = StringField('Country', validators=[Length(max=64)])
    tax_code = StringField('Tax Code', validators=[Length(max=128)])
    mobile_phone = StringField('Mobile Phone')
    work_phone = StringField('Work Phone', validators=[Length(max=128)])

    submit = SubmitField('Sign Up')


class UserRoleForm(FlaskForm):
    user = SelectField('User')
    role = SelectField('Role')
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')

class WorkflowStepForm(FlaskForm):
    workflow = SelectField('Workflow')
    step = SelectField('Step')
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


'''
class WorkflowBaseDataForm(FlaskForm):
    workflow = SelectField('Workflow')
    base_data = SelectField('BaseData')
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')
'''

'''
OLD
class WorkflowBaseDataForm(FlaskForm):
    workflow = SelectField('Select Workflow', validators=[DataRequired()])
    base_data = SelectField('Select Document', validators=[DataRequired()])
    hidden_data = HiddenField()  # To store existing workflow_base_data IDs
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')
    insert_record = SubmitField('Insert new record')

'''

# NEW:
class WorkflowBaseDataForm(FlaskForm):
    workflow = SelectField('Select Workflow', validators=[DataRequired()], id='workflow_base_data_id')
    base_data = SelectField('Select Document', validators=[DataRequired()], id='base_data_id')
    hidden_data = HiddenField('hidden_data', id='hidden_data')  # To store existing workflow_base_data IDs
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')
    insert_record = SubmitField('Insert new record')



class BaseDataWorkflowStepForm(FlaskForm):
    base_data = SelectField('BaseData')
    workflow = SelectField('Workflow')
    step = SelectField('Step')
    auto_move = BooleanField('Auto Move')
    #hidden_data = HiddenField()  # To store existing workflow_base_data IDs
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')
    remove = SubmitField('Remove')  # New field for removing entries
    new_record = SubmitField('New Record')


class CompanyUserForm(FlaskForm):
    company = SelectField('Company')
    user = SelectField('User')
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class QuestionnaireCompanyForm(FlaskForm):
    questionnaire = SelectField('Questionnaire')
    company = SelectField('Company')
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class QuestionnaireQuestionForm(FlaskForm):
    questionnaire = SelectField('Questionnaire')
    question = SelectField('Question')
    add = SubmitField('Add')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class CompanyForm(FlaskForm):
    existing_company = SelectField('Select Existing Company', coerce=int)
    company_id = HiddenField('Company ID')
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    address = StringField('Address')
    phone_number = StringField('Phone Number')
    email = StringField('Email')
    website = StringField('Website')
    tax_code = StringField('Tax Code')
    add = SubmitField('Add', render_kw={'class': 'btn btn-primary'})
    edit = SubmitField('Edit', render_kw={'class': 'btn btn-warning'})
    cancel = SubmitField('Cancel', render_kw={'class': 'btn btn-secondary'})
    delete = SubmitField('Delete', render_kw={'class': 'btn btn-danger'})


class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')])
    company = SelectField('Company', coerce=int)



class QuestionnaireForm(FlaskForm):
    submit = SubmitField('Submit')


from wtforms import StringField, IntegerField, SelectField

class DynamicForm(Form):
    pass


# TODO unused?
def create_dynamic_form_from_data(answers_data):
    class DynamicForm(Form):
        pass

    for answer in answers_data:
        field_name = f'question_{answer.question_id}_field'

        try:
            # Attempt to parse answer_type as JSON
            answer_type = json.loads(answer.question.answer_type)
        except (ValueError, TypeError):
            # If parsing fails, use it as a regular string
            answer_type = answer.question.answer_type

        if isinstance(answer_type, dict):
            # Handle the JSON object as needed
            # For example, if answer_type contains 'type' and 'default' keys
            field_type = answer_type.get('type', 'text')
            default_value = answer_type.get('default', '')

            if field_type == 'text':
                setattr(DynamicForm, field_name, StringField(label=answer.question.text, default=default_value))
            elif field_type == 'boolean':
                setattr(DynamicForm, field_name,
                        BooleanField(label=answer.question.text, default=default_value.lower() == 'yes'))
            elif field_type == 'float':
                setattr(DynamicForm, field_name, FloatField(label=answer.question.text, default=float(
                    default_value) if default_value else None))
            elif field_type == 'file':
                # Add file handling logic if needed
                setattr(DynamicForm, field_name, FileField(label=answer.question.text))
            elif field_type == 'date':
                default_value = datetime.strptime(default_value, '%Y-%m-%d') if default_value else None
                setattr(DynamicForm, field_name, DateField(label=answer.question.text, default=default_value))
            elif field_type == 'time':
                default_value = datetime.strptime(default_value, '%H:%M:%S') if default_value else None
                setattr(DynamicForm, field_name, DateField(label=answer.question.text, default=default_value))
            elif field_type == 'yes_no':
                setattr(DynamicForm, field_name,
                        SelectField(label=answer.question.text, choices=[('yes', 'Yes'), ('no', 'No')],
                                    default=default_value))
            elif field_type == 'integer':
                setattr(DynamicForm, field_name,
                        IntegerField(label=answer.question.text, default=int(default_value) if default_value else None))
            elif field_type == 'float':
                setattr(DynamicForm, field_name,
                        FloatField(label=answer.question.text, default=float(default_value) if default_value else None))
            else:
                setattr(DynamicForm, field_name, StringField(label=answer.question.text, default=default_value))
        else:
            # Handle as a regular string if not JSON
            if answer_type == 'text':
                setattr(DynamicForm, field_name, StringField(label=answer.question.text, default=answer.answer_text))
            elif answer_type == 'boolean':
                setattr(DynamicForm, field_name,
                        BooleanField(label=answer.question.text, default=answer.answer_text.lower() == 'yes'))
            elif answer_type == 'float':
                setattr(DynamicForm, field_name, FloatField(label=answer.question.text, default=float(
                    answer.answer_text) if answer.answer_text else None))
            elif answer_type == 'file':
                # Add file handling logic if needed
                setattr(DynamicForm, field_name, FileField(label=answer.question.text))
            elif answer_type == 'date':
                default_value = datetime.strptime(answer.answer_text, '%Y-%m-%d') if answer.answer_text else None
                setattr(DynamicForm, field_name, DateField(label=answer.question.text, default=default_value))
            elif answer_type == 'time':
                default_value = datetime.strptime(answer.answer_text, '%H:%M:%S') if answer.answer_text else None
                setattr(DynamicForm, field_name, DateField(label=answer.question.text, default=default_value))
            elif answer_type == 'yes_no':
                setattr(DynamicForm, field_name,
                        SelectField(label=answer.question.text, choices=[('yes', 'Yes'), ('no', 'No')],
                                    default=answer.answer_text))
            elif answer_type == 'integer':
                setattr(DynamicForm, field_name, IntegerField(label=answer.question.text, default=int(
                    answer.answer_text) if answer.answer_text else None))
            elif answer_type == 'float':
                setattr(DynamicForm, field_name, FloatField(label=answer.question.text, default=float(
                    answer.answer_text) if answer.answer_text else None))
            else:
                setattr(DynamicForm, field_name, StringField(label=answer.question.text, default=answer.answer_text))

    return DynamicForm()


def create_dynamic_form_from_data_sqlite(answers_data):
    class DynamicForm(Form):
        pass

    for answer in answers_data:
        field_name = f'question_{answer.question_id}_field'
        answer_type = answer.question.answer_type

        # Adjust the field types and attributes based on your Answer model
        if answer_type == 'text':
            setattr(DynamicForm, field_name, StringField(label=answer.question.text, default=answer.answer_text))
        elif answer_type == 'boolean':
            setattr(DynamicForm, field_name,
                    BooleanField(label=answer.question.text, default=answer.answer_text == 'yes'))
        elif answer_type == 'float':
            setattr(DynamicForm, field_name, FloatField(label=answer.question.text, default=float(
                answer.answer_text) if answer.answer_text else None))
        elif answer_type == 'file':
            # Add file handling logic if needed
            setattr(DynamicForm, field_name, FileField(label=answer.question.text))

        elif answer_type == 'date':
            default_value = datetime.strptime(answer.answer_text, '%Y-%m-%d') if answer.answer_text else None
            setattr(DynamicForm, field_name, DateField(label=answer.question.text, default=default_value))

        elif answer_type == 'time':
            default_value = datetime.strptime(answer.answer_text, '%hh:%mm:%ss') if answer.answer_text else None
            setattr(DynamicForm, field_name, DateField(label=answer.question.text, default=default_value))

        elif answer_type == 'yes_no':
            setattr(DynamicForm, field_name,
                    SelectField(label=answer.question.text, choices=[('yes', 'Yes'), ('no', 'No')],
                                default=answer.answer_text))
        # Add handling for other answer types as needed
        elif answer_type == 'integer':
            setattr(DynamicForm, field_name, IntegerField(label=answer.question.text, default=answer.answer_text))
        elif answer_type == 'float':
            setattr(DynamicForm, field_name, FloatField(label=answer.question.text, default=answer.answer_text))

        else:
            setattr(DynamicForm, field_name, StringField(label=answer.question.text, default=answer.answer_text))
    return DynamicForm()



class ComplexField(FieldList):
    def __init__(self, subfields=None, **kwargs):
        super().__init__(StringField(), **kwargs)
        if subfields:
            for label in subfields:
                self.append_entry(StringField(label=label))


def create_field(label, subfields=None):
    if label == 'complex':
        if subfields is not None:
            return ComplexField(subfields=subfields)
        else:
            print("subfields is None, cannot create ComplexField")
            # Handle the case when subfields is None, possibly fallback to StringField
            return StringField()
    elif label == 'text':
        return StringField()
    elif label == 'integer':
        return IntegerField()
    elif label == 'yes_no':
        return SelectField(choices=[(None, ''), ('yes', 'Yes'), ('no', 'No')])
    elif label == 'date':
        return DateField(format='%Y-%m-%d')
    elif label == 'boolean':
        return BooleanField()
    elif label == 'float':
        return FloatField()
    elif label == 'time':
        return TimeField()
    else:
        return StringField()  # Default to StringField if label is not recognized

class MySubForm(FlaskForm):
    def add_field(self, field_label, field_value):
        setattr(self, field_label, StringField(label=field_label, default=field_value))

    text_field_1 = StringField(label="Label for Text Field 1")
    file_field = FileField(label="File Upload")
    integer_field = IntegerField(label="Integer Input")
    text_field_2 = StringField(label="Label for Text Field 2")
    # Add other fields as needed based on your question types

from wtforms import Form, StringField, IntegerField, FileField, BooleanField, SelectField, DateField
import json
from typing import List, Dict, Any


class QuestionForm(FlaskForm):
    text = StringField('Question Text', validators=[DataRequired()])
    answer_fields = StringField('Answer Fields', validators=[DataRequired()])


class BaseSurveyForm(FlaskForm):
    questionnaire_id = HiddenField()
    company_id = HiddenField()
    user_id = HiddenField()
    action_id = HiddenField()
    save = SubmitField('Save')
    submit = SubmitField('Submit')


def extract_index_with_regex(field_name):
    match = re.match(r'^(\d+)_(\d+)_(\w+)$', field_name)
    if match:
        question_id, input_index, input_type = match.groups()
        return int(input_index)  # Convert to integer if necessary
    else:
        return 0
        # raise ValueError("Field name does not match the expected format")


def create_dynamic_form(form, data, company_id, horizontal=False):
    html_form = f"{form.hidden_tag()}"
    questions = data.get('questions', [])
    base_path = f"static/docs/company_files/company_id_{company_id}/{datetime.now().year}"

    for question in questions:
        html_form += generate_question_html(question, question['answer_fields'], base_path, horizontal)

    html_form += "<div class='button-group'>"
    html_form += "<button type='submit' class='btn btn-primary'>Save</button>"
    html_form += "<button type='submit' class='btn btn-primary'>Submit</button>"
    html_form += "</div>"

    return html_form


def generate_question_html(question, existing_answers, base_path, horizontal=False):
    html = f"<div class='question'><h6>{question['question_id']}. {question['text']}</h6>"
    answer_fields = json.loads(existing_answers) if isinstance(existing_answers, str) else existing_answers

    input_html = "<div class='answers horizontal'>" if horizontal else "<div class='answers vertical'>"
    for idx, answer_field in enumerate(answer_fields):
        try:
            input_type = answer_field['type']
            field_name = f"{question['id']}_{idx + 1}_{input_type}"
            existing_value = answer_field.get('value', '')
            input_width = answer_field.get('width')  # Extract width from the answer fields
            #print('field_name', field_name, 'existing_value', existing_value, 'input_width', input_width)
            order_number = idx + 1 if not horizontal else None
            input_html += generate_input_html(input_type, field_name, existing_value, base_path, horizontal, order_number, input_width)
        except:
            pass
    input_html += "</div>"
    html += input_html
    html += "</div><hr>"
    return html



def generate_input_html(input_type, field_name, existing_value, base_path, horizontal=False, order_number=None, width=None):
    css_class = "form-control"
    horizontal_class = "horizontal" if horizontal else "vertical"
    html = ""

    # Define a style for width if provided, and additional flexbox alignment
    width_style = f" style='width: {width}px; display: flex; align-items: center;'" if width else " style='display: flex; align-items: center;'"

    if order_number:
        html += f"<div class='input-group {horizontal_class}'{width_style}>"
        html += f"<label class='order-number'>{order_number}.</label> "
    else:
        order_number = extract_index_with_regex(field_name)
        html += f"<div class='{horizontal_class}'{width_style}>"

    # Define specific CSS classes for inputs to ensure alignment
    input_css_class = f"{css_class} form-input"  # Use form-input to handle specific styling

    # Control specific HTML generation
    if input_type == 'CB':
        checked = 'checked' if existing_value.lower() == 'on' else ''
        html += f"<input type='hidden' name='{field_name}' value='off'>"
        html += f"<input type='checkbox' class='form-check-input' id='{field_name}' name='{field_name}' value='on' {checked}>"
        label_text = f"A.{order_number}" if order_number else "A "  # Example label
        html += f"<label class='form-check-label' for='{field_name}'>{label_text}</label>"

    elif input_type == 'TLT':
        html += f"<textarea name='{field_name}' class='{input_css_class}'>{existing_value}</textarea>"

    elif input_type == 'NI(0-10)':
        options = ''.join(
            f"<option value='{num}' {'selected' if str(num) == existing_value else ''}>{num}</option>" for num in
            range(11))
        html += f"<select name='{field_name}' class='{input_css_class}'>{options}</select>"

        '''
        old version, where the file existence was checked IN THE DIRECTORY
        elif input_type == 'FILE':
            print('FILE type??', input_type)
            if existing_value:
                print('existing value, base path:', existing_value, base_path)
                file_path = url_for('static', filename=f"{base_path}/{existing_value}")
                html += f"Current File: <a href='{file_path}' target='_blank'>{existing_value}</a><br>"
    
            html += f"""
            <input type='file' name='{field_name}' class='{input_css_class}'>
            <label for='{field_name}'>Replace Existing File</label>
            <input type='checkbox' id='{field_name}_replace' name='replace_existing'>
            <br>
            """
        '''

    # new version, where the file existence is only checked in the DB field!
    elif input_type == 'FILE':
        # Check if existing_value is present in the database field
        if existing_value:
            # Don't check for file existence on disk (remove unnecessary print statements)

            html += f"Current File: {existing_value}<br>"  # Display the filename from the database

            # Replace logic using checkbox and database field
            html += f"""
                <input type='file' name='{field_name}' class='{input_css_class}'>
                <label for='{field_name}'>Replace Existing File</label>
                <input type='checkbox' id='{field_name}_replace' name='replace_existing' value='{existing_value}'>
                <br>
                """
        else:
            # No existing value, show standard upload field
            html += f"""
                <input type='file' name='{field_name}' class='{input_css_class}'>
                <label for='{field_name}'>Upload File</label>
                <br>
                """

    elif input_type == 'DD':
        html += f"<input type='date' name='{field_name}' value='{existing_value}' class='{input_css_class}'>"

    elif input_type == 'BYN':
        yes_selected = "selected" if "Yes" == existing_value else ""
        no_selected = "selected" if "No" == existing_value else ""
        html += f"<select name='{field_name}' class='{input_css_class}'>"
        html += f"<option value='Yes' {yes_selected}>Yes</option>"
        html += f"<option value='No' {no_selected}>No</option></select>"

    elif input_type == 'HML':
        high_selected = "selected" if existing_value == 'H' else ""
        medium_selected = "selected" if existing_value == 'M' else ""
        low_selected = "selected" if existing_value == 'L' else ""
        html += f"<select name='{field_name}' class='{input_css_class}'>"
        html += f"<option value='H' {high_selected}>High</option>"
        html += f"<option value='M' {medium_selected}>Medium</option>"
        html += f"<option value='L' {low_selected}>Low</option></select>"

    elif input_type == 'NUM':
        html += f"<input type='number' name='{field_name}' value='{existing_value}' step='0.01' class='{input_css_class}'>"

    elif input_type == 'INT':
        # Fetch data from the interval table
        intervals = db.session.query(Interval).all()  # Assuming Interval is your model for the interval table
        options = ''.join(
            f"<option value='{interval.id}' {'selected' if str(interval.id) == existing_value else ''}>{interval.description}</option>"
            for interval in intervals)
        html += f"<select name='{field_name}' class='{input_css_class}'>{options}</select>"

    else:
        html += f"<input type='text' name='{field_name}' value='{existing_value}' class='{input_css_class}' autocomplete='off'>"

    html += "</div><br>"
    return html



def generate_input_html222(input_type, field_name, existing_value, base_path, horizontal=False, order_number=None, width=None):
    css_class = "form-control"
    horizontal_class = "horizontal" if horizontal else "vertical"
    html = ""

    # Define a style for width if provided, and additional flexbox alignment
    width_style = f" style='width: {width}px; display: flex; align-items: center;'" if width else " style='display: flex; align-items: center;'"

    if order_number:
        html += f"<div class='input-group {horizontal_class}'{width_style}>"
        html += f"<label class='order-number'>{order_number}.</label> "
    else:
        order_number = extract_index_with_regex(field_name)
        html += f"<div class='{horizontal_class}'{width_style}>"

    # Define specific CSS classes for inputs to ensure alignment
    input_css_class = f"{css_class} form-input"  # Use form-input to handle specific styling

    # Control specific HTML generation
    if input_type == 'CB':
        checked = 'checked' if existing_value.lower() == 'on' else ''
        html += f"<input type='hidden' name='{field_name}' value='off'>"
        html += f"<input type='checkbox' class='form-check-input' id='{field_name}' name='{field_name}' value='on' {checked}>"
        label_text = f"A.{order_number}" if order_number else "A "  # Example label
        html += f"<label class='form-check-label' for='{field_name}'>{label_text}</label>"

    elif input_type == 'TLT':
        html += f"<textarea name='{field_name}' class='{input_css_class}'>{existing_value}</textarea>"

    elif input_type == 'NI(0-10)':
        options = ''.join(
            f"<option value='{num}' {'selected' if str(num) == existing_value else ''}>{num}</option>" for num in
            range(11))
        html += f"<select name='{field_name}' class='{input_css_class}'>{options}</select>"

    elif input_type == 'FILE':
        print('FILE type?', input_type)
        if existing_value:
            print('existing value', existing_value)
            file_path = url_for('static', filename=f"{base_path}/{existing_value}")
            html += f"Current File: <a href='{file_path}' target='_blank'>{existing_value}</a>"
        html += f"<input type='file' name='{field_name}' class='{input_css_class}'>"

    elif input_type == 'DD':
        html += f"<input type='date' name='{field_name}' value='{existing_value}' class='{input_css_class}'>"

    elif input_type == 'BYN':
        yes_selected = "selected" if "Yes" == existing_value else ""
        no_selected = "selected" if "No" == existing_value else ""
        html += f"<select name='{field_name}' class='{input_css_class}'>"
        html += f"<option value='Yes' {yes_selected}>Yes</option>"
        html += f"<option value='No' {no_selected}>No</option></select>"

    elif input_type == 'HML':
        high_selected = "selected" if existing_value == 'H' else ""
        medium_selected = "selected" if existing_value == 'M' else ""
        low_selected = "selected" if existing_value == 'L' else ""
        html += f"<select name='{field_name}' class='{input_css_class}'>"
        html += f"<option value='H' {high_selected}>High</option>"
        html += f"<option value='M' {medium_selected}>Medium</option>"
        html += f"<option value='L' {low_selected}>Low</option></select>"

    elif input_type == 'NUM':
        html += f"<input type='number' name='{field_name}' value='{existing_value}' step='0.01' class='{input_css_class}'>"

    else:
        html += f"<input type='text' name='{field_name}' value='{existing_value}' class='{input_css_class}' autocomplete='off'>"

    html += "</div><br>"
    return html




class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    title = StringField('Title', validators=[DataRequired(), Length(max=50)])
    first_name = StringField('First Name', validators=[Length(min=3, max=50)])
    mid_name = StringField('Middle Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(min=3, max=128)])
    address = StringField('Address', validators=[Length(max=128)])
    address1 = StringField('Address 1', validators=[Length(max=128)])
    city = StringField('City', validators=[Length(max=128)])
    province = StringField('Province', validators=[Length(max=64)])
    region = StringField('Region', validators=[Length(max=128)])
    zip_code = StringField('Zip Code', validators=[Length(max=24)])
    country = StringField('Country', validators=[Length(max=64)])
    tax_code = StringField('Tax Code', validators=[Length(max=128)])
    mobile_phone = StringField('Mobile Phone')
    work_phone = StringField('Work Phone', validators=[Length(max=128)])

    '''
    def validate_registration_date(self, field):
        if field.data:
            try:
                # Convert the string to a datetime object
                field.data = datetime.strptime(field.data, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                raise ValidationError('Invalid date format')
    '''


# TODO sistemare transition, forse deve avre solo base_data_id e poi da stato a stato, plus messaggio e scadenza?
class AuditLogForm(FlaskForm):
    action = StringField('Action', validators=[DataRequired(), Length(max=256)])
    details = TextAreaField('Details')
    user_id = SelectField('User', coerce=int)  # Assuming you want a user selection field
    company_id = SelectField('Company', coerce=int)  # Assuming you want a company selection field
    base_data_id = SelectField('Base Data', coerce=int)  # Assuming you want a base data selection field
    workflow_id = HiddenField('Workflow ID')  # Pre-populate this based on route context
    step_id = HiddenField('Step ID')  # Pre-populate this based on route context

    # Populate SelectFields with options based on relationships
    def __init__(self, *args, **kwargs):
        super(AuditLogForm, self).__init__(*args, **kwargs)
        # Fill user_id, company_id, and base_data_id choices from related models



class PostType(Enum):
    noticeboard = 'noticeboard'
    email = 'email'
    service_message = 'service_message'

class LifespanType(Enum):
    one_off = 'one-off'
    persistent = 'persistent'

class PostForm(FlaskForm):
    company_id = SelectField('Company', coerce=int, optional=True)  # Optional based on model definition
    user_id = SelectField('User', coerce=int, optional=True)  # Optional based on model definition
    sender = StringField('Sender', validators=[DataRequired(), Length(max=255)])
    message_type = RadioField('Message Type', choices=PostType, coerce=str, default=PostType.noticeboard)
    subject = StringField('Subject', validators=[DataRequired(), Length(max=255)])
    body = TextAreaField('Body', validators=[DataRequired()])
    lifespan = RadioField('Lifespan', choices=LifespanType, coerce=str, default=LifespanType.one_off)
    created_at = HiddenField('Created At')  # Pre-populate if needed

    # Populate SelectFields with options based on relationships (if applicable)
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Fill company_id and user_id choices from related models (if used)

