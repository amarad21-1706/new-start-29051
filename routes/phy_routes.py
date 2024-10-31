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
    return render_template('phy-dashboard/futures_prices.html', futures_data=futures_data)

# Route to view exchange rates data
@phy_bp.route('/exchange_rates')
def exchange_rates_view():
    exchange_data = ExchangeRate.query.all()
    return render_template('phy-dashboard/exchange_rates.html', exchange_data=exchange_data)

# Route to view inflation data
@phy_bp.route('/inflation_data')
def inflation_data_view():
    inflation_data = InflationData.query.all()
    return render_template('phy-dashboard/inflation_data.html', inflation_data=inflation_data)

# Route to view historical prices data
@phy_bp.route('/historical_prices')
def historical_prices_view():
    historical_data = HistoricalPrice.query.all()
    return render_template('phy-dashboard/historical_prices.html', historical_data=historical_data)

# Route to view benchmark data
@phy_bp.route('/benchmark_data')
def benchmark_data_view():
    benchmark_data = BenchmarkData.query.all()
    return render_template('phy-dashboard/benchmark_data.html', benchmark_data=benchmark_data)


# Route for comparative analysis
@phy_bp.route('/comparative_analysis')
def comparative_analysis():
    # Load all contracts and futures data
    contracts = PhysicalContract.query.all()
    futures_data = FuturesPrice.query.all()

    # Dictionary to store futures prices by date for easy lookup
    futures_prices_by_date = {f.date: f for f in futures_data}

    # Add comparison logic to each contract
    comparative_results = []
    for contract in contracts:
        # Get the future price for the contract's period, if it exists
        future_price = futures_prices_by_date.get(contract.date)

        if future_price:
            # Compare market price with future price and annotate results
            comparison = {
                'contract_id': contract.contract_id,
                'price': contract.price,
                'market_price': contract.market_price,
                'futures_price': future_price.future_price,
                'comparison': "Above Futures Price" if contract.market_price > future_price.future_price else "Below Futures Price"
            }
        else:
            # If no future price is available for the contract's date
            comparison = {
                'contract_id': contract.contract_id,
                'price': contract.price,
                'market_price': contract.market_price,
                'futures_price': None,
                'comparison': "No Matching Future Price"
            }

        comparative_results.append(comparison)

    return render_template('phy-dashboard/comparative_analysis.html', comparative_results=comparative_results)


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

def load_data_from_fred_old():
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


def load_data_from_fred():
    fred_key = os.getenv("FRED_API_KEY")
    fred = Fred(api_key=fred_key)

    try:

        # Inflation Data
        inflation_series = fred.get_series('CPIAUCSL')
        for date, rate in inflation_series.items():
            date_str = str(date).split()[0]  # Split off any time part if present
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if not InflationData.query.filter_by(date=date_obj).first():
                db.session.add(InflationData(date=date_obj, inflation_rate=round(rate, 2)))

        print('inflation')


        # Futures Prices
        futures_series = fred.get_series('DGS10')  # Replace 'DGS10' with the appropriate FRED series ID
        for date, price in futures_series.items():
            date_str = str(date).split()[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if not FuturesPrice.query.filter_by(date=date_obj).first():
                db.session.add(FuturesPrice(date=date_obj, future_price=round(price, 2), contract_period="10-Year"))

        print('futures')

        # Exchange Rates
        exchange_series = fred.get_series('DEXUSEU')  # Replace 'EXUSUK' with the appropriate series ID
        for date, rate in exchange_series.items():
            date_str = str(date).split()[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if not ExchangeRate.query.filter_by(date=date_obj).first():
                db.session.add(ExchangeRate(date=date_obj, currency="USD/EUR", exchange_rate=round(rate, 4)))

        print('exchange')

        # Historical Prices
        historical_series = fred.get_series('SP500')  # Replace 'SP500' with the appropriate series ID
        for date, price in historical_series.items():
            date_str = str(date).split()[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if not HistoricalPrice.query.filter_by(date=date_obj).first():
                db.session.add(HistoricalPrice(date=date_obj, historical_price=round(price, 2)))

        print('sp500')

        # Benchmark Data
        benchmark_series = fred.get_series('GS10')  # Example: U.S. 10-Year Treasury Yield
        for date, price in benchmark_series.items():
            date_str = str(date).split()[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if not BenchmarkData.query.filter_by(contract_type="10-Year Treasury Yield", benchmark_price=price).first():
                db.session.add(BenchmarkData(contract_type="10-Year Treasury Yield", benchmark_price=round(price, 2),
                                             benchmark_conditions="Standard"))

        print('GS10')

        db.session.commit()
        print("All data loaded successfully.")
        flash("All data loaded successfully!", "success")

    except Exception as e:
        print(f"Error loading data: {e}")
        flash("Failed to load some data from FRED.", "danger")

