# admin_views.py
# You can continue defining other ModelViews for your models
from db import db
from flask_admin import Admin
from flask import Blueprint, render_template

from flask_admin import Admin, AdminIndexView, expose
from flask_login import current_user
from flask import session
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.widgets import Input

from flask import current_app as app
from flask import get_flashed_messages
from flask_admin.form.rules import FieldSet
from flask_admin.model import typefmt
from flask_admin.model.fields import InlineFormField, InlineFieldList
from wtforms.fields import StringField, TextAreaField, DateTimeField, SelectField, BooleanField, SubmitField
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_admin.form import Select2Widget, rules
from flask_admin.contrib.sqla import ModelView
from flask import has_request_context
from wtforms.validators import Email, InputRequired, NumberRange
from sqlalchemy.ext.hybrid import hybrid_property
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_admin.model.widgets import XEditableWidget
from wtforms.fields import DateField, DateTimeField, DateTimeLocalField
from flask_admin import BaseView
from flask_admin.base import expose
from wtforms import IntegerField, FileField, HiddenField
from datetime import datetime, date, timedelta
from sqlalchemy import and_, desc
from wtforms.fields import DateField
from wtforms.widgets import DateInput
from flask_wtf import FlaskForm
from flask_admin.form import rules
from flask import current_app
from flask_login import current_user, login_required, LoginManager
from flask_admin.actions import action  # Import the action decorator
from flask_admin.form import JSONField
from flask.views import MethodView
from sqlalchemy import distinct
from copy import deepcopy

from flask_admin.model.template import macro
import traceback

from wtforms import StringField
from flask_admin.form import rules

from flask import request, redirect, url_for

from sqlalchemy import text
from sqlalchemy.orm.exc import NoResultFound

from app_factory import roles_required, subscription_required

from config.config import (get_if_active, get_subarea_name, get_current_interval, get_current_intervals,
                           get_subarea_interval_type, create_audit_log, remove_duplicates,
                           create_notification)

from config.custom_fields import CustomFileUploadField  # Import the custom field

from models.user import (Users, UserRoles, Role, Table, Questionnaire, Question,
                                QuestionnaireQuestions, BaseData, Product, Plan, PlanProducts,
                                Answer, Company, Area, Subarea, AreaSubareas,
                                QuestionnaireCompanies, CompanyUsers, Status, Lexic,
                                Interval, Subject, Cart, AuditLog, Post, Ticket, StepQuestionnaire,
                                Workflow, Step, BaseData, BaseDataInline, WorkflowSteps, WorkflowBaseData,
                                DocumentWorkflow, DocumentWorkflowHistory,
                                Container, Config,
                                Contract, ContractParty, ContractTerm, ContractDocument,
                                ContractStatusHistory, ContractArticle, Party,
                                get_config_values)

from wtforms.widgets import DateTimeInput

from forms.forms import (LoginForm, ForgotPasswordForm, ResetPasswordForm101, RegistrationForm,
                QuestionnaireCompanyForm, CustomBaseDataForm,
                QuestionnaireQuestionForm, WorkflowStepForm, WorkflowBaseDataForm,
                BaseDataWorkflowStepForm, BaseDataInlineModelForm, ContractArticleInlineModelForm,
                UserRoleForm, CompanyUserForm, UserDocumentsForm, DocumentWorkflowInlineForm,
                create_dynamic_form, CustomFileLoaderForm,
                CustomSubjectAjaxLoader, BaseSurveyForm)

from flask_admin.form import FileUploadField
from wtforms import (SelectField, BooleanField, ValidationError, EmailField, HiddenField)
from config.config import (Config, check_status, check_status_limited,
                           check_status_extended)

from flask import session

from flask import flash, redirect, url_for, Markup
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.exc import IntegrityError, ProgrammingError
import uuid

from flask_admin import Admin, AdminIndexView, expose
from flask_login import current_user
from flask import session

config = Config()

'''
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        # Refresh session or set necessary variables
        if current_user.is_authenticated:
            session['roles'] = [role.name for role in current_user.roles] if current_user.roles else ['Guest']
            session['is_authenticated'] = True
        else:
            session['roles'] = ['Guest']
            session['is_authenticated'] = False
        session.modified = True
        return super(MyAdminIndexView, self).index()

# Ensure the AdminIndexView has a unique name and endpoint
index_view = MyAdminIndexView(name='contracts_admin_index')  # Add a unique name for the index view
'''

# Define the Blueprint
admin_all = Blueprint('admin_all', __name__)


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


class DocumentsView(ModelView):
    can_view_details = True
    can_export = True
    can_edit = True
    can_delete = False
    can_create = True

    # Limit fields displayed to specific fields
    column_list = ['nr_of_doc', 'date_of_doc', 'ft1', 'company_id', 'user_id', 'fc1', 'file_path', 'no_action']

    # Only show base_data records with area_id in [1, 3]
    def get_query(self):
        return super(DocumentsView, self).get_query().filter(BaseData.area_id.in_([1, 3]))

    # Filtering based on user roles
    def get_list(self, page, sort_field, sort_desc, search, filters, execute=True, **kwargs):
        query = self.get_query()
        if current_user.has_role('Admin'):
            return super(DocumentsView, self).get_list(page, sort_field, sort_desc, search, filters, execute, **kwargs)
        elif current_user.has_role('Manager'):
            company_id = session.get('company_id')
            query = query.filter(BaseData.company_id == company_id)
        elif current_user.has_role('Employee'):
            user_id = current_user.id
            query = query.filter(BaseData.user_id == user_id)

        count = query.count()
        return count, query.all()

    # Add file_path with a file upload widget and no_action boolean, and add date_of_doc with date picker widget
    form_extra_fields = {
        'file_path': FileUploadField('File Path', base_path='/path/to/save/files'),
        'no_action': BooleanField('No Action'),
        'date_of_doc': DateField('Document Date', widget=DateInput(), format='%Y-%m-%d')
    }

    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.has_role('Admin') or current_user.has_role('Employee') or current_user.has_role('Manager')
        )

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_on = datetime.utcnow()
        model.updated_on = datetime.utcnow()

        # Example of ensuring correct types
        if form.number_of_doc.data:
            model.number_of_doc = str(form.number_of_doc.data)

        # Handling date fields correctly
        if form.date_of_doc.data:
            if isinstance(form.date_of_doc.data, datetime):
                model.date_of_doc = form.date_of_doc.data
            elif isinstance(form.date_of_doc.data, date):
                model.date_of_doc = datetime.combine(form.date_of_doc.data, datetime.min.time())
            elif isinstance(form.date_of_doc.data, str):
                model.date_of_doc = datetime.strptime(form.date_of_doc.data, '%Y-%m-%d %H:%M:%S')
            else:
                raise ValidationError("Invalid date format for date_of_doc.")

    def create_form(self, obj=None):
        form = super(DocumentsView, self).create_form(obj)
        return form

    def edit_form(self, obj=None):
        form = super(DocumentsView, self).edit_form(obj)
        return form


class BaseDataView(ModelView):
    can_view_details = True
    can_export = True
    can_edit = False
    can_delete = False
    can_create = True

    def is_accessible(self):
        return current_user.is_authenticated and (current_user.has_role('Admin') or current_user.has_role('Employee')
                                                  or current_user.has_role('Manager'))

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

    '''
    def can_edit(self):
        return current_user.is_authenticated and (current_user.has_role('Admin') or current_user.has_role('Manager')
                                                  or current_user.has_role('Employee'))

    def can_delete(self):
        return current_user.is_authenticated and current_user.has_role('Admin')

    def can_create(self):
        return current_user.is_authenticated and (current_user.has_role('Admin') or current_user.has_role('Manager')
                                                  or current_user.has_role('Employee'))

    def can_view_details(self):
        return current_user.is_authenticated and (current_user.has_role('Admin') or current_user.has_role('Manager')
                                                  or current_user.has_role('Employee'))
    '''

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to the login page if the user doesn't have access
        return redirect(url_for('login', next=request.url))

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_on = datetime.utcnow()
        model.updated_on = datetime.utcnow()

        # Example of ensuring correct types
        if form.number_of_doc.data:
            model.number_of_doc = str(form.number_of_doc.data)
        # if form.deadline.data:
        #     model.deadline = form.deadline.data if isinstance(form.deadline.data, datetime) else datetime.strptime(
        #         form.deadline.data, '%Y-%m-%d %H:%M:%S')
        # Handling date fields correctly
        if form.date_of_doc.data:
            if isinstance(form.date_of_doc.data, datetime):
                model.date_of_doc = form.date_of_doc.data
            elif isinstance(form.date_of_doc.data, date):
                model.date_of_doc = datetime.combine(form.date_of_doc.data, datetime.min.time())
            elif isinstance(form.date_of_doc.data, str):
                model.date_of_doc = datetime.strptime(form.date_of_doc.data, '%Y-%m-%d %H:%M:%S')
            else:
                raise ValidationError("Invalid date format for date_of_doc.")

    def create_form(self, obj=None):
        form = super(BaseDataView, self).create_form(obj)
        return form

    def edit_form(self, obj=None):
        form = super(BaseDataView, self).edit_form(obj)
        return form


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


class SignedContractsView(ModelView):
    column_list = ['contract_name', 'contract_status', 'created_by_user',
                   'start_date', 'end_date']

    # Columns that can be edited (if editing were allowed)
    form_columns = ['contract_name', 'contract_type', 'contract_status',
                    'start_date', 'end_date', 'description', 'created_by_user']

    # Columns that can be filtered
    column_filters = ['contract_status', 'start_date', 'end_date']

    # Add search functionality
    column_searchable_list = ['contract_name', 'description']

    # Include inline articles
    inline_models = [ContractArticleInlineModelForm(ContractArticle)]

    def is_accessible(self):
        return current_user.is_authenticated  # Customize your authentication

    def get_query(self):
        return super(SignedContractsView, self).get_query().filter(
            Contract.contract_status.in_(['Signed', 'Active'])
        )

    def get_count_query(self):
        return super(SignedContractsView, self).get_count_query().filter(
            Contract.contract_status.in_(['Signed', 'Active'])
        )

    # Disable editing
    def is_editable(self, obj=None):
        return False

    # Disable creating new entries
    can_create = False
    # Disable deleting entries
    can_delete = False


class ContractArticleAdmin(ModelView):
    can_edit = True
    can_delete = True
    can_create = False
    can_export = True
    can_view_details = True
    can_set_page_size = True
    # Specify the columns to be displayed in the list view
    column_list = ['article_title', 'article_body', 'contract_id', 'contract_name']

    # Use column_formatters to display the contract name properly
    column_formatters = {
        'contract_name': lambda v, c, m, p: m.contract.contract_name if m.contract else 'No Contract'
    }

    # Specify the fields to be shown in the form
    form_columns = ['article_title', 'article_body', 'article_order', 'created_at', 'updated_at']

    # Override the query to filter by contract_id if it is provided in the URL
    def get_query(self):
        query = super(ContractArticleAdmin, self).get_query()

        # Get contract_id from the URL parameters
        contract_id = request.args.get('contract_id')

        if contract_id:
            try:
                query = query.filter(ContractArticle.contract_id == int(contract_id))
            except Exception as e:
                print(f"Error filtering query: {str(e)}")

        return query

    def get_count_query(self):
        count_query = super(ContractArticleAdmin, self).get_count_query()

        # Get contract_id from the URL parameters
        contract_id = request.args.get('contract_id')

        if contract_id:
            try:
                count_query = count_query.filter(ContractArticle.contract_id == int(contract_id))
            except Exception as e:
                print(f"Error filtering count query: {str(e)}")

        return count_query

    def scaffold_form(self):
        form_class = super(ContractArticleAdmin, self).scaffold_form()

        # Add contract_name field as a read-only field
        form_class.contract_name = StringField('Contract Name', render_kw={'readonly': True})

        return form_class

    def create_form(self, obj=None):
        form = super(ContractArticleAdmin, self).create_form(obj)
        # Prefill contract_id and contract_name if provided via URL parameter
        contract_id = request.args.get('contract_id')
        if contract_id:
            contract = db.session.query(Contract).get(contract_id)
            if contract:
                form.contract_name.data = contract.contract_name  # Show contract name

        return form

    def edit_form(self, obj=None):
        form = super(ContractArticleAdmin, self).edit_form(obj)

        # Prefill contract_name field during edit
        if obj and obj.contract:
            form.contract_name.data = obj.contract.contract_name

        return form

    def on_model_change(self, form, model, is_created):
        """
        Ensure the contract_id is set correctly when creating a new article.
        """
        # When creating a new article, set contract_id if available in the URL
        if is_created:  # Only handle logic if creating a new article
            # Use the existing get_create_url to construct the URL with contract_id
            url = self.get_create_url()  # Call get_create_url method
            if not url:  # Check if URL construction failed (missing contract_id?)
                # Handle missing contract_id (e.g., display an error message)
                flash("Contract ID is required for creating a new article.")
                return
            return redirect(url)  # Redirect to the constructed URL
        super(ContractArticleAdmin, self).on_model_change(form, model, is_created)

    def get_create_url(self):
        """
        Override the get_create_url method to include the contract_id in the URL when creating a new article.
        """
        contract_id = request.args.get('contract_id')
        if contract_id:
            return url_for('.create_view', contract_id=contract_id)
        return url_for('.create_view')

    def _handle_view(self, name, **kwargs):
        """
        Handle redirection for the 'create' action to ensure the correct URL.
        """
        if name == 'create_view' and 'contract_id' not in request.args:
            # Check if contract_id is in the query parameters
            contract_id = request.args.get('contract_id')
            if contract_id:
                # Redirect to the create view with the correct contract_id
                return redirect(url_for('.create_view', contract_id=contract_id))
            else:
                # Redirect to a list view or an error page
                return redirect(url_for('.index_view'))  # Adjust to your requirement



class DraftingContractsView(ModelView):
    can_view_details = True
    # Configure the columns to display in the list view
    column_list = ['contract_name', 'contract_status', 'view_articles', 'create_article']

    # Override the form field to make 'contract_type' a select box
    form_overrides = {
        'contract_type': SelectField
    }

    # Define the choices for the select field
    form_args = {
        'contract_type': {
            'choices': [
                ('fornitura servizi', 'Fornitura Servizi'),
                ('fornitura prodotti', 'Fornitura Prodotti'),
                ('compravendita', 'Compravendita'),
                ('altro', 'Altro')
            ]
        }
    }

    # Formatter for the 'view_articles' and 'create_article' columns
    column_formatters = {
        'view_articles': lambda v, c, m, p: DraftingContractsView.view_articles_link(m),
        'create_article': lambda v, c, m, p: DraftingContractsView.create_article_button(m)
    }

    # Static method to create the "View Articles" link
    @staticmethod
    def view_articles_link(obj):
        print(f"Generating view articles link for: {obj}")
        if obj.contract_articles:
            # Pass the specific contract_id as a query parameter
            url = url_for('contract_articles.index_view', contract_id=obj.contract_id)
            return Markup(f'<a href="{url}">View Articles</a>')
        else:
            return Markup('No Articles')

    # Static method to create the "Create Article" button
    @staticmethod
    def create_article_button(obj):
        csrf_token = generate_csrf()  # Generate a fresh CSRF token each time

        # Button that triggers the modal
        modal_trigger = f'''
            <button type="button" class="btn btn-success" data-toggle="modal" data-target="#createArticleModal_{obj.contract_id}">
                Create Article
            </button>
            <!-- Modal -->
            <div class="modal fade" id="createArticleModal_{obj.contract_id}" tabindex="-1" role="dialog" aria-labelledby="createArticleModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg" role="document"> <!-- Add modal-lg for large modal -->
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="createArticleModalLabel">Create New Article for Contract: {obj.contract_name}</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <form action="{url_for('create_article')}" method="POST">
                                <input type="hidden" name="csrf_token" value="{csrf_token}">
                                <input type="hidden" name="contract_id" value="{obj.contract_id}">
                                <div class="form-group">
                                    <label for="article_title">Article Title</label>
                                    <input type="text" class="form-control" id="article_title" name="article_title" required>
                                </div>
                                <div class="form-group">
                                    <label for="article_body">Article Body</label>
                                    <textarea class="form-control" id="article_body" name="article_body" rows="3" required></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">Save Article</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        '''
        return Markup(modal_trigger)

    # Other methods...

    # Other configurations...

    def scaffold_form(self):
        form_class = super(DraftingContractsView, self).scaffold_form()
        return form_class

    def create_form(self, obj=None):
        form = super(DraftingContractsView, self).create_form(obj)
        return form

    def on_model_change(self, form, model, is_created):
        # No need to handle contract_id manually for a new contract creation
        super(DraftingContractsView, self).on_model_change(form, model, is_created)

    def _handle_view(self, name, **kwargs):
        # Remove contract_id check from create_view handling
        return super(DraftingContractsView, self)._handle_view(name, **kwargs)


