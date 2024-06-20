# admin_views.py
# You can continue defining other ModelViews for your models
from flask_admin.model import typefmt
from flask_admin.model.fields import InlineFormField, InlineFieldList
from wtforms.fields import StringField, TextAreaField, DateTimeField, SelectField, BooleanField, SubmitField
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_admin.form import Select2Widget, rules
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView
from flask_admin.base import expose
from datetime import datetime
from db import db
from sqlalchemy import and_
from flask_wtf import FlaskForm
from flask_admin.form import rules
from flask import current_app
from flask_login import current_user
from flask_admin.actions import action  # Import the action decorator
from flask_admin.form import JSONField
from flask.views import MethodView
from flask_admin.contrib.sqla import ModelView
from copy import deepcopy


from models.user import (Users, UserRoles, Role, Table, Questionnaire, Question,
        QuestionnaireQuestions, BaseData,
        Answer, Company, Area, Subarea, AreaSubareas,
        QuestionnaireCompanies, CompanyUsers, Status, Lexic,
        Interval, Subject,
        AuditLog, Post, Ticket, StepQuestionnaire,
        Workflow, Step, BaseData, WorkflowSteps, WorkflowBaseData, StepBaseData, Config, get_config_values)


class ContainerAdmin(ModelView):
    form_overrides = {
        'content': JSONField
    }
    form_create_rules = [
        rules.FieldSet(('page', 'position', 'content_type', 'content'), 'Container Details')
    ]

# Custom view for surveys open for editing
class OpenQuestionnairesView(BaseView):
    @expose('/')
    def index(self):
        today = datetime.now().date()

        #print('current user, comp, quest', current_user, db.session.query(Questionnaire).join(QuestionnaireCompanies).filter(
        #    QuestionnaireCompanies.company_id == current_user.company_id).first())

        # Query surveys open for editing for the current user's company
        '''
        open_surveys = db.session.query(Questionnaire).join(QuestionnaireCompanies).join(CompanyUsers).filter(
            CompanyUsers.user_id == current_user.id,
            Questionnaire.deadline_date > today,
            Questionnaire.status_id < 3
        ).all()
        '''

        '''
        open_surveys = db.session.query(Questionnaire). \
            join(QuestionnaireCompanies, QuestionnaireCompanies.questionnaire_id == Questionnaire.id). \
            join(CompanyUsers, and_(CompanyUsers.company_id == QuestionnaireCompanies.company_id,
                                    CompanyUsers.user_id == current_user.id)). \
            filter(Questionnaire.deadline_date > today,
                   Questionnaire.questionnaire_type != 'Survey',
                   Questionnaire.status_id < 3,
                   QuestionnaireCompanies.status_id != 10). \
            all()
        '''

        open_surveys = db.session.query(Questionnaire). \
            join(QuestionnaireCompanies, QuestionnaireCompanies.questionnaire_id == Questionnaire.id). \
            join(CompanyUsers, and_(CompanyUsers.company_id == QuestionnaireCompanies.company_id,
                                    CompanyUsers.user_id == current_user.id)). \
            filter(Questionnaire.deadline_date > today,
                   Questionnaire.status_id < 3,
                   QuestionnaireCompanies.status_id != 10). \
            all()

        print('open surveys', open_surveys)

        return self.render('open_questionnaires.html', open_questionnaires=open_surveys)



# Custom view for surveys open for editing
class OpenSurveysView(BaseView):

    @expose('/')
    def index(self):
        today = datetime.now().date()

        print('current user, comp, quest', current_user, db.session.query(Questionnaire).join(QuestionnaireCompanies).filter(
            QuestionnaireCompanies.company_id == current_user.company_id).first())

        # Query surveys open for editing for the current user's company
        '''
        open_surveys = db.session.query(Questionnaire).join(QuestionnaireCompanies).join(CompanyUsers).filter(
            CompanyUsers.user_id == current_user.id,
            Questionnaire.deadline_date > today,
            Questionnaire.status_id < 3
        ).all()
        '''

        open_surveys = db.session.query(Questionnaire). \
            join(QuestionnaireCompanies, QuestionnaireCompanies.questionnaire_id == Questionnaire.id). \
            join(CompanyUsers, and_(CompanyUsers.company_id == QuestionnaireCompanies.company_id,
                                    CompanyUsers.user_id == current_user.id)). \
            filter(Questionnaire.deadline_date > today,
                   Questionnaire.questionnaire_type == 'Survey',
                   Questionnaire.status_id < 3). \
            all()

        return self.render('open_surveys.html', open_surveys=open_surveys)


