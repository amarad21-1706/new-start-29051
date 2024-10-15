from flask import Flask, jsonify
from forms.forms import MainForm
import requests
from models.user import (Users, UserRoles, Event,
        Plan, Product, PlanProducts, UserPlans
        #, Application,
        )

from flask import Blueprint, render_template, jsonify
from flask import render_template, request, redirect, url_for, flash
from db import db
from forms.forms import PlanForm  # Assuming your form is in forms.py
from flask_login import login_required
from app_factory import create_app

app = create_app() #Flask(__name__)

# Create the blueprint object
plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/', endpoint='plan_dashboard')
def plan_dashboard():
    print("Plan dashboard route hit")
    return render_template('argon-dashboard/plan_dashboard.html')


@plan_bp.route('/plans', methods=['GET', 'POST'])
@login_required
def plans_view():
    form = PlanForm()  # Initialize the form
    plans = Plan.query.all()  # Fetch the plans

    # Pass the form to the template along with the plans
    return render_template('argon-dashboard/plans.html', plans=plans, form=form)


@plan_bp.route('/<int:id>', methods=['GET'])
@login_required
def view_plan(id):
    plan = Plan.query.get_or_404(id)  # Fetch the plan or return 404 if not found
    return render_template('argon-dashboard/view_plan.html', plan=plan)


@plan_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_plan():
    form = PlanForm()
    if form.validate_on_submit():
        # Get form data
        name = form.name.data
        description = form.description.data
        price = form.price.data
        stripe_plan_id = form.stripe_plan_id.data  # Get Stripe plan ID
        stripe_price_id = form.stripe_price_id.data  # Get Stripe price ID
        billing_cycle = form.billing_cycle.data  # Get billing cycle

        # Create new plan object and add it to the database
        new_plan = Plan(
            name=name,
            description=description,
            stripe_plan_id=stripe_plan_id,
            stripe_price_id=stripe_price_id,
            price=price,
            billing_cycle=billing_cycle
        )
        db.session.add(new_plan)
        db.session.commit()

        flash('Plan created successfully!', 'success')
        return redirect(url_for('plan.plans_view'))

    return render_template('argon-dashboard/create_plan.html', form=form)


@plan_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
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
            return redirect(url_for('plan.view_plan', id=plan.id))
        except:
            flash('Error updating plan', 'danger')
            return redirect(url_for('plan.edit_plan', id=plan.id))
    return render_template('argon-dashboard/edit_plan.html', plan=plan, form=form)


@plan_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_plan(id):
    plan = Plan.query.get_or_404(id)
    try:
        db.session.delete(plan)
        db.session.commit()
        flash('Plan deleted successfully!', 'success')
        return redirect(url_for('list_plans'))
    except:
        flash('Error deleting plan', 'danger')
        return redirect(url_for('plan.view_plan', id=id))


