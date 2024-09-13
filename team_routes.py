
from flask import Blueprint, render_template, flash, redirect, url_for, request
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect, validate_csrf, generate_csrf
from app_factory import csrf  # Import the CSRF object from your app setup
from functools import wraps
from flask import session  # Import session to manage CSRF token

import datetime
from datetime import datetime
from models.user import (Users, UserRoles, Role, Company,
         Plan, UserPlans, Subscription, # Adjust based on actual imports
         Contract, ContractParty, ContractTerm, ContractDocument, ContractStatusHistory,
         ContractArticle, Party, Team, TeamMembership, ContractTeam
         )
from forms.forms import TeamForm

from db import db

# Define the blueprint
team_bp = Blueprint('team', __name__)
# Define the blueprint with the desired URL prefix
contract_bp = Blueprint('contract', __name__, url_prefix='/contracts')


@contract_bp.route('/test')
def test_route():
    return "Admin Blueprint is Working!"

@contract_bp.route('/')
def contract_route():
    return "Contract Blueprint is Working!"


@team_bp.route('/create_team', methods=['GET', 'POST'])
def create_team():
    form = TeamForm()

    if form.validate_on_submit():
        try:
            # Retrieve form data from FlaskForm
            team_name = form.team_name.data
            description = form.description.data

            # Create a new team instance
            new_team = Team(name=team_name, description=description)
            db.session.add(new_team)
            db.session.commit()

            flash('Team created successfully!', 'success')
            return redirect(url_for('team.view_teams'))

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            flash('An error occurred while creating the team. Please try again.', 'danger')
            return redirect(url_for('team.create_team'))

    return render_template('create_team.html', form=form)


@team_bp.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)  # Get the team by ID or return 404 if not found

    if request.method == 'POST':
        try:
            # Get the form data
            team_name = request.form.get('team_name')
            description = request.form.get('description')

            print(f"Updating team: {team_name}, description: {description}")  # Debugging print

            # Update the team's attributes
            team.name = team_name
            team.description = description
            team.updated_at = datetime.utcnow()  # Update the timestamp
            db.session.commit()

            flash('Team updated successfully!', 'success')
            return redirect(url_for('team.view_teams'))  # Redirect to view_teams after successful update

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            flash('An error occurred while updating the team. Please try again.', 'danger')
            return redirect(url_for('team.edit_team', team_id=team_id))

    # For GET request, generate CSRF token and render the form
    csrf_token = generate_csrf()
    return render_template('edit_team.html', team=team, csrf_token=csrf_token)


