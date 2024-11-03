import json
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

    # Populate the form with existing metrics on GET request
    if request.method == 'GET':
        form.metrics.entries = []  # Clear previous entries

        # Loop through the metrics and mark those that exist for this chart
        for metric_name in metric_choices:
            label = existing_metrics.get(metric_name, metric_name)  # Use existing label or default to column name
            selected = metric_name in existing_metrics  # Checkbox selected if metric exists in chart

            form.metrics.append_entry({
                'column_name': metric_name,
                'metric': selected,  # True if already selected for this chart
                'label': label  # Pre-fill label if exists
            })

    # Handle form submission for updating the chart
    if form.validate_on_submit():
        # Update the chart configuration
        chart.chart_name = form.chart_name.data
        chart.chart_type = form.chart_type.data
        chart.x_axis_label = form.x_axis_label.data
        chart.y_axis_label = form.y_axis_label.data
        chart.company_id = form.company_id.data
        chart.area_id = form.area_id.data
        chart.subarea_id = form.subarea_id.data
        chart.fi0 = form.fi0.data

        # Delete old metrics before saving the new ones
        db.session.query(ChartMetric).filter_by(config_chart_id=chart.id).delete()

        # Process metrics and save the updated ones
        for metric_data in form.metrics.data:
            if metric_data['metric']:  # Only process if the checkbox is checked
                metric_name = metric_data['column_name']
                label = metric_data['label'] or metric_name  # Use the default label if not provided

                if metric_name:
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
@chart_bp.route('/view_chart/<int:chart_id>', methods=['GET'])
@login_required
def view_chart(chart_id):
    # Fetch the selected chart configuration
    chart = ConfigChart.query.get_or_404(chart_id)
    print(f"Chart Config: {chart}")  # Debugging: Show chart configuration

    # Fetch the associated metrics for the chart
    metrics = ChartMetric.query.filter_by(config_chart_id=chart.id).all()
    print(f"Metrics: {metrics}")  # Debugging: Show associated metrics

    # List of metric names (fi1, fi2, fn1, etc.)
    metric_names = [metric.metric_name for metric in metrics]
    display_labels = {metric.metric_name: metric.display_label for metric in metrics}
    print(f"Metric Names: {metric_names}")  # Debugging: Show metric names
    print(f"Display Labels: {display_labels}")  # Debugging: Show display labels

    # Dynamically build a query to get the relevant columns from base_data
    selected_columns = [getattr(BaseData, name) for name in metric_names]
    print(f"Selected Columns: {selected_columns}")  # Debugging: Show selected columns

    # Build base query for base_data
    base_data_query = BaseData.query.with_entities(*selected_columns)

    # Apply filters conditionally
    if chart.area_id:
        base_data_query = base_data_query.filter_by(area_id=chart.area_id)

    if chart.subarea_id:
        base_data_query = base_data_query.filter_by(subarea_id=chart.subarea_id)

    # If company_id is None/Null, fetch data for all companies
    if chart.company_id:
        base_data_query = base_data_query.filter_by(company_id=chart.company_id)

    # If fi0 (year) is None/Null, fetch data for all years
    if chart.fi0:
        base_data_query = base_data_query.filter_by(fi0=chart.fi0)

    # Execute the query and fetch the data
    base_data_result = base_data_query.all()
    print(f"Base Data Result: {base_data_result}")  # Debugging: Show result from base_data query

    # Check if base_data_query returns any data
    if not base_data_result:
        print("No data found for this chart configuration.")
        flash('No data available for this chart.')
        return redirect(url_for('charts.list_charts'))

    # Prepare data for the chart (assuming we're generating JSON for a chart library like Chart.js)
    chart_data = {
        "labels": [row[0] for row in base_data_result],  # Assuming first column for x-axis (e.g., Year)
        "datasets": []
    }
    print(f"Chart Data Labels: {chart_data['labels']}")  # Debugging: Show x-axis labels

    # Build datasets from the query
    for idx, metric_name in enumerate(metric_names):
        dataset = {
            "label": display_labels[metric_name],
            "data": [row[idx] for row in base_data_result],
            "fill": False  # Optional: no fill for line charts
        }
        print(f"Dataset for {metric_name}: {dataset}")  # Debugging: Show dataset for each metric
        chart_data['datasets'].append(dataset)

    print(f"Final Chart Data: {chart_data}")  # Debugging: Show final chart data

    # Render the chart template, passing the chart data as JSON
    return render_template('charts/view_chart.html', chart=chart, chart_data=json.dumps(chart_data))