class SurveyResponseView(MethodView):
   def get(self, survey_id):
       survey = Survey.query.get_or_404(survey_id)
       return render_template('survey_response.html', survey=survey)

   def post(self, survey_id):
       survey = Survey.query.get_or_404(survey_id)
       responses = request.form.to_dict()
       for question_id, response in responses.items():
           answer = Answer(question_id=question_id, user_id=current_user.id, response=response)
           db.session.add(answer)
       db.session.commit()
       flash('Survey responses submitted successfully.')
       return redirect(url_for('home'))


# Define custom forms for each model
class CompanyForm(ModelView):
    form_excluded_columns = ('employees',)  # Exclude employees relationship from the form

class QuestionnaireForm(ModelView):
    can_create = True
    can_delete = True
    can_export = True
    can_view_details = True
    column_list = ('questionnaire_id', 'questionnaire_type', 'name', 'created_on', 'deadline_date', 'status_id')
    column_labels = {'questionnaire_id': 'Survey ID', 'questionnaire_type': 'Type', 'name': 'Name', 'description': 'Description',
                     'created_on': 'Date of creation', 'status_id': 'Status'}
    form_columns = column_list
    column_exclude_list = ('id')  # Specify the columns you want to exclude


class QuestionnaireQuestionsForm(ModelView):
    can_create = False
    can_delete = False
    can_export = True
    can_view_details = True
    pass  # No custom form needed for Questionnaire

class QuestionnaireCompaniesForm(ModelView):
    column_list = ('questionnaire_id', 'company_id', 'status_id')  # Specify the columns you want to include
    column_labels = {'questionnaire_id': 'Questionnaire ID', 'company_id': 'Company ID', 'status_id': 'Status'}
    form_columns = ('questionnaire_id', 'company_id')  # Specify the columns you want to include in the form

    column_exclude_list = ('id')  # Specify the columns you want to exclude
    column_descriptions = {'questionnaire_id': 'Questionnaire Unique ID', 'company_id': 'Company', 'status_id': 'Status of Questionnaire'}


    column_default_sort = ('questionnaire_id', True)  # Sort by question_id (ascending)
    pass

class AuditLogForm(ModelView):
    pass  # No custom form needed for Questionnaire

class TicketForm(ModelView):
    pass  # No custom form needed for Questionnaire

# Define custom forms for each mode
class QuestionForm(ModelView):
    column_list = ('question_id', 'text', 'answer_type', 'answer_width')  # Specify the columns you want to include
    column_labels = {'question_id': 'Question ID', 'text': 'Description', 'answer_type': 'Answer(s) type(s list)', 'answer_width': 'Answer(s) length(s list)'}
    form_columns = ('question_id', 'text', 'answer_type', 'answer_width')  # Specify the columns you want to include in the form

    column_exclude_list = ('id')  # Specify the columns you want to exclude
    column_descriptions = {'question_id': 'Question Unique ID',
                           'text': 'Question text', 'answer_type': 'Type of answer field(s)', 'answer_width': 'Width of answer field(s)'}

    column_default_sort = ('question_id', True)  # Sort by question_id (ascending)
    @action('clone', 'Clone', 'Are you sure you want to clone selected records?')
    def action_clone(self, ids):
        for id in ids:
            original_record = self.get_one(id)
            # Create a deep copy of the original record's attributes
            cloned_attributes = deepcopy(original_record.__dict__)
            # Remove the '_sa_instance_state' key from the dictionary
            cloned_attributes.pop('_sa_instance_state', None)
            # Create a new instance of the Question model with the copied attributes
            cloned_record = Question(**cloned_attributes)
            # Optionally modify any attributes of the cloned record here
            db.session.add(cloned_record)
            db.session.commit()
        # Redirect to the edit form for the last cloned record
        return redirect(url_for('.edit_view', id=cloned_record.id))


