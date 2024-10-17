from flask import Flask, jsonify
from forms.forms import MainForm
import requests
from models.user import (Users, UserRoles, Event, Role,
        ConfigChart, ChartMetric, Company, Area, Subarea, BaseData
        #, Application,
        )

# from master_password_reset import admin_reset_password, AdminResetPasswordForm
from forms.forms import (ConfigChartForm, ChartMetricForm)
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

from flask import Blueprint, render_template, jsonify
from db import db
from forms.forms import PlanForm  # Assuming your form is in forms.py
from flask_login import login_required
#from app_factory import create_app
from app_factory import roles_required
# app = create_app() #Flask(__name__)

# Create the blueprint object
chart_bp = Blueprint('charts', __name__)


# Routes
# List all chart configurations
@chart_bp.route('/charts')
def list_charts():
    charts = ConfigChart.query.all()
    return render_template('charts/list_charts.html', charts=charts)


# Delete a chart configuration
@chart_bp.route('/delete/<int:id>', methods=['POST'])
def delete_chart(id):
    chart = ConfigChart.query.get_or_404(id)
    db.session.delete(chart)
    db.session.commit()
    flash('Chart configuration deleted successfully!')
    return redirect(url_for('charts.list_charts'))



@chart_bp.route('/add_chart', methods=['GET', 'POST'])
@login_required
def add_chart():
    form = ConfigChartForm()

    # Dynamically extract BaseData columns for fi* and fn*
    base_data_columns = BaseData.__table__.columns
    metric_choices = [col.name for col in base_data_columns if col.name.startswith('fi') or col.name.startswith('fn')]

    # On GET request: Set up form fields dynamically
    if request.method == 'GET':
        form.metrics.entries = []  # Clear previous entries

        # Add each metric checkbox, its editable label, and show the column name
        for metric_name in metric_choices:
            form.metrics.append_entry({
                'column_name': metric_name,  # Display the actual column name (hidden but stored)
                'metric': False,  # Default unchecked
                'label': metric_name  # Default label set to the column name (editable)
            })

    # On POST request: Handle form submission
    if form.validate_on_submit():
        # Create the chart configuration
        new_chart = ConfigChart(
            chart_name=form.chart_name.data,
            chart_type=form.chart_type.data,
            x_axis_label=form.x_axis_label.data,
            y_axis_label=form.y_axis_label.data,
            company_id=form.company_id.data,
            area_id=form.area_id.data,
            subarea_id=form.subarea_id.data,
            fi0=form.fi0.data
        )
        db.session.add(new_chart)
        db.session.commit()

        # Process each selected metric and save it with the custom label
        for metric_data in form.metrics.data:
            metric_name = metric_data.get('column_name')  # Ensure we get the correct column name
            if metric_data['metric']:  # Only process if checked
                label = metric_data['label'] or metric_name  # Default label if not provided

                if metric_name:  # Ensure metric_name is not None
                    print(f"Saving Metric: column_name={metric_name}, label={label}")  # Debugging step
                    new_metric = ChartMetric(
                        config_chart_id=new_chart.id,
                        metric_name=metric_name,  # Save the actual column name
                        display_label=label  # Save the custom label
                    )
                    db.session.add(new_metric)

        db.session.commit()

        flash('Chart configuration added successfully!')
        return redirect(url_for('charts.list_charts'))

    return render_template('charts/add_chart.html', form=form)


@chart_bp.route('/edit_chart/<int:chart_id>', methods=['GET', 'POST'])
@login_required
def edit_chart(chart_id):
    chart = ConfigChart.query.get_or_404(chart_id)
    form = ConfigChartForm(obj=chart)

    # Get existing metrics for this chart
    existing_metrics = {metric.metric_name: metric.display_label for metric in chart.chart_metrics}

    # Dynamically extract BaseData columns for fi* and fn*
    base_data_columns = BaseData.__table__.columns
    metric_choices = [col.name for col in base_data_columns if col.name.startswith('fi') or col.name.startswith('fn')]

    # Populate the form with existing metrics
    # ... (existing code)
    if request.method == 'GET':
        form.metrics.entries = []  # Clear previous entries

        # Populate the form with existing metrics
        for metric_name, label in existing_metrics.items():
            selected = True  # Checkbox selected for existing metrics

            form.metrics.append_entry({
                'column_name': metric_name,  # HiddenField for column name
                'metric': selected,  # Checkbox state based on existing data
                'label': label  # Editable label, pre-filled from existing data
            })

    # On form submission
    if form.validate_on_submit():
        # Update chart details
        chart.chart_name = form.chart_name.data
        chart.chart_type = form.chart_type.data
        chart.x_axis_label = form.x_axis_label.data
        chart.y_axis_label = form.y_axis_label.data
        chart.company_id = form.company_id.data
        chart.area_id = form.area_id.data
        chart.subarea_id = form.subarea_id.data
        chart.fi0 = form.fi0.data

        # Remove old metrics
        db.session.query(ChartMetric).filter_by(config_chart_id=chart.id).delete()

        # Add new metrics
        for metric_data in form.metrics.data:
            if metric_data['metric']:  # Only save selected metrics
                metric_name = metric_data.get('column_name')
                label = metric_data.get('label') or metric_name

                if metric_name is None:
                    flash("Error: metric_name is None.")
                    return render_template('charts/edit_chart.html', form=form)

                new_metric = ChartMetric(
                    config_chart_id=chart.id,
                    metric_name=metric_name,
                    display_label=label
                )
                db.session.add(new_metric)

        db.session.commit()

        flash('Chart configuration updated successfully!')
        return redirect(url_for('charts.list_charts'))

    return render_template('charts/edit_chart.html', form=form)

