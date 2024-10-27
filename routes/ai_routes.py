import os
from flask import Flask, jsonify
import requests
from models.user import (BaseData, Users, UserRoles, Event,
        Questionnaire, Question, QuestionnaireQuestions, Questionnaire_psf, Response_psf,
        Contract, ContractParty, ContractTerm, ContractDocument, ContractStatusHistory,
        ContractArticle, Party,
        Company, CompanyUsers, Area, Subarea, AreaSubareas, Answer,
        Team, TeamMembership, ContractTeam,
        Plan, Product, PlanProducts, UserPlans, Post,
        Dossier, Action
        )

import os
from werkzeug.utils import secure_filename

from flask_login import current_user
from datetime import datetime, timedelta

from flask import Blueprint, render_template, jsonify
from flask import render_template, request, redirect, url_for, flash
from db import db
from forms.forms import (MainForm, PlanForm, QuestionnaireFormArgon, QuestionFormArgon,
                         AddQuestionFormArgon, ProductForm, PlanProductsForm) # Assuming your form is in forms.py
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, extract

from app_factory import roles_required, subscription_required

from datetime import datetime
from datetime import timedelta

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from art_intelligence import detect_anomalies, predict_future_trends, analyze_sentiment, comparative_analysis  # Import AI functions

# ai_bp = Blueprint('ai', __name__, url_prefix='/ai-dashboard')
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai_dashboard')
@login_required
def ai_dashboard():
    return render_template('ai-dashboard/ai_dashboard.html')


def get_data_for_anomalies():
    # Dummy data or real data fetching function
    return [{'total_volume': 100, 'average_percentage': 5}, {'total_volume': 110, 'average_percentage': 6}]

def get_data_for_anomalies():
    # Replace this with your data fetching logic, e.g., from a database
    return [
        {'total_volume': 100, 'average_percentage': 5},
        {'total_volume': 110, 'average_percentage': 6},
        # Add more records as needed
    ]

def get_time_series_data():
    # Fetch or generate time series data, e.g., from a database or CSV
    return [
        {'timestamp': '2023-01-01', 'metric_column': 100},
        {'timestamp': '2023-02-01', 'metric_column': 110},
        # Add more records as needed
    ]

def get_feedback_texts():
    # Replace with actual feedback data fetching logic
    return [
        "This product is great!",
        "The service could be improved.",
        "Very satisfied with the support!",
        # Add more feedbacks as needed
    ]


def get_comparative_data():
    # Define all metrics
    metrics = [f'fi{i}' for i in range(1, 15)]

    # Simulate or fetch data, filtering only for area_id in [1, 2]
    data = [
        {'company_id': 1, 'area_id': 1, 'subarea_id': 101, 'fi1': 75, 'fi2': 60},
        {'company_id': 1, 'area_id': 2, 'subarea_id': 102, 'fi1': 85, 'fi3': 78},
        {'company_id': 2, 'area_id': 1, 'subarea_id': 101, 'fi2': 88, 'fi3': 82},
        {'company_id': 2, 'area_id': 2, 'subarea_id': 102, 'fi1': 76, 'fi4': 80},
        # Add more records as necessary
    ]

    # Filter for area_id in [1, 2]
    filtered_data = [record for record in data if record['area_id'] in [1, 2]]

    # Ensure all records have all metrics, filling missing values with NaN
    for record in filtered_data:
        for metric in metrics:
            record.setdefault(metric, None)  # Set to None if metric is missing

    return filtered_data


@ai_bp.route('/anomalies')
def anomalies_view():
    anomalies_data = detect_anomalies(get_data_for_anomalies())
    return render_template('ai-dashboard/anomalies.html', anomalies=anomalies_data)


@ai_bp.route('/api/anomalies', methods=['POST'])
@login_required
def api_anomalies():
    data = request.get_json()
    anomalies = detect_anomalies(data)
    return jsonify(anomalies)

@ai_bp.route('/predict', methods=['GET'])
@login_required
def predict_view():
    metrics = [f'fi{i}' for i in range(1, 13)]
    data = get_time_series_data()  # Replace this with your actual data-fetching logic
    forecast_data = predict_future_trends(data, metrics, periods=4)  # Get forecast data for all metrics

    return render_template('ai-dashboard/predict.html', forecast=forecast_data)

@ai_bp.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    data = request.get_json()
    metric = data.get("metric_column")
    forecast = predict_future_trends(data["data"], metric)
    return jsonify(forecast)

@ai_bp.route('/sentiment', methods=['GET'])
@login_required
def sentiment_view():
    sentiment_data = [analyze_sentiment(feedback) for feedback in get_feedback_texts()]
    return render_template('ai-dashboard/sentiment.html', sentiment=sentiment_data)

@ai_bp.route('/api/sentiment', methods=['POST'])
@login_required
def api_sentiment():
    feedback_text = request.get_json().get("feedback_text")
    sentiment = analyze_sentiment(feedback_text)
    return jsonify({"sentiment": sentiment})


@ai_bp.route('/comparative', methods=['GET'])
@login_required
def comparative_view():
    # Fetch data
    data = get_comparative_data()
    # Perform comparative analysis for a specific company and set of metrics
    company_id = 1  # Example company_id to analyze
    metrics = ['fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fi6', 'fi7', 'fi8', 'fi9', 'fi10', 'fi11', 'fi12']

    # Get analysis results
    print(f"Calling comparative_analysis with data: {data}, metrics: {metrics}")
    comparative_data = comparative_analysis(data, metrics)

    # Render the template
    return render_template('ai-dashboard/comparative.html', comparative=comparative_data)


@ai_bp.route('/api/comparative', methods=['POST'])
@login_required
def api_comparative():
    data = request.get_json()
    company_id = data.get("company_id")
    metric = data.get("metric")
    result = comparative_analysis(data["data"], company_id, metric)
    return jsonify(result)

# EOF AI Insights
