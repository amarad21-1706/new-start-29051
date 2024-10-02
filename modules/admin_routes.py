import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from db import db  # Adjust this import based on your actual project structure
from models.user import Product, PlanProducts, Plan, Users, UserPlans  # Adjust based on actual imports
from forms.forms import ManageProductForm, ManagePlanForm  # Adjust based on your project structure
from flask_login import login_required, LoginManager
import logging
from flask import flash  # Import flash function
from sqlalchemy.exc import IntegrityError

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/manage_products', methods=['GET', 'POST'])
@login_required
def admin_manage_products():
    logging.basicConfig(level=logging.DEBUG)
    try:
        form = ManageProductForm()
        logging.debug('Form initialized.')

        if request.method == 'POST':
            logging.debug('POST request received.')
            if form.validate_on_submit():
                logging.debug('Form validated successfully.')
                product_id = form.id.data
                name = form.name.data
                description = form.description.data
                stripe_product_id = form.stripe_product_id.data
                stripe_price_id = form.stripe_price_id.data
                price = form.price.data
                currency = form.currency.data
                path = form.path.data
                icon = form.icon.data

                logging.debug(f'Form data: product_id={product_id}, name={name}, description={description}, stripe_product_id={stripe_product_id}, stripe_price_id={stripe_price_id}, price={price}, currency={currency}, path={path}, icon={icon}')

                if product_id:  # Edit existing product
                    logging.debug(f'Editing existing product with ID: {product_id}')
                    product = Product.query.get(product_id)
                    if product:
                        logging.debug(f'Found product: {product}')
                        product.name = name
                        product.description = description
                        product.stripe_product_id = stripe_product_id
                        product.stripe_price_id = stripe_price_id
                        product.price = price
                        product.currency = currency
                        product.path = path
                        product.icon = icon
                        db.session.commit()
                        logging.debug('Product updated successfully.')
                        flash('Product updated successfully!', 'success')
                    else:
                        logging.error('Product not found.')
                        flash('Product not found.', 'danger')
                else:  # Create new product
                    logging.debug('Creating new product.')
                    existing_product = Product.query.filter_by(name=name).first()
                    if existing_product:
                        logging.error(f'A product with the name {name} already exists.')
                        flash(f'A product with the name {name} already exists. Please choose a different name.', 'danger')
                    else:
                        try:
                            new_product = Product(
                                name=name,
                                description=description,
                                stripe_product_id=stripe_product_id,
                                stripe_price_id=stripe_price_id,
                                price=price,
                                currency=currency,
                                path=path,
                                icon=icon
                            )
                            db.session.add(new_product)
                            db.session.commit()
                            logging.debug('New product created successfully.')
                            flash('New product created successfully!', 'success')
                        except IntegrityError as e:
                            db.session.rollback()
                            logging.error(f'Error creating product: {e}')
                            flash('An error occurred while creating the product. Please try again.', 'danger')

                return redirect(url_for('admin.admin_manage_products'))

        product_id = request.args.get('product_id')
        logging.debug(f'GET request received. product_id={product_id}')
        product = Product.query.get(product_id) if product_id else None
        products = Product.query.all()
        logging.debug(f'Products retrieved: {products}')

        if product:
            form.id.data = product.id
            form.name.data = product.name
            form.description.data = product.description
            form.stripe_product_id.data = product.stripe_product_id
            form.stripe_price_id.data = product.stripe_price_id
            form.price.data = product.price
            form.currency.data = product.currency
            form.path.data = product.path
            form.icon.data = product.icon

        return render_template('admin/admin_manage_products.html', form=form, products=products)
    except Exception as e:
        logging.error(f"Error in admin_manage_products: {e}")
        flash('An error occurred. Please try again later.', 'danger')
        return render_template('admin/admin_manage_products.html', form=form, products=Product.query.all()), 500


@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.admin_manage_products'))



@admin_bp.route('/list-icons', methods=['GET'])
def list_icons():
    icons_dir = os.path.join(current_app.root_path, 'static', 'icons')
    icons = []
    for filename in os.listdir(icons_dir):
        if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.svg'):
            icons.append(filename)
    return jsonify(icons)

@admin_bp.route('/manage_plans', methods=['GET', 'POST'])
@login_required
def admin_manage_plans():
    logging.basicConfig(level=logging.DEBUG)
    try:
        form = ManagePlanForm()
        logging.debug('Form initialized.')

        if request.method == 'POST':
            logging.debug('POST request received.')
            if form.validate_on_submit():
                logging.debug('Form validated successfully.')
                plan_id = form.id.data
                name = form.name.data
                description = form.description.data
                billing_cycle = form.billing_cycle.data

                logging.debug(f'Form data: plan_id={plan_id}, name={name}, description={description}, billing_cycle={billing_cycle}')

                if plan_id:  # Edit existing plan
                    logging.debug(f'Editing existing plan with ID: {plan_id}')
                    plan = Plan.query.get(plan_id)
                    if plan:
                        logging.debug(f'Found plan: {plan}')
                        plan.name = name
                        plan.description = description
                        plan.billing_cycle = billing_cycle
                        db.session.commit()
                        logging.debug('Plan updated successfully.')
                        flash('Plan updated successfully!', 'success')
                    else:
                        logging.error('Plan not found.')
                        flash('Plan not found.', 'danger')
                else:  # Create new plan
                    logging.debug('Creating new plan.')
                    existing_plan = Plan.query.filter_by(name=name).first()
                    if existing_plan:
                        logging.error(f'A plan with the name {name} already exists.')
                        flash(f'A plan with the name {name} already exists. Please choose a different name.', 'danger')
                    else:
                        try:
                            new_plan = Plan(
                                name=name,
                                description=description,
                                billing_cycle=billing_cycle
                            )
                            db.session.add(new_plan)
                            db.session.commit()
                            logging.debug('New plan created successfully.')
                            flash('New plan created successfully!', 'success')
                        except IntegrityError as e:
                            db.session.rollback()
                            logging.error(f'Error creating plan: {e}')
                            flash('An error occurred while creating the plan. Please try again.', 'danger')

                return redirect(url_for('admin.admin_manage_plans'))

        plan_id = request.args.get('plan_id')
        if plan_id:
            logging.debug(f'GET request to edit plan with ID: {plan_id}')
        plan = Plan.query.get(plan_id) if plan_id else None
        plans = Plan.query.all()
        logging.debug(f'Plans retrieved: {plans}')

        if plan:
            form.id.data = plan.id
            form.name.data = plan.name
            form.description.data = plan.description
            form.billing_cycle.data = plan.billing_cycle

        return render_template('admin/admin_manage_plans.html', form=form, plans=plans)
    except Exception as e:
        logging.error(f"Error in admin_manage_plans: {e}")
        flash('An error occurred. Please try again later.', 'danger')
        return render_template('admin/admin_manage_plans.html', form=form, plans=Plan.query.all()), 500



@admin_bp.route('/delete_plan/<int:plan_id>', methods=['POST'])
@login_required
def admin_delete_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    flash('Plan deleted successfully!', 'success')
    return redirect(url_for('admin.admin_manage_plans'))