class UnassignedDocumentsBaseDataView(ModelView):
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
                     'file_path': 'File', 'created_on': 'Date created', 'number_of_doc': 'Doc. #',
                     'fc1': 'Note', 'no_action': 'No doc.'}

    column_default_sort = ('created_on', True)
    column_searchable_list = ('company_id', 'user_id', 'fi0', 'subject_id', 'legal_document_id', 'file_path')
    column_filters = ('company_id', 'user_id', 'fi0', 'subject_id', 'legal_document_id', 'file_path')

    form_excluded_columns = ('company_id', 'status_id', 'created_by', 'updated_on')

    def get_query(self):
        # Query documents that are not yet assigned to any workflow
        query = db.session.query(BaseData)

        # Filter documents with no workflows assigned
        query = query.outerjoin(DocumentWorkflow).filter(DocumentWorkflow.id is None)
        # Filter for documents with workflows

        # Filter based on user roles
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()
                query = query.filter(BaseData.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                query = query.filter(BaseData.user_id == current_user.id)
                return query

        return query

    def get_count_query(self):
        return None  # Disable pagination count query

    def get_list(self, page, sort_column, sort_desc, search, filters, page_size=None):
        try:
            count, data = super().get_list(page, sort_column, sort_desc, search, filters, page_size)

            for item in data:
                item.company_name = item.company.name if item.company else 'n.a.'
                item.user_name = item.user.last_name if item.user else 'n.a.'
                item.interval_name = item.interval.description if item.interval else 'n.a.'
                item.area_name = item.area.name if item.area else 'n.a.'
                item.subarea_name = item.subarea.name if item.subarea else 'n.a.'
                item.subject_name = item.subject.name if item.subject else 'n.a.'
                item.legal_name = item.subject.name if item.subject else 'n.a.'

            return count, data
        except Exception as e:
            app.logger.error(f"Error in get_list: {e}")
            raise  # Re-raise the exception so you still get the 500 if necessary

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                return True
        return False

    @action('action_attach_to_workflow', 'Attach to Workflow',
            'Are you sure you want to assign these documents to a workflow?')
    def action_attach_to_workflow(self, ids):
        try:
            # Log the IDs of the selected documents
            app.logger.info(f"Attach to Workflow triggered for document IDs: {ids}")

            # Parse the document IDs into integers
            document_ids = [int(id_1) for id_1 in ids]

            # Query the selected documents based on their IDs
            selected_documents = BaseData.query.filter(BaseData.id.in_(document_ids)).all()

            # Fetch all available workflows and steps
            workflows = Workflow.query.all()
            steps = Step.query.all()

            # Render the final form with workflows, steps, and selected documents
            return render_template('admin/attach_to_workflow.html',  # The form template
                                   workflows=workflows,
                                   steps=steps,
                                   selected_documents=selected_documents)
        except Exception as e:
            # Log the error and flash a message
            app.logger.error(f"Error in action_attach_to_workflow: {e}")
            flash(f"Error attaching documents to workflow: {e}", 'error')

            # Redirect back to the admin page in case of error
            return redirect(url_for('open_admin_3.index'))  # Replace with the correct admin endpoint

class DocumentsBaseDataDetails(ModelView):
    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True

    name = 'Manage Document Flow'

    # Exclude document number, date, and name since they shouldn't be editable
    form_excluded_columns = ['base_data_id', 'ft1', 'number_of_doc', 'date_of_doc', 'hidden_data']

    column_list = [
        'base_data.number_of_doc',  # Display the document number
        'workflow.name',  # Display workflow name
        'step.name',  # Display step name
        'company_name',  # Company name
        'user_name',  # User name
        'status_id',  # Status ID (dropdown)
        'start_date',
        'end_date',
        'deadline_date',
        'auto_move',
        'open_action',
        'comments'
    ]

    # Only include changeable fields
    form_columns = [
        'workflow_id',
        'step_id',
        'status_id',
        'start_date',
        'end_date',
        'deadline_date',
        'auto_move',
        'open_action',
        'recall_value',
        'recall_unit',
        'comments'  # Add other fields if necessary
    ]

    column_labels = {
        'base_data.number_of_doc': 'Document Number',
        'workflow.name': 'Workflow',
        'step.name': 'Step',
        'company_name': 'Company',
        'user_name': 'User',
        'status_id': 'Status',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'deadline_date': 'Deadline Date',
        'auto_move': 'Auto Transition',
        'open_action': 'Open Action',
        'comments': 'Comments'
    }

    # Use column_formatters to display the company and user names
    column_formatters = {
        'name': lambda view, context, model, name: model.base_data.company.name if model.base_data and model.base_data.company else 'No Company',
        'username': lambda view, context, model, name: model.base_data.user.name if model.base_data and model.base_data.user else 'No User'
    }

    # Add filters for company_id, user_id, comments, workflow, step, and document number
    column_filters = [
        'base_data.company_id',  # Company filter by ID
        'base_data.user_id',  # User filter by ID
        'comments',  # Search by comments
        'workflow.name',  # Search by workflow name
        'step.name',  # Search by step name
        'base_data.number_of_doc'  # Filter by document number
    ]

    # Define how the filters are displayed
    column_searchable_list = [
        'comments',  # Make comments searchable
        'workflow.name',  # Allow search by workflow name
        'step.name',  # Allow search by step name
        'base_data.number_of_doc'  # Allow search by document number
    ]
    # Form customization for only changeable attributes
    form_extra_fields = {
        'workflow_id': QuerySelectField(
            'Workflow',
            query_factory=lambda: Workflow.query.all(),
            get_label='name'
        ),
        'step_id': QuerySelectField(
            'Step',
            query_factory=lambda: Step.query.all(),
            get_label='name'
        ),
        'status_id': QuerySelectField(
            'Status',
            query_factory=lambda: Status.query.all(),  # Fetch all statuses from Status model
            get_label='name',  # Assuming the field to display is 'status_name'
            allow_blank=False
        ),
        'start_date': DateField('Start Date', format='%Y-%m-%d'),
        'end_date': DateField('End Date', format='%Y-%m-%d'),
        'deadline_date': DateField('Deadline Date', format='%Y-%m-%d'),
        'auto_move': BooleanField('Auto Move'),
        'open_action': BooleanField('Open Action'),
        'recall_value': IntegerField('Recall Value', default=0),
        'recall_unit': SelectField('Recall Unit', choices=[(0, 'None'), (1, 'Day'), (2, 'Week'), (3, 'Month')]),
        'comments': TextAreaField('Comments')
    }

    def get_query(self):
        query = super(DocumentsBaseDataDetails, self).get_query()

        if current_user.is_authenticated:
            if current_user.has_role('Admin'):
                # Admins can access all records
                query = query
            elif current_user.has_role('Manager'):
                # Managers can access records from their own company
                company_id = current_user.company_id  # Assuming current_user has a company_id attribute
                query = query.filter(BaseData.company_id == company_id)
            elif current_user.has_role('Employee'):
                # Employees can only access their own records
                user_id = current_user.id
                query = query.filter(BaseData.user_id == user_id)

        # Use select_from() to join DocumentWorkflow explicitly with the ON clause
        query = query.select_from(BaseData).join(
            DocumentWorkflow,
            DocumentWorkflow.base_data_id == BaseData.id
        )

        # Apply sorting: First by 'DocumentWorkflow.updated_on' DESC, then by 'BaseData.date_of_doc' DESC
        query = query.order_by(BaseData.date_of_doc.desc())

        return query

    def on_model_change(self, form, model, is_created):
        # Populate model fields with form data
        form.populate_obj(model)

        # Make sure to save only the IDs for workflow_id and step_id
        model.workflow_id = form.workflow_id.data.id if form.workflow_id.data else None
        model.step_id = form.step_id.data.id if form.step_id.data else None
        model.status_id = form.status_id.data.id if form.status_id.data else None

        # Other logic if necessary
        super().on_model_change(form, model, is_created)

        if is_created:
            model.created_on = datetime.now()  # Set created_on date if this is a new record
        return model

    def create_form(self):
        form = super(DocumentsBaseDataDetails, self).create_form()
        return form

    def edit_form(self, obj=None):
        form = super(DocumentsBaseDataDetails, self).edit_form(obj)
        return form

class DocumentsBaseDataDetails_two(ModelView):
    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True

    name = 'Manage Document Flow'

    # Exclude document number, date, and name
    form_excluded_columns = ['base_data_id', 'ft1', 'number_of_doc', 'date_of_doc', 'hidden_data']

    # Only include changeable fields
    form_columns = [
        'workflow_id',
        'step_id',
        'status_id',
        'start_date',
        'end_date',
        'deadline_date',
        'auto_move',
        'open_action',
        'recall_value',
        'recall_unit',
        'comments'  # Add other fields if necessary
    ]

    # Form customization for only changeable attributes
    form_extra_fields = {
        'workflow_id': QuerySelectField(
            'Workflow',
            query_factory=lambda: Workflow.query.all(),
            get_label='name'
        ),
        'step_id': QuerySelectField(
            'Step',
            query_factory=lambda: Step.query.all(),
            get_label='name'
        ),
        'start_date': DateField('Start Date', format='%Y-%m-%d'),
        'end_date': DateField('End Date', format='%Y-%m-%d'),
        'deadline_date': DateField('Deadline Date', format='%Y-%m-%d'),
        'auto_move': BooleanField('Auto Move'),
        'open_action': BooleanField('Open Action'),
        'recall_value': IntegerField('Recall Value', default=0),
        'recall_unit': SelectField('Recall Unit', choices=[(0, 'None'), (1, 'Day'), (2, 'Week'), (3, 'Month')]),
        'comments': TextAreaField('Comments')
    }

    def get_base_data_choices(self):
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        query = BaseData.query.filter(BaseData.created_on >= one_year_ago)

        if current_user.has_role('Admin'):
            pass
        elif current_user.has_role('Manager'):
            company_id = session.get('company_id')
            query = query.filter(BaseData.company_id == company_id)
        elif current_user.has_role('Employee'):
            user_id = session.get('user_id', current_user.id)
            query = query.filter(BaseData.user_id == user_id)

        choices = [(base_data.id, f"{base_data.number_of_doc} - {base_data.date_of_doc.strftime('%Y-%m-%d') if base_data.date_of_doc else 'No Date'}") for base_data in query.all()]
        return choices

    def on_model_change(self, form, model, is_created):
        # Populate model fields with form data
        form.populate_obj(model)

        # Other logic if necessary
        super().on_model_change(form, model, is_created)

        if is_created:
            model.created_on = datetime.now()  # Set created_on date
        return model

    def create_form(self):
        form = super(DocumentsBaseDataDetails, self).create_form()
        # Ensure document_selection field is added to the form manually
        form.document_selection = QuerySelectField(
            'Select Document',
            query_factory=lambda: BaseData.query.all(),
            get_label='number_of_doc',
            allow_blank=True
        )
        return form

    def edit_form(self, obj=None):
        form = super(DocumentsBaseDataDetails, self).edit_form(obj)
        # Ensure document_selection field is added to the form manually
        form.document_selection = QuerySelectField(
            'Select Document',
            query_factory=lambda: BaseData.query.all(),
            get_label='number_of_doc',
            allow_blank=True
        )
        return form

    @action('action_manage_dws_deadline', 'Deadline Setting', 'Are you sure you want to change the document deadline?')
    def action_manage_dws_deadline(self, ids):
        id_list = [int(id_1) for id_1 in ids]
        column_list = [
            DocumentWorkflow.base_data_id,
            DocumentWorkflow.workflow_id,
            DocumentWorkflow.step_id,
            DocumentWorkflow.status_id,
            DocumentWorkflow.auto_move,
            DocumentWorkflow.start_date,
            DocumentWorkflow.deadline_date,
            DocumentWorkflow.end_date,
            DocumentWorkflow.hidden_data,
            DocumentWorkflow.start_recall,
            DocumentWorkflow.deadline_recall,
            DocumentWorkflow.end_recall,
            DocumentWorkflow.recall_unit
        ]
        selected_documents = DocumentWorkflow.query.with_entities(*column_list).filter(DocumentWorkflow.base_data_id.in_(id_list)).all()
        return render_template('admin/set_documents_deadline.html', selected_documents=selected_documents)

class BaseDataViewCommon(ModelView):
    can_view_details = True
    can_export = True
    inline_models = (DocumentWorkflowInlineForm(DocumentWorkflow),)

    form_extra_fields = {
        'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)
    }

    def __init__(self, model, session, *args, **kwargs):
        self.intervals = kwargs.pop('intervals', None)
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(model, session, *args, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super().scaffold_form()
        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)
        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year
        )
        form_class.no_action = BooleanField('Confirm no documents to attach', default=False)

        config_values = get_config_values(config_type='area_interval', company_id=None,
                                          area_id=self.area_id, subarea_id=None)
        nr_intervals = config_values[0]

        # config_values = get_config_values(config_type='area_interval', company_id=None, area_id=1,
        # subarea_id=None)
        # intervals = get_current_intervals(db.session)

        try:
            current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
        except:
            current_interval = intervals[1]
            pass

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
        document_workflow_records = DocumentWorkflow.query.filter(DocumentWorkflow.base_data_id.in_(ids)).all()
        model_records = self.model.query.filter(self.model.id.in_(ids)).all()
        return self.render('basedata_workflow_step_list.html', step_base_data_records=document_workflow_records, model_records=model_records)

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

    def create_model(self, form):
        try:
            print("Creating a new model instance one")
            # Create a new instance of the model
            model = self.model()
            # Populate the model with form data
            form.populate_obj(model)
            print(f"Model populated: {model.__dict__}")

            # Convert `no_action` field to boolean
            model.no_action = bool(form.no_action.data)

            # If the model has `auto_move` or `open_action`, ensure they're booleans
            if hasattr(model, 'auto_move'):
                model.auto_move = bool(form.auto_move.data)

            if hasattr(model, 'open_action'):
                model.open_action = bool(form.open_action.data)

            self.session.add(model)
            self.session.commit()
            print(f"Model created with values: {model.__dict__}")
            return model
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(f'Failed to create record. {str(ex)}', 'error')
            self.session.rollback()
            return False

    def on_model_change(self, form, model, is_created):
        """
        Override method to convert form values before saving the object.
        """
        try:
            # Ensure 'no_action' is a boolean
            model.no_action = bool(form.no_action.data)

            # Ensure 'auto_move' is a boolean
            if hasattr(model, 'auto_move'):
                model.auto_move = bool(form.auto_move.data)

            # Ensure 'open_action' is a boolean
            if hasattr(model, 'open_action'):
                model.open_action = bool(form.open_action.data)

            # Continue with the normal model save process
            super().on_model_change(form, model, is_created)

        except Exception as ex:
            flash(f'Error during model change: {str(ex)}', 'error')
            raise


