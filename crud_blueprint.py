# crud_blueprint.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, jsonify, send_from_directory
from datetime import datetime
from utils.utils import get_except_fields

from db import db  # Assuming you have a SQLAlchemy database instance
from models.user import (Users, UserRoles, Role, Table, Questionnaire, Question, Answer, Company, CompanyUsers,
                         QuestionnaireQuestions, QuestionnaireCompanies, CompanyUsers, Subject, Status,
                         Config, Workflow, Step, BaseData, Lexic, Question,
                         WorkflowSteps, WorkflowBaseData, StepBaseData, Area, Subarea, AreaSubareas,
                         Post)
# crud_blueprint.py
from sqlalchemy import inspect
from crud_validation import validate_and_add_item
from sqlalchemy.orm import joinedload


def extract_model_name(request):
    # Placeholder logic to extract model name from request
    # This can vary depending on how the model name is encoded in the request
    # For example, it might be part of the URL path or query parameters
    model_name = request.args.get('model')
    return model_name

def retrieve_model_from_database(model_name):
    print('retrieve_model_from_database')
    # Placeholder logic to retrieve model from the database
    # This will vary based on your database setup and ORM framework (if any)
    # Example: Model.query.filter_by(name=model_name).first()
    return None  # Placeholder for demonstration


def get_field_labels(model):
    # Assuming you have a mapped table object for the model
    inspector = inspect(model)
    mapped_table = inspector.mapped_table

    # Get the names of all the columns in the table
    table_columns = mapped_table.columns

    # Retrieve field names from the Table object
    field_labels = {field.name: field.name.capitalize() for field in table_columns}

    return field_labels


def get_item_by_id(model_name, item_id):
    # Retrieve the model based on the model_name
    model = get_model_by_name(model_name)

    print('THE model', model)

    # Check if the model is found
    if not model:
        return None

    # Use your ORM or database query to retrieve the item by its ID
    # This will depend on your specific implementation
    item = model.query.get(item_id)

    return item


def get_model_name(request):
    # Extract the model name from the request

    # Add debug statement to print request information
    print("Request Method:", request.method)
    print("Request Path:", request.path)
    # Add logic to extract model name from request, if applicable
    model_name = extract_model_name(request)
    print("Model Name Extracted:", model_name)

    #model_name = request.args.get('model_name')
    # Check if the model name is provided
    if not model_name:
        return None
    # Ensure the model name is in the correct format (e.g., lowercase)
    return model_name.lower()


def get_model_by_name(model_name):
    # Assuming you have a dictionary mapping model names to model classes

    # Add debug statement to print the model name being looked up
    print("Looking up model:", model_name)
    # Add logic to retrieve model by name from the database or wherever it's defined
    model = retrieve_model_from_database(model_name)
    if model:
        print("Model found:", model)
    else:
        print("Model not found for name:", model_name)


    model_mapping = {'model_user': Users, 'model_company': Company, 'model_company_users': CompanyUsers,
                     'model_role': Role,
        'model_user_roles': UserRoles, 'model_question': Question, 'model_questionnaire': Questionnaire,
        'model_questionnaire_questions': QuestionnaireQuestions, 'model_status': Status, 'model_answer': Answer,
        'model_lexic': Lexic, 'model_area': Area, 'model_subareas': Subarea, 'model_area_subareas': AreaSubareas,
        'model_base_data': BaseData,
        'model_subject': Subject, 'model_document': BaseData.get_documents(), 'model_step': Step,
        'model_step_base_data': StepBaseData, 'model_workflow': Workflow, 'model_workflow_steps': WorkflowSteps,
        'model_workflow_base_data': WorkflowBaseData,
        }
    # Adjust as per your actual model classes
    return model_mapping.get(model_name)


