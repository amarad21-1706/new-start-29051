import os
from flask import Flask, jsonify
import requests
from models.user import (BaseData, Users, UserRoles, Event,
        Questionnaire, Question, QuestionnaireQuestions, Questionnaire_psf, Response_psf,
        Contract, ContractParty, ContractTerm, ContractDocument, ContractStatusHistory,
        ContractArticle, Party,
        Company, CompanyUsers, Area, Subarea, AreaSubareas, Answer,
        Team, TeamMembership, ContractTeam,
        Plan, Product, PlanProducts, UserPlans, Post
        )

from flask_login import current_user
from datetime import datetime, timedelta

from flask import Blueprint, render_template, jsonify
from flask import render_template, request, redirect, url_for, flash
from db import db
from forms.forms import (MainForm, PlanForm, QuestionnaireFormArgon, QuestionFormArgon,
                         AddQuestionFormArgon, ProductForm, PlanProductsForm) # Assuming your form is in forms.py
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app_factory import roles_required, subscription_required

# from app_factory import create_app

# app = Flask(__name__)
# app = create_app() #Flask(__name__, static_folder='static')

# Create the blueprint object
argon_bp = Blueprint('argon', __name__)


@argon_bp.route('/list_icons')
def icons_view():
    # Assuming your static files are in "static/icons/"
    icons_path = os.path.join('static', 'icons')
    icons = os.listdir(icons_path)

    # Generate the full URL for each icon
    icon_urls = [url_for('static', filename=f'icons/{icon}') for icon in icons]

    return render_template('argon-dashboard/list_icons.html', icon_urls=icon_urls)