class Tabella21_dataView(ModelView):
    create_template = 'admin/create_base_data.html'
    area_id = 2
    subarea_id = 9  # Define subarea_id as a class attribute

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

    column_list = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')
    form_columns = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Specify form columns with dropdowns

    column_labels = {'company_id': 'Comp', 'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'UDD', 'fi2': 'PdR',
                     'fc1': 'Note'}
    column_descriptions = {'company_id': 'Comp', 'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (in formato YYYY)',
                           'fi1': 'Numero UDD', 'fi2': 'Numero PdR',
                           'fc1': 'Note (opzionale)'}

    # Customize inlist for the View class
    column_default_sort = ('company_id', 'fi0')
    column_searchable_list = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')
    # Adjust based on your model structure
    column_filters = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

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
    area_id = 2
    subarea_id = 10  # Define subarea_id as a class attribute

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

    column_list = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')
    form_columns = ('fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Specify form columns with dropdowns

    column_labels = {'company_id': 'Comp.', 'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'UDD', 'fi2': 'PdR',
                     'fc1': 'Note'}
    column_descriptions = {'company_id': 'Company', 'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (in formato YYYY)',
                           'fi1': 'Numero UDD', 'fi2': 'Numero PdR',
                           'fc1': 'Note (opzionale)'}

    # Customize inlist for the View class
    column_default_sort = ('company_id', 'fi0')
    column_searchable_list = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Adjust based on your model structure
    column_filters = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fc1')  # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

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


class Tabella24_dataView(ModelView):
    create_template = 'admin/create_base_data.html'
    area_id = 2
    subarea_id = 12  # Define subarea_id as a class attribute

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

    column_list = ('company_id', 'interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    form_columns = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    # Specify form columns with dropdowns

    column_labels = {'company_id': 'Comp.', 'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Totale', 'fi2': 'IVI', 'fi3': 'Altri',
                     'fi4': 'Lavori semplici', 'fi5': 'Lavori complessi',
                     'fc1': 'Note'}
    column_descriptions = {'company_id': 'Comp.', 'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)',
                           'fi1': 'Totale', 'fi2': 'di cui: IVI', 'fi3': 'altri',
                           'fi4': 'Lavori semplici', 'fi5': 'Lavori complessi',
                           'fc1': 'Inserire commento'}

    # Customize inlist for class dataView
    column_default_sort = ('company_id', 'fi0')
    column_searchable_list = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    # Adjust based on your model structure
    column_filters = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fc1')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

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
    area_id = 2
    subarea_id = 13  # Define subarea_id as a class attribute

    # Specify the fields to be edited inline using XEditableWidget
    column_editable_list = ['fc1']
    # Customize the widget for inline editing
    form_widget_args = {
        'fc1': {'widget': XEditableWidget()},
    }

    def __init__(self, *args, **kwargs):
        self.intervals = kwargs.pop('intervals', None)
        super().__init__(*args, **kwargs)
        self.subarea_id = Tabella25_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Tabella25_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    column_list = ('company_id', 'subject_id', 'interval_ord', 'fi0',
                    'fi1', 'fi2', 'fi7', 'fi4', 'fi5', 'fi6', 'fn1', 'fn2', 'fn3', 'fn4', 'fn5', 'fn6', 'fc1')
    form_columns = ('subject_id', 'interval_ord', 'fi0',
                    'fi1', 'fi2', 'fi4', 'fi5', 'fc1')

    column_labels = {
        'company_id': 'Comp.',
        'subject_id': 'Fascia di domanda',
        'interval_ord': 'Periodo',
        'fi0': 'Anno',
        'fi1': 'Numero POD/PDR vendita IVI (*)',
        'fi2': 'Numero POD/PDR vendita Altri (*)',
        'fi7': 'Totale Nr.',
        'fi4': 'Quantità Smc/KWh vendita IVI (*)',
        'fi5': 'Quantità Smc/KWh vendita Altri (*)',
        'fi6': 'Totale Q',

        'fn1': '% Nr IVI',
        'fn2': '% Nr Altri',
        'fn3': '% Nr Totale',
        'fn4': '% Q IVI',
        'fn5': '% Q Altri',
        'fn6': '% Q Totale',

        'fc1': 'Note'
    }
    column_descriptions = {
        'company_id': 'Comp.',
        'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
        'fi0': 'Inserire anno (es. 2024)',

        'fi1': 'Numero POD/PDR nel settore di vendita IVI',
        'fi2': 'Numero POD/PDR nel settore di vendita Altri',
        'fi7': 'Totale numero POD/PDR complessivo IVI e Altri',
        'fi4': 'Quantità Smc/KWh vendita IVI',
        'fi5': 'Quantità Smc/KWh vendita Altri',
        'fi6': 'Totale quantità complessiva IVI e Altri',

        'fn1': 'quota di mercato numero POD/PDR IVI sul totale',
        'fn2': 'quota di mercato numerp POD/PDR Altri sul totale',
        'fn3': 'Totale quota di mercato numero POD/PDR',
        'fn4': 'quota di mercato numero POD/PDR IVI',
        'fn5': 'quota di mercato numero POD/PDR Altri',
        'fn6': 'Totale quota di mercato numero POD/PDR',

        'fc1': 'Inserire commento al report complessivo del periodo'
    }

    column_default_sort = ('company_id', 'fi0')
    column_searchable_list = ('company_id', 'fi0', 'interval_ord', 'subject.name', 'fi1', 'fi2', 'fi4', 'fi5', 'fc1')
    column_filters = ('company_id', 'fi0', 'interval_ord', 'subject.name', 'fi1', 'fi2', 'fi4', 'fi5', 'fc1')

    form_excluded_columns = ('user_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    # formaters*

    def _subject_formatter(view, context, model, name):
        if model.subject_id:
            if isinstance(model.subject, Subject):
                return model.subject.name
            else:
                return Subject.query.get(model.subject_id).name
        return ''

    column_formatters = {
        'subject_id': _subject_formatter,
        'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
        'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,
        'fn3': lambda view, context, model, name: "%.2f" % model.fn3 if model.fn3 is not None else None,
        'fn4': lambda view, context, model, name: "%.2f" % model.fn4 if model.fn4 is not None else None,
        'fn5': lambda view, context, model, name: "%.2f" % model.fn5 if model.fn5 is not None else None,
        'fn6': lambda view, context, model, name: "%.2f" % model.fn6 if model.fn6 is not None else None,
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

    def scaffold_form(self):
        form_class = super(Tabella25_dataView, self).scaffold_form()

        form_class.subject_id = SelectField(
            'Fascia di domanda',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Utenti").all()]
        )

        current_year = datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
        default_year = str(current_year)

        form_class.fi0 = SelectField(
            'Anno',
            coerce=int,
            choices=year_choices,
            default=default_year
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
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

        return form_class

    form_create_rules = ('subject_id', 'interval_ord', 'fi0',
                         'fi1', 'fi2', 'fi4', 'fi5',
                         'fc1')

    def create_model(self, form):
        try:
            model = self.model()
            form.populate_obj(model)
            comp_id = None
            if current_user.is_authenticated:
                model.user_id = current_user.id
                created_by = current_user.username

                # calculate totals
                # NUMBERS
                if form.fi1.data and form.fi2.data and form.fi1.data + form.fi2.data != 0:
                    model.fi7 = form.fi1.data + form.fi2.data
                    model.fn1 = 100 * form.fi1.data / (form.fi1.data + form.fi2.data)
                    model.fn2 = 100 * form.fi2.data / (form.fi1.data + form.fi2.data)
                    model.fn3 = 100 * (form.fi1.data / (form.fi1.data + form.fi2.data) +
                                       form.fi2.data / (form.fi1.data + form.fi2.data))
                else:
                    model.fi7 = 0
                    model.fn1 = 0
                    model.fn2 = 0
                    model.fn3 = 0

                # QUANT
                if form.fi4.data and form.fi5.data and form.fi4.data + form.fi5.data != 0:
                    model.fi6 = form.fi4.data + form.fi5.data
                    model.fn4 = 100 * form.fi4.data / (form.fi4.data + form.fi5.data)
                    model.fn5 = 100 * form.fi5.data / (form.fi4.data + form.fi5.data)
                    model.fn6 = 100 * (form.fi4.data / (form.fi4.data + form.fi5.data) +
                                       form.fi5.data / (form.fi4.data + form.fi5.data))
                else:
                    model.fi6 = 0
                    model.fn4 = 0
                    model.fn5 = 0
                    model.fn6 = 0

                try:
                    company_user = CompanyUsers.query.filter_by(user_id=current_user.id).first()
                    comp_id = company_user.company_id if company_user else None
                    model.company_id = comp_id
                except Exception:
                    model.company_id = None

                model.record_type = 'control_area'
                model.data_type = self.subarea_name
                model.created_by = created_by
                model.created_on = datetime.now()

                model.area_id = self.area_id
                model.subarea_id = self.subarea_id
                config_values = get_config_values(config_type='area_interval', company_id=comp_id,
                                                  area_id=self.area_id,
                                                  subarea_id=self.subarea_id)
                model.interval_id = config_values[0]


                self.session.add(model)
                self.session.commit()
                return model
            else:
                raise ValidationError('User not authenticated.')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(f'Failed to create record. {str(ex)}', 'error')
            self.session.rollback()
            return False


    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id
                ).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                query = query.filter(self.model.user_id == current_user.id)
                return query

        return query.filter(self.model.id < 0)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                return True

        return False

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        form.populate_obj(model)

        fi0_value = model.fi0

        now = datetime.now()
        current_year = now.year
        if fi0_value > current_year:
            raise ValidationError(
                f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

        if is_created:
            model.created_on = datetime.now()
            pass
        else:
            pass

        user_id = current_user.id
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

        fields_to_check = ['fi0',
                           'fi1', 'fi2', 'fi4', 'fi5',
                           'interval_ord']

        for field_name in fields_to_check:
            if form[field_name].data is None:
                raise ValidationError(f"Field {field_name} cannot be null")
        if form.interval_ord.data > 52 or form.interval_ord.data < 0:
            raise ValidationError(
                "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
            pass
        if form.fi0.data < 2000 or form.fi0.data > 2099:
            raise ValidationError("Please check the year")
            pass

        if (form.fi1.data is None or form.fi2.data is None or form.fi4.data is None or form.fi5.data is None):
            raise ValidationError("Please enter all required data.")

        if form.fi1.data + form.fi2.data + form.fi4.data + form.fi5.data == 0:
            raise ValidationError("Please enter non-zero values for the fields.")

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
        model.updated_on = datetime.now()
        model.company_id = company_id

        # calculate totals
        # NUMBERS
        if form.fi1.data and form.fi2.data and form.fi1.data + form.fi2.data != 0:
            model.fi7 = form.fi1.data + form.fi2.data
            model.fn1 = 100 * form.fi1.data / (form.fi1.data + form.fi2.data)
        else:
            model.fi7 = 0
            model.fn1 = 0

        if (form.fi1.data + form.fi2.data) != 0:
            model.fn2 = 100 * form.fi2.data / (form.fi1.data + form.fi2.data)
        else:
            model.fn2 = 0

        if (form.fi1.data + form.fi2.data) != 0:
            model.fn3 = 100 * (form.fi1.data / (form.fi1.data + form.fi2.data) +
                        form.fi2.data / (form.fi1.data + form.fi2.data))

        # QUANT
        if form.fi4.data and form.fi5.data and form.fi4.data + form.fi5.data != 0:
            model.fi6 = form.fi4.data + form.fi5.data
            model.fn4 = 100 * form.fi4.data / (form.fi4.data + form.fi5.data)
        else:
            model.fi6 = -1
            model.fn4 = 0
        if (form.fi4.data + form.fi5.data) != 0:
            model.fn5 = 100 * form.fi5.data / (form.fi4.data + form.fi5.data)
        else:
            model.fn5 = 0

        if (form.fi4.data + form.fi5.data) != 0:
            model.fn6 = 100 * (form.fi4.data / (form.fi4.data + form.fi5.data) +
                        form.fi5.data / (form.fi4.data + form.fi5.data))

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

    column_list = ('company_id', 'interval_ord', 'fi0',
                   'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4',
                   'fi6', 'fn5', 'fi7', 'fn6', 'fi8', 'fi9', 'fn7', 'fi10', 'fi11', 'fn8',
                   'fc1')
    form_columns = ('interval_ord', 'fi0',
                    'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4',
                    'fi6', 'fn5', 'fi7', 'fn6', 'fi8', 'fi9', 'fn7', 'fi10', 'fi11', 'fn8',
                    'fc1')
    # Specify form columns with dropdowns

    column_labels = {'company_id': 'Comp.', 'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Totale rich. (a)', 'fi2': 'IVI (b)', 'fn1': '% (c)', 'fi3': 'Esito positivo (d)',
                     'fn2': '% (e)', 'fi4': 'Esito negativo (f)', 'fn3': '% (g)',
                     'fi5': 'ALTRI (h)', 'fn4': '% (i)',
                     'fi6': 'Esito pos. (j)', 'fn5': '% (k)', 'fi7': 'Esito neg. (l)', 'fn6': '% (m)',
                     'fi8': 'Rich. altri su PdR altri (n)', 'fi9': 'Esito neg. (p)', 'fn7': '% (q)',
                     'fi10': 'Rich altri su PdR IVI (r)', 'fi11': 'Esito neg. (s)', 'fn8': '% (t)',
                     'fc1': 'Note'}
    column_descriptions = {'company_id': 'Comp.',
                           'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
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
    column_default_sort = ('company_id', 'fi0')
    column_searchable_list = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5',
                              'fi6', 'fi7', 'fi8', 'fi9', 'fi10', 'fi11', 'fc1')
    # Adjust based on your model structure
    column_filters = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fi4', 'fi5',
                      'fi6', 'fi7', 'fi8', 'fi9', 'fi10', 'fi11', 'fc1')

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
        'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,
        'fn3': lambda view, context, model, name: "%.2f" % model.fn3 if model.fn3 is not None else None,
        'fn4': lambda view, context, model, name: "%.2f" % model.fn4 if model.fn4 is not None else None,
        'fn5': lambda view, context, model, name: "%.2f" % model.fn5 if model.fn5 is not None else None,
        'fn6': lambda view, context, model, name: "%.2f" % model.fn6 if model.fn6 is not None else None,
        'fn7': lambda view, context, model, name: "%.2f" % model.fn7 if model.fn7 is not None else None,
        'fn8': lambda view, context, model, name: "%.2f" % model.fn8 if model.fn8 is not None else None,
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
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
    area_id = 2
    subarea_id = 15  # Define subarea_id as a class attribute

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

    column_list = ('company_id', 'interval_ord', 'fi0', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    form_columns = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    # Specify form columns with dropdowns

    column_labels = {'company_id': 'Comp.',
                     'interval_ord': 'Periodo', 'fi0': 'Anno',
                     'fi1': 'Totale', 'fi2': 'domestico', 'fn1': '%',
                     'fi3': 'IVI', 'fn2': '%',
                     'fi4': 'altri', 'fn3': '%',
                     'fi5': 'PdR', 'fn4': 'Tasso switching PdR',
                     'fc1': 'Note'}
    column_descriptions = {'company_id': 'Comp.',
                           'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                           'fi0': 'Inserire anno (es. 2024)',
                           'fi1': 'Totale', 'fi2': 'di cui: domestico', 'fn1': 'domestico, in percentuale',
                           'fi3': 'di cui IVI', 'fn2': 'IVI, in percentuale',
                           'fi4': 'altri', 'fn3': 'altri, in percentuale',
                           'fi5': 'PdR', 'fn4': 'Tasso switching PdR (percentuale)',
                           'fc1': 'Inserire commento'}

    # Customize inlist for the View class
    column_default_sort = ('company_id', 'fi0')
    column_searchable_list = (
    'company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    # Adjust based on your model structure
    column_filters = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fn1', 'fi3', 'fn2', 'fi4', 'fn3', 'fi5', 'fn4', 'fc1')
    # Adjust based on your model structure

    # Specify fields to be excluded from the form
    form_excluded_columns = ('user_id', 'status_id', 'created_by', 'created_on', 'updated_on')

    column_formatters = {
        'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
        'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,
        'fn3': lambda view, context, model, name: "%.2f" % model.fn3 if model.fn3 is not None else None,
        'fn4': lambda view, context, model, name: "%.2f" % model.fn4 if model.fn4 is not None else None,
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
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


class DocumentUploadView(BaseDataViewCommon):
    # Template for creating records
    create_template = 'admin/area_1/create_base_data_8.html'
    can_create = False
    can_delete = False
    can_edit = False
    can_export = True
    can_view_details = True
    # Area and subarea identifiers for filtering records
    area_id = 3
    subarea_id = 1

    # Columns to display in the list view
    column_list = ('company_id', 'fi0', 'interval_ord', 'subject', 'ft1', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')

    # Columns to include in the form view
    form_columns = ('fi0', 'interval_ord', 'ft1', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')

    # Custom labels for columns
    column_labels = {
        'company_id': 'Comp.',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'subject': 'Oggetto',
        'ft1': 'Codice documento',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegati',
        'no_action': 'Conferma assenza doc.',
        'fc2': 'Note'
    }

    # Descriptions for form fields
    column_descriptions = {
        'company_id': 'Company',
        'ft1': 'Codice interno documento',
        'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fi0': 'Inserire anno (es. 2024)',
        'subject_id': 'Seleziona oggetto',
        'fc2': 'Note',
        'file_path': 'Allegati',
        'no_action': 'Dichiarazione di assenza di documenti (1)'
    }

    # Filters to use in the list view
    column_filters = ('company_id', 'ft1', 'subject', 'fc2', 'no_action')

    # Fields to exclude from the form view
    form_excluded_columns = ('user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    # Define column formatters to display the first 5 letters of the company name
    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

    def __init__(self, model, session, *args, **kwargs):
        # Initialize with intervals, area_id, and subarea_id passed as kwargs
        super().__init__(model, session, *args, **kwargs)

    def on_model_change(self, form, model, is_created):
        """
        Override method to add custom logic before saving the object.
        """
        try:
            # Validate no-action checkbox logic
            self._validate_no_action(model, form)
            # Uncheck no-action if a document is uploaded
            self._uncheck_if_document(model, form)

            # Custom logic if a new model is created
            if is_created:
                # Example: Set some initial values or states for the new record
                model.created_on = datetime.utcnow()
                flash(f'New document upload created successfully.', 'success')
            else:
                flash(f'Document upload updated successfully.', 'success')
        except Exception as ex:
            flash(f'Error during model change: {str(ex)}', 'error')
            raise

    def _validate_no_action(self, model, form):
        """
        Validate that the 'no_action' field is appropriately set.
        """
        super()._validate_no_action(model, form)

    def _uncheck_if_document(self, model, form):
        """
        Ensure 'no_action' field is unset if a document is uploaded.
        """
        super()._uncheck_if_document(model, form)

from sqlalchemy import desc, func

def get_query(self):
    """
    Override default query to filter records by area, subarea, and user role.
    Sort by workflow, step, deadline_date (descending), and end_date (descending if deadline_date is null).
    """
    # Base query filtered by area and subarea
    # query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
    # Base query filtered by area_id in [1, 3] and specific subarea_id
    query = self.session.query(self.model).filter(
        self.model.area_id.in_([1, 3]),  # Filtering for area_id in [1, 3]
        self.model.subarea_id == self.subarea_id  # Filtering by exact subarea_id
    )
    # Role-based filtering
    if current_user.is_authenticated:
        if current_user.has_role('Admin'):
            # Admins can access all documents, no additional filtering needed
            print("Admin access: fetching all documents.")
        elif current_user.has_role('Manager'):
            # Managers can access documents of their own company_id
            subquery = db.session.query(CompanyUsers.company_id).filter(CompanyUsers.user_id == current_user.id).subquery()
            query = query.filter(self.model.company_id.in_(subquery))
            print(f"Manager access: fetching documents for company_id(s) {subquery}.")
        elif current_user.has_role('Employee'):
            # Employees can only access their own documents
            query = query.filter(self.model.user_id == current_user.id)
            print(f"Employee access: fetching documents for user_id {current_user.id}.")
    else:
        print("Unauthenticated access: returning empty query.")
        query = query.filter(self.model.id < 0)

    # Sorting by workflow, step, and deadline_date or end_date
    query = query.join(self.model.document_workflows) \
        .join(DocumentWorkflow.workflow) \
        .join(DocumentWorkflow.step) \
        .order_by(
            Workflow.name,  # Sorting by workflow name
            Step.name,  # Sorting by step name
            desc(func.coalesce(DocumentWorkflow.deadline_date, DocumentWorkflow.end_date))  # Sort by deadline_date or end_date if deadline_date is null
        )

    return query


class DocumentUploadViewExisting(BaseDataViewCommon):
    # Template for creating records
    can_delete = False
    can_export = True
    can_create = False
    can_edit = True
    can_set_page_size = True
    can_view_details = True

    create_template = 'admin/area_1/create_base_data_8.html'

    def __init__(self, model, session, area_id=3, subarea_id=1, *args, **kwargs):
        # Initialize with intervals, area_id, and subarea_id passed as kwargs
        super().__init__(model, session, *args, **kwargs)
        self.area_id = area_id  # Define area_id as an instance variable
        self.subarea_id = subarea_id  # Define area_id as an instance variable

    # Override form fields
    form_overrides = {
        'number_of_doc': QuerySelectField
    }

    # form_args for static attributes
    '''
    form_args = {
        'number_of_doc': {
            'query_factory': lambda: db.session.query(BaseData).filter(BaseData.area_id.in_([1, 3])).all(),
            'get_label': lambda x: f"{x.ft1} - {x.number_of_doc}/{x.date_of_doc.strftime('%Y-%m-%d')}",
            # Combine doc number and date
            'allow_blank': False
        }
    }
    '''

    form_args = {
        'number_of_doc': {
            'query_factory': lambda: db.session.query(BaseData).filter(BaseData.area_id.in_([1, 3])).all(),
            'get_label': lambda
                x: f"{x.ft1} - {x.number_of_doc}/{x.date_of_doc.strftime('%Y-%m-%d') if x.date_of_doc else 'No Date'}/",
            # Handle None case
            'allow_blank': False
        }
    }

    # Columns to display in the list view
    column_list = ('company_id', 'fi0', 'interval_ord', 'subject', 'ft1', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')

    # Columns to include in the form view
    form_columns = ('fi0', 'interval_ord', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')

    # Custom labels for columns
    column_labels = {
        'company_id': 'Comp.',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'subject': 'Oggetto',
        'ft1': 'Codice documento',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegati',
        'no_action': 'Conferma assenza doc.',
        'fc2': 'Note'
    }

    # Descriptions for form fields
    column_descriptions = {
        'company_id': 'Company',
        'ft1': 'Codice interno documento',
        'interval_ord': '(inserire il numero; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fi0': 'Inserire anno (es. 2024)',
        'subject_id': 'Seleziona oggetto',
        'ft1': 'Codice documento/Prot. n.',
        'fc2': 'Note',
        'file_path': 'Allegati',
        'no_action': 'Dichiarazione di assenza di documenti (1)'
    }

    # Filters to use in the list view
    column_filters = ('company_id', 'ft1', 'subject', 'fc2', 'no_action')

    # Fields to exclude from the form view
    form_excluded_columns = ('user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    # Define column formatters to display the first 5 letters of the company name
    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

    # Prefill form to ensure the correct document is selected
    def on_form_prefill(self, form, id):
        """
        Override the form prefill method to select the correct document.
        """
        # Get the current document record based on the ID
        document = db.session.query(self.model).get(id)

        # Set the selected document in the 'number_of_doc' field
        form.number_of_doc.data = document  # Pre-select the document in the dropdown

        # If the form contains other data to prepopulate, handle it here (e.g., workflows, steps, etc.)
        super(DocumentUploadViewExisting, self).on_form_prefill(form, id)

    def get_query(self):
        """
        Override default query to filter records by area, subarea, and user role.
        """
        # Base query filtered by area and subarea
        # query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        # Base query filtered by area_id in [1, 3] and specific subarea_id

        query = self.session.query(self.model).filter(
            self.model.area_id.in_([1, 3]),  # Filtering for area_id in [1, 3]
            self.model.subarea_id == self.subarea_id  # Filtering by exact subarea_id
        ).order_by(desc(self.model.updated_on),
                   desc(self.model.created_on))  # Order by updated_on DESC, then created_on DESC

        if current_user.is_authenticated:
            if current_user.has_role('Admin'):
                # Admins can access all documents, no additional filtering needed
                print("Admin access: fetching all documents.")
                return query
            elif current_user.has_role('Manager'):
                # Managers can access documents of their own company_id
                subquery = db.session.query(CompanyUsers.company_id).filter(CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
                print(f"Manager access: fetching documents for company_id(s) {subquery}.")
            elif current_user.has_role('Employee'):
                # Employees can only access their own documents
                query = query.filter(self.model.user_id == current_user.id)
                print(f"Employee access: fetching documents for user_id {current_user.id}.")
        else:
            print("Unauthenticated access: returning empty query.")
            # If the user is not authenticated or does not have any specific role, return an empty query
            query = query.filter(self.model.id < 0)

        # Sorting by workflow, step, and deadline_date or end_date
        query = query.join(self.model.document_workflows) \
            .join(DocumentWorkflow.workflow) \
            .join(DocumentWorkflow.step) \
            .order_by(
            Workflow.name,  # Sorting by workflow name
            Step.name,  # Sorting by step name
            desc(func.coalesce(DocumentWorkflow.deadline_date, DocumentWorkflow.end_date))
            # Sort by deadline_date or end_date if deadline_date is null
        )
        return query

    def on_model_change(self, form, model, is_created):
        """
        Override method to add custom logic before saving the object.
        """
        try:
            # Ensure number_of_doc is selected
            if not form.number_of_doc.data:
                flash('Error: Document number is required.', 'error')
                form.number_of_doc.errors.append('Document number cannot be empty.')
                return False

            selected_document = form.number_of_doc.data

            # Ensure document date is present
            if not selected_document.date_of_doc:
                flash('Error: Document date is required.', 'error')
                form.number_of_doc.errors.append('Document date cannot be empty.')
                return False

            # Assign values to the model
            model.number_of_doc = str(selected_document.number_of_doc)
            model.base_data_id = int(selected_document.id)

            # Clear any existing duplicate warning messages first
            for message in get_flashed_messages():
                if 'Duplicate workflow/step detected' in message:
                    # This clears the existing warning messages if a change has been made
                    continue

            # Debugging: Check the document workflows entries
            if hasattr(form, 'document_workflows'):
                for i, dwf_item in enumerate(form.document_workflows.entries):  # Use entries from the inline form

                    # Access workflow and step objects
                    workflow = dwf_item.workflow.data  # This accesses the selected workflow object
                    step = dwf_item.step.data  # This accesses the selected step object

                    # Get the workflow_id and step_id from the selected objects
                    workflow_id = workflow.id if workflow else None
                    step_id = step.id if step else None

                    if not workflow_id or not step_id:
                        flash('Error: Workflow and Step are required.', 'error')
                        return False

                    # Before querying for potential duplicates, ensure the session is flushed
                    self.session.flush()  # This ensures changes are reflected in the database

                    # Query for potential duplicates
                    results = self.session.query(DocumentWorkflow).filter_by(
                        base_data_id=model.base_data_id,
                        workflow_id=workflow_id,
                        step_id=step_id
                    ).all()

                    if len(results) > 1:
                        flash(f'Warning: Duplicate workflow/step detected ({len(results)}-C).', 'error')
                        return False  # Prevent further saving

                    # Ensure start_date is set
                    if dwf_item.start_date.data is None:
                        dwf_item.start_date.data = datetime.utcnow()

                    # Set end_date to one month after start_date if not set
                    if dwf_item.end_date.data is None:
                        dwf_item.end_date.data = dwf_item.start_date.data + timedelta(days=30)

            # Proceed with the default behavior if all checks pass
            return super(DocumentUploadViewExisting, self).on_model_change(form, model, is_created)

        except Exception as e:
            db.session.rollback()
            flash(f'Error during save: {str(e)}', 'error')
            print(f"Error during save: {e}")  # Log the error for debugging
            return False

    def create_model(self, form):
        """
        Override create_model to handle deletions, prevent saving duplicates, and handle errors.
        """
        try:
            with self.session.no_autoflush:
                # Handle deletions first by checking the hidden 'delete' field
                if hasattr(form, 'document_workflows'):
                    to_remove = []
                    for dwf_item in form.document_workflows.entries:
                        if dwf_item.delete.data:
                            # Ensure dwf_item.data is an object and not a dictionary
                            if isinstance(dwf_item.data, DocumentWorkflow) and dwf_item.data.id:
                                dwf_to_delete = self.session.query(DocumentWorkflow).get(dwf_item.data.id)
                                if dwf_to_delete:
                                    self.session.delete(dwf_to_delete)
                            to_remove.append(dwf_item)

                    # Remove the deleted entries from the form's entries after processing
                    for dwf_item in to_remove:
                        form.document_workflows.entries.remove(dwf_item)

                # Ensure number_of_doc and date_of_doc are present
                if not form.number_of_doc.data:
                    flash('Error: Document number is required.', 'error')
                    form.number_of_doc.errors.append('Document number cannot be empty.')
                    raise ValidationError('Document number is missing')

                selected_document = form.number_of_doc.data

                if not selected_document.date_of_doc:
                    flash('Error: Document date is required.', 'error')
                    form.number_of_doc.errors.append('Document date cannot be empty.')
                    raise ValidationError('Document date is missing')

                # Proceed with creating the model
                model = self.model()
                model.number_of_doc = str(selected_document.number_of_doc)
                model.base_data_id = int(selected_document.id)

                # Validate document workflows after deletions
                if hasattr(form, 'document_workflows'):
                    for dwf_item in form.document_workflows.entries:
                        workflow = dwf_item.workflow.data
                        step = dwf_item.step.data

                        # Check if workflow and step are objects and not dicts
                        if isinstance(workflow, dict) or isinstance(step, dict):
                            flash('Error: Invalid workflow or step selection.', 'error')
                            raise ValidationError('Invalid workflow or step')

                        workflow_id = workflow.id if workflow else None
                        step_id = step.id if step else None

                        if not workflow_id or not step_id:
                            flash('Error: Workflow and Step are required.', 'error')
                            raise ValidationError('Workflow and Step are required')

                        # Query for potential duplicates
                        results = self.session.query(DocumentWorkflow).filter_by(
                            base_data_id=model.base_data_id,
                            workflow_id=workflow_id,
                            step_id=step_id
                        ).all()

                        if len(results) > 1:
                            flash(f'Warning: Duplicate workflow/step detected ({len(results)}-CM).', 'error')
                            raise ValidationError('Duplicate workflow/step found')

                        # Ensure start_date and end_date are set
                        if dwf_item.start_date.data is None:
                            dwf_item.start_date.data = datetime.utcnow()

                        if dwf_item.end_date.data is None:
                            dwf_item.end_date.data = dwf_item.start_date.data + timedelta(days=30)

                # Commit all changes at the end
                return super(DocumentUploadViewExisting, self).create_model(form)

        except ValidationError as e:
            flash(str(e), 'error')
            return False

        except IntegrityError as e:
            self.session.rollback()
            if 'uq_base_data_workflow_step' in str(e.orig):
                flash('Error: The combination of Document, Workflow, and Step must be unique.', 'error')
            else:
                flash('Error: A database error occurred.', 'error')
            return False

        except Exception as e:
            self.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}', 'error')
            return False

    def update_model(self, form, model):
        """
        Override update_model to handle inline form deletions, prevent saving when duplicates are detected, and clear old messages.
        """
        try:
            with self.session.no_autoflush:
                # Clear any existing duplicate warning messages first
                for message in get_flashed_messages():
                    if 'Duplicate workflow/step detected' in message:
                        continue  # Skip the duplicate message

                # Ensure number_of_doc and date_of_doc are present
                if not form.number_of_doc.data:
                    flash('Error: Document number is required.', 'error')
                    form.number_of_doc.errors.append('Document number cannot be empty.')
                    raise ValidationError('Document number is missing')

                selected_document = form.number_of_doc.data

                if not selected_document.date_of_doc:
                    flash('Error: Document date is required.', 'error')
                    form.number_of_doc.errors.append('Document date cannot be empty.')
                    raise ValidationError('Document date is missing')

                # Extract number_of_doc or id instead of assigning the whole object
                model.number_of_doc = str(selected_document.number_of_doc)
                model.base_data_id = int(selected_document.id)

                # Handle deletions first by checking the delete flag
                if hasattr(form, 'document_workflows'):
                    to_remove = []
                    for dwf_item in form.document_workflows.entries:
                        if dwf_item.delete.data:
                            # Ensure dwf_item.data is an object and not a dictionary
                            if isinstance(dwf_item.data, DocumentWorkflow) and dwf_item.data.id:
                                dwf_to_delete = self.session.query(DocumentWorkflow).get(dwf_item.data.id)
                                if dwf_to_delete:
                                    self.session.delete(dwf_to_delete)
                            to_remove.append(dwf_item)

                    for dwf_item in to_remove:
                        form.document_workflows.entries.remove(dwf_item)

                # Flush all deletions to the database
                self.session.flush()

                # Validate document workflows after deletions
                if hasattr(form, 'document_workflows'):
                    for dwf_item in form.document_workflows.entries:
                        workflow = dwf_item.workflow.data
                        step = dwf_item.step.data

                        # Check if workflow and step are objects and not dicts
                        if isinstance(workflow, dict) or isinstance(step, dict):
                            flash('Error: Invalid workflow or step selection.', 'error')
                            raise ValidationError('Invalid workflow or step')

                        workflow_id = workflow.id if workflow else None
                        step_id = step.id if step else None

                        if not workflow_id or not step_id:
                            flash('Error: Workflow and Step are required.', 'error')
                            return False

                        # Query for potential duplicates
                        results = self.session.query(DocumentWorkflow).filter_by(
                            base_data_id=model.base_data_id,
                            workflow_id=workflow_id,
                            step_id=step_id
                        ).all()

                        if len(results) > 1:
                            flash(f'Warning: Duplicate workflow/step detected ({len(results)}-UM).', 'error')
                            return False  # Prevent saving the record if duplicates are found

                        # Ensure start_date is set
                        if dwf_item.start_date.data is None:
                            dwf_item.start_date.data = datetime.utcnow()

                        if dwf_item.end_date.data is None:
                            dwf_item.end_date.data = dwf_item.start_date.data + timedelta(days=30)

                # Commit all changes
                return super(DocumentUploadViewExisting, self).update_model(form, model)

        except ValidationError as e:
            flash(str(e), 'error')
            return False

        except IntegrityError as e:
            self.session.rollback()
            if 'uq_base_data_workflow_step' in str(e.orig):
                flash('Error: The combination of Document, Workflow, and Step must be unique.', 'error')
            else:
                flash('Error: A database error occurred.', 'error')
            return False

        except Exception as e:
            self.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}', 'error')
            return False

    def handle_view_exception(self, exc):
        """
        Handle view exceptions and ensure rollback of the session.
        """
        # Rollback the session in case of IntegrityError or general errors
        if isinstance(exc, IntegrityError) or isinstance(exc, ValidationError):
            db.session.rollback()
            flash("The transaction was rolled back due to an error.", 'error')
            return False  # Suppress Flask-Admin's default behavior for this error
        return super(DocumentUploadViewExisting, self).handle_view_exception(exc)

    def _validate_no_action(self, model, form):
        """
        Validate that the 'no_action' field is appropriately set.
        """
        # Custom validation logic here
        if not form.no_action.data and not form.file_path.data:
            raise ValueError("You must either upload a document or check 'no_action'.")

    def _uncheck_if_document(self, model, form):
        """
        Ensure 'no_action' field is unset if a document is uploaded.
        """
        # Custom logic to uncheck 'no_action' if a document is uploaded
        if form.file_path.data:
            form.no_action.data = False

class AttiDataView(BaseDataView):
    create_template = 'admin/area_1/create_base_data_2.html'
    area_id = 1
    subarea_id = 2

    # Adjusted order of fields
    column_list = ('company_id', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_columns = ('number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')

    column_labels = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegato',
        'no_action': 'Conferma assenza doc.',
        'subject_id': 'Oggetto',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'fc2': 'Note'
    }

    column_descriptions = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento allegato',
        'date_of_doc': 'Data documento allegato',
        'file_path': 'Allegato',
        'no_action': 'Dichiarazione di assenza di documenti da allegare (1)',
        'subject_id': 'Seleziona oggetto',
        'fi0': 'Inserire anno di riferimento (in formato YYYY)',
        'interval_ord': '(inserire il periodo; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fc2': 'Note',
    }

    # Define column formatters to display the first 5 letters of the company name
    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

    column_filters = ('company_id', 'number_of_doc', 'date_of_doc', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_excluded_columns = ('company_id', 'user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    def __init__(self, model, session, **kwargs):
        self.intervals = kwargs.pop('intervals', [])
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(model, session, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super().scaffold_form()

        current_year = datetime.now().year
        year_choices = [(year, year) for year in range(current_year - 11, current_year + 1)]
        default_year = current_year

        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year,
            widget=Select2Widget()
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        if self.intervals:
            current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
            first_element = current_interval[0] if current_interval else None
            interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]
        else:
            first_element = None
            interval_choices = []

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,
            default=first_element,
            widget=Select2Widget()
        )

        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1='Legale').all()],
            widget=Select2Widget()
        )

        form_class.no_action = BooleanField('Dichiarazione di assenza di documenti')  # Use BooleanField
        form_class.fc2 = StringField('Note')

        # Ensure base_path is set for FileUploadField
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        form_class.file_path = FileUploadField('Allegati',
                                               base_path=upload_folder)  # Correctly display file upload button

        return form_class

    def on_model_change(self, form, model, is_created):

        # Custom validation logic
        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null")

        if not form.date_of_doc.data or not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.file_path.data and not form.no_action.data:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

        if form.file_path.data and form.no_action.data:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

        # Populate the necessary fields
        model.user_id = current_user.id
        model.company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        model.area_id = self.area_id
        model.subarea_id = self.subarea_id
        model.interval_id = form.interval_ord.data  # Assuming interval_id is same as interval_ord
        model.created_by = current_user.id
        # Check for duplicate documents
        existing_document = self.session.query(self.model).filter_by(
            number_of_doc=form.number_of_doc.data,
            date_of_doc=form.date_of_doc.data,
            company_id=model.company_id,
            subarea_id=model.subarea_id,
            area_id=model.area_id,
            subject_id=form.subject_id.data,
        ).first()
        if existing_document and existing_document.id != model.id:
            raise ValidationError('A document with the same number, date, subarea, area, and subject already exists.')

        if is_created:
            model.status_id = 1
            model.created_on = datetime.now()
        else:
            model.status_id = 14 # Updated

        super().on_model_change(form, model, is_created)

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def create_form(self, obj=None):
        form = super(AttiDataView, self).create_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form

    def edit_form(self, obj=None):
        form = super(AttiDataView, self).edit_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form


class ContenziosiDataView(BaseDataView):
    create_template = 'admin/area_1/create_base_data_4.html'
    area_id = 1
    subarea_id = 3

    # Adjusted order of fields
    column_list = ('company_id', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_columns = ('number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')

    column_labels = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegato',
        'no_action': 'Conferma assenza doc.',
        'subject_id': 'Oggetto',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'fc2': 'Note'
    }

    column_descriptions = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento allegato',
        'date_of_doc': 'Data documento allegato',
        'file_path': 'Allegato',
        'no_action': 'Dichiarazione di assenza di documenti da allegare (1)',
        'subject_id': 'Seleziona oggetto',
        'fi0': 'Inserire anno di riferimento (in formato YYYY)',
        'interval_ord': '(inserire il periodo; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fc2': 'Note',
    }

    column_filters = ('company_id', 'number_of_doc', 'date_of_doc', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_excluded_columns = ('company_id', 'user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

    def __init__(self, model, session, **kwargs):
        self.intervals = kwargs.pop('intervals', [])
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(model, session, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super().scaffold_form()

        current_year = datetime.now().year
        year_choices = [(year, year) for year in range(current_year - 11, current_year + 1)]
        default_year = current_year

        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year,
            widget=Select2Widget()
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        if self.intervals:
            current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
            first_element = current_interval[0] if current_interval else None
            interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]
        else:
            first_element = None
            interval_choices = []

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,
            default=first_element,
            widget=Select2Widget()
        )

        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1='Legale').all()],
            widget=Select2Widget()
        )

        form_class.no_action = BooleanField('Dichiarazione di assenza di documenti')  # Use BooleanField
        form_class.fc2 = StringField('Note')

        # Ensure base_path is set for FileUploadField
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        form_class.file_path = FileUploadField('Allegati',
                                               base_path=upload_folder)  # Correctly display file upload button

        return form_class

    def on_model_change(self, form, model, is_created):

        # Custom validation logic
        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null")

        if not form.date_of_doc.data or not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.file_path.data and not form.no_action.data:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

        if form.file_path.data and form.no_action.data:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

        # Populate the necessary fields
        model.user_id = current_user.id
        model.company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        model.area_id = self.area_id
        model.subarea_id = self.subarea_id
        model.interval_id = form.interval_ord.data  # Assuming interval_id is same as interval_ord
        model.created_by = current_user.id
        # Check for duplicate documents
        existing_document = self.session.query(self.model).filter_by(
            number_of_doc=form.number_of_doc.data,
            date_of_doc=form.date_of_doc.data,
            company_id=model.company_id,
            subarea_id=model.subarea_id,
            area_id=model.area_id,
            subject_id=form.subject_id.data,
        ).first()
        if existing_document and existing_document.id != model.id:
            raise ValidationError('A document with the same number, date, subarea, area, and subject already exists.')

        if is_created:
            model.status_id = 1
            model.created_on = datetime.now()
        else:
            model.status_id = 14 # Updated

        super().on_model_change(form, model, is_created)

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def create_form(self, obj=None):
        form = super(ContenziosiDataView, self).create_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form

    def edit_form(self, obj=None):
        form = super(ContenziosiDataView, self).edit_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form


class ContingenciesDataView(BaseDataView):
    create_template = 'admin/area_1/create_base_data_4.html'
    area_id = 1
    subarea_id = 4

    # Adjusted order of fields
    column_list = ('company_id', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_columns = ('number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')

    column_labels = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegato',
        'no_action': 'Conferma assenza doc.',
        'subject_id': 'Oggetto',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'fc2': 'Note'
    }

    column_descriptions = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento allegato',
        'date_of_doc': 'Data documento allegato',
        'file_path': 'Allegato',
        'no_action': 'Dichiarazione di assenza di documenti da allegare (1)',
        'subject_id': 'Seleziona oggetto',
        'fi0': 'Inserire anno di riferimento (in formato YYYY)',
        'interval_ord': '(inserire il periodo; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fc2': 'Note',
    }

    column_filters = ('company_id', 'number_of_doc', 'date_of_doc', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_excluded_columns = ('company_id', 'user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }

    def __init__(self, model, session, **kwargs):
        self.intervals = kwargs.pop('intervals', [])
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(model, session, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super().scaffold_form()

        current_year = datetime.now().year
        year_choices = [(year, year) for year in range(current_year - 11, current_year + 1)]
        default_year = current_year

        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year,
            widget=Select2Widget()
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        if self.intervals:
            current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
            first_element = current_interval[0] if current_interval else None
            interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]
        else:
            first_element = None
            interval_choices = []

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,
            default=first_element,
            widget=Select2Widget()
        )

        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1='Legale').all()],
            widget=Select2Widget()
        )

        form_class.no_action = BooleanField('Dichiarazione di assenza di documenti')  # Use BooleanField
        form_class.fc2 = StringField('Note')

        # Ensure base_path is set for FileUploadField
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        form_class.file_path = FileUploadField('Allegati',
                                               base_path=upload_folder)  # Correctly display file upload button

        return form_class

    def on_model_change(self, form, model, is_created):

        # Custom validation logic
        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null")

        if not form.date_of_doc.data or not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.file_path.data and not form.no_action.data:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

        if form.file_path.data and form.no_action.data:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

        # Populate the necessary fields
        model.user_id = current_user.id
        model.company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        model.area_id = self.area_id
        model.subarea_id = self.subarea_id
        model.interval_id = form.interval_ord.data  # Assuming interval_id is same as interval_ord
        model.created_by = current_user.id
        # Check for duplicate documents
        existing_document = self.session.query(self.model).filter_by(
            number_of_doc=form.number_of_doc.data,
            date_of_doc=form.date_of_doc.data,
            company_id=model.company_id,
            subarea_id=model.subarea_id,
            area_id=model.area_id,
            subject_id=form.subject_id.data,
        ).first()
        if existing_document and existing_document.id != model.id:
            raise ValidationError('A document with the same number, date, subarea, area, and subject already exists.')

        if is_created:
            model.status_id = 1
            model.created_on = datetime.now()
        else:
            model.status_id = 14 # Updated

        super().on_model_change(form, model, is_created)

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def create_form(self, obj=None):
        form = super(ContingenciesDataView, self).create_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form

    def edit_form(self, obj=None):
        form = super(ContingenciesDataView, self).edit_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form



class IniziativeDsoAsDataView(BaseDataView):
    create_template = 'admin/area_1/create_base_data_8.html'
    area_id = 1
    subarea_id = 6

    # Adjusted order of fields
    column_list = ('company_id', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_columns = ('number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')

    column_labels = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegato',
        'no_action': 'Conferma assenza doc.',
        'subject_id': 'Oggetto',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'fc2': 'Note'
    }

    column_descriptions = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento allegato',
        'date_of_doc': 'Data documento allegato',
        'file_path': 'Allegato',
        'no_action': 'Dichiarazione di assenza di documenti da allegare (1)',
        'subject_id': 'Seleziona oggetto',
        'fi0': 'Inserire anno di riferimento (in formato YYYY)',
        'interval_ord': '(inserire il periodo; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fc2': 'Note',
    }

    column_filters = ('company_id', 'number_of_doc', 'date_of_doc', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_excluded_columns = ('company_id', 'user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }
    def __init__(self, model, session, **kwargs):
        self.intervals = kwargs.pop('intervals', [])
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(model, session, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super().scaffold_form()

        current_year = datetime.now().year
        year_choices = [(year, year) for year in range(current_year - 11, current_year + 1)]
        default_year = current_year

        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year,
            widget=Select2Widget()
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        if self.intervals:
            current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
            first_element = current_interval[0] if current_interval else None
            interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]
        else:
            first_element = None
            interval_choices = []

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,
            default=first_element,
            widget=Select2Widget()
        )

        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1='Legale').all()],
            widget=Select2Widget()
        )

        form_class.no_action = BooleanField('Dichiarazione di assenza di documenti')  # Use BooleanField
        form_class.fc2 = StringField('Note')

        # Ensure base_path is set for FileUploadField
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        form_class.file_path = FileUploadField('Allegati',
                                               base_path=upload_folder)  # Correctly display file upload button

        return form_class

    def on_model_change(self, form, model, is_created):

        # Custom validation logic
        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null")

        if not form.date_of_doc.data or not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.file_path.data and not form.no_action.data:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

        if form.file_path.data and form.no_action.data:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

        # Populate the necessary fields
        model.user_id = current_user.id
        model.company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        model.area_id = self.area_id
        model.subarea_id = self.subarea_id
        model.interval_id = form.interval_ord.data  # Assuming interval_id is same as interval_ord
        model.created_by = current_user.id
        # Check for duplicate documents
        existing_document = self.session.query(self.model).filter_by(
            number_of_doc=form.number_of_doc.data,
            date_of_doc=form.date_of_doc.data,
            company_id=model.company_id,
            subarea_id=model.subarea_id,
            area_id=model.area_id,
            subject_id=form.subject_id.data,
        ).first()
        if existing_document and existing_document.id != model.id:
            raise ValidationError('A document with the same number, date, subarea, area, and subject already exists.')

        if is_created:
            model.status_id = 1
            model.created_on = datetime.now()
        else:
            model.status_id = 14 # Updated

        super().on_model_change(form, model, is_created)

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def create_form(self, obj=None):
        form = super(IniziativeDsoAsDataView, self).create_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form

    def edit_form(self, obj=None):
        form = super(IniziativeDsoAsDataView, self).edit_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form




class IniziativeAsDsoDataView(BaseDataView):
    create_template = 'admin/area_1/create_base_data_7.html'
    area_id = 1
    subarea_id = 7

    # Adjusted order of fields
    column_list = ('company_id', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_columns = ('number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')

    column_labels = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegato',
        'no_action': 'Conferma assenza doc.',
        'subject_id': 'Oggetto',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'fc2': 'Note'
    }

    column_descriptions = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento allegato',
        'date_of_doc': 'Data documento allegato',
        'file_path': 'Allegato',
        'no_action': 'Dichiarazione di assenza di documenti da allegare (1)',
        'subject_id': 'Seleziona oggetto',
        'fi0': 'Inserire anno di riferimento (in formato YYYY)',
        'interval_ord': '(inserire il periodo; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fc2': 'Note',
    }

    column_filters = ('company_id', 'number_of_doc', 'date_of_doc', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_excluded_columns = ('company_id', 'user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }
    def __init__(self, model, session, **kwargs):
        self.intervals = kwargs.pop('intervals', [])
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(model, session, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super().scaffold_form()

        current_year = datetime.now().year
        year_choices = [(year, year) for year in range(current_year - 11, current_year + 1)]
        default_year = current_year

        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year,
            widget=Select2Widget()
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        if self.intervals:
            current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
            first_element = current_interval[0] if current_interval else None
            interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]
        else:
            first_element = None
            interval_choices = []

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,
            default=first_element,
            widget=Select2Widget()
        )

        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1='Legale').all()],
            widget=Select2Widget()
        )

        form_class.no_action = BooleanField('Dichiarazione di assenza di documenti')  # Use BooleanField
        form_class.fc2 = StringField('Note')

        # Ensure base_path is set for FileUploadField
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        form_class.file_path = FileUploadField('Allegati',
                                               base_path=upload_folder)  # Correctly display file upload button

        return form_class

    def on_model_change(self, form, model, is_created):

        # Custom validation logic
        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null")

        if not form.date_of_doc.data or not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.file_path.data and not form.no_action.data:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

        if form.file_path.data and form.no_action.data:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

        # Populate the necessary fields
        model.user_id = current_user.id
        model.company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        model.area_id = self.area_id
        model.subarea_id = self.subarea_id
        model.interval_id = form.interval_ord.data  # Assuming interval_id is same as interval_ord
        model.created_by = current_user.id

        # Check for duplicate documents
        existing_document = self.session.query(self.model).filter_by(
            number_of_doc=form.number_of_doc.data,
            date_of_doc=form.date_of_doc.data,
            company_id=model.company_id,
            subarea_id=model.subarea_id,
            area_id=model.area_id,
            subject_id=form.subject_id.data,
        ).first()
        if existing_document and existing_document.id != model.id:
            raise ValidationError('A document with the same number, date, subarea, area, and subject already exists.')

        if is_created:
            model.status_id = 1
            model.created_on = datetime.now()
        else:
            model.status_id = 14 # Updated

        super().on_model_change(form, model, is_created)

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def create_form(self, obj=None):
        form = super(IniziativeAsDsoDataView, self).create_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form

    def edit_form(self, obj=None):
        form = super(IniziativeAsDsoDataView, self).edit_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form