@team_bp.route('/delete_team/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    try:
        # Fetch the CSRF token from the request form
        csrf_token = request.form.get('csrf_token')
        print(f"Received CSRF token: {csrf_token}")

        # Fetch the team to be deleted
        team = Team.query.get_or_404(team_id)

        # Delete the team
        db.session.delete(team)
        db.session.commit()

        flash('Team deleted successfully!', 'success')
        return redirect(url_for('team.view_teams'))

    except Exception as e:
        print(f"An error occurred while deleting the team: {str(e)}")
        flash('An error occurred while deleting the team. Please try again.', 'danger')
        return redirect(url_for('team.view_teams'))


@team_bp.route('/view_teams', methods=['GET'])
def view_teams():
    try:
        # Fetch all teams sorted by last modified date (descending order)
        teams = Team.query.order_by(Team.updated_at.desc()).all()

        # Map teams to their contracts and members
        team_contracts = {team.id: [ct.contract for ct in team.contract_teams] for team in teams}
        team_members = {team.id: [tm.user for tm in team.memberships] for team in teams}

        return render_template(
            'view_teams.html',
            teams=teams,
            team_contracts=team_contracts,
            team_members=team_members
        )

    except Exception as e:
        print(f"An error occurred in view_teams: {str(e)}")
        flash('An error occurred while retrieving the team list. Please try again.', 'danger')
        return redirect(url_for('team.create_team'))


@team_bp.route('/add_member/<int:team_id>', methods=['GET', 'POST'])
def add_member(team_id):
    try:
        team = Team.query.get_or_404(team_id)

        if request.method == 'POST':
            user_id = request.form.get('user_id')
            role = request.form.get('role')
            access_level = request.form.get('access_level')

            print(f"Received user_id: {user_id}, role: {role}, access_level: {access_level} for team_id: {team_id}")

            if not user_id or not role:
                flash('Both User ID and Role are required to add a member.', 'danger')
                return redirect(url_for('team.add_member', team_id=team_id))

            # Check if the user is already a member of the team
            existing_member = TeamMembership.query.filter_by(user_id=user_id, team_id=team_id).first()
            if existing_member:
                flash('This user is already a member of the team.', 'info')
                return redirect(url_for('team.add_member', team_id=team_id))

            # Add new team member
            new_member = TeamMembership(user_id=user_id, team_id=team_id, role=role, access_level=access_level)
            db.session.add(new_member)

            # Update the team's updated_at field
            team.updated_at = datetime.utcnow()
            db.session.commit()

            flash('Member added successfully!', 'success')
            return redirect(url_for('team.view_teams'))

        # For GET request, render the template to add a member
        users = Users.query.all()
        csrf_token = generate_csrf()
        return render_template('add_member.html', team=team, users=users, csrf_token=csrf_token)

    except Exception as e:
        print(f"An error occurred in add_member: {str(e)}")  # Debugging print to show error
        flash('An error occurred while adding the member. Please try again.', 'danger')
        return redirect(url_for('team.view_teams'))


@team_bp.route('/delete_member/<int:team_id>/<int:user_id>', methods=['POST'])
def delete_member(team_id, user_id):
    try:
        # Retrieve team and member details
        team = Team.query.get_or_404(team_id)
        member = TeamMembership.query.filter_by(team_id=team_id, user_id=user_id).first()

        if not member:
            flash('Member not found in the team.', 'danger')
            return redirect(url_for('team.view_teams'))

        # Remove the member
        db.session.delete(member)

        # Update the team's updated_at field
        team.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Member deleted successfully!', 'success')
        return redirect(url_for('team.view_teams'))

    except Exception as e:
        print(f"An error occurred in delete_member: {str(e)}")  # Debugging print to show error
        flash('An error occurred while deleting the member. Please try again.', 'danger')
        return redirect(url_for('team.view_teams'))

@team_bp.route('/assign_contract/<int:team_id>', methods=['GET', 'POST'])
def assign_contract(team_id):
    try:
        team = Team.query.get_or_404(team_id)
        if request.method == 'POST':
            contract_id = request.form.get('contract_id')
            print(f"Received contract_id: {contract_id} for team_id: {team_id}")

            if not contract_id:
                flash('Contract is required.', 'danger')
                return redirect(url_for('team.assign_contract', team_id=team_id))

            # Check if the contract is already assigned to the team
            existing_assignment = ContractTeam.query.filter_by(team_id=team_id, contract_id=contract_id).first()
            if existing_assignment:
                flash('This contract is already assigned to the team.', 'info')
                return redirect(url_for('team.view_teams'))

            # Create a new assignment of the contract to the team
            contract_team = ContractTeam(team_id=team_id, contract_id=contract_id)
            db.session.add(contract_team)

            # Update the team's updated_at field
            team.updated_at = datetime.utcnow()
            db.session.commit()

            flash('Contract assigned successfully!', 'success')
            return redirect(url_for('team.view_teams'))

        # For GET request, render the form
        contracts = Contract.query.all()
        csrf_token = generate_csrf()
        return render_template('assign_contract.html', team=team, contracts=contracts, csrf_token=csrf_token)

    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Debugging print to show error
        flash('An error occurred while assigning the contract. Please try again.', 'danger')
        return redirect(url_for('team.view_teams'))


def team_member_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        team_id = kwargs.get('team_id')
        if not team_id:
            flash('Team ID is required.', 'danger')
            return redirect(url_for('team.view_teams'))

        user_id = current_user.id  # Assuming Flask-Login is used
        membership = TeamMembership.query.filter_by(user_id=user_id, team_id=team_id).first()
        if not membership:
            flash('You do not have access to this team.', 'danger')
            return redirect(url_for('team.view_teams'))

        return func(*args, **kwargs)
    return wrapper


def user_has_access_to_contract(user_id, contract_id, required_access_level='view'):
   """
   Check if a user has access to a specific contract.
   """
   # Query the memberships and contract teams
   memberships = TeamMembership.query.filter_by(user_id=user_id).all()
   for membership in memberships:
       contract_team = ContractTeam.query.filter_by(contract_id=contract_id, team_id=membership.team_id).first()
       if contract_team:
           if required_access_level == 'view' or contract_team.access_level == required_access_level:
               return True
   return False


@contract_bp.route('/create_article', methods=['POST'])
def create_article():
    try:
        # Get data from the form
        contract_id = request.form.get('contract_id')
        article_title = request.form.get('article_title')
        article_body = request.form.get('article_body')
        csrf_token = request.form.get('csrf_token')  # CSRF token for security

        # Check if all required fields are present
        if not contract_id or not article_title or not article_body:
            flash("All fields are required.", "danger")
            return redirect(request.referrer)

        # Validate CSRF token
        try:
            validate_csrf(csrf_token)
        except Exception as e:
            flash("CSRF token is invalid or missing.", "danger")
            print(f"Error validating CSRF token: {str(e)}")
            return redirect(request.referrer)

        # Create a new ContractArticle instance
        new_article = ContractArticle(
            contract_id=contract_id,
            article_title=article_title,
            article_body=article_body,
            created_at=func.now(),
            updated_at=func.now()
        )

        # Add to the session and commit to the database
        db.session.add(new_article)
        db.session.commit()

        flash("Article created successfully.", "success")
        return redirect(url_for('drafting_contracts.index_view'))  # Corrected endpoint name

    except Exception as e:
        # Handle any errors
        flash(f"An error occurred (01): {str(e)}", "danger")
        return redirect(request.referrer)



@team_bp.route('/protected_team_route/<int:team_id>')
@team_member_required
def protected_team_route(team_id):
    # Your logic here
    pass
