# app/modules/custom_admin_views.py
from flask_admin import Admin, AdminIndexView
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, DateField
from wtforms.validators import InputRequired, NumberRange

from app.modules.admin_views import (Flussi_dataView, Atti_dataView, Contenziosi_dataView, Contingencies_dataView,
                                     Iniziative_dso_as_dataView, Iniziative_as_dso_dataView, Iniziative_dso_dso_dataView,
                                     Tabella21_dataView, Tabella22_dataView, Tabella23_dataView, Tabella24_dataView,
                                     Tabella25_dataView, Tabella26_dataView, Tabella27_dataView)
from models.user import BaseData


# Use import_views function where needed
# Import the views by calling the function

def create_custom_admin_views(app):
    from app.modules.db import db
    class CustomFlussiDataView(Flussi_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1


    class CustomAttiDataView(Atti_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomContenziosiDataView(Contenziosi_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomContingenciesDataView(Contingencies_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomIniziativeDsoAsDataView(Iniziative_dso_as_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomIniziativeAsDsoDataView(Iniziative_as_dso_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomIniziativeDsoDsoDataView(Iniziative_dso_dso_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm1

    class CustomTabella21DataView(Tabella21_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

    class CustomTabella22DataView(Tabella22_dataView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form = CustomForm2

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

    admin_app1 = Admin(app,
                       name='Area di controllo 1 - Documenti e atti',
                       url='/open_admin',
                       template_mode='bootstrap4',
                       endpoint='open_admin',
                       )

    # Add views to admin_app1
    admin_app1.add_view(CustomFlussiDataView(BaseData, db.session,
                                             name="Flussi pre-complaint", endpoint='flussi_data_view'))
    admin_app1.add_view(CustomAttiDataView(BaseData, db.session,
                                           name='Atti di complaint', endpoint='atti_data_view'))
    admin_app1.add_view(CustomContingenciesDataView(BaseData, db.session,
                                                    name='Contingencies', endpoint='contingencies_data_view'))
    admin_app1.add_view(CustomContenziosiDataView(BaseData, db.session,
                                                  name='Contenziosi', endpoint='contenziosi_data_view'))
    admin_app1.add_view(CustomIniziativeDsoAsDataView(BaseData, db.session,
                                                      name='Iniziative DSO vs amministrazioni',
                                                      endpoint='iniziative_dso_as_data_view'))
    admin_app1.add_view(CustomIniziativeAsDsoDataView(BaseData, db.session,
                                                      name='Amministrazioni vs DSO',
                                                      endpoint='iniziative_as_dso_data_view'))
    admin_app1.add_view(CustomIniziativeDsoDsoDataView(BaseData, db.session,
                                                       name='DSO vs DSO/TSO',
                                                       endpoint='iniziative_dso_dso_data_view'))

    admin_app2 = Admin(app,
                       name='Area di controllo 2 - Elementi quantitativi',
                       url='/open_admin_2',
                       template_mode='bootstrap4',
                       endpoint='open_admin_2',
                       )
    admin_app2.add_view(CustomTabella21DataView(BaseData, db.session, name="Struttura offerta",
                                                endpoint='view_struttura_offerta'))
    admin_app2.add_view(CustomTabella22DataView(BaseData, db.session, name="Area di contendibilita'",
                                                endpoint="view_area_contendibilita'"))
    admin_app2.add_view(CustomTabella23DataView(BaseData, db.session, name="Grado di contendibilita'",
                                                endpoint="view_grado_contendibilita'"))
    admin_app2.add_view(CustomTabella24DataView(BaseData, db.session, name='Accesso venditori a DSO',
                                                endpoint='view_accesso_venditori'))
    admin_app2.add_view(CustomTabella25DataView(BaseData, db.session, name='Quote mercato IVI',
                                                endpoint='view_quote_mercato_ivi'))
    admin_app2.add_view(CustomTabella26DataView(BaseData, db.session, name='Trattamento switching',
                                                endpoint='view_trattamento_switching'))
    admin_app2.add_view(CustomTabella27DataView(BaseData, db.session, name="Livello di contendibilta'",
                                                endpoint="view_livello_contendibilita'"))

    admin_app3 = Admin(app,
                       name='Documents Workflow',
                       url='/open_admin_3',
                       template_mode='bootstrap4',
                       endpoint='open_admin_3',
                       )

    admin_app3.add_view(ModelView(name='Workflows Dictionary', model=Workflow, session=db.session))
    admin_app3.add_view(ModelView(name='Steps Dictionary', model=Step, session=db.session))
    admin_app3.add_view(DocumentsAssignedBaseDataView(name='Documents Assigned to Workflows',
                                                      model=BaseData, session=db.session,
                                                      endpoint='assigned_documents'))
    admin_app3.add_view(DocumentsNewBaseDataView(name='New Unassigned Documents', model=BaseData, session=db.session,
                                                 endpoint='new_documents'))
    admin_app3.add_view(
        DocumentsBaseDataDetails(name='Documents Workflow Management', model=StepBaseData, session=db.session))

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
    admin_app4.add_view(BaseDataView(BaseData, db.session, name='Data', endpoint='base_data_view'))

    # Add other ModelViews as needed...

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
    # admin_app10.add_view(StatusView(Status, db.session, name='E. Dictionary of Status',
    #                                endpoint='status_questionnaire_view'))

    return admin_views

# Custom Forms
class CustomForm1(FlaskForm):
    fi0 = IntegerField('fi0', validators=[InputRequired(), NumberRange(min=2000, max=2199)])  # anno
    interval_ord = IntegerField('interval_ord', validators=[InputRequired(), NumberRange(min=0, max=52)])  # periodo
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