class IniziativeDsoDsoDataView(BaseDataView):
    create_template = 'admin/area_1/create_base_data_8.html'
    area_id = 1
    subarea_id = 8

    # Adjusted order of fields
    column_list = ('company_id', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_columns = ('number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'subject_id', 'fi0', 'interval_ord', 'fc2')

    column_labels = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento',
        'date_of_doc': 'Data documento',
        'file_path': 'Allegato',
        'no_action': 'Conferma assenza doc.',
        'subject_id': 'Oggetto',
        'fi0': 'Anno di rif.',
        'interval_ord': 'Periodo di rif.',
        'fc2': 'Note'
    }

    column_descriptions = {
        'company_id': 'Comp.',
        'number_of_doc': 'Nr. documento allegato',
        'date_of_doc': 'Data documento allegato',
        'file_path': 'Allegato',
        'no_action': 'Dichiarazione di assenza di documenti da allegare (1)',
        'subject_id': 'Seleziona oggetto',
        'fi0': 'Inserire anno di riferimento (in formato YYYY)',
        'interval_ord': '(inserire il periodo; es. 1: primo quadrimestre; 2: secondo ecc.)',
        'fc2': 'Note',
    }

    column_filters = ('company_id', 'number_of_doc', 'date_of_doc', 'subject_id', 'fi0', 'interval_ord', 'fc2')
    form_excluded_columns = ('company_id', 'user_id', 'status_id', 'created_on', 'updated_on', 'data_type')

    column_formatters = {
        'company_id': lambda view, context, model, name: (
            model.company.name[:5] if model.company and model.company.name else 'N/A')
    }
    def __init__(self, model, session, **kwargs):
        self.intervals = kwargs.pop('intervals', [])
        self.area_id = kwargs.pop('area_id', None)
        self.subarea_id = kwargs.pop('subarea_id', None)
        super().__init__(model, session, **kwargs)
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def scaffold_form(self):
        form_class = super().scaffold_form()

        current_year = datetime.now().year
        year_choices = [(year, year) for year in range(current_year - 11, current_year + 1)]
        default_year = current_year

        form_class.fi0 = SelectField(
            'Anno di rif.',
            coerce=int,
            choices=year_choices,
            default=default_year,
            widget=Select2Widget()
        )

        config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                          subarea_id=None)
        nr_intervals = config_values[0]

        if self.intervals:
            current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
            first_element = current_interval[0] if current_interval else None
            interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]
        else:
            first_element = None
            interval_choices = []

        form_class.interval_ord = SelectField(
            'Periodo di rif.',
            coerce=int,
            choices=interval_choices,
            default=first_element,
            widget=Select2Widget()
        )

        form_class.subject_id = SelectField(
            'Tipo di documento',
            validators=[InputRequired()],
            coerce=int,
            choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1='Legale').all()],
            widget=Select2Widget()
        )

        form_class.no_action = BooleanField('Dichiarazione di assenza di documenti')  # Use BooleanField
        form_class.fc2 = StringField('Note')

        # Ensure base_path is set for FileUploadField
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        form_class.file_path = FileUploadField('Allegati',
                                               base_path=upload_folder)  # Correctly display file upload button

        return form_class

    def on_model_change(self, form, model, is_created):

        # Custom validation logic
        if not form.fi0.data or not form.interval_ord.data:
            raise ValidationError("Time interval reference fields cannot be null")

        if not form.date_of_doc.data or not form.number_of_doc.data:
            raise ValidationError("Document data is missing.")

        if form.date_of_doc.data.year != form.fi0.data:
            raise ValidationError("Date of document must be consistent with the reporting year.")

        if not form.file_path.data and not form.no_action.data:
            raise ValidationError(
                'If no file exists, then this absence must be acknowledged by checking the "no documents" box.')

        if form.file_path.data and form.no_action.data:
            raise ValidationError(
                'The no-document box is checked but a document was uploaded - please confirm either of the two.')

        # Populate the necessary fields
        model.user_id = current_user.id
        model.company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
        model.area_id = self.area_id
        model.subarea_id = self.subarea_id
        model.interval_id = form.interval_ord.data  # Assuming interval_id is same as interval_ord
        model.created_by = current_user.id
        # Check for duplicate documents
        existing_document = self.session.query(self.model).filter_by(
            number_of_doc=form.number_of_doc.data,
            date_of_doc=form.date_of_doc.data,
            company_id=model.company_id,
            subarea_id=model.subarea_id,
            area_id=model.area_id,
            subject_id=form.subject_id.data,
        ).first()
        if existing_document and existing_document.id != model.id:
            raise ValidationError('A document with the same number, date, subarea, area, and subject already exists.')

        if is_created:
            model.status_id = 1
            model.created_on = datetime.now()
        else:
            model.status_id = 14 # Updated

        super().on_model_change(form, model, is_created)

    def get_query(self):
        query = self.session.query(self.model).filter_by(area_id=self.area_id, subarea_id=self.subarea_id)
        if current_user.is_authenticated:
            if current_user.has_role('Admin') or current_user.has_role('Authority'):
                return query
            elif current_user.has_role('Manager'):
                subquery = db.session.query(CompanyUsers.company_id).filter(
                    CompanyUsers.user_id == current_user.id).subquery()
                query = query.filter(self.model.company_id.in_(subquery))
            elif current_user.has_role('Employee'):
                return query.filter(self.model.user_id == current_user.id)
        return query.filter(self.model.id < 0)

    def create_form(self, obj=None):
        form = super(IniziativeDsoDsoDataView, self).create_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form

    def edit_form(self, obj=None):
        form = super(IniziativeDsoDsoDataView, self).edit_form(obj)
        form.subject_id = form.subject_id
        form.number_of_doc = form.number_of_doc
        form.date_of_doc = form.date_of_doc
        form.file_path = form.file_path
        form.no_action = form.no_action
        form.fi0 = form.fi0
        form.interval_ord = form.interval_ord
        form.fc2 = form.fc2
        return form

