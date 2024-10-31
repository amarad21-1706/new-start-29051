# physical contracts routes and defs
import os

from fredapi import Fred

import requests
from models.user import (BaseData, Users, UserRoles, Event,
        Questionnaire, Question, QuestionnaireQuestions, Questionnaire_psf, Response_psf,
        Contract, ContractParty, ContractTerm, ContractDocument, ContractStatusHistory,
        ContractArticle, Party,
        Company, CompanyUsers, Area, Subarea, AreaSubareas, Answer,
        Team, TeamMembership, ContractTeam,
        Plan, Product, PlanProducts, UserPlans, Post,
        Dossier, Action, PhysicalContract,
        FuturesPrice, ExchangeRate, InflationData, HistoricalPrice, BenchmarkData
        )

import os
from werkzeug.utils import secure_filename

from flask_login import current_user
from datetime import datetime, timedelta

from flask import Blueprint, render_template
from flask import flash, jsonify, redirect, url_for, render_template, request, redirect
from db import db
from forms.forms import (PhysicalContractForm) # Assuming your form is in forms.py
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
phy_bp = Blueprint('phy', __name__)


# Route for the main dashboard
@phy_bp.route('/phy_dashboard')
@login_required
def ai_dashboard():
    return render_template('phy-dashboard/phy_dashboard.html')


@phy_bp.route('/add', methods=['GET', 'POST'])
def add_contract():
    form = PhysicalContractForm()
    if form.validate_on_submit():
        # Check if contract already exists to avoid duplicates
        existing_contract = PhysicalContract.query.filter_by(contract_id=form.contract_id.data).first()
        if existing_contract:
            flash("Contract already exists.")
            return redirect(url_for('phy.add_contract'))

        # Create and add new contract
        new_contract = PhysicalContract(
            contract_id=form.contract_id.data,
            price=form.price.data,
            costs=form.costs.data,
            margins=form.margins.data,
            market_price=form.market_price.data,
            futures_prices=form.futures_prices.data,
            terms=form.terms.data
        )
        db.session.add(new_contract)
        db.session.commit()
        return redirect(url_for('phy.compare_physical_contracts', contract_id=new_contract.id))

    return render_template('phy-dashboard/add_physical_contract.html', form=form)



# Route to view futures prices data
@phy_bp.route('/futures_prices')
def futures_prices_view():
    futures_data = FuturesPrice.query.all()
    return render_template('futures_prices.html', futures_data=futures_data)

# Route to view exchange rates data
@phy_bp.route('/exchange_rates')
def exchange_rates_view():
    exchange_data = ExchangeRate.query.all()
    return render_template('exchange_rates.html', exchange_data=exchange_data)

# Route to view inflation data
@phy_bp.route('/inflation_data')
def inflation_data_view():
    inflation_data = InflationData.query.all()
    return render_template('phy-dashboard/inflation_data.html', inflation_data=inflation_data)

# Route to view historical prices data
@phy_bp.route('/historical_prices')
def historical_prices_view():
    historical_data = HistoricalPrice.query.all()
    return render_template('historical_prices.html', historical_data=historical_data)

# Route to view benchmark data
@phy_bp.route('/benchmark_data')
def benchmark_data_view():
    benchmark_data = BenchmarkData.query.all()
    return render_template('benchmark_data.html', benchmark_data=benchmark_data)

# Route for comparative analysis (optional)
@phy_bp.route('/comparative_analysis')
def comparative_analysis():
    # Logic for comparative analysis goes here (e.g., comparing PhysicalContracts with FuturesPrice data)
    # Assuming you need to load both PhysicalContract and FuturesPrice for comparison
    contracts = PhysicalContract.query.all()
    futures_data = FuturesPrice.query.all()
    return render_template('comparative_analysis.html', contracts=contracts, futures_data=futures_data)


# Separate route to load data from FRED or other sources

@phy_bp.route('/load_data', methods=['POST'])
def load_data():
    try:
        print('loading data from Fred triggered')
        load_data_from_fred()  # Fetch and load data from FRED
        flash("Data loaded successfully!", "success")
        return jsonify({"message": "Data loaded successfully"}), 200
    except Exception as e:
        print(f"Error loading data: {e}")
        flash("Failed to load data from FRED.", "danger")
        return jsonify({"message": "Failed to load data"}), 500

from datetime import datetime

def load_data_from_fred():
    fred_key = os.getenv("FRED_API_KEY")  # Load FRED API key
    fred = Fred(api_key=fred_key)
    print('FRED API initialized.')

    # Fetching inflation data as an example
    inflation_series = fred.get_series('CPIAUCSL')  # Replace with desired FRED series ID

    # Process and store each data point
    for date, rate in inflation_series.items():
        # print(date, rate)
        # Remove time portion from datetime string
        date_str = str(date).split()[0]  # Gets only the date portion
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Check if record for this date already exists to prevent duplicates
        existing_record = InflationData.query.filter_by(date=date_obj).first()

        if not existing_record:
            # Create a new entry for each date-rate pair
            inflation_entry = InflationData(
                date=date_obj,
                inflation_rate=round(rate, 2)  # Rounding as needed
            )
            db.session.add(inflation_entry)
        else:
            print(f"Data for {date_obj} already exists. Skipping.")

    # Commit the transaction to save all entries at once
    db.session.commit()
    print("Data successfully loaded into the database.")
