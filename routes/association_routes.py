from flask import Flask, jsonify
from forms.forms import MainForm
import requests
from models.user import (Users, UserRoles, Event, Role,
        Plan, Product, PlanProducts, UserPlans,
        Question, QuestionnaireQuestions, Questionnaire,
        Workflow, WorkflowSteps, WorkflowBaseData, DocumentWorkflow, Step,
        Company, CompanyUsers,
        Area, Subarea, AreaSubareas
        #, Application,
        )

# from master_password_reset import admin_reset_password, AdminResetPasswordForm
from forms.forms import (CompanyUserForm, QuestionnaireCompanyForm,
PlanProductsForm, QuestionnaireQuestionForm, WorkflowStepForm,
                         UserDocumentsForm, UserRoleForm, AreaSubareaForm)

from flask import Blueprint, render_template, jsonify
from flask import render_template, request, redirect, url_for, flash
from db import db
from forms.forms import PlanForm  # Assuming your form is in forms.py
from flask_login import login_required
#from app_factory import create_app
from app_factory import roles_required
# app = create_app() #Flask(__name__)

# Create the blueprint object
# Create the blueprint object
association_bp = Blueprint('association', __name__)

@association_bp.route('/manage_user_roles', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_user_roles():
    form = UserRoleForm()
    message = None

    # Populate choices for users and roles
    form.user.choices = [(user.id, user.username) for user in Users.query.all()]
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.cancel.data:
                # Handle cancel button
                return redirect(url_for('index'))
            elif form.add.data:
                # Handle add button
                user_id = form.user.data
                role_id = form.role.data

                # Check if the user-role association already exists
                existing_user_role = UserRoles.query.filter_by(user_id=user_id, role_id=role_id).first()

                if existing_user_role:
                    message = "User role already exists."
                else:
                    # Add logic to associate the user with the selected role
                    new_user_role = UserRoles(user_id=user_id, role_id=role_id)
                    db.session.add(new_user_role)
                    db.session.commit()
                    # Set a success message
                    message = "User role added successfully."

            elif form.delete.data:
                # Handle delete button
                user_id = form.user.data
                role_id = form.role.data

                # Find and delete the user-role association
                user_role_to_delete = UserRoles.query.filter_by(user_id=user_id, role_id=role_id).first()

                if user_role_to_delete:
                    db.session.delete(user_role_to_delete)
                    db.session.commit()
                    message = "User role deleted successfully."
                else:
                    message = "User role not found."
        else:
            message = "Form validation failed. Please check your input."

    # Handle GET request or any case where form validation failed
    return render_template('manage_user_roles.html', form=form, message=message)


@association_bp.route('/get_user_roles/<int:user_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def get_user_roles(user_id):
    try:
        # Fetch the user by ID
        user = Users.query.get_or_404(user_id)

        # Fetch the roles associated with the user
        roles = [{'id': role.id, 'name': role.name, 'description': role.description} for role in
                 user.roles]  # Correctly access role attributes

        return jsonify({'roles': roles}), 200
    except Exception as e:
        app.logger.error(f"Error fetching roles for user {user_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching roles'}), 500


@association_bp.route('/manage_workflow_steps', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def manage_workflow_steps():
    form = WorkflowStepForm()
    message = None

    # Populate choices for workflows and steps
    form.workflow.choices = [(workflow.id, workflow.name) for workflow in Workflow.query.all()]
    form.step.choices = [(step.id, step.name) for step in Step.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.cancel.data:
                # Handle cancel button
                return redirect(url_for('index'))
            elif form.add.data:
                # Handle add button
                workflow_id = form.workflow.data
                step_id = form.step.data

                # Check if the workflow-step association already exists
                existing_workflow_step = WorkflowSteps.query.filter_by(workflow_id=workflow_id, step_id=step_id).first()

                if existing_workflow_step:
                    message = "Workflow step already exists."
                else:
                    # Add logic to associate the workflow to the selected step
                    new_workflow_step = WorkflowSteps(workflow_id=workflow_id, step_id=step_id)
                    db.session.add(new_workflow_step)
                    db.session.commit()
                    # Set a success message
                    message = "Workflow step added successfully."

            elif form.delete.data:
                # Handle delete button
                workflow_id = form.workflow.data
                step_id = form.step.data

                # Find and delete the wkf-step association
                workflow_step_to_delete = WorkflowSteps.query.filter_by(workflow_id=workflow_id, step_id=step_id).first()

                if workflow_step_to_delete:
                    db.session.delete(workflow_step_to_delete)
                    db.session.commit()
                    message = "Workflow step deleted successfully."
                else:
                    message = "Workflow step not found."
        else:
            message = "Form validation failed. Please check your input."

    # Handle GET request or any case where form validation failed
    return render_template('manage_workflow_steps.html', form=form, message=message)


@association_bp.route('/get_workflow_steps/<int:workflow_id>', methods=['GET'])
@login_required
@roles_required('Admin', 'Manager', 'Employee')
def get_workflow_steps(workflow_id):
    try:
        # Fetch the steps associated with the given workflow_id
        workflow = Workflow.query.get_or_404(workflow_id)
        steps = [
            {
                'id': ws.step.id,
                'name': ws.step.name,
            }
            for ws in workflow.workflow_steps  # Assuming `workflow_steps` is a relationship on Workflow model
        ]

        return jsonify({'steps': steps}), 200
    except Exception as e:
        app.logger.error(f"Error fetching steps for workflow {workflow_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching steps'}), 500



@association_bp.route('/manage_company_users', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_company_users():
    form = CompanyUserForm()
    message = None

    # Populate choices for users and roles
    form.company.choices = [(company.id, company.name) for company in Company.query.all()]
    form.user.choices = [(user.id, user.username) for user in Users.query.all()]

    if form.validate_on_submit():
        if form.cancel.data:
            # Handle cancel button
            return redirect(url_for('index'))
        elif form.add.data:
            # Handle add button
            company_id = form.company.data
            user_id = form.user.data

            # Check if the user-role association already exists
            existing_company_user = CompanyUsers.query.filter_by(company_id=company_id, user_id=user_id).first()

            if existing_company_user:
                message = "Link company-user already exists."

            else:
                # Add logic to associate the user with the selected role
                new_company_user = CompanyUsers(company_id=company_id, user_id=user_id)
                db.session.add(new_company_user)
                db.session.commit()
                # Set a success message
                message = "Company user added successfully."

        elif form.delete.data:
            # Handle delete button
            company_id = form.company.data
            user_id = form.user.data

            # Find and delete the user-role association
            company_user_to_delete = CompanyUsers.query.filter_by(company_id=company_id, user_id=user_id).first()

            if company_user_to_delete:
                db.session.delete(company_user_to_delete)
                db.session.commit()
                message = "Company User deleted successfully."

            else:
                message = "Company User not found."

    return render_template('manage_company_users.html', form=form, message=message)


@association_bp.route('/get_company_users/<int:company_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def get_company_users(company_id):
    try:
        # Fetch the users associated with the given company_id
        company = Company.query.get_or_404(company_id)
        users = [
            {
                'id': cu.user.id,
                'username': cu.user.username,
            }
            for cu in company.company_users  # Assuming `company_users` is a relationship on the Company model
        ]

        return jsonify({'users': users}), 200
    except Exception as e:
        app.logger.error(f"Error fetching users for company {company_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching users'}), 500


@association_bp.route('/manage_questionnaire_companies', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_questionnaire_companies():
    form = QuestionnaireCompanyForm()
    message = None

    # Populate choices for users and roles
    form.questionnaire.choices = [(questionnaire.id, questionnaire.name) for questionnaire in Questionnaire.query.all()]
    form.company.choices = [(company.id, company.name) for company in Company.query.all()]

    if form.validate_on_submit():

        if form.cancel.data:
            # Handle cancel button
            return redirect(url_for('index'))
        elif form.add.data:
            # Handle add button
            questionnaire_id = form.questionnaire.data
            company_id = form.company.data

            # Check if the user-role association already exists
            existing_questionnaire_company = QuestionnaireCompanies.query.filter_by(
                company_id=company_id, questionnaire_id=questionnaire_id).first()

            if existing_questionnaire_company:
                message = "Link questionnaire-to-company already exists."

            else:
                # Add logic to associate the user with the selected role
                new_questionnaire_company = QuestionnaireCompanies(
                    company_id=company_id, questionnaire_id=questionnaire_id)
                db.session.add(new_questionnaire_company)
                db.session.commit()
                # Set a success message
                message = "Questionnaire assigned successfully to company."

        elif form.delete.data:
            # Handle delete button
            company_id = form.company.data
            questionnaire_id = form.questionnaire.data

            # Find and delete the user-role association
            questionnaire_company_to_delete = QuestionnaireCompanies.query.filter_by(
                company_id=company_id, questionnaire_id=questionnaire_id).first()

            if questionnaire_company_to_delete:
                db.session.delete(questionnaire_company_to_delete)
                db.session.commit()
                message = "Questionnaire assignment to company deleted successfully."

            else:
                message = "Association of this questionnaire to company not found."

    return render_template('manage_questionnaire_companies.html', form=form, message=message)


@association_bp.route('/get_company_questionnaires/<int:company_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def get_company_questionnaires(company_id):
    try:
        # Fetch questionnaires associated with the selected company
        company = Company.query.get_or_404(company_id)
        questionnaires = [
            {
                'id': qc.questionnaire.id,
                'name': qc.questionnaire.name,
            }
            for qc in company.questionnaire_companies  # Assuming 'questionnaire_companies' is the relationship
        ]

        return jsonify({'questionnaires': questionnaires}), 200
    except Exception as e:
        app.logger.error(f"Error fetching questionnaires for company {company_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching questionnaires'}), 500


@association_bp.route('/manage_questionnaire_questions', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_questionnaire_questions():
    form = QuestionnaireQuestionForm()
    message = None

    # Populate choices for questionnaires and questions
    form.questionnaire.choices = [(questionnaire.id, questionnaire.name) for questionnaire in Questionnaire.query.all()]
    form.question.choices = [(question.id, question.text) for question in Question.query.order_by('question_id').all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.cancel.data:
                return redirect(url_for('index'))
            elif form.add.data:
                questionnaire_id = form.questionnaire.data
                question_id = form.question.data

                existing_questionnaire_question = QuestionnaireQuestions.query.filter_by(
                    question_id=question_id, questionnaire_id=questionnaire_id).first()

                if existing_questionnaire_question:
                    message = "Link questionnaire-to-question already exists."
                else:
                    try:
                        new_questionnaire_question = QuestionnaireQuestions(
                            question_id=question_id, questionnaire_id=questionnaire_id)
                        db.session.add(new_questionnaire_question)
                        db.session.commit()
                        message = f"Question {question_id} assigned successfully to questionnaire {questionnaire_id}."
                    except Exception as e:
                        db.session.rollback()
                        message = f"Question {question_id} not assigned to questionnaire {questionnaire_id}. Error: {e}."

            elif form.delete.data:
                question_id = form.question.data
                questionnaire_id = form.questionnaire.data

                questionnaire_question_to_delete = QuestionnaireQuestions.query.filter_by(
                    question_id=question_id, questionnaire_id=questionnaire_id).first()

                if questionnaire_question_to_delete:
                    db.session.delete(questionnaire_question_to_delete)
                    db.session.commit()
                    message = "Question assignment to questionnaire deleted successfully."
                else:
                    message = "Association of this question to questionnaire not found."

    return render_template('manage_questionnaire_questions.html', form=form, message=message)


@association_bp.route('/get_questionnaire_questions/<int:questionnaire_id>', methods=['GET'])
@login_required
@roles_required('Admin')
def get_questionnaire_questions(questionnaire_id):
    try:
        # Fetch the questionnaire with an order applied to the questions by question_id
        questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
        questions = [
            {
                'id': q.question.id,
                'text': q.question.text,
            }
            for q in questionnaire.questionnaire_questions
            # Apply ordering by question_id
            if q.question
        ]

        # Sort by question ID
        questions = sorted(questions, key=lambda x: x['id'])

        return jsonify({'questions': questions}), 200
    except Exception as e:
        app.logger.error(f"Error fetching questions for questionnaire {questionnaire_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching questions'}), 500


@association_bp.route('/manage_area_subareas', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def manage_area_subareas():
    form = AreaSubareaForm()
    message = None

    # Populate choices for areas and subareas
    form.area.choices = [(area.id, area.name) for area in Area.query.all()]
    form.subarea.choices = [(subarea.id, subarea.name) for subarea in Subarea.query.all()]

    if request.method == 'POST':
        print('AREA post')
        if form.validate_on_submit():

            print('AREA post valid')
            if form.cancel.data:
                return redirect(url_for('index'))
            elif form.add.data:
                # Handle adding a subarea to an area
                area_id = form.area.data
                subarea_id = form.subarea.data

                print('AREA post checking')
                # Check if the area-subarea association already exists
                existing_area_subarea = AreaSubareas.query.filter_by(area_id=area_id, subarea_id=subarea_id).first()

                print('AREA post checked')
                if existing_area_subarea:
                    message = "This subarea is already associated with the selected area."
                else:

                    print('AREA post inserting')
                    try:
                        # Add the new area-subarea association
                        new_area_subarea = AreaSubareas(area_id=area_id, subarea_id=subarea_id)
                        db.session.add(new_area_subarea)
                        db.session.commit()
                        message = "Subarea added to the area successfully."
                    except Exception as e:
                        db.session.rollback()  # Roll back the transaction on error
                        print(f"Error adding subarea: {e}")
                        message = "An error occurred while adding the subarea."

            elif form.delete.data:
                # Handle removing a subarea from an area
                area_id = form.area.data
                subarea_id = form.subarea.data

                # Find and delete the area-subarea association
                area_subarea_to_delete = AreaSubareas.query.filter_by(area_id=area_id, subarea_id=subarea_id).first()

                if area_subarea_to_delete:
                    db.session.delete(area_subarea_to_delete)
                    db.session.commit()
                    message = "Subarea removed from the area successfully."
                else:
                    message = "Subarea not found in the selected area."
        else:
            message = "Form validation failed. Please check your input."

    return render_template('manage_area_subareas.html', form=form, message=message)


@association_bp.route('/get_area_subareas/<int:area_id>', methods=['GET'])
@login_required
def get_area_subareas(area_id):
    # Query the AreaSubareas table to get the subareas for the selected area
    area_subareas = AreaSubareas.query.filter_by(area_id=area_id).all()
    subareas = [{'name': subarea.subarea.name, 'description': subarea.subarea.description} for subarea in area_subareas]

    return jsonify({'subareas': subareas})