# END OF SIMILAR VIEWS


def create_admin_views(app, intervals):

    with app.app_context():
        # Custom admin view

        class CustomFlussiDataView(ModelView):
            create_template = 'admin/area_1/create_base_data_1.html'
            area_id = 1
            subarea_id = 1
            inline_models = (BaseDataInlineModelForm(BaseDataInline),)

            def __init__(self, *args, **kwargs):
                self.intervals = kwargs.pop('intervals', None)
                super().__init__(*args, **kwargs)
                self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

            form_extra_fields = {
                'file_path': CustomFileUploadField('File', base_path=config.UPLOAD_FOLDER)
            }

            column_editable_list = ['fc1']
            form_widget_args = {
                'fc1': {'widget': XEditableWidget()},
            }

            form_columns = ['interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fc1']
            column_list = ['company_id', 'interval_ord', 'fi0', 'lexic', 'subject', 'fi1', 'fi2', 'fi3', 'fc1']

            column_labels = {
                'company_id': 'Comp.',
                'interval_ord': 'Periodo',
                'fi0': 'Anno',
                'fi1': 'Totale',
                'fi2': 'IVI',
                'fi3': 'Altri',
                'fc1': 'Notes'
            }

            # Define column formatters to display the first 5 letters of the company name
            column_formatters = {
                'company_id': lambda view, context, model, name: (
                    model.company.name[:5] if model.company and model.company.name else 'N/A')
            }

            def scaffold_form(self):
                form_class = super(CustomFlussiDataView, self).scaffold_form()
                current_year = datetime.now().year
                year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 2)]
                default_year = str(current_year)

                form_class.lexic_id = SelectField(
                    'Tipo pre-complaint',
                    validators=[InputRequired()],
                    coerce=int,
                    choices=[(lexic.id, lexic.name) for lexic in Lexic.query.filter_by(category="Precomplaint").all()]
                )

                form_class.subject_id = SelectField(
                    'Oggetto',
                    validators=[InputRequired()],
                    coerce=int,
                    choices=[(subject.id, subject.name) for subject in Subject.query.filter_by(tier_1="Utenti").all()]
                )

                form_class.fi0 = SelectField(
                    'Anno',
                    coerce=int,
                    choices=year_choices,
                    default=default_year
                )

                config_values = get_config_values(config_type='area_interval', company_id=None, area_id=self.area_id,
                                                  subarea_id=None)
                nr_intervals = config_values[0]
                current_interval = [t[2] for t in self.intervals if t[0] == nr_intervals]
                first_element = current_interval[0] if current_interval else None
                interval_choices = [(str(interv), str(interv)) for interv in range(1, nr_intervals + 1)]

                form_class.interval_ord = SelectField(
                    'Periodo',
                    coerce=int,
                    choices=interval_choices,
                    default=first_element
                )

                return form_class

            def get_query(self):
                query = self.session.query(self.model)

                # Filter by area_id and subarea_id
                query = query.filter_by(area_id=self.area_id, subarea_id=self.subarea_id)

                # Filter by company_id based on user role (optional):
                if current_user.is_authenticated:
                    if current_user.has_role('Admin') or current_user.has_role('Authority'):
                        # No additional filtering needed for Admin or Authority roles
                        pass
                    elif current_user.has_role('Manager'):
                        # Filter for Manager's companies
                        subquery = db.session.query(CompanyUsers.company_id).filter(
                            CompanyUsers.user_id == current_user.id).subquery()
                        query = query.filter(self.model.company_id.in_(subquery))
                    elif current_user.has_role('Employee'):
                        # Filter for Employee's records
                        query = query.filter(self.model.user_id == current_user.id)

                # Additional filtering based on other criteria (optional):
                # You can add further filtering logic here based on other fields
                # in your model, like specific dates, statuses, etc.

                return query
            def create_model(self, form):

                try:
                    model = self.model()
                    form.populate_obj(model)

                    # Ensure required fields are not null
                    # Ensure required fields are not null
                    if model.fi1 is None or model.fi2 is None or model.fi3 is None:
                        raise ValidationError("Fields 'Total', 'IVI', and 'A' cannot be null.")

                    # Check if at least one inline record exists
                    if model.fi3 != 0 and not model.base_data_inlines:
                        raise ValidationError("At least one Vendor record is required.")

                    # Ensure that the sum of fi2 and fi3 equals fi1
                    if model.fi1 != model.fi2 + model.fi3:
                        raise ValidationError("The sum of 'IVI' and 'A' must equal 'Total'.")

                    # ... other logic ...

                    # Ensure the relationship is correctly defined
                    if not hasattr(model, 'base_data_inlines'):
                        raise Exception('base_data_inlines relationship is not defined on the model')

                    # Set area_id and subarea_id from your class attributes
                    model.area_id = self.area_id
                    model.subarea_id = self.subarea_id


                    # Determine company_id based on user role or logic (handle None case)
                    try:
                        company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                    except:
                        company_id = None  # Consider handling this case differently if necessary
                    model.company_id = company_id

                    # Set user_id from current user
                    model.user_id = current_user.id

                    self.session.add(model)
                    self.session.commit()

                    # Update record_type for each inline model
                    for inline in model.base_data_inlines:
                        inline.record_type = 'pre-complaint'
                        self.session.add(inline)

                    self.session.commit()

                    # ... remaining code ...

                    return model

                except Exception as ex:
                    if not self.handle_view_exception(ex):
                        raise
                    flash(f'Failed to create record. {str(ex)}', 'error')
                    self.session.rollback()
                    return False

            def on_model_change(self, form, model, is_created):
                super().on_model_change(form, model, is_created)
                form.populate_obj(model)
                if is_created:
                    model.created_on = datetime.now()
                else:
                    pass

                user_id = current_user.id
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None
                    pass

                area_id = self.area_id
                subarea_id = self.subarea_id
                subarea_name = self.subarea_name
                status_id = 1

                config_values = get_config_values(config_type='area_interval', company_id=company_id,
                                                  area_id=self.area_id, subarea_id=self.subarea_id)
                interval_id = config_values[0]
                interval_ord = form.interval_ord.data
                year_id = form.fi0.data
                lexic_id = form.lexic_id.data
                subject_id = form.subject_id.data

                record_type = 'control_area'
                data_type = self.subarea_name
                legal_document_id = None

                if form.fi2.data is None or form.fi3.data is None:
                    raise ValidationError("Please enter all required data.")

                if (form.fi1.data + form.fi2.data + form.fi3.data == 0) or (
                        form.fi1.data < 0 or form.fi2.data < 0 or form.fi3.data < 0) or (
                        form.fi1.data != form.fi2.data + form.fi3.data):
                    raise ValidationError("Please check the values you entered.")

                # Check if at least one inline record exists
                if model.fi3 != 0 and not model.base_data_inlines:
                    raise ValidationError("At least one Vendor record is required.")

                if form.fi0.data == None or form.interval_ord.data == None:
                    raise ValidationError(f"Time interval reference fields cannot be null")

                if form.interval_ord.data > 3 or form.interval_ord.data < 0:
                    raise ValidationError(
                        "Period must be less than or equal to the number of fractions (e.g. 4 for quarters, 12 for months)")
                    pass

                if form.fi0.data < 2000 or form.fi0.data > 2099:
                    raise ValidationError("Please check the year")
                    pass

                with current_app.app_context():
                    result, message = check_status_extended(is_created, company_id, lexic_id, subject_id,
                                                            legal_document_id, interval_ord, interval_id, year_id,
                                                            area_id, subarea_id, form.fi1.data, None, None, None, None,
                                                            None, None, None, None, datetime.today(), db.session)

                if result == False:
                    raise ValidationError(message)
                    pass

                model.lexic_id = lexic_id
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
                model.legal_document_id = legal_document_id

                # Update record_type for each inline model
                for inline in model.base_data_inlines:
                    print('set precomplaint for', inline)
                    inline.record_type = 'pre-complaint'

                if is_created:
                    self.session.add(model)
                else:
                    self.session.merge(model)
                self.session.commit()

                return model


        # =================================================================================================================
        # Define custom form for CustomAdminIndexView2
        # =================================================================================================================
        # class CustomForm2(BaseData):
        class CustomForm21(FlaskForm):
            fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2099)])
            interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])
            fi1 = IntegerField('fi1', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi2 = IntegerField('fi2', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

            fc1 = StringField('fc1')

        class CustomForm22(FlaskForm):
            fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2099)])
            interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])
            fi1 = IntegerField('fi1', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi2 = IntegerField('fi2', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

            fc1 = StringField('fc1')

        class CustomTabella23DataView(ModelView):

            create_template = 'admin/create_base_data.html'
            area_id = 2
            subarea_id = 11  # Define subarea_id as a class attribute

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
                # self.class_name = self.__class__.__name__  # Store the class name
                self.subarea_id = CustomTabella23DataView.subarea_id  # Initialize subarea_id in __init__
                self.area_id = CustomTabella23DataView.area_id  # Initialize area_id in __init__
                self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

            column_list = ('company_id', 'interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
            form_columns = ('interval_ord', 'fi0', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
            # Specify form columns with dropdowns

            column_labels = {'company_id': 'Comp.', 'interval_ord': 'Periodo', 'fi0': 'Anno',
                             'fi1': 'Totale', 'fi2': 'PdR domestico *', 'fi3': 'PdR non domestico *',
                             'fn1': 'Tasso Switching (%)', 'fn2': '',
                             'fc1': 'Note'}
            column_descriptions = {
                'company_id': 'Comp.', 'interval_ord': '(inserire il numero - es. 1 - primo quadrimestre; 2 - secondo ecc.)',
                'fi0': 'Inserire anno (in formato YYYY)',
                'fi1': '(numero)', 'fi2': 'di cui: PdR domestico', 'fi3': 'PdR non domestico',
                'fn1': 'di cui % domestico', 'fn2': '% non domestico',
                'fc1': '(opzionale)'}

            # Customize inlist for the class
            column_default_sort = ('company_id', 'fi0')
            column_searchable_list = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
            # Adjust based on your model structure
            column_filters = ('company_id', 'fi0', 'interval_ord', 'fi1', 'fi2', 'fi3', 'fn1', 'fn2', 'fc1')
            # Adjust based on your model structure

            # Specify fields to be excluded from the form
            form_excluded_columns = ('user_id', 'status_id', 'created_by', 'created_on', 'updated_on')

            column_formatters = {
                'company_id': lambda view, context, model, name: (
                    model.company.name[:5] if model.company and model.company.name else 'N/A'),
                'fn1': lambda view, context, model, name: "%.2f" % model.fn1 if model.fn1 is not None else None,
                'fn2': lambda view, context, model, name: "%.2f" % model.fn2 if model.fn2 is not None else None,
            }

            def scaffold_form(self):
                form_class = super(CustomTabella23DataView, self).scaffold_form()

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
                model = super(CustomTabella23DataView, self).create_model(form)
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
                query = super(CustomTabella23DataView, self).get_query().filter_by(data_type=self.subarea_name)

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
                # Custom validation logic
                fi0_value = form.fi0.data
                now = datetime.now()
                current_year = now.year
                if fi0_value > current_year:
                    raise ValidationError(
                        f"Year in fi0 field cannot be in the future. Please enter a year less than or equal to {current_year}.")

                if form.fi2.data is None or form.fi3.data is None:
                    raise ValidationError("fi2 and fi3 cannot be null")
                if form.fi2.data == 0 and form.fi3.data == 0:
                    raise ValidationError("Please enter at least one non-zero value for fi2 or fi3")

                # Calculate fi1
                model.fi1 = form.fi2.data + form.fi3.data

                # Calculate fn1 and fn2
                if model.fi1 != 0:
                    model.fn1 = round(100 * (form.fi2.data / model.fi1), 2)  # Percentage of fi2 in fi1
                    model.fn2 = round(100 * (form.fi3.data / model.fi1), 2)  # Percentage of fi3 in fi1
                else:
                    model.fn1 = 0
                    model.fn2 = 0

                # Additional validation if needed
                if form.fi0.data < 2000 or form.fi0.data > 2199:
                    raise ValidationError("Please check the year")

                if form.interval_ord.data > 52 or form.interval_ord.data < 0:
                    raise ValidationError("Period must be between 0 and 52 inclusive")

                # Perform actions relevant to both creation and edit:
                user_id = current_user.id  # Get the current user's ID or any other criteria
                try:
                    company_id = CompanyUsers.query.filter_by(user_id=current_user.id).first().company_id
                except:
                    company_id = None

                area_id = self.area_id
                subarea_id = self.subarea_id
                status_id = 1
                config_values = get_config_values(config_type='area_interval', company_id=company_id,
                                                  area_id=self.area_id, subarea_id=self.subarea_id)
                interval_id = config_values[0]
                subject_id = None
                legal_document_id = None
                record_type = 'control_area'
                data_type = self.subarea_name

                if form.fi0.data is None or form.interval_ord.data is None:
                    raise ValidationError(f"Time interval reference fields cannot be null")

                with current_app.app_context():
                    result, message = check_status(is_created, company_id, None, None, form.fi0.data,
                                                   form.interval_ord.data, interval_id, area_id, subarea_id,
                                                   datetime.today(), db.session)

                model.user_id = user_id
                model.data_type = data_type
                model.record_type = record_type
                model.area_id = area_id
                model.subarea_id = subarea_id
                model.interval_id = interval_id
                model.status_id = status_id
                model.legal_document_id = legal_document_id
                model.subject_id = subject_id
                model.updated_on = datetime.now()  # Set the updated_on timestamp
                model.company_id = company_id

                if not result:
                    raise ValidationError(message)

                # Assign form data to model explicitly
                model.fi0 = form.fi0.data
                model.interval_ord = form.interval_ord.data
                model.fi2 = form.fi2.data
                model.fi3 = form.fi3.data
                model.fc1 = form.fc1.data

                # Commit the changes to the database
                if is_created:
                    self.session.add(model)
                else:
                    self.session.merge(model)
                self.session.commit()

                # Debug print after commit
                print(
                    f"Model after commit: fi0={model.fi0}, interval_ord={model.interval_ord}, fi2={model.fi2}, fi3={model.fi3}, fi1={model.fi1}, fn1={model.fn1}, fn2={model.fn2}")

                return model

        class CustomForm24(FlaskForm):
            fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2099)])
            interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])
            fi1 = IntegerField('fi1', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi2 = IntegerField('fi2', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

            fc1 = StringField('fc1')

        class CustomForm25(FlaskForm):
            fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2099)])
            interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])
            fi1 = IntegerField('fi1', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi2 = IntegerField('fi2', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

            fc1 = StringField('fc1')

        class CustomForm26(FlaskForm):
            fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2099)])
            interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])
            fi1 = IntegerField('fi1', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi2 = IntegerField('fi2', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

            fc1 = StringField('fc1')

        class CustomForm27(FlaskForm):
            fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2099)])
            interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])
            fi1 = IntegerField('fi1', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi2 = IntegerField('fi2', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi4 = IntegerField('fi4', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])
            fi5 = IntegerField('fi5', validators=[InputRequired(), NumberRange(min=0, max=1000000000)])

            fc1 = StringField('fc1')

        class CustomTabella21DataView(Tabella21_dataView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form = CustomForm21

        class CustomTabella22DataView(Tabella22_dataView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form = CustomForm22

        class CustomTabella24DataView(Tabella24_dataView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form = CustomForm24

        class CustomTabella25DataView(Tabella25_dataView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form = CustomForm25

        class CustomTabella26DataView(Tabella26_dataView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form = CustomForm26

        class CustomTabella27DataView(Tabella27_dataView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.form = CustomForm27


        admins_off_set = 0

        # First Flask-Admin instance with the first custom index view
        admin_app1 = Admin(app,
                       name='Area di controllo 1 - Documenti e atti',
                       url='/open_admin_1',
                       template_mode='bootstrap3',
                       endpoint='open_admin_1',
        )

        admin_app1.add_view(CustomFlussiDataView(model=BaseData, session=db.session, name='Pre-complaint flows',
                                                 intervals=intervals,
                                                 endpoint='flussi_data_view'))

        admin_app1.add_view(
            AttiDataView(model=BaseData, session=db.session, name='Atti complaint', intervals=intervals, area_id=1,
                                subarea_id=2, endpoint='atti_data_view'))

        admin_app1.add_view(
            ContenziosiDataView(model=BaseData, session=db.session, name='Contenziosi', intervals=intervals, area_id=1,
                                subarea_id=3, endpoint='contenziosi_data_view'))

        admin_app1.add_view(
            ContingenciesDataView(model=BaseData, session=db.session, name='Contingencies', intervals=intervals, area_id=1,
                                subarea_id=4, endpoint='contingencies_data_view'))
        admin_app1.add_view(
            IniziativeDsoAsDataView(model=BaseData, session=db.session, name='DSO-AS Initiatives', intervals=intervals, area_id=1,
                                subarea_id=6, endpoint='iniziative_dso_as_data_view'))
        admin_app1.add_view(
            IniziativeAsDsoDataView(model=BaseData, session=db.session, name='AS-DSO Initiatives', intervals=intervals, area_id=1,
                                subarea_id=7, endpoint='iniziative_as_dso_data_view'))

        admin_app1.add_view(
            IniziativeDsoDsoDataView(model=BaseData, session=db.session, name='Iniziative DSO-DSO', intervals=intervals, area_id=1,
                                subarea_id=8, endpoint='iniziative_dso_dso_data_view'))

        # Second Flask-Admin instance with the second Area index view
        # ===========================================================
        admin_app2 = Admin(app,
                           name='Area di controllo 2 - Elementi quantitativi',
                           url='/open_admin_2',
                           template_mode='bootstrap4',
                           endpoint='open_admin_2',
                           )

        # Add views to admin_app2
        admin_app2.add_view(CustomTabella21DataView(BaseData, db.session, name="Struttura offerta",
                                                    endpoint='view_struttura_offerta', intervals=intervals))

        admin_app2.add_view(CustomTabella22DataView(BaseData, db.session, name="Area di contendibilità",
                                                    endpoint="view_area_contendibilita", intervals=intervals))
        admin_app2.add_view(CustomTabella23DataView(BaseData, db.session, name="Grado di contendibilità",
                                                    endpoint = 'view_grado_contendibilita', intervals = intervals))
        admin_app2.add_view(CustomTabella24DataView(BaseData, db.session, name='Accesso venditori a DSO',
                                                    endpoint='view_accesso_venditori', intervals=intervals))
        admin_app2.add_view(CustomTabella25DataView(BaseData, db.session, name='Quote mercato IVI',
                                                    endpoint='view_quote_mercato_ivi', intervals=intervals))
        admin_app2.add_view(CustomTabella26DataView(BaseData, db.session, name='Trattamento switching',
                                                    endpoint='view_trattamento_switching', intervals=intervals))
        admin_app2.add_view(CustomTabella27DataView(BaseData, db.session, name="Livello di contendibilita'",
                                                    endpoint="view_livello_contendibilita", intervals=intervals))

        # Third Flask-Admin instance with the third Area index view
        # ===========================================================
        admin_app3 = Admin(app,
                           name='Documents Workflow',
                           url='/open_admin_3',
                           template_mode='bootstrap4',
                           endpoint='open_admin_3',
                           )

        admin_app3.add_view(DocumentsBaseDataDetails(
                                                name='Documents in Workflows',
                                                model=DocumentWorkflow,  # Replacing Step Base Data with the correct model
                                                session=db.session,
                                                endpoint='document_workflow'  # Make sure the endpoint is unique
        ))

        admin_app3.add_view(UnassignedDocumentsBaseDataView(name='Documents Unassigned To Workflows',
                                                     model=BaseData,
                                                     session=db.session,
                                                    endpoint='new_documents'))
        admin_app3.add_view(ModelView(name='Workflows Dictionary',
                                      model=Workflow,
                                      session=db.session))
        admin_app3.add_view(ModelView(name='Steps Dictionary',
                                      model=Step,
                                      session=db.session))


        # Fourth Flask-Admin instance
        # ===========================================================
        # admin_app4 = Admin(app, name='Setup', url = '/open_setup_basic', template_mode='bootstrap4', endpoint = 'setup_basic')

        admin_app4 = Admin(app, name='System Setup',
                           url='/open_admin_4',
                           template_mode='bootstrap4',
                           endpoint='open_admin_4')
        # Add your ModelViews to Flask-Admin
        admin_app4.add_view(CompanyView(Company, db.session, name='Companies', endpoint='companies_data_view'))
        admin_app4.add_view(UsersView(Users, db.session, name='Users', endpoint='users_data_view'))
        admin_app4.add_view(
            QuestionnaireModelView(Questionnaire, db.session, name='Questionnaires', endpoint='questionnaires_data_view'))
        admin_app4.add_view(QuestionView(Question, db.session, name='Questions', endpoint='questions_data_view'))
        admin_app4.add_view(StatusView(Status, db.session, name='Status', endpoint='status_data_view'))
        admin_app4.add_view(LexicModelView(Lexic, db.session, name='Dictionary', endpoint='dictionary_data_view'))
        admin_app4.add_view(AreaModelView(Area, db.session, name='Areas', endpoint='areas_data_view'))
        admin_app4.add_view(SubareaModelView(Subarea, db.session, name='Subareas', endpoint='subareas_data_view'))
        admin_app4.add_view(SubjectModelView(Subject, db.session, name='Subjects', endpoint='subjects_data_view'))
        admin_app4.add_view(WorkflowView(Workflow, db.session, name='Workflows', endpoint='workflows_data_view'))
        admin_app4.add_view(StepView(Step, db.session, name='Steps', endpoint='steps_data_view'))
        # admin_app4.add_view(AuditLogView(AuditLog, db.session, name='Audit Log', endpoint='audit_data_view'))
        admin_app4.add_view(PostView(Post, db.session, name='Posts', endpoint='posts_data_view'))
        admin_app4.add_view(TicketView(Ticket, db.session, name='Tickets', endpoint='tickets_data_view'))
        admin_app4.add_view(BaseDataView(BaseData, db.session, name='Database', endpoint='base_data_view'))
        admin_app4.add_view(DocumentsView(BaseData, db.session, name='Documents', endpoint='bdocuments_view'))
        admin_app4.add_view(ContainerView(Container, db.session, name='Container', endpoint='container_view'))
        admin_app4.add_view(PlanView(Plan, db.session, name='Plans', endpoint='plan_view'))
        admin_app4.add_view(ProductView(Product, db.session, name='Products', endpoint='product_view'))

        # TODO Associazione di 1->m da non consentire qui (can_create = False) , in quanto già fatta (con controllo IF EXISTS) altrove
        # TODO ***** le risposte ai questionnari *** - answer - sono da STORE non in Answer, ma in BaseData (cu data_type='answer')!


        # Area 5: document upload

        # === = ==================================== === ====================================
        admin_app5 = Admin(app,
                           name='Workflow Documenti',
                           url='/open_admin_5',
                           template_mode='bootstrap4',
                           endpoint='open_admin_5',
                           )

        # Add views to admin_app2
        admin_app5.add_view(
            DocumentUploadViewExisting(model=BaseData, session=db.session, name='Attach Existing Document(s) to Workflow(s)', intervals=intervals, area_id=3,
                                subarea_id=1, endpoint='upload_documenti_view_existing'))
        # Add views to admin_app2
        admin_app5.add_view(
            DocumentUploadView(model=BaseData, session=db.session, name='List of Document Workflow', intervals=intervals, area_id=3,
                                subarea_id=1, endpoint='upload_documenti_view'))


        # EOF app5
        # === = ==================================== === ====================================

        # App 6 - contracts

        # Initialize Flask-Admin
        admin_app6 = Admin(app,
                           name='Contracts Management',
                           url='/open_admin_6',
                           template_mode='bootstrap4',
                           endpoint='open_admin_6')

        # Add views for each model
        # (Use the custom view for contracts)
        # Register the Signed Contracts view with a unique name and endpoint
        admin_app6.add_view(
            SignedContractsView(Contract, db.session, name="Signed & Active Contracts", endpoint="signed_contracts"))

        # Register the Drafting Contracts view with a unique name and endpoint
        admin_app6.add_view(
            DraftingContractsView(Contract, db.session, name="Drafting Contracts", endpoint="drafting_contracts"))

        admin_app6.add_view(
            ContractArticleAdmin(ContractArticle, db.session, name='Contract Articles', endpoint="contract_articles")
        )
        # Add views for each model
        admin_app6.add_view(ModelView(ContractParty, db.session, name='Contract Parties'))
        admin_app6.add_view(ModelView(ContractTerm, db.session, name='Contract Terms'))
        admin_app6.add_view(ModelView(ContractDocument, db.session, name='Contract Documents'))
        admin_app6.add_view(ModelView(ContractStatusHistory, db.session, name='Contract Status History'))
        # Optionally, you can add views for related models (e.g., Company, Party, User)
        admin_app6.add_view(ModelView(Party, db.session, name='Parties'))


        # 10-th Flask-Admin instance
        # ===========================================================
        admin_app10 = Admin(app, name='Surveys & Questionnaires Workflow',
                            url='/open_admin_10',
                            template_mode='bootstrap4',
                            endpoint='open_admin_10')

        # Add your ModelViews to Flask-Admin
        admin_app10.add_view(OpenQuestionnairesView(name='Open Questionnaires', endpoint='open_questionnaires'))

        admin_app10.add_view(StepQuestionnaireView(StepQuestionnaire, db.session,
                                                   name='A. Questionnaires & Surveys (Q&S) Workflow',
                                                   endpoint='stepquestionnaire_questionnaire_view'))
        admin_app10.add_view(QuestionnaireModelView(Questionnaire, db.session, name='B.1 Q&S Repository',
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

    @admin_all.route('/open_admin_app_1')
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

        return redirect(url_for('open_admin_1.index'))

    @admin_all.route('/open_admin_app_2')
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
    @admin_all.route('/open_admin_app_3')
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

    @admin_all.route('/open_admin_app_4')
    @login_required
    @roles_required('Admin')
    # Define the index route
    def open_admin_app_4():
        user_id = current_user.id
        return redirect(url_for('open_admin_4.index'))

    @admin_all.route('/open_admin_app_5')
    @login_required
    @roles_required('Admin')
    # Define the index route
    def open_admin_app_5():
        user_id = current_user.id
        return redirect(url_for('open_admin_5.index'))

    @admin_all.route('/open_admin_app_6')
    @login_required
    @roles_required('Admin', 'Manager', 'Employee')
    # Define the index route
    def open_admin_app_6():
        user_id = current_user.id
        return redirect(url_for('open_admin_6.index'))

    @admin_all.route('/open_admin_app_10')
    @login_required
    @roles_required('Admin', 'Manager', 'Employee')
    def open_admin_app_10():
        try:
            print('quest 0')
            user_id = current_user.id
            print('quest 1', user_id)
            company_row = db.session.query(Company.name) \
                .join(CompanyUsers, CompanyUsers.company_id == Company.id) \
                .filter(CompanyUsers.user_id == user_id) \
                .first()
            print('quest 2', company_row)
            company_name = company_row[0] if company_row else None  # Extracting the name attribute
            print('quest 3', company_name)

            if admin_app10 is None:
                raise ValueError("admin_app10 is not initialized.")

            template = "Surveys & Questionnaires"
            placeholder_value = company_name
            formatted_string = template.format(placeholder_value) if placeholder_value else template
            admin_app10.name = formatted_string

            print('quest 4', admin_app10.name, 'redirect to open_Admin_10')
            return redirect(url_for('open_admin_10.index'))

        except Exception as e:
            print('Error occurred:', str(e))
            return 'An error occurred', 500

    return admin_app1, admin_app2, admin_app3, admin_app4, admin_app5, admin_app6, admin_app10


class ContainerAdmin(ModelView):
    form_overrides = {
        'content': JSONField
    }

    form_create_rules = [
        rules.FieldSet(('page', 'position', 'content_type', 'content', 'image', 'description', 'action_type', 'action_url', 'container_order'), 'Container Details'),
        'created_at', 'updated_at'
    ]

    form_columns = ['page', 'position', 'content_type', 'content', 'created_at', 'updated_at', 'image', 'description', 'action_type', 'action_url', 'container_order']

    column_list = ['page', 'position', 'content_type', 'content', 'created_at', 'updated_at', 'image', 'description', 'action_type', 'action_url', 'container_order']

    def scaffold_form(self):
        form_class = super(ContainerAdmin, self).scaffold_form()

        form_class.created_at = HiddenField()
        form_class.updated_at = HiddenField()

        # Add any custom field settings if needed
        return form_class

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_at = datetime.now()
        model.updated_at = datetime.now()
        return super(ContainerAdmin, self).on_model_change(form, model, is_created)



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

class CompanyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    address = StringField('Address')
    phone_number = StringField('Phone Number')
    website = StringField('Website')
    taxcode = StringField('Tax Code', render_kw={'readonly': True})
    email = StringField('Email', validators=[Email()])

    created_on = DateTimeField('Created', format='%Y-%m-%d %H:%M:%S', widget=DateTimeInput(), render_kw={'readonly': True})
    updated_on = DateTimeField('Updated', format='%Y-%m-%d %H:%M:%S', widget=DateTimeInput(), render_kw={'readonly': True})


class QuestionnaireForm(ModelView):
    can_create = True
    can_delete = True
    can_export = True
    can_view_details = True
    column_list = ('questionnaire_id', 'questionnaire_type', 'name', 'interval', 'deadline_date', 'status_id', 'headers')
    column_labels = {'questionnaire_id': 'Survey ID', 'questionnaire_type': 'Type', 'name': 'Name',
                     'interval': 'Interval', 'deadline_date': 'Deadline', 'status_id': 'Status', 'headers': 'Header'}
    form_columns = column_list
    column_exclude_list = ('id', 'created_on')  # Specify the columns you want to exclude


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


class PlanForm(ModelView):
    column_list = ('name', 'description', 'billing_cycle')
    column_labels = {
        'name': 'Name',
        'description': 'Description',
        'billing_cycle': 'Billing Cycle'
    }
    form_columns = ('name', 'description', 'billing_cycle')
    column_exclude_list = ['id']
    column_descriptions = {
        'name': 'Given Plan Name',
        'description': 'Description of the Plan',
        'billing_cycle': 'Billing Cycle (one-off, monthly, quarterly, yearly)',
    }

    form_overrides = {
        'billing_cycle': SelectField
    }

    form_args = {
        'billing_cycle': {
            'choices': [('one-off', 'One-off'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'),
                        ('yearly', 'Yearly')],
            'coerce': str
        }
    }

    # Additional configurations (optional)
    form_excluded_columns = ['id']
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    create_modal = True
    edit_modal = True


class ProductForm(ModelView):
    # Override form fields
    form_columns = [
        'name',
        'description',
        'stripe_product_id',
        'stripe_price_id',
        'price',
        'currency',
        'path',
        'icon'
    ]

    column_labels = {
        'name': 'Name',
        'description': 'Description',
        'stripe_product_id': 'Stripe Product ID',
        'stripe_price_id': 'Stripe Price ID',
        'price': 'Product Price (in cents)',
        'currency': 'Currency',
        'path': 'Path (for applications only)',
        'icon': 'Icon'
    }

    # Automatically hide the 'id' field in forms
    form_widget_args = {
        'id': {
            'type': 'hidden'
        }
    }

    # Additional configurations (optional)
    column_exclude_list = ['id']
    form_excluded_columns = ['id']
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    create_modal = True
    edit_modal = True


class ContainerForm(ModelView):
    # Override form fields
    form_columns = [
        'page',
        'position',
        'content_type',
        'content',
        'company_id',
        'role_id',
        'area_id',
        'created_at',
        'updated_at',
        'image',
        'description',
        'action_type',
        'action_url',
        'container_order'
    ]

    # Override form field type for 'id'
    form_overrides = {
        'id': HiddenField
    }

    # Automatically hide the 'id' field in forms
    form_widget_args = {
        'id': {
            'type': 'hidden'
        }
    }

    # Customize form choices (if any)
    # form_choices = {
    #     'content_type': [
    #         ('type1', 'Type 1'),
    #         ('type2', 'Type 2')
    #     ]
    # }

    # Additional configurations (optional)
    column_exclude_list = ['id']
    form_excluded_columns = ['id']
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    create_modal = True
    edit_modal = True

class WorkflowStepsForm(ModelView):
    can_create = False
    can_delete = False
    can_export = True
    can_view_details = True
    pass



class CompanyView(ModelView):
    form = CompanyForm  # Set the form

    form_excluded_columns = ('id', 'updated_on', 'created_on')  # Exclude employees relationship from the form

    column_searchable_list = ['name', 'description', 'address', 'phone_number', 'email']
    column_filters = column_searchable_list

    def on_model_change(self, form, model, is_created):
        # Convert string dates to datetime objects
        if hasattr(form, 'created_on') and form.created_on.data:
            if isinstance(form.created_on.data, str):
                model.created_on = datetime.strptime(form.created_on.data, '%Y-%m-%d %H:%M:%S')
            else:
                model.created_on = form.created_on.data

        if hasattr(form, 'updated_on') and form.updated_on.data:
            if isinstance(form.updated_on.data, str):
                model.updated_on = datetime.strptime(form.updated_on.data, '%Y-%m-%d %H:%M:%S')
            else:
                model.updated_on = form.updated_on.data

    def create_form(self, obj=None):
        form = super(CompanyView, self).create_form(obj)
        if form.created_on.data and isinstance(form.created_on.data, str):
            form.created_on.data = datetime.strptime(form.created_on.data, '%Y-%m-%d %H:%M:%S')
        if form.updated_on.data and isinstance(form.updated_on.data, str):
            form.updated_on.data = datetime.strptime(form.updated_on.data, '%Y-%m-%d %H:%M:%S')
        return form

    def edit_form(self, obj=None):
        form = super(CompanyView, self).edit_form(obj)
        if form.created_on.data and isinstance(form.created_on.data, str):
            form.created_on.data = datetime.strptime(form.created_on.data, '%Y-%m-%d %H:%M:%S')
        if form.updated_on.data and isinstance(form.updated_on.data, str):
            form.updated_on.data = datetime.strptime(form.updated_on.data, '%Y-%m-%d %H:%M:%S')
        return form

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
    pass  # No customizations needed

class LegalDocumentView(LegalDocumentForm):
    pass  # No customizations needed for LegalDocumentView



class TicketView(TicketForm):
    pass  # No customizations needed for


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

class ContainerView(ContainerForm):
    pass  # No customizations needed for

class PlanView(PlanForm):
    pass  # No customizations needed for

class ProductView(ProductForm):
    pass  # No customizations needed for now

class QuestionnaireModelView(ModelView):
    form_columns = ['questionnaire_id', 'questionnaire_type', 'name', 'interval', 'deadline_date', 'status_id', 'headers']

    def create_model(self, form):
        print('Starting create_model method for Questionnaire')  # Debugging print
        try:
            print('Form data:')
            print(f'questionnaire_id: {form.questionnaire_id.data}')
            print(f'questionnaire_type: {form.questionnaire_type.data}')
            print(f'name: {form.name.data}')
            print(f'interval: {form.interval.data}')
            print(f'deadline_date: {form.deadline_date.data}')
            print(f'status_id: {form.status_id.data}')
            print(f'headers: {form.headers.data}')

            model = Questionnaire(
                questionnaire_id=form.questionnaire_id.data,
                questionnaire_type=form.questionnaire_type.data,
                name=form.name.data,
                interval=form.interval.data,
                deadline_date=form.deadline_date.data,
                status_id=form.status_id.data,
                headers=form.headers.data
            )
            print(f'Questionnaire model created: {model}')  # Debugging print

            self.session.add(model)
            print('Questionnaire model added to session')  # Debugging print

            self.session.commit()
            print('Questionnaire session committed')  # Debugging print

            return model
        except IntegrityError as e:
            if not self.handle_view_exception(e):
                raise
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False
        except Exception as e:
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False


class LexicModelView(ModelView):
    form_columns = ['category', 'name']

    def create_model(self, form):
        print('Starting create_model method for Lexic')  # Debugging print
        try:
            model = self.model()  # Instantiate the model without arguments
            print(f'Empty Lexic model created: {model}')  # Debugging print

            form.populate_obj(model)
            print(f'Lexic model populated: {model}')  # Debugging print

            self.session.add(model)
            print('Lexic model added to session')  # Debugging print

            self.session.commit()
            print('Lexic session committed')  # Debugging print

            return model
        except IntegrityError as e:
            if not self.handle_view_exception(e):
                raise
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False
        except Exception as e:
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False

class AreaModelView(ModelView):
    form_columns = ['name', 'description']

    def create_model(self, form):
        try:
            # Print the current sequence value
            current_sequence_value = self.session.execute(text("SELECT last_value FROM area_id_seq")).fetchone()
            print(f'Current sequence value: {current_sequence_value[0]}')

            model = self.model()  # Instantiate the model without arguments
            print(f'Empty Area model created: {model}')  # Debugging print

            form.populate_obj(model)
            print(f'Area model populated: {model}')  # Debugging print

            self.session.add(model)
            print('Area model added to session')  # Debugging print

            self.session.commit()
            print('Area session committed')  # Debugging print

            return model
        except IntegrityError as e:
            if not self.handle_view_exception(e):
                raise
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False
        except Exception as e:
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False


class SubareaModelView(ModelView):
    form_columns = ['name', 'description', 'data_type']

    def create_model(self, form):
        print('Starting create_model method for Subarea')  # Debugging print
        try:
            # Print the current sequence value
            current_sequence_value = self.session.execute(text("SELECT last_value FROM subarea_id_seq")).fetchone()
            print(f'Current sequence value: {current_sequence_value[0]}')

            model = self.model()  # Instantiate the model without arguments
            print(f'Empty Subarea model created: {model}')  # Debugging print

            form.populate_obj(model)
            print(f'Subarea model populated: {model}')  # Debugging print

            self.session.add(model)
            print('Subarea model added to session')  # Debugging print

            self.session.commit()
            print('Subarea session committed')  # Debugging print

            return model
        except IntegrityError as e:
            if not self.handle_view_exception(e):
                raise
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False
        except Exception as e:
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False


class SubjectModelView(ModelView):
    form_columns = ['name', 'tier_1', 'tier_2', 'tier_3']

    def create_model(self, form):
        print('Starting create_model method')  # Debugging print
        try:
            model = self.model()  # Instantiate the model without arguments
            print(f'Empty model created: {model}')  # Debugging print

            form.populate_obj(model)
            '''
            print(f'Model populated: {model}')  # Debugging print

            # Add specific debug prints for each field
            print(f'ID: {model.id}')
            print(f'Name: {model.name}')
            print(f'Tier 1: {model.tier_1}')
            print(f'Tier 2: {model.tier_2}')
            print(f'Tier 3: {model.tier_3}')
            '''

            self.session.add(model)
            # print('Model added to session')  # Debugging print

            self.session.commit()
            # print('Session committed')  # Debugging print

            return model
        except IntegrityError as e:
            if not self.handle_view_exception(e):
                raise
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False
        except Exception as e:
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False


class ContainerModelView(ModelView):
    form_rules = [
        'page',
        'position',
        'content_type',
        'content',
        'company_id',
        'role_id',
        'area_id',
        'image',
        'description',
        'action_type',
        'action_url',
        'container_order',
        rules.Header('Timestamps'),
        'created_at',
        'updated_at'
    ]

    def create_model(self, form):
        print('Starting create_model method for Container')  # Debugging print
        try:
            model = self.model()  # Instantiate the model without arguments
            print(f'Empty Container model created: {model}')  # Debugging print

            form.populate_obj(model)
            print(f'Container model populated: {model}')  # Debugging print

            self.session.add(model)
            print('Container model added to session')  # Debugging print

            self.session.commit()
            print('Container session committed')  # Debugging print

            return model
        except IntegrityError as e:
            if not self.handle_view_exception(e):
                raise
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False
        except Exception as e:
            flash('Failed to create record. {}'.format(str(e)), 'error')
            self.session.rollback()
            return False


# Make sure Blueprint is accessible in other modules
__all__ = ['admin_all']
