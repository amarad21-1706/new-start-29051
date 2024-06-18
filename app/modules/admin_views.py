import logging
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

from flask_admin.actions import action  # Import action here
from flask_login import current_user
from wtforms import SelectField, StringField, PasswordField, BooleanField  # Use BooleanField instead of CheckboxField

from wtforms.validators import InputRequired
from app.modules.db import db

from config.config import get_subarea_name, get_config_values, check_status_extended
from app.utils.widgets import XEditableWidget, FileUploadField  # Import FileUploadField here
from forms.forms import CustomSubjectAjaxLoader
from models.user import Interval
from flask_admin.contrib.sqla import ModelView
from app.modules.db import db
from app.utils.helpers import create_file_upload_field  # Import the helper function

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

        logging.debug("flussi...Admin view initialized")
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

        intervals = current_app.config['CURRENT_INTERVALS']
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

        form_class.file_path = FileUploadField('File', base_path=current_app.config[
            'UPLOAD_FOLDER'])  # Initialize file_path here

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


class Atti_dataView(ModelView):
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 2  # Define subarea_id as a class attribute
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

        logging.debug("atti...Admin view initialized")
        #self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Atti_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Atti_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False

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
        'no_action': BooleanField
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

        intervals = current_app.config['CURRENT_INTERVALS']
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
        form_class.no_action = BooleanField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        form_class.file_path = FileUploadField('File', base_path=current_app.config[
            'UPLOAD_FOLDER'])  # Initialize file_path here

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



class Contingencies_dataView(ModelView):
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 3  # Define subarea_id as a class attribute
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

        logging.debug("conting...Admin view initialized")
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Contingencies_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Contingencies_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False

    column_list = (
    'fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
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
        'no_action': BooleanField
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

        intervals = current_app.config['CURRENT_INTERVALS']
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
        form_class.no_action = BooleanField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        form_class.file_path = FileUploadField('File', base_path=current_app.config[
            'UPLOAD_FOLDER'])  # Initialize file_path here

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


class Contenziosi_dataView(ModelView):
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 4  # Define subarea_id as a class attribute
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

        logging.debug("contenz...Admin view initialized")
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Contenziosi_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Contenziosi_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False

    column_list = (
    'fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
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
        'no_action': BooleanField
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

        intervals = current_app.config['CURRENT_INTERVALS']
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
        form_class.no_action = BooleanField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        form_class.file_path = FileUploadField('File', base_path=current_app.config[
            'UPLOAD_FOLDER'])  # Initialize file_path here

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



class Iniziative_dso_as_dataView(ModelView):
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 6  # Define subarea_id as a class attribute
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

        logging.debug("iniz...dso as Admin view initialized")
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Iniziative_dso_as_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Iniziative_dso_as_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False

    column_list = (
    'fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
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
        'no_action': BooleanField
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

        intervals = current_app.config['CURRENT_INTERVALS']
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
        form_class.no_action = BooleanField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')
        form_class.file_path = FileUploadField('File', base_path=current_app.config[
            'UPLOAD_FOLDER'])  # Initialize file_path here

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
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 7  # Define subarea_id as a class attribute
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

        logging.debug("iniz as dso...Admin view initialized")
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Iniziative_as_dso_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Iniziative_as_dso_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False

    column_list = (
    'fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
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
        'no_action': BooleanField
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

        intervals = current_app.config['CURRENT_INTERVALS']
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
        form_class.no_action = BooleanField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')
        form_class.file_path = FileUploadField('File', base_path=current_app.config[
            'UPLOAD_FOLDER'])  # Initialize file_path here

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
    create_template = 'admin/area_1/create_base_data_1.html'
    subarea_id = 7  # Define subarea_id as a class attribute
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

        logging.debug("iniz dso dso...Admin view initialized")
        # self.class_name = self.__class__.__name__  # Store the class name
        self.subarea_id = Iniziative_dso_dso_dataView.subarea_id  # Initialize subarea_id in __init__
        self.area_id = Iniziative_dso_dso_dataView.area_id  # Initialize area_id in __init__
        self.subarea_name = get_subarea_name(area_id=self.area_id, subarea_id=self.subarea_id)

    def is_accessible(self):
        if current_user.is_authenticated:
            if (current_user.has_role('Admin') or current_user.has_role('Authority')
                    or current_user.has_role('Manager') or current_user.has_role('Employee')):
                # Allow access for Admin, Manager, and Employee
                return True
        return False

    column_list = (
    'fi0', 'interval_ord', 'subject', 'number_of_doc', 'date_of_doc', 'file_path', 'no_action', 'fc2')
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
        'no_action': BooleanField
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

        logging.debug("Scaffolding form for UserAdmin dso dso")
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

        intervals = current_app.config['CURRENT_INTERVALS']
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
        form_class.no_action = BooleanField('Confirm no documents to attach',
                                             default=False)  # Set default value to False

        form_class.form_excluded_columns = ('user_id', 'company_id', 'status_id',
                                            'created_by', 'created_on', 'updated_on', 'data_type')
        # Set default values for specific fields
        form_class.fc2 = MyStringField('Note')

        form_class.file_path = FileUploadField('File', base_path=current_app.config[
            'UPLOAD_FOLDER'])  # Initialize file_path here

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

        intervals = current_app.config['CURRENT_INTERVALS']
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

        intervals = current_app.config['CURRENT_INTERVALS']
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

        intervals = current_app.config['CURRENT_INTERVALS']
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

        intervals = current_app.config['CURRENT_INTERVALS']
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

        intervals = current_app.config['CURRENT_INTERVALS']
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

        intervals = current_app.config['CURRENT_INTERVALS']
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

        intervals = current_app.config['CURRENT_INTERVALS']
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