class StatusForm(ModelView):
    pass  # No custom form needed for Status

class LexicForm(ModelView):
    pass  # No custom form needed for Lexic



class UsersView(ModelView):

    can_view_details = False  # Disable the "Retrieve" view

    # Exclude specific fields from the form
    form_excluded_columns = ['password_hash', 'user_2fa_secret']

    # Exclude specific fields from the list view
    column_exclude_list = ['password_hash', 'user_2fa_secret']
    def is_accessible(self):
        # Add logic here to check if the user has access to this view
        return True

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to the login page if the user doesn't have access
        return redirect(url_for('login', next=request.url))

    def on_model_change(self, form, model, is_created):
        # Convert string dates to datetime objects
        for field_name in ['created_on', 'updated_on', 'end_of_registration']:
            field = getattr(form, field_name)
            if field.data and isinstance(field.data, str):
                model_data = self._parse_datetime_string(field.data)
                setattr(model, field_name, model_data)

    def on_form_prefill(self, form, id):
        # Ensure date fields are datetime objects
        for field_name in ['created_on', 'updated_on', 'end_of_registration']:
            field = getattr(form, field_name)
            data = getattr(field, 'data')
            if data and isinstance(data, str):
                form_data = self._parse_datetime_string(data)
                setattr(field, 'data', form_data)

    def _parse_datetime_string(self, date_string):
        """Parse datetime string to datetime object with multiple formats."""
        datetime_formats = [
            "%Y-%m-%d %H:%M:%S.%f%z",  # with microseconds and timezone
            "%Y-%m-%d %H:%M:%S.%f",    # with microseconds
            "%Y-%m-%d %H:%M:%S%z",     # with timezone
            "%Y-%m-%d %H:%M:%S",       # without microseconds and timezone
            "%Y-%m-%d"                 # date only
        ]
        for fmt in datetime_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        raise ValueError(f"Time data '{date_string}' does not match any of the formats.")



class BaseDataView(ModelView):

    can_view_details = False  # Disable the "Retrieve" view

    def is_accessible(self):
        # Add logic here to check if the user has access to this view
        return True

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to the login page if the user doesn't have access
        return redirect(url_for('login', next=request.url))

    def on_model_change(self, form, model, is_created):
        # Convert string dates to datetime objects
        for field_name in ['created_on', 'updated_on', 'deadline', 'date_of_doc']:
            field = getattr(form, field_name)
            if field.data and isinstance(field.data, str):
                model_data = self._parse_datetime_string(field.data)
                setattr(model, field_name, model_data)

    def on_form_prefill(self, form, id):
        # Ensure date fields are datetime objects
        for field_name in ['created_on', 'updated_on', 'deadline', 'date_of_doc']:
            field = getattr(form, field_name)
            data = getattr(field, 'data')
            if data and isinstance(data, str):
                form_data = self._parse_datetime_string(data)
                setattr(field, 'data', form_data)

    def _parse_datetime_string(self, date_string):
        """Parse datetime string to datetime object with multiple formats."""
        datetime_formats = [
            "%Y-%m-%d %H:%M:%S.%f%z",  # with microseconds and timezone
            "%Y-%m-%d %H:%M:%S.%f",    # with microseconds
            "%Y-%m-%d %H:%M:%S%z",     # with timezone
            "%Y-%m-%d %H:%M:%S",       # without microseconds and timezone
            "%Y-%m-%d"                 # date only
        ]
        for fmt in datetime_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        raise ValueError(f"Time data '{date_string}' does not match any of the formats.")


class AreaForm(ModelView):
    pass  # No custom form needed for Area

class SubareaForm(ModelView):
    pass  # No custom form needed for Subarea

class StepQuestionnaireForm(ModelView):
    can_create = True
    can_delete = True
    can_export = True
    can_view_details = True
    pass