def create_crud_blueprint(model, model_name):
    # Add 'model_' prefix to model_name
    model_name_with_prefix = 'model_' + model_name
    #document_blueprint = Blueprint('model_document', __name__)

    blueprint = Blueprint(model_name_with_prefix, __name__, template_folder='templates')

    def get_filtered_items(model):
        # Retrieve filter values from the URL parameters
        filter_field = request.args.get('filter_field', default=None)
        filter_value = request.args.get('filter_value', default=None)

        # Handle unexpected values or None
        if filter_field is None or filter_field not in model.__table__.columns:
            filter_field = model.__table__.columns.keys()[0]  # Set to the first valid column name as default

        # Filter items based on the retrieved filter values
        if filter_field and filter_value:
            # Use ilike for case-insensitive partial string matching
            filtered_items = model.query.filter(model.__table__.columns[filter_field].ilike(f"%{filter_value}%"))

            # Add eager loading options for related objects if applicable
            if model == QuestionnaireQuestions:
                filtered_items = filtered_items.options(joinedload('questionnaire'), joinedload('question'))
            elif model == QuestionnaireCompanies:
                filtered_items = filtered_items.options(joinedload('questionnaire'), joinedload('company'))
            elif model == WorkflowBaseData:
                filtered_items = filtered_items.options(joinedload('workflow'), joinedload('base_data'))

            elif model == StepBaseData:
                filtered_items = filtered_items.options(joinedload('step'), joinedload('base_data'))

            elif model == WorkflowSteps:
                filtered_items = filtered_items.options(joinedload('workflow'), joinedload('step'))

            elif model == Workflow:
                filtered_items = filtered_items.options(joinedload('step_base_data.step'),
                                                        joinedload('step_base_data.base_data'))
            elif model == Step:
                filtered_items = filtered_items.options(joinedload('step_base_data.base_data'), joinedload('workflow'))

            elif model == BaseData:
                # No joins needed for BaseData
                pass
            elif model == UserRoles:
                filtered_items = filtered_items.options(joinedload('user'), joinedload('role'))
            elif model == AreaSubareas:
                filtered_items = filtered_items.options(joinedload('area'), joinedload('subarea'))
        else:
            filtered_items = model.query

        return filtered_items, filter_field, filter_value

    @blueprint.route('/', methods=['GET', 'POST'], endpoint='read')
    def read():
        # Access the model_name from the URL parameters
        model_name = request.args.get('model_name')

        # Define models and model names based on the requested URL
        if 'answer' in request.url.lower():
            model = Answer
            model_name = 'model_answer'
        elif 'base_data' in request.url.lower():
            model = BaseData
            model_name = 'model_base_data'
        elif 'document' in request.url.lower():
            query, *model_instances = BaseData.get_documents()
            model = model_instances[0].__class__ if model_instances else None
            model_name = 'model_document'
            # Assuming get_documents() returns a list of model instances
            #model_instances = BaseData.get_documents()

            # Assuming model_instances is not None or empty
            #model = model_instances[0].__class__
            #model_name = 'model_document'
        elif 'config' in request.url.lower():
            model = Config
            model_name = 'model_config'

        elif 'company_users' in request.url.lower():
            model = CompanyUsers
            model_name = 'model_company_users'

        elif 'company' in request.url.lower():
            model = Company
            model_name = 'model_company'
        elif 'questionnaire' in request.url.lower():
            model = Questionnaire
            model_name = 'model_questionnaire'
        elif 'question' in request.url.lower():
            model = Question
            model_name = 'model_question'
        elif 'questionnaire_questions' in request.url.lower():
            model = QuestionnaireQuestions
            model_name = 'model_questionnaire_questions'
        elif 'lexic' in request.url.lower():
            model = Lexic
            model_name = 'model_lexic'
        elif 'role' in request.url.lower():
            model = Role
            model_name = 'model_role'
        elif 'step' in request.url.lower():
            model = Step
            model_name = 'model_step'
        elif 'step_base_data' in request.url.lower():
            model = Step_BaseData
            model_name = 'model_step_base_data'
        elif 'subject' in request.url.lower():
            model = Subject
            model_name = 'model_subject'
        elif 'status' in request.url.lower():
            model = Status
            model_name = 'model_status'
        elif 'user_roles' in request.url.lower():
            model = UserRoles
            model_name = 'model_user_roles'
        elif 'user' in request.url.lower():
            model = Users
            model_name = 'model_user'
        elif 'workflow' in request.url.lower():
            model = Workflow
            model_name = 'model_workflow'
        elif 'workflow_base_data' in request.url.lower():
            model = WorkflowBaseData
            model_name = 'model_workflow_base_data'
        elif 'workflow_steps' in request.url.lower():
            model = WorkflowSteps
            model_name = 'model_workflow_steps'
        # Add other models and model names here...

        # Get the filtered items based on URL parameters
        filtered_items, filter_field, filter_value = get_filtered_items(model)
        # Paginate the filtered_items
        page = request.args.get('page', 1, type=int)
        per_page = 10
        paginated_items = filtered_items.paginate(page=page, per_page=per_page)

        # Get the items for the current page
        items_for_current_page = paginated_items.items

        items_for_current_page_with_details = []

        for item in paginated_items.items:  # Assuming items are directly accessible
            items_for_current_page_with_details.append(item)

        # Initialize a dictionary to store field labels
        field_labels = {}

        # Retrieve field names from the Table object
        field_names = get_field_names(model)

        # Iterate through the field names and extract field names and labels
        for field in field_names:
            field_labels[field] = field

        # for testing
        # items_formatted = items_for_current_page #_with_details
        items_formatted = [item.readable_format() if hasattr(item, 'readable_format') else item for item in
                           paginated_items]

        return render_template(
            'crud_read_template.html',
            field_labels=field_labels,
            field_names=field_names,
            paginated_items=paginated_items, #items_for_current_page_with_details,  # Make sure to pass paginated_items to the template
            items_formatted=items_formatted,  # Pass formatted items to the template
            model=model,
            model_name=model_name,
            add_form=True,  # Add this line to pass the add_form variable
        )

    # Helper functions

    def get_field_names(model):
        # Get the underlying Table object for the model
        inspector = inspect(model)
        mapped_table = inspector.mapped_table

        # Get the names of all the columns in the table
        table_columns = mapped_table.columns

        # Retrieve field names from the Table object
        field_names = [field.name for field in table_columns]

        return field_names

    def filter_criteria_match(item):
        # Get filter criteria from both GET and POST requests
        filter_field = request.values.get('filter_field')
        filter_value = request.values.get('filter_value')

        if filter_field and filter_value:
            # Use ilike for case-insensitive partial string matching
            return str(getattr(item, filter_field)).lower().find(str(filter_value).lower()) != -1
        else:
            return False

    @blueprint.route('/<model_name>/<int:item_id>/retrieve', methods=['GET'])
    async def retrieve(model_name, item_id):
        print('model is', model)

        item = model.query.get_or_404(item_id)
        inspector = inspect(model)
        mapped_table = inspector.mapped_table
        table_columns = mapped_table.columns
        field_names = [field.name for field in table_columns]

        return render_template(
            'crud_retrieve_template.html',
            item=item,
            field_names=field_names,
            model_name=model_name,
            filter_criteria_match=filter_criteria_match
        )

    @blueprint.route('/add', methods=['GET', 'POST'])
    async def add():
        print('CRUD add template one')

        model_name = get_model_name(request)

        print('CRUD add template two', model_name)

        # Validate the model_name and get the model
        model = get_model_by_name(model_name)
        if not model:
            return jsonify({'status': 'error', 'message': 'Invalid model'})

        # Get the underlying Table object for the model
        inspector = inspect(model)
        mapped_table = inspector.mapped_table

        # Get the names of all the columns in the table
        table_columns = mapped_table.columns

        # Retrieve field names from the Table object
        field_names = [field.name for field in table_columns]

        if request.method == 'POST':
            return validate_and_add_item(model, request, db)

        field_labels = get_field_labels(model)
        page = request.args.get('page', 1, type=int)  # Get the page parameter from the URL
        per_page = 12
        paginated_items = model.query.paginate(page=page, per_page=per_page)

        print('CRUD add template open next')

        # Return the appropriate template for adding data
        return render_template(
            'crud_add_template.html',  # Change this to the add template name
            field_labels=field_labels,
            field_names=field_names,
            paginated_items=paginated_items,
            items_for_current_page=paginated_items.items,
            model=model,
            model_name=model_name,
            add_form=True,
        )

        '''
        return render_template(
            'crud_add_template.html',
            field_labels=field_labels,
            field_names=field_names,
            paginated_items=paginated_items,
            items_for_current_page=paginated_items.items,
            model=model,
            model_name=model_name,
            add_form=True,
        )
        '''

    @blueprint.route('/<string:model_name>/<int:item_id>/update', methods=['GET', 'POST'])
    def update(model_name, item_id):
        item = model.query.get_or_404(item_id)

        # Get the underlying Table object for the model
        inspector = inspect(model)
        mapped_table = inspector.mapped_table

        # Get the names of all the columns in the table
        table_columns = mapped_table.columns

        # Retrieve field names from the Table object
        except_fields = get_except_fields()
        field_names = [field.name for field in table_columns if field.name not in except_fields]

        if request.method == 'POST':
            for key, value in request.form.items():
                # Skip updating fields in except_fields
                if key in except_fields:
                    continue

                # Convert 'config_date' to datetime if it's not 'None' or an empty string
                if key == 'config_date' and (not value or value.lower() == 'none'):
                    value = None  # Set to None if 'None' or an empty string
                elif key == 'config_date':
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # Handle the case where the provided value is not a valid datetime format
                        flash(f"Invalid datetime format for {key}: {value}", 'error')
                        continue  # Skip updating this field

                # Convert 'config_integer' and 'config_number' to int and float respectively
                if key == 'config_integer':
                    value = int(value) if value.isdigit() else None
                elif key == 'config_number':
                    try:
                        value = float(value)
                    except ValueError:
                        # Handle the case where the provided value is not a valid float
                        flash(f"Invalid numeric format for {key}: {value}", 'error')
                        continue  # Skip updating this field

                setattr(item, key, value)

            db.session.commit()
            flash('Update successful', 'success')
            return redirect(url_for('{}.read'.format(model_name)))

        # If the method is GET, render the update template with the item data
        return render_template('crud_update_template.html', item=item, field_names=field_names, model_name=model_name)


    @blueprint.route('/<string:model_name>/<int:item_id>/delete', methods=['GET', 'POST'])
    async def delete(model_name, item_id):

        # model_name = request.args.get('model_name')
        item = model.query.get_or_404(item_id)
        print(item_id, 'to be deleted next', 'from model name', model_name)
        # Check the request method
        print('Request method:', request.method)

        # If it's a GET request, render the confirmation template
        if request.method == 'GET':
            return render_template('crud_delete_template.html', item=item, model_name=model_name, item_id=item_id)

        # If it's a POST request, handle the confirmation
        if request.method == 'POST':
            # Actual deletion logic
            db.session.delete(item)
            db.session.commit()
            print('Record deleted.')

            return redirect(url_for('{}.read'.format(model_name)))


    # Assuming you have a blueprint named 'blueprint' defined earlier
    @blueprint.route('/<model_name>/delete_confirmation/<int:item_id>', methods=['GET', 'POST'])
    def delete_confirmation(model_name, item_id):
        # Access the model_name and item_id from the form data
        item = get_item_by_id(model_name, item_id)
        print('***item is', item, 'model_name', model_name, 'item_id', item_id)
        if not item:
            # Handle item not found, return an error response or redirect
            return jsonify({'status': 'error', 'message': 'Item not found'})

        return render_template('crud_delete_template.html', model_name=model_name, item_id=item_id, item=item)

    return blueprint

# Add more functions as needed
