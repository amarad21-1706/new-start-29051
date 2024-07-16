import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from db import db  # Adjust this import based on your actual project structure
from models.user import Application, PlanApplications, Plan, Users, UserPlans  # Adjust based on actual imports
from forms.forms import AssociateAppsForm, ManageAppForm  # Adjust based on your project structure

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/manage_apps', methods=['GET', 'POST'])
def admin_manage_apps():
    form = ManageAppForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            app_id = form.app_id.data
            name = form.name.data
            path = form.path.data
            icon = form.icon.data

            if app_id:  # Edit existing application
                application = Application.query.get(app_id)
                application.name = name
                application.path = path
                application.icon = icon
            else:  # Create new application
                application = Application(name=name, path=path, icon=icon)
                db.session.add(application)

            db.session.commit()
            return redirect(url_for('admin.admin_manage_apps'))

    app_id = request.args.get('app_id')
    app = Application.query.get(app_id) if app_id else None
    applications = Application.query.all()

    if app:
        form.app_id.data = app.id
        form.name.data = app.name
        form.path.data = app.path
        form.icon.data = app.icon

    return render_template('admin/admin_manage_apps.html', form=form, applications=applications)

@admin_bp.route('/admin/delete_app/<int:app_id>')
def admin_delete_app(app_id):
    application = Application.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for('admin.admin_manage_apps'))

@admin_bp.route('/admin/associate_apps', methods=['GET', 'POST'])
def admin_associate_apps():
    form = AssociateAppsForm()
    form.plan_id.choices = [(plan.id, plan.name) for plan in Plan.query.all()]
    form.application_ids.choices = [(app.id, f'{app.name} ({app.path})') for app in Application.query.all()]

    if form.validate_on_submit():
        plan_id = form.plan_id.data
        application_ids = form.application_ids.data

        # Remove existing associations
        db.session.query(PlanApplications).filter_by(plan_id=plan_id).delete()

        # Add new associations
        for app_id in application_ids:
            association = PlanApplications(plan_id=plan_id, application_id=app_id)
            db.session.add(association)

        db.session.commit()
        return redirect(url_for('admin.admin_associate_apps'))

    return render_template('admin/admin_associate_apps.html', form=form)



@admin_bp.route('/list-icons', methods=['GET'])
def list_icons():
    icons_dir = os.path.join(current_app.root_path, 'static', 'icons')
    icons = []
    for filename in os.listdir(icons_dir):
        if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.svg'):
            icons.append(filename)
    return jsonify(icons)

