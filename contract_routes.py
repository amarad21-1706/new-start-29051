


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

# Define the blueprint with the desired URL prefix
contract_bp = Blueprint('contract', __name__, url_prefix='/contracts')

# Add your route definitions here
@contract_bp.route('/')
def contract_home():
    return "This is the contract home page"

@contract_bp.route('/contract_articles/<int:contract_id>')
def contract_articles(contract_id):
    # Fetch articles filtered by contract_id and ordered by article_order
    print(f"Fetching articles for contract ID: {contract_id}")
    articles = ContractArticle.query.filter_by(contract_id=contract_id).order_by(ContractArticle.article_order).all()
    return render_template('contract_articles.html', articles=articles, contract_id=contract_id)


@contract_bp.route('/edit_article/<int:contract_id>/<int:article_id>', methods=['GET', 'POST'])
def edit_article(contract_id, article_id):
    print(f"Editing article with ID: {article_id} for contract ID: {contract_id}")
    article = ContractArticle.query.get_or_404(article_id)

    if request.method == 'POST':
        try:
            # Update article data
            article.article_title = request.form['article_title']
            article.article_body = request.form['article_body']
            db.session.commit()
            flash('Article updated successfully!', 'success')
        except Exception as e:
            print(f"Error updating article: {e}")
            db.session.rollback()
            flash('An error occurred while updating the article.', 'danger')

        return redirect(url_for('contract_bp.contract_articles', contract_id=contract_id))

    return render_template('edit_article.html', article=article, contract_id=contract_id)


@contract_bp.route('/create_article/<int:contract_id>', methods=['GET', 'POST'])
def create_article(contract_id):
    if request.method == 'POST':
        try:
            # Retrieve form data and create a new article
            article_title = request.form['article_title']
            article_body = request.form['article_body']

            new_article = ContractArticle(
                contract_id=contract_id,
                article_title=article_title,
                article_body=article_body
            )
            db.session.add(new_article)
            db.session.commit()

            flash('New article created successfully!', 'success')
        except Exception as e:
            print(f"Error creating article: {e}")
            db.session.rollback()
            flash('An error occurred while creating the article.', 'danger')

        return redirect(url_for('contract_bp.contract_articles', contract_id=contract_id))

    return render_template('create_article.html', contract_id=contract_id)


@contract_bp.route('/delete_article/<int:contract_id>/<int:article_id>', methods=['POST'])
def delete_article(contract_id, article_id):
    print(f"Deleting article with ID: {article_id} for contract ID: {contract_id}")
    try:
        article = ContractArticle.query.get_or_404(article_id)
        db.session.delete(article)
        db.session.commit()
        flash("Article deleted successfully.", "success")
    except Exception as e:
        print(f"Error deleting article: {e}")
        db.session.rollback()
        flash('An error occurred while deleting the article.', 'danger')

    return redirect(url_for('contract_bp.contract_articles', contract_id=contract_id))
