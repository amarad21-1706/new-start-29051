# admin_views.py
# You can continue defining other ModelViews for your models
from flask_admin import Admin
from flask_admin.model import typefmt
from flask_admin.model.fields import InlineFormField, InlineFieldList
from wtforms.fields import StringField, TextAreaField, DateTimeField, SelectField, BooleanField, SubmitField
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_admin.form import Select2Widget, rules
from flask_admin.contrib.sqla import ModelView
from wtforms.validators import Email, InputRequired, NumberRange

from flask_admin.model.widgets import XEditableWidget
from wtforms.fields import DateField
from flask_admin import BaseView
from flask_admin.base import expose
from wtforms import IntegerField, FileField
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
from sqlalchemy import distinct
from copy import deepcopy

from config.config import (get_if_active, get_subarea_name, get_current_interval, get_subarea_interval_type,
create_audit_log, remove_duplicates, create_notification)

from config.custom_fields import CustomFileUploadField  # Import the custom field

from models.user import (Users, UserRoles, Role, Table, Questionnaire, Question,
        QuestionnaireQuestions, BaseData,
        Answer, Company, Area, Subarea, AreaSubareas,
        QuestionnaireCompanies, CompanyUsers, Status, Lexic,
        Interval, Subject,
        AuditLog, Post, Ticket, StepQuestionnaire,
        Workflow, Step, BaseData, WorkflowSteps, WorkflowBaseData, StepBaseData,
                         Container, Config, get_config_values)


from forms.forms import (LoginForm, ForgotPasswordForm, ResetPasswordForm101, RegistrationForm,
                         QuestionnaireCompanyForm, CustomBaseDataForm,
        QuestionnaireQuestionForm, WorkflowStepForm, WorkflowBaseDataForm,
                         BaseDataWorkflowStepForm,
        UserRoleForm, CompanyUserForm, UserDocumentsForm, StepBaseDataInlineForm,
        create_dynamic_form, CustomFileLoaderForm,
        CustomSubjectAjaxLoader, BaseSurveyForm)

from flask_admin.form import FileUploadField

from wtforms import (SelectField, BooleanField, ValidationError, EmailField)
from config.config import Config, check_status, check_status_limited, check_status_extended

config = Config()

def check_record_exists(form, company_id):
    # Assuming form fields map to model fields
    query = BaseData.query.filter_by(
        date_of_doc=form.date_of_doc.data,
        number_of_doc=form.number_of_doc.data,
        fi0=form.fi0.data,
        interval_ord=form.interval_ord.data,
        subject_id=form.subject_id.data,
        company_id=company_id,
    )
    return query.first() is not None

class CustomBooleanField(BooleanField):
    def process_formdata(self, valuelist):
        if not valuelist or valuelist[0] == '':  # Check for empty string or empty list
            self.data = 0
        else:
            self.data = 1 if valuelist[0].lower() in ('y', 'yes', 'true', 't', '1', 's') else 0

class CheckboxField(BooleanField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = True
        else:
            self.data = False
    def populate_obj(self, obj, name):
        setattr(obj, name, "Yes" if self.data else "No")  # Customize as per your model



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





# admin -  f l u s s i  precomplaint
class Flussi_dataView(ModelView):
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 1  # Define subarea_id as a class attribute
    area_id = 1

    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)  # Use the custom field
    }

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
        self.intervals = kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
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
        with current_app.app_context():

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