class NewSurveyForm(ModelView):
    can_create = False
    can_delete = False
    can_export = True
    can_view_details = True
    column_list = ('questionnaire_id', 'name', 'created_on', 'deadline_date', 'status_id')
    column_labels = {'questionnaire_id': 'Survey ID', 'name': 'Name', 'description': 'Description',
                     'created_on': 'Date of creation', 'status_id': 'Status'}
    form_columns = column_list
    column_exclude_list = ('id')  # Specify the columns you want to exclude
    pass

class SubjectForm(ModelView):
    name = StringField('Name', validators=[DataRequired()])
    tier_1 = SelectField('Tier 1', choices=[
        ('Legale', 'Legale'),
        ('Contabilità', 'Contabilità'),
        ('Servizi', 'Servizi'),
        ('Utenti', 'Utenti'),
        ('Altro', 'Altro')
    ], validators=[DataRequired()])
    tier_2 = StringField('Tier 2', validators=[DataRequired()])
    tier_3 = StringField('Tier 3', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LegalDocumentForm(ModelView):
    pass  # No custom form needed for Legal_document


class PostForm(ModelView):
    pass

class WorkflowForm(ModelView):
    column_list = ('name', 'description', 'restricted')
    column_labels = {'name': 'Name', 'description': 'Description', 'restricted': 'Restricted'}
    form_columns = ('name', 'description', 'restricted')
    column_exclude_list = ('id')  # Specify the columns you want to exclude

    column_descriptions = {'name': 'Given Workflow Name',
                           'description': 'Brief Description of Workflow',
                           'restricted': 'Reserved to Admin'}


class StepForm(ModelView):
    column_list = ('name', 'description', 'action', 'order', 'next_step_id', )
    column_labels = {'name': 'Name', 'description': 'Description', 'action': 'Action', 'order': 'Order',
                     'next_step_id': 'Next Step',  }
    form_columns = ('name', 'description', 'action', 'order', 'next_step_id', )
    column_exclude_list = ('id')  # Specify the columns you want to exclude
    column_descriptions = {'name': 'Given Step Name',
                           'description': 'Brief Description of Step',
                           'action': 'Description of Action Taken with this Step',
                           'order': 'Order of Step in Workflow',}

class WorkflowStepsForm(ModelView):
    can_create = False
    can_delete = False
    can_export = True
    can_view_details = True
    pass

# Define ModelView declarations for each model
class CompanyView(CompanyForm):
    column_searchable_list = ['name', 'description', 'address', 'phone_number', 'email']
    column_filters = ['name', 'address', 'phone_number', 'email']

class QuestionnaireView(QuestionnaireForm):
    pass  # No customizations needed for QuestionnaireView

class StepQuestionnaireView(StepQuestionnaireForm):
    can_create = True
    can_delete = True
    can_export = True
    can_view_details = True
    pass  # No customizations needed for QuestionnaireView

class NewSurveyView(NewSurveyForm):
    can_create = False
    can_delete = False
    can_export = True
    can_view_details = True
    pass  # No customizations needed for QuestionnaireView


class QuestionView(QuestionForm):
    pass  # No customizations needed for QuestionView

class StatusView(StatusForm):
    pass  # No customizations needed for StatusView

class LexicView(LexicForm):
    pass  # No customizations needed for LexicView

class AreaView(AreaForm):
    pass  # No customizations needed for AreaView

class SubareaView(SubareaForm):
    pass  # No customizations needed for SubareaView

class SubjectView(SubjectForm):
    pass  # No customizations needed for SubjectView


class LegalDocumentView(LegalDocumentForm):
    pass  # No customizations needed for LegalDocumentView


class AuditLogView(AuditLogForm):
    pass  # No customizations needed for SubjectView

class TicketView(TicketForm):
    pass  # No customizations needed for SubjectView


class PostView(PostForm):
    pass

class WorkflowView(WorkflowForm):
    pass  # No customizations needed for WorkflowView

class StepView(StepForm):
    pass  # No customizations needed for StepView

class WorkflowStepsView(WorkflowStepsForm):
    pass

class QuestionnaireQuestionsView(QuestionnaireQuestionsForm):
    pass

class QuestionnaireCompaniesView(QuestionnaireCompaniesForm):
    pass