@argon_bp.route('/manage_plan_products', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_plan_products():
    form = PlanProductsForm()
    message = None  # Reset the message at the start

    try:
        # Populate choices for plans and products
        form.plan_id.choices = [(plan.id, plan.name) for plan in Plan.query.all()]
        form.product_id.choices = [(product.id, product.name) for product in Product.query.all()]

        if request.method == 'POST':
            # Reset the message before each submission
            message = None

            if form.validate_on_submit():
                if form.cancel.data:
                    # Handle cancel button
                    return redirect(url_for('index'))
                elif form.add.data:
                    # Handle add button
                    plan_id = form.plan_id.data
                    product_id = form.product_id.data

                    # Check if the plan-product association already exists
                    existing_plan_product = PlanProducts.query.filter_by(plan_id=plan_id, product_id=product_id).first()

                    if existing_plan_product:
                        message = "Association plan-product already exists."
                    else:
                        # Add logic to associate the plan with the selected product
                        new_association = PlanProducts(plan_id=plan_id, product_id=product_id)
                        db.session.add(new_association)
                        db.session.commit()
                        # Set a success message
                        message = "Association plan-product added successfully."

                elif form.delete.data:
                    # Handle delete button
                    plan_id = form.plan_id.data
                    product_id = form.product_id.data

                    # Find and delete the plan-product association
                    association_to_delete = PlanProducts.query.filter_by(plan_id=plan_id, product_id=product_id).first()

                    if association_to_delete:
                        db.session.delete(association_to_delete)
                        db.session.commit()
                        message = "Association plan-product deleted successfully."
                    else:
                        message = "Association plan-product not found."
            else:
                message = "Form validation failed. Please check your input."
    except Exception as e:
        # Log the error and set a message for the template
        app.logger.error(f"Error managing plan products: {e}")
        message = "An unexpected error occurred. Please try again later."

    # Handle GET request or any case where form validation failed
    return render_template('argon-dashboard/manage_plan_products.html', form=form, message=message)


@argon_bp.route('/get_plan_products/<int:plan_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def get_plan_products(plan_id):
    try:
        # Fetch the products associated with the given plan_id
        plan = Plan.query.get_or_404(plan_id)
        products = [
            {
                'id': pp.product.id,
                'name': pp.product.name,
            }
            for pp in plan.plan_products
        ]

        return jsonify({'products': products}), 200
    except Exception as e:
        app.logger.error(f"Error fetching products for plan {plan_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching products'}), 500



@argon_bp.route('/multi_format_dashboard')
@login_required
def multi_format_dashboard():
    companies = Company.query.all()
    areas = Area.query.all()
    subareas = AreaSubareas.query.all()

    years = BaseData.query.with_entities(BaseData.fi0).distinct().order_by(BaseData.fi0.asc()).all()
    years = [year.fi0 for year in years]

    record_types = BaseData.query.with_entities(BaseData.record_type).distinct().all()
    record_types = [record_type.record_type for record_type in record_types]

    return render_template('argon-dashboard/multi_format_dashboard.html',
                           companies=companies,
                           areas=areas,
                           subareas=subareas,
                           record_types=record_types,
                           years=years)



#@argon_bp.route('/argon')
@argon_bp.route('/', endpoint='argon_dashboard')
@login_required
def argon_dashboard():
    print("Argon Dashboard route hit")
    return render_template('argon-dashboard/argon_dashboard.html')


@argon_bp.route('/teams')
@login_required
def argon_teams_view():

    print("Teams route hit")
    teams = Team.query.all()  # Get all teams
    return render_template('argon-dashboard/teams.html', teams=teams)


@argon_bp.route('/contracts')
@login_required
def contracts_view():
    contracts = Contract.query.all()  # Fetch all contracts
    return render_template('argon-dashboard/contracts.html', contracts=contracts)


@argon_bp.route('/members')
@login_required
def members_view():
    members = Users.query.join(TeamMembership).all()  # Fetch users with team memberships
    return render_template('argon-dashboard/members.html', members=members)


@argon_bp.route('/', endpoint='plan_dashboard')
def plan_dashboard():
    print("Plan dashboard route hit")
    return render_template('argon-dashboard/plan_dashboard.html')


@argon_bp.route('/plans', methods=['GET', 'POST'])
@login_required
def plans_view():
    form = PlanForm()  # Initialize the form
    plans = Plan.query.all()  # Fetch the plans

    # Pass the form to the template along with the plans
    return render_template('argon-dashboard/plans.html', plans=plans, form=form)


@argon_bp.route('/argon/<int:id>', methods=['GET'])
@login_required
def view_plan(id):
    plan = Plan.query.get_or_404(id)  # Fetch the plan or return 404 if not found
    return render_template('argon-dashboard/view_plan.html', plan=plan)


@argon_bp.route('/create_plan', methods=['GET', 'POST'])
@login_required
def create_plan():
    form = PlanForm()
    if form.validate_on_submit():
        # Get form data and create a new plan
        name = form.name.data
        description = form.description.data
        stripe_plan_id = form.stripe_plan_id.data
        stripe_price_id = form.stripe_price_id.data
        price = form.price.data
        billing_cycle = form.billing_cycle.data

        # Create new plan object
        new_plan = Plan(
            name=name,
            description=description,
            stripe_plan_id=stripe_plan_id,
            stripe_price_id=stripe_price_id,
            price=price,
            billing_cycle=billing_cycle
        )

        try:
            # Attempt to add the new plan to the database
            db.session.add(new_plan)
            db.session.commit()

            flash('Plan created successfully!', 'success')
            return redirect(url_for('argon.plans_view'))

        except IntegrityError:
            # Rollback the session in case of an error
            db.session.rollback()
            flash('Error: A plan with this name already exists. Please choose a different name.', 'danger')
            return redirect(url_for('argon.create_plan'))

    # Render the create plan template
    return render_template('argon-dashboard/create_plan.html', form=form)


@argon_bp.route('/edit_plan/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_plan(id):
    plan = Plan.query.get_or_404(id)
    form = PlanForm(obj=plan)  # Instantiate the form with the plan data
    if request.method == 'POST':
        # Update plan details from form
        plan.name = request.form['name']
        plan.description = request.form['description']
        plan.price = request.form['price']
        plan.billing_cycle = request.form['billing_cycle']
        try:
            db.session.commit()
            flash('Plan updated successfully!', 'success')
            return redirect(url_for('argon.view_plan', id=plan.id))
        except:
            flash('Error updating plan', 'danger')
            return redirect(url_for('argon.edit_plan', id=plan.id))
    return render_template('argon-dashboard/edit_plan.html', plan=plan, form=form)


@argon_bp.route('/delete_plan/<int:id>', methods=['POST'])
@login_required
def delete_plan(id):
    plan = Plan.query.get_or_404(id)

    try:
        db.session.delete(plan)
        db.session.commit()
        flash('Plan deleted successfully!', 'success')
        return redirect(url_for('argon.plans_view'))  # Redirect to the plans view
    except Exception as e:
        db.session.rollback()
        flash('Error deleting the plan. Please try again.', 'danger')
        return redirect(url_for('argon.plans_view'))  # Redirect back to the plans view

# Questionnaires

@argon_bp.route('/', endpoint='questionnaire_dashboard')
def questionnaire_dashboard():
    print("Questionnaire dashboard route hit")
    return render_template('argon-dashboard/questionnaire_dashboard.html')


@argon_bp.route('/questionnaires', methods=['GET', 'POST'])
@login_required
def questionnaires_view():
    form = QuestionnaireFormArgon()  # Initialize the form
    questionnaires = Questionnaire.query.order_by(Questionnaire.questionnaire_id.asc()).all()  # Fetch questions ordered by question_id
    # Pass the form to the template along with the questionnaires
    return render_template('argon-dashboard/questionnaires.html', questionnaires=questionnaires, form=form)


@argon_bp.route('/questionnaire/<int:id>', methods=['GET'])
@login_required
def view_questionnaire(id):
    questionnaire = Questionnaire.query.get_or_404(id)  # Fetch the questionnaire or return 404 if not found
    return render_template('argon-dashboard/view_questionnaire.html', questionnaire=questionnaire)


@argon_bp.route('/create_questionnaire', methods=['GET', 'POST'])
@login_required
def create_questionnaire():
    form = QuestionnaireFormArgon()

    if form.validate_on_submit():
        # Create a new questionnaire instance
        new_questionnaire = Questionnaire(
            questionnaire_id=form.questionnaire_id.data,
            name=form.name.data,
            questionnaire_type=form.questionnaire_type.data,
            interval=form.interval.data,
            deadline_date=form.deadline_date.data,
            status_id=form.status_id.data,
        )

        try:
            # Try to add and commit the new questionnaire
            db.session.add(new_questionnaire)
            db.session.commit()
            flash('Questionnaire created successfully!', 'success')
            return redirect(url_for('argon.questionnaires_view'))

        except IntegrityError:
            # Rollback the session in case of an integrity error
            db.session.rollback()
            flash('Error: A questionnaire with the same ID or name already exists.', 'danger')
            return redirect(url_for('argon.create_questionnaire'))

    # Render the form if GET request or if the form is not valid
    return render_template('argon-dashboard/create_questionnaire.html', form=form)


@argon_bp.route('/edit_questionnaire/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_questionnaire(id):
    questionnaire = Questionnaire.query.get_or_404(id)
    form = QuestionnaireFormArgon(obj=questionnaire)  # Populate form with existing data

    if form.validate_on_submit():  # Validate the form submission
        # Use form.data to populate the model
        form.populate_obj(questionnaire)

        try:
            db.session.commit()
            flash('Questionnaire updated successfully!', 'success')
            return redirect(url_for('argon.view_questionnaire', id=questionnaire.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating questionnaire: {str(e)}', 'danger')
            return redirect(url_for('argon.edit_questionnaire', id=questionnaire.id))

    return render_template('argon-dashboard/edit_questionnaire.html', form=form, questionnaire=questionnaire)


@argon_bp.route('/delete_questionnaire/<int:id>', methods=['POST'])
@login_required
def delete_questionnaire(id):
    questionnaire = Questionnaire.query.get_or_404(id)

    try:
        db.session.delete(questionnaire)
        db.session.commit()
        flash('Questionnaire deleted successfully!', 'success')
        return redirect(url_for('argon.questionnaires_view'))  # Redirect to the questionnaires view
    except Exception as e:
        db.session.rollback()
        flash('Error deleting the questionnaire. Please try again.', 'danger')
        return redirect(url_for('argon.questionnaires_view'))  # Redirect back to the questionnaires view


# Question

@argon_bp.route('/', endpoint='question_dashboard')
def question_dashboard():
    print("Questions dashboard route hit")
    return render_template('argon-dashboard/question_dashboard.html')


@argon_bp.route('/questions', methods=['GET', 'POST'])
@login_required
def questions_view():
    form = QuestionFormArgon()  # Initialize the form
    page = request.args.get('page', 1, type=int)  # Get the current page from the query string (default to 1)
    per_page = 12  # Set the number of records per page
    questions = Question.query.order_by(Question.question_id.asc()).paginate(page=page, per_page=per_page)

    return render_template('argon-dashboard/questions.html', questions=questions, form=form)


@argon_bp.route('/create_question', methods=['GET', 'POST'])
@login_required
def create_question():
    form = QuestionFormArgon()  # Instantiate the form for a new question
    if form.validate_on_submit():  # If the form is submitted and validated
        # Create a new Question object using the form data
        new_question = Question(
            question_id=form.question_id.data,
            text=form.text.data,
            answer_type=form.answer_type.data,
            answer_width=form.answer_width.data,
            answer_fields=form.answer_fields.data
        )
        try:
            # Add the new question to the database
            db.session.add(new_question)
            db.session.commit()

            flash('Question created successfully!', 'success')
            return redirect(url_for('argon.questions_view'))  # Redirect to the question list view
        except IntegrityError:
            db.session.rollback()  # Rollback the session in case of error
            flash('Question ID already exists. Please try a different one.', 'danger')
            return redirect(url_for('argon.create_question'))  # Redirect back to the create page
    return render_template('argon-dashboard/create_question.html', form=form)  # Render the create form


@argon_bp.route('/edit_question/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_question(id):
    question = Question.query.get_or_404(id)  # Fetch the question by ID or return 404
    form = QuestionFormArgon(obj=question)  # Pre-fill the form with question data

    if form.validate_on_submit():  # If the form is submitted and valid
        # Update the question with the form data
        question.question_id = form.question_id.data
        question.text = form.text.data
        question.answer_type = form.answer_type.data
        question.answer_width = form.answer_width.data
        question.answer_fields = form.answer_fields.data

        try:
            db.session.commit()  # Commit changes to the database
            flash('Question updated successfully!', 'success')
            return redirect(url_for('argon.questions_view'))  # Redirect to the question list view
        except IntegrityError:
            db.session.rollback()  # Rollback the session in case of error
            flash('Error updating question. Please try again.', 'danger')
            return redirect(url_for('argon.edit_question', id=id))  # Redirect back to the edit page
    return render_template('argon-dashboard/edit_question.html', form=form, question=question)  # Render the edit form


@argon_bp.route('/question/<int:id>', methods=['GET'])
@login_required
def view_question(id):
    question = Question.query.get_or_404(id)  # Fetch the question by ID or return 404
    return render_template('argon-dashboard/view_question.html', question=question)  # Render the view template


@argon_bp.route('/delete_question/<int:id>', methods=['POST'])
@login_required
def delete_question(id):
    question = Question.query.get_or_404(id)  # Fetch the question by ID or return 404
    try:
        db.session.delete(question)  # Delete the question from the database
        db.session.commit()
        flash('Question deleted successfully!', 'success')
    except:
        db.session.rollback()  # Rollback in case of error
        flash('Error deleting question. Please try again.', 'danger')
    return redirect(url_for('argon.questions_view'))  # Redirect back to the questions list


@argon_bp.route('/surveys_two')
@login_required
def surveys_view_two():
    # Fetch all the questionnaire-question relationships along with the relevant fields
    questionnaire_questions = db.session.query(
        QuestionnaireQuestions,
        Questionnaire.questionnaire_id.label('questionnaire_code'),
        Questionnaire.name.label('questionnaire_name'),
        Questionnaire.questionnaire_type.label('questionnaire_type'),
        Question.question_id.label('question_code'),
        Question.text.label('question_text')
    ).join(Questionnaire, QuestionnaireQuestions.questionnaire_id == Questionnaire.id) \
     .join(Question, QuestionnaireQuestions.question_id == Question.id) \
     .order_by(Questionnaire.questionnaire_id.asc(), Question.question_id.asc()) \
     .all()

    # Optionally, fetch all questionnaires and questions separately for further use
    surveys = Questionnaire.query.order_by(Questionnaire.questionnaire_id.asc()).all()
    questions = Question.query.order_by(Question.question_id.asc()).all()

    # Render the template, passing the questionnaire-question relationships
    return render_template('argon-dashboard/surveys.html',
                           questionnaire_questions=questionnaire_questions,
                           surveys=surveys,
                           questions=questions)


@argon_bp.route('/surveys')
@login_required
def surveys_view():
    # Fetch all the questionnaire-question relationships, ordered by the actual `questionnaire_id` and `question_id`
    questionnaire_questions = db.session.query(QuestionnaireQuestions) \
        .join(Question).join(Questionnaire) \
        .order_by(Questionnaire.questionnaire_id.asc(), Question.question_id.asc()) \
        .all()

    # Render the template, passing the questionnaire-question relationships
    return render_template('argon-dashboard/surveys.html', questionnaire_questions=questionnaire_questions)


@argon_bp.route('/surveys_three')
@login_required
def surveys_view_three():
    # Fetch all the questionnaire-question relationships
    questionnaire_questions = db.session.query(QuestionnaireQuestions).join(Question).join(Questionnaire).all()

    # Render the template, passing the questionnaire-question relationships
    # Optionally, fetch all questionnaires and questions separately for further use
    surveys = Questionnaire.query.order_by(Questionnaire.questionnaire_id.asc()).all()
    questions = Question.query.order_by(Question.question_id.asc()).all()

    return render_template('argon-dashboard/surveys.html',
                           questionnaire_questions=questionnaire_questions,
                           surveys=surveys,
                           questions=questions)



@argon_bp.route('/add_question_to_survey/<int:questionnaire_id>', methods=['GET', 'POST'])
@login_required
def add_question_to_survey(questionnaire_id):
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    form = AddQuestionFormArgon()

    if form.validate_on_submit():
        question_id = form.question_id.data
        question = Question.query.get_or_404(question_id)

        # Create a new relationship in QuestionnaireQuestions
        new_link = QuestionnaireQuestions(questionnaire_id=questionnaire_id, question_id=question_id)
        db.session.add(new_link)
        db.session.commit()

        flash('Question successfully added to the questionnaire!', 'success')
        return redirect(url_for('argon.surveys_view'))

    questions = Question.query.all()  # Fetch all questions
    return render_template('argon-dashboard/add_question_to_survey.html', form=form, questionnaire=questionnaire, questions=questions)


@argon_bp.route('/api/subareas/<int:area_id>', methods=['GET'])
@login_required
def get_subareas(area_id):
    # Join AreaSubareas and Subarea to get both ID and name
    subareas = db.session.query(AreaSubareas, Subarea).join(Subarea, AreaSubareas.subarea_id == Subarea.id).filter(AreaSubareas.area_id == area_id).all()

    # Extract subarea ID and name from the joined query
    subareas_data = [{'id': subarea.Subarea.id, 'name': subarea.Subarea.name} for subarea in subareas]

    print('subareas', subareas_data)
    return jsonify(subareas_data)


@argon_bp.route('/remove_question_from_survey/<int:id>', methods=['POST'])
@login_required
def remove_question_from_survey(id):
    # Find the relationship entry in QuestionnaireQuestions using the ID
    relationship = QuestionnaireQuestions.query.get_or_404(id)

    # Delete the relationship (not the question itself)
    db.session.delete(relationship)
    db.session.commit()

    flash('Question removed from the survey successfully!', 'success')
    return redirect(url_for('argon.surveys_view'))



@argon_bp.route('/api/get_workflow_summary_one', methods=['GET'])
@login_required
def get_workflow_summary_one():
    from flask_login import current_user
    from datetime import datetime, timedelta

    two_years_ago = datetime.utcnow() - timedelta(days=365 * 2)

    # Fetch filter parameters from the request
    company_id = request.args.get('company_id')
    area_id = request.args.get('area_id')
    subarea_id = request.args.get('subarea_id')
    year = request.args.get('year')

    # Base query for fetching documents and workflows
    query = db.session.query(
        BaseData.id.label('document_id'),
        Workflow.id.label('workflow_id')
    ).join(
        DocumentWorkflow, DocumentWorkflow.base_data_id == BaseData.id
    ).join(
        Workflow, DocumentWorkflow.workflow_id == Workflow.id
    ).filter(
        BaseData.area_id.in_([1, 3]),  # Filter area_id in [1, 3]
        DocumentWorkflow.end_date >= two_years_ago  # Filter for workflows ending in the last 2 years
    )

    # Apply dynamic filtering based on selected filters
    if company_id and company_id != "":
        query = query.filter(BaseData.company_id == company_id)
    if area_id and area_id != "":
        query = query.filter(BaseData.area_id == area_id)
    if subarea_id and subarea_id != "":
        query = query.filter(BaseData.subarea_id == subarea_id)
    if year and year != "":
        query = query.filter(BaseData.fi0 == year)

    # Apply role-based filtering
    if current_user.has_role('Admin'):
        pass  # Admins can see everything
    elif current_user.has_role('Manager'):
        company_id = session.get('company_id')  # Assuming company_id is stored in the session
        query = query.filter(BaseData.company_id == company_id)
    elif current_user.has_role('Employee'):
        user_id = current_user.id  # Assuming user_id is associated with BaseData
        query = query.filter(BaseData.user_id == user_id)

    # Fetch distinct document-workflow tuples
    distinct_documents_workflows = query.distinct().all()

    # Calculate the workflow summary
    num_documents = len(set([row.document_id for row in distinct_documents_workflows]))
    num_workflows = len(set([row.workflow_id for row in distinct_documents_workflows]))

    # Create a summary description
    summary_description = f"{num_documents} document(s) in {num_workflows} workflow(s)"

    # Return the workflow summary in JSON format
    summary = {
        'num_documents': num_documents,
        'num_workflows': num_workflows,
        'description': summary_description
    }

    return jsonify(summary)


@argon_bp.route('/api/get_workflow_summary', methods=['GET'])
@login_required
def get_workflow_summary():

    two_years_ago = datetime.utcnow() - timedelta(days=365 * 2)

    # Fetch filter parameters from the request
    company_id = request.args.get('company_id')
    area_id = request.args.get('area_id')
    subarea_id = request.args.get('subarea_id')
    year = request.args.get('year')

    # Base query with joins
    query = db.session.query(
        BaseData.id.label('document_id'),
        Workflow.id.label('workflow_id')
    ).join(
        DocumentWorkflow, DocumentWorkflow.base_data_id == BaseData.id
    ).join(
        Workflow, DocumentWorkflow.workflow_id == Workflow.id
    ).filter(
        BaseData.area_id.in_([1, 3]),  # Filter area_id in [1, 3]
        DocumentWorkflow.end_date >= two_years_ago  # Filter for end_date in the last 2 years
    )

    # Apply dynamic filtering from the request arguments
    if company_id and company_id != "":
        query = query.filter(BaseData.company_id == company_id)
    if area_id and area_id != "":
        query = query.filter(BaseData.area_id == area_id)
    if subarea_id and subarea_id != "":
        query = query.filter(BaseData.subarea_id == subarea_id)
    if year and year != "":
        query = query.filter(BaseData.fi0 == year)

    # Apply role-based filtering
    if current_user.has_role('Admin'):
        pass  # Admins can see everything
    elif current_user.has_role('Manager'):
        company_id = session.get('company_id')  # Assume company_id is stored in the session
        query = query.filter(BaseData.company_id == company_id)
    elif current_user.has_role('Employee'):
        user_id = current_user.id  # Assume user_id is associated with BaseData
        query = query.filter(BaseData.user_id == user_id)

    # Fetch distinct document-workflow tuples
    distinct_documents_workflows = query.distinct().all()

    # Calculate the summary
    num_documents = len(set([row.document_id for row in distinct_documents_workflows]))
    num_workflows = len(set([row.workflow_id for row in distinct_documents_workflows]))

    summary = {
        'num_documents': num_documents,
        'num_workflows': num_workflows,
        'description': f"{num_documents} documents in {num_workflows} workflows"
    }

    return jsonify(summary)


@argon_bp.route('/multi_format_dashboard_data', methods=['GET'])
@login_required
def multi_format_dashboard_data():
    try:
        print("Fetching multi-format dashboard data...")

        # Get filter parameters from request arguments
        company_id = request.args.get('company_id')
        area_id = request.args.get('area_id')
        subarea_id = request.args.get('subarea_id')
        year = request.args.get('year')
        record_type = request.args.get('record_type')

        query = BaseData.query

        if company_id and company_id != "":
            query = query.filter(BaseData.company_id == company_id)
        if area_id and area_id != "":
            query = query.filter(BaseData.area_id == area_id)
        if subarea_id and subarea_id != "":
            query = query.filter(BaseData.subarea_id == subarea_id)
        if year and year != "":
            query = query.filter(BaseData.fi0 == year)
        if record_type and record_type != "":
            query = query.filter(BaseData.record_type == record_type)

        query = query.order_by(BaseData.updated_on)
        records = query.all()
        print(f"Number of records found: {len(records)}")

        # Candlestick data logic for fi* fields
        candlestick_data_fi = []
        for i in range(1, 10):
            fi_values = [(getattr(record, f'fi{i}', None), record.updated_on) for record in records if
                         getattr(record, f'fi{i}', None) not in [None, 0]]
            if fi_values:
                fi_values.sort(key=lambda x: x[1])
                fi_only_values = [val[0] for val in fi_values]
                candlestick_data_fi.append({
                    'x': f'fi{i}',
                    'f': fi_only_values[0],
                    'h': max(fi_only_values),
                    'l': min(fi_only_values),
                    's': fi_only_values[-1],
                })

        print(f"Candlestick Data (fi): {candlestick_data_fi}")

        # Candlestick data logic for fn* fields
        candlestick_data_fn = []
        for i in range(1, 10):
            fn_values = [(getattr(record, f'fn{i}', None), record.updated_on) for record in records if
                         getattr(record, f'fn{i}', None) not in [None, 0]]
            if fn_values:
                fn_values.sort(key=lambda x: x[1])
                fn_only_values = [val[0] for val in fn_values]
                candlestick_data_fn.append({
                    'x': f'fn{i}',
                    'f': fn_only_values[0],
                    'h': max(fn_only_values),
                    'l': min(fn_only_values),
                    's': fn_only_values[-1],
                })

        print(f"Candlestick Data (fn): {candlestick_data_fn}")

        # Filtered document type and area data
        document_type_data = db.session.query(BaseData.record_type, db.func.count(BaseData.id)).group_by(
            BaseData.record_type).filter(
            BaseData.company_id == company_id if company_id else True,
            BaseData.area_id == area_id if area_id else True).all()

        document_type_data = [{'name': record_type or "Unknown", 'value': count} for record_type, count in document_type_data]

        document_area_data = db.session.query(BaseData.area_id, db.func.count(BaseData.id)).group_by(
            BaseData.area_id).filter(
            BaseData.company_id == company_id if company_id else True).all()

        # Handle the case where Area.query.get(area_id) returns None
        document_area_data = [
            {
                'name': (Area.query.get(area_id).name if area_id and Area.query.get(area_id) else "Unknown Area"),
                'value': count
            }
            for area_id, count in document_area_data
        ]

        # Fetch subarea distribution based on the filters, handling NULL values
        '''
        subarea_distribution = db.session.query(
            Area.name,
            func.coalesce(func.count(BaseData.subarea_id), 0).label('subarea_count'),
            Area.id  # Include Area.id for ordering
        ).join(BaseData).filter(
            # Apply your filtering logic here based on company, area, subarea, etc.
        ).group_by(Area.name, Area.id).order_by(Area.id).all()  # Group by and order by Area.id

        # Find the maximum subarea count for percentage calculations
        max_subarea_count = max([count for _, count, _ in subarea_distribution]) if subarea_distribution else 1

        # Prepare the data for the front-end, calculating percentages and rounding to 2 decimal places
        subarea_distribution_data = [
            {
                'area_name': area_name,
                'subarea_count': count,
                'percentage': round((count / max_subarea_count) * 100, 2)  # Calculate percentage and round
            }
            for area_name, count, _ in subarea_distribution
        ]
        '''

        # Fetch subarea distribution based on the filters, handling NULL values
        subarea_distribution = db.session.query(
            Area.name,
            func.coalesce(func.count(BaseData.subarea_id), 0).label('subarea_count'),
            Area.id  # Include Area.id for ordering
        ).join(BaseData).filter(
            # Apply dynamic filtering logic
            BaseData.company_id == company_id if company_id else True,
            BaseData.area_id == area_id if area_id else True,
            BaseData.subarea_id == subarea_id if subarea_id else True,
            BaseData.fi0 == year if year else True
        ).group_by(Area.name, Area.id).order_by(Area.id).all()  # Group by and order by Area.id

        # Find the maximum subarea count for percentage calculations
        max_subarea_count = max([count for _, count, _ in subarea_distribution]) if subarea_distribution else 1

        # Prepare the data for the front-end, calculating percentages and rounding to 2 decimal places
        subarea_distribution_data = [
            {
                'area_name': area_name,
                'subarea_count': count,
                'percentage': round((count / max_subarea_count) * 100, 2)  # Calculate percentage and round
            }
            for area_name, count, _ in subarea_distribution
        ]

        try:
            return jsonify({
                'candlestick_data_fi': candlestick_data_fi or [],
                'candlestick_data_fn': candlestick_data_fn or [],
                'document_type_data': document_type_data or [],
                'document_area_data': document_area_data or [],
                'subarea_distribution': subarea_distribution_data or []
            })
        except Exception as e:
            print(f"Error during dashboard data fetch: {e}")
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        print(f"Error during dashboard data fetch: {e}")
        return jsonify({'error': str(e)}), 500




@argon_bp.route('/products', methods=['GET'])
@login_required
def products_view():
    products = Product.query.all()  # Fetch all products
    return render_template('argon-dashboard/products.html', products=products)


# Create Product
@argon_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    form = ProductForm()  # Assume you have a ProductForm for product creation
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            type=form.type.data,
            description=form.description.data,
            price=form.price.data,
            currency=form.currency.data,
            stripe_product_id=form.stripe_product_id.data,
            stripe_price_id=form.stripe_price_id.data,
            path=form.path.data,
            icon=form.icon.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully', 'success')
        return redirect(url_for('argon.products_view'))
    return render_template('argon-dashboard/create_product.html', form=form)


# View Product
@argon_bp.route('/products/<int:id>', methods=['GET'])
@login_required
def view_product(id):
    product = Product.query.get_or_404(id)
    return render_template('argon-dashboard/view_product.html', product=product)

# Edit Product
@argon_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)  # Populate form with existing data
    if request.method == 'POST' and form.validate_on_submit():
        product.name = form.name.data
        product.type = form.type.data
        product.description = form.description.data
        product.price = form.price.data
        product.currency = form.currency.data
        product.stripe_product_id = form.stripe_product_id.data
        product.stripe_price_id = form.stripe_price_id.data
        product.path = form.path.data
        product.icon = form.icon.data
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('argon.view_product', id=product.id))
    return render_template('argon-dashboard/edit_product.html', form=form)

# Delete Product
@argon_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('argon.products_view'))


# MAIN DASHBOARD - with the 3 areas

@argon_bp.route('/main_dashboard')
def main_dashboard():
    # Query for posts where company_id matches the user's company_id
    # and lifespan is either 'persistent' or 'one_off' with marked_as_read = False
    posts = Post.query.filter(
        Post.company_id == current_user.company_id,
        db.or_(
            Post.lifespan == 'persistent',
            db.and_(Post.lifespan == 'one_off', Post.marked_as_read == False)
        )
    ).order_by(Post.created_at.desc()).all()

    # Render the main dashboard with the posts for the message board
    return render_template('argon-dashboard/main_dashboard.html', posts=posts)


@argon_bp.route('/raccolta_dati/open')
def raccolta_dati_open():
    # Render the reusable template with the appropriate filters
    return render_template('argon-dashboard/dossier_view.html', area_ids=[1, 2])

@argon_bp.route('/audit/open')
def audit_open():
    # Render the reusable template for audits
    return render_template('argon-dashboard/dossier_view.html', area_ids=[3], initiator_id=0)

@argon_bp.route('/remediation/open')
def remediation_open():
    # Render the reusable template for remediation
    return render_template('argon-dashboard/dossier_view.html', area_ids=[3], initiator_id='Authority')


@argon_bp.route('/argon/audit_archive')
def audit_archive():
    # Logic for displaying archived audits
    # return render_template('argon-dashboard/audit_archive.html')
    return render_template('argon-dashboard/dossier_view.html', area_ids=[3], initiator_id=0)

@argon_bp.route('/argon/remediation_archive')
def remediation_archive():
    # Logic for displaying archived remediations
    # return render_template('argon-dashboard/remediation_archive.html')
    return render_template('argon-dashboard/dossier_view.html', area_ids=[3], initiator_id='Authority')