class BaseDataView(ModelView):
    can_export = True
    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)
    }

    def __init__(self, *args, **kwargs):
        self.intervals = kwargs.pop('intervals', None)
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(*args, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super(BaseDataView, self).scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id, subarea_id=None)
        nr_intervals = config_values[0]

        current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
        first_element = current_interval[0] if current_interval else None
        interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,
            default=first_element
        )

        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Legale").all()]
        )

        form_class.no_action = CustomBooleanField('Confirm no documents to attach', default=False)
        form_class.fc2 = MyStringField('Note')

        return form_class

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()
        model_records = self.model.query.filter(self.model.id.in_(ids)).all()
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records, model_records=model_records)

    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        print('Implement next step action')
        pass

    def _validate_no_action(self, model, form):
        if model.file_path is None and form.no_action.data == 0:
            raise ValidationError('If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        if model.file_path is not None and form.no_action.data:
            raise ValidationError('The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        form.populate_obj(model)

        uploaded_file = form.file_path.data
        if is_created:
            model.created_on = datetime.now()

        user_id = current_user.id
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None

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
        no_action = form.no_action.data

        if form.date_of_doc.data and form.number_of_doc.data and form.fi0.data and form.interval_ord.data and form.subject_id.data:
            if check_record_exists(form, company_id):
                raise ValidationError("Document already exists!")

        if not form.date_of_doc.data and not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data:
            if form.date_of_doc.data > datetime.today().date():
                raise ValidationError("Date of document cannot be a future date.")

        if form.date_of_doc.data:
            if form.date_of_doc.data.year != form.fi0.data:
                raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null.")

        if not form.subject_id.data:
            raise ValidationError("Document type can not be null.")

        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError("Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError("Please check the year")

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass

        with current_app.app_context():
            result, message = check_status_limited(is_created, company_id, subject_id, None, year_id, interval_ord, interval_id, area_id, subarea_id, datetime.today(), db.session)

        if not result:
            raise ValidationError(message)

        model.updated_on = datetime.now()
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
        model.no_action = no_action

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        inline_form_data = form.data.get('steps_relationship', [])
        if form.date_of_doc.data:
            inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
            inline_data_string += f"was created by the user {user_id} ({company_id}. "
            inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"

        try:
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
        except:
            print('Error creating notification')

        action_type = 'update'
        if is_created:
            action_type = 'create'

        try:
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
        except:
            print('Error creating audit trail record')

        return model


class AttiDataView(BaseDataView):
    create_template = 'admin/area_1/create_base_data_2.html'
    subarea_id = 2
    area_id = 1
    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati', 'no_action': 'Dichiarazione di assenza di documenti (1)'}
    column_filters = ('subject', 'fc2', 'no_action')
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')


class Atti_dataView(ModelView):
    can_export = True  # Default to enabled

    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # form_base_class = CustomBaseDataForm  # Use our custom form class
    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)  # Use the custom field
    }
    create_template = 'admin/area_1/create_base_data_2.html'
    subarea_id = 2
    area_id = 1

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc2']
    form_widget_args = {
        'fc2': {'widget': XEditableWidget()},
    }

    def __init__(self, *args, **kwargs):
        self.intervals = kwargs.pop('intervals', None)
        super().__init__(*args, **kwargs)
        self.subarea_id = Atti_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Atti_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
    column_labels = {'fi0': 'Anno di rif.', 'interval_ord': 'Periodo di rif.', 'subject': 'Oggetto',
                     'number_of_doc': 'Nr. documento', 'date_of_doc': 'Data documento', 'file_path': 'Allegati',
                     'no_action': 'Conferma assenza doc.', 'fc2': 'Note'}
    column_descriptions = {'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)', 'subject_id': 'Seleziona oggetto',
                           'fc2': 'Note', 'file_path': 'Allegati', 'no_action': 'Dichiarazione di assenza di documenti (1)'}
    form_overrides = {
        'no_action': CheckboxField
    }
    column_filters = ('subject', 'fc2', 'no_action')  # Adjust based on your model structure
    form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    @action('custom_action', 'List Workflows of Documents')
    def custom_action(self, ids):
        step_base_data_records = StepBaseData.query.filter(StepBaseData.base_data_id.in_(ids)).all()
        model_records = BaseData.query.filter(BaseData.id.in_(ids)).all()
        return self.render('basedata_workflow_step_list.html', step_base_data_records=step_base_data_records, model_records=model_records)

    @action('custom_action_next_step', 'Transition to next Step')
    def custom_action_next_step(self, ids):
        print('Implement next step action')
        pass

    def _subject_formatter(view, context, model, name):
        if model.subject:
            if isinstance(model.subject, Subject):
                return model.subject.name
            else:
                return Subject.query.get(model.subject).name
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

        current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
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
        #form_class.no_action = CheckboxField('Confirm no documents to attach',
        #                                     default=False)  # Set default value to False

        form_class.no_action = CustomBooleanField('Confirm no documents to attach', default=False)

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        return form_class #ExtendedForm

    def _validate_no_action(self, model, form):
        print('*** no_action.data', form.no_action.data, '. model.file_path ***', model.file_path)
        if model.file_path is None and form.no_action.data == 0:
            raise ValidationError('If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

    def _uncheck_if_document(self, model, form):
        if model.file_path is not None and form.no_action.data:
            raise ValidationError('The no-document box is checked but a document was uploaded - please confirm either of the two.')

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        form.populate_obj(model)

        uploaded_file = form.file_path.data
        if is_created:
            model.created_on = datetime.now()

        user_id = current_user.id
        try:
            company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        except:
            company_id = None

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
        no_action = form.no_action.data

        # chg 2

        if form.date_of_doc.data and form.number_of_doc.data and form.fi0.data and form.interval_ord.data \
            and form.subject_id.data:
            print('form.company_id', company_id)
            if check_record_exists(form, company_id):
                raise ValidationError("Document already exists!")

        if not form.date_of_doc.data and not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data:
            if form.date_of_doc.data > datetime.today().date():
                raise ValidationError("Date of document cannot be a future date.")

        if form.date_of_doc.data:
            if form.date_of_doc.data.year != form.fi0.data:
                raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null.")

        if not form.subject_id.data:
            raise ValidationError("Document type can not be null.")

        if form.interval_ord.data > 3 or form.interval_ord.data < 0:
            raise ValidationError("Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months).")

        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError("Please check the year")

        if self._uncheck_if_document(model, form):
            pass
        if self._validate_no_action(model, form):
            pass

        with current_app.app_context():
            result, message = check_status_limited(is_created, company_id, subject_id, None, year_id, interval_ord, interval_id, area_id, subarea_id, datetime.today(), db.session)

        if not result:
            raise ValidationError(message)

        model.updated_on = datetime.now()
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
        model.no_action = no_action

        if is_created:
            self.session.add(model)
        else:
            self.session.merge(model)
        self.session.commit()

        remove_duplicates(self.session, StepBaseData, ['base_data_id', 'workflow_id', 'step_id'])

        inline_form_data = form.data.get('steps_relationship', [])
        if form.date_of_doc.data:
            inline_data_string = f"At {datetime.now()} a new document dated {form.date_of_doc.data.year} "
            inline_data_string += f"was created by the user {user_id} ({company_id}. "
            inline_data_string += f"Area {area_id}, subarea {subarea_id}, reference period {interval_ord}/{interval_id}/{year_id}. "

        for data in inline_form_data:
            for field_name, field_value in data.items():
                inline_data_string += f"{field_name}: {field_value}\n"

        try:
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
        except:
            print('Error creating notification')

        action_type = 'update'
        if is_created:
            action_type = 'create'

        try:
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
        except:
            print('Error creating audit trail record')

        return model


class Contingencies_dataView(ModelView):

    can_export = True  # Default to enabled

    inline_models = (StepBaseDataInlineForm(StepBaseData),)
    # inline_models = [(StepBaseDataInlineForm, StepBaseData, 'ONE_TO_MANY')]  # Assuming a one-to-one relationship
    # form_base_class = CustomBaseDataForm  # Use our custom form class
    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)  # Use the custom field
    }

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
        self.intervals = kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
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
        print('no_action_value', no_action_value, '. model.file_path', model.file_path)
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

        if form.date_of_doc.data > datetime.today().date():
            raise ValidationError("Date of document cannot be a future date.")

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
        with current_app.app_context():
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
    # form_base_class = CustomBaseDataForm  # Use our custom form class
    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)  # Use the custom field
    }
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

        self.intervals = kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals] #int(get_current_interval(3))  # quadriester
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

        if form.date_of_doc.data > datetime.today().date():
            raise ValidationError("Date of document cannot be a future date.")

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
        with current_app.app_context():
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
    # form_base_class = CustomBaseDataForm  # Use our custom form class
    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)  # Use the custom field
    }
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
        self.intervals=kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if
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

        if form.date_of_doc.data > datetime.today().date():
            raise ValidationError("Date of document cannot be a future date.")

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
        with current_app.app_context():
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
    # form_base_class = CustomBaseDataForm  # Use our custom form class
    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)  # Use the custom field
    }
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

        self.intervals=kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if
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

        if form.date_of_doc.data > datetime.today().date():
            raise ValidationError("Date of document cannot be a future date.")

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
        with current_app.app_context():
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
    # form_base_class = CustomBaseDataForm  # Use our custom form class
    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)  # Use the custom field
    }
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

        self.intervals=kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if
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

        if form.date_of_doc.data > datetime.today().date():
            raise ValidationError("Date of document cannot be a future date.")

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
        with current_app.app_context():
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
        self.intervals=kwargs.pop('intervals', None)
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
    # form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

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

        current_interval = [t[2] for t in self.intervals if
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

        self.intervals=kwargs.pop('intervals', None)
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
    # form_excluded_columns = ('user_id', 'company_id', 'status_id', 'created_by', 'created_on', 'updated_on')

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

        current_interval = [t[2] for t in self.intervals if
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

        self.intervals=kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if
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

        with current_app.app_context():
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

        self.intervals=kwargs.pop('intervals', None)
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

        current_interval = [t[2] for t in self.intervals if
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
        # query = super(Tabella24_dataView, self).get_query().filter_by(data_type=self.subarea_name)
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

        with current_app.app_context():
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

        self.intervals=kwargs.pop('intervals', None)
        super().__init__(*args, **kwargs)
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Tabella25_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella25_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('interval_ord', 'fi0', 'fi1', 'fn1', 'fi2', 'fn2', 'fi3', 'fc1')
    form_columns = (
    'interval_ord', 'fi0', 'fi1', 'fn1', 'fi2', 'fn2', 'fi3', 'fc1')  # Specify form columns with dropdowns

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
    column_searchable_list = ('fi0', 'interval_ord', 'subject.name', 'fi3', 'fn1', 'fi4', 'fn2', 'fi5', 'fc1', 'fc2')
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

        current_interval = [t[2] for t in self.intervals if
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
        # query = super(Tabella25_dataView, self).get_query().filter_by(data_type=self.subarea_name)
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
                                          subarea_id=self.subarea_id)
        interval_id = config_values[0]
        subject_id = form.subject_id.data
        legal_document_id = None
        record_type = 'control_area'

        if form.fi0.data == None or form.interval_ord.data == None:
            raise ValidationError(f"Time interval reference fields cannot be null")

        with current_app.app_context():
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

        self.intervals=kwargs.pop('intervals', None)
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
                           'fi1': 'Totale richieste presentate', 'fi2': 'di cui IVI',
                           'fn1': 'Percentuale richieste IVI (=b/a)',
                           'fi3': 'Richieste con esito positivo',
                           'fn2': 'Percentuale delle richieste IVI con esito positivo (=d/b)',
                           'fi4': 'Richieste con esito negativo (=b-d)',
                           'fn3': 'Percentuale delle richieste IVI con esito negativo (=f/b)',
                           'fi5': 'Richieste ALTRI operatori (=a-b)',
                           'fn4': 'Percentuale ALTRI sul totale (=h/a)',
                           'fi6': 'Richieste ALTRI con esito positivo',
                           'fn5': 'Percentuale di richieste ALTRI con esito positivo (=j/h)',
                           'fi7': 'Richieste ALTRI con esito negativo (=h-j)',
                           'fn6': 'Percentuale richieste ALTRI con esito negativo (=l/h)',
                           'fi8': 'Richieste ALTRI su PdR altri', 'fi9': 'di cui con esito negativo',
                           'fn7': 'Percentuale di richieste ALTRI con esito negativo (=p/n)',
                           'fi10': 'Richieste ALTRI su PdR IVI',
                           'fi11': 'di cui con esito negativo',
                           'fn8': 'Percentuale di richieste ALTRI su PdR IVI con esito negativo (=s/r)',
                           'fc1': '(opzionale)'}

    # Customize inlist for tabella26
    column_default_sort = ('fi0', True)
    column_searchable_list = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5',
                              'fi6', 'fi7', 'fi8', 'fi9', 'fi10', 'fi11', 'fc1')
    # Adjust based on your model structure
    column_filters = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5',
                      'fi6', 'fi7', 'fi8', 'fi9', 'fi10', 'fi11', 'fc1')

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

        current_interval = [t[2] for t in self.intervals if
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

    def get_query(self):
        # query = super(Tabella26_dataView, self).get_query().filter_by(data_type=self.subarea_name)
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

        with current_app.app_context():
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
                form.fn1.data = round(100 * (form.fi2.data / form.fi1.data), 2)  # IVI/tot
                form.fn4.data = round(100 * (form.fi5.data / form.fi1.data), 2)  # altri/TOT
            if form.fi2.data is not None and form.fi2.data != 0:
                form.fn2.data = round(100 * (form.fi3.data / form.fi2.data), 2)  # pct IVI pos
                form.fn3.data = round(100 * (form.fi4.data / form.fi2.data), 2)  # PCT IVI neg
            if form.fi5.data is not None and form.fi5.data != 0:
                form.fn5.data = round(100 * (form.fi6.data / form.fi5.data), 2)  # PCT POS altri
                form.fn6.data = round(100 * (form.fi7.data / form.fi5.data), 2)  # PCT NEG altri

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

        self.intervals=kwargs.pop('intervals', None)
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
                     'fi5': 'PdR', 'fn4': 'Tasso switching PdR',
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
    column_searchable_list = (
    'fi0', 'interval_ord', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
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

        current_interval = [t[2] for t in self.intervals if
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
        # query = super(Tabella27_dataView, self).get_query().filter_by(data_type=self.subarea_name)
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

        with current_app.app_context():
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

class MyStringField(StringField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, default='Enter content here', **kwargs)
        self.help_text = 'Click to edit field'  # Store help text separately


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


def create_admin_views(app, intervals):

    with app.app_context():

        class CustomAdminIndexView1(BaseData):
            default_view = 'flussi_data_view'  # Or any other valid view name

            def index(self):
                # Customize the index view here for the first custom index view
                return self.render('open_admin.html')
                # return 'Hello From first admin :{}.'.format(self)

        # Define the second custom index view class
        class CustomAdminIndexView2(BaseData):
            default_view = 'view_struttura_offerta'  # Or the intended first view for "Area 2"

            def index(self):
                # Customize the index view here for the second custom index view
                return self.render('open_admin_2.html')  # Adjust template path if needed

        # Define custom form for CustomAdminIndexView1
        class CustomForm1(FlaskForm):  # was BaseForm
            fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2199)])  # anno
            interval_ord = IntegerField('interval_ord',
                                        validators=[InputRequired(), NumberRange(min=0, max=52)])  # periodo

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


        class CustomAttiDataView(Atti_dataView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form = CustomForm1

        class CustomContingenciesDataView(Contingencies_dataView):
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
        # class CustomForm2(BaseData):
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

        admin_app1.add_view(CustomFlussiDataView(name='Flussi pre-complaint', session=db.session, model=BaseData, intervals=intervals,
                                                 endpoint='flussi_data_view'))
        admin_app1.add_view(CustomAttiDataView(name='Atti complaint', session=db.session, model=BaseData, intervals=intervals,
                                               endpoint='atti_data_view'))
        # TODO de ce nu Custom?
        admin_app1.add_view(CustomContingenciesDataView(name='Contingencies', session=db.session, model=BaseData, intervals=intervals))
        admin_app1.add_view(CustomContenziosiDataView(name='Contenziosi', session=db.session, model=BaseData, intervals=intervals,
                                                      endpoint='contenziosi_data_view'))
        admin_app1.add_view(CustomIniziative_dso_asDataView(BaseData, db.session,
                                                            name='Iniziative DSO vs amministrazioni',
                                                            endpoint='iniziative_dso_as_data_view', intervals=intervals))
        admin_app1.add_view(CustomIniziative_as_dsoDataView(BaseData, db.session,
                                                            name='Amministrazioni vs DSO',
                                                            endpoint='iniziative_as_dso_data_view', intervals=intervals))
        admin_app1.add_view(CustomIniziative_dso_dsoDataView(BaseData, db.session,
                                                             name='DSO vs DSO/TSO',
                                                             endpoint='iniziative_dso_dso_data_view', intervals=intervals))

        # Add views to admin_app1
        admins_off_set += 1
        sub_off_set = 0

        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            pass
            #admin_app1.add_view(CustomFlussiDataView(BaseData, db.session,
            #                                         name="Flussi pre-complaint", endpoint='flussi_data_view'))

        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            pass
            # Register the view with Flask Admin
            # admin_app1.add_view(CustomAttiBaseView(name='Workflow Manager (Atti complaint)',
            #                    endpoint='custom_base_atti'))
            #admin_app1.add_view(CustomAttiDataView(BaseData, db.session,
            #                                       name='Atti di complaint', endpoint='atti_data_view'))

        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            pass
            #admin_app1.add_view(Contingencies_dataView(BaseData, db.session,
            #                                           name='Contingencies', endpoint='contingencies_data_view'))

        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            pass
            #admin_app1.add_view(CustomContenziosiDataView(BaseData, db.session,
            #                                              name='Contenziosi', endpoint='contenziosi_data_view'))

        sub_off_set += 1

        if get_if_active(admins_off_set, sub_off_set):
            pass
            #admin_app1.add_view(CustomIniziative_dso_asDataView(BaseData, db.session,
            #                                                    name='Iniziative DSO vs amministrazioni',
            #                                                    endpoint='iniziative_dso_as_data_view'))

        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            pass
            #admin_app1.add_view(CustomIniziative_as_dsoDataView(BaseData, db.session,
            #                                                    name='Amministrazioni vs DSO',
            #                                                    endpoint='iniziative_as_dso_data_view'))

        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            pass
            #admin_app1.add_view(CustomIniziative_dso_dsoDataView(BaseData, db.session,
            #                                                     name='DSO vs DSO/TSO',
            #                                                     endpoint='iniziative_dso_dso_data_view'))

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
        if get_if_active(admins_off_set, sub_off_set):
            admin_app2.add_view(CustomTabella21DataView(BaseData, db.session, name="Struttura offerta",
                                                        endpoint='view_struttura_offerta', intervals=intervals))
        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            admin_app2.add_view(CustomTabella22DataView(BaseData, db.session, name="Area di contendibilita'",
                                                        endpoint="view_area_contendibilita'", intervals=intervals))
        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            admin_app2.add_view(CustomTabella23DataView(BaseData, db.session, name="Grado di contendibilita'",
                                                        endpoint="view_grado_contendibilita'", intervals=intervals))
        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            admin_app2.add_view(CustomTabella24DataView(BaseData, db.session, name='Accesso venditori a DSO',
                                                        endpoint='view_accesso_venditori', intervals=intervals))
        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            admin_app2.add_view(CustomTabella25DataView(BaseData, db.session, name='Quote mercato IVI',
                                                        endpoint='view_quote_mercato_ivi', intervals=intervals))
        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            admin_app2.add_view(CustomTabella26DataView(BaseData, db.session, name='Trattamento switching',
                                                        endpoint='view_trattamento_switching', intervals=intervals))
        sub_off_set += 1
        if get_if_active(admins_off_set, sub_off_set):
            admin_app2.add_view(CustomTabella27DataView(BaseData, db.session, name="Livello di contendibilta'",
                                                        endpoint="view_livello_contendibilita'", intervals=intervals))



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

        # Initialize Flask-Admin
        # admin_app4 = Admin(app, name='Setup', url = '/open_setup_basic', template_mode='bootstrap4', endpoint = 'setup_basic')

        admin_app4 = Admin(app, name='System Setup', url='/open_admin_4', template_mode='bootstrap4',
                           endpoint='open_admin_4')
        # Add your ModelViews to Flask-Admin
        admin_app4.add_view(CompanyView(Company, db.session, name='Companies', endpoint='companies_data_view'))
        admin_app4.add_view(UsersView(Users, db.session, name='Users', endpoint='users_data_view'))
        admin_app4.add_view(
            QuestionnaireView(Questionnaire, db.session, name='Questionnaires', endpoint='questionnaires_data_view'))
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
        admin_app4.add_view(BaseDataView(BaseData, db.session, name='Database', endpoint='base_data_view'))
        admin_app4.add_view(BaseDataView(Container, db.session, name='Container', endpoint='container_view'))

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

        admin_app10.add_view(ContainerAdmin(Container, db.session, name='Containers data'))
        # admin_app10.add_view(StatusView(Status, db.session, name='E. Dictionary of Status',
        #                                endpoint='status_questionnaire_view'))


    return admin_app1, admin_app2, admin_app3, admin_app4, admin_app10


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
    form_columns = column_list # ('questionnaire_id', 'company_id')  # Specify the columns you want to include in the form

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
    form_columns = column_list # ('question_id', 'text', 'answer_type', 'answer_width')  # Specify the columns you want to include in the form

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
    form_columns = column_list #('name', 'description', 'restricted')
    column_exclude_list = ('id')  # Specify the columns you want to exclude

    column_descriptions = {'name': 'Given Workflow Name',
                           'description': 'Brief Description of Workflow',
                           'restricted': 'Reserved to Admin'}


class StepForm(ModelView):
    column_list = ('name', 'description', 'action', 'order', 'next_step_id', )
    column_labels = {'name': 'Name', 'description': 'Description', 'action': 'Action', 'order': 'Order',
                     'next_step_id': 'Next Step',  }
    form_columns = column_list # ('name', 'description', 'action', 'order', 'next_step_id', )
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