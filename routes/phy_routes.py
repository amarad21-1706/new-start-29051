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

from flask import Blueprint, render_template, session
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
def phy_dashboard():
    # Ensure the session flag is reset when the dashboard loads
    session['show_spinner'] = False
    print('spinner off')
    return render_template('phy-dashboard/phy_dashboard.html')


@phy_bp.route('/trigger_spinner')
def trigger_spinner():
    # Set the spinner status to true when the button is clicked
    session['show_spinner'] = True
    return redirect(url_for('page_a'))

# Placeholder function for external benchmark data (e.g., industry data or indices)
def get_external_benchmark_data():
    # Replace with logic to fetch data from an external source, like ARERA indices or market reports
    return 100  # Example benchmark value

# Placeholder function for internal benchmark data (e.g., contracts within the company)
def get_internal_benchmark_data(contract):
    # Replace with logic to find similar contracts in the company for internal comparison
    return 95  # Example internal benchmark value

# Placeholder function for transportation cost
def get_transportation_cost(contract):
    # Replace with actual transportation cost calculation
    return 10  # Example transportation cost

# Placeholder function for storage cost
def get_storage_cost(contract):
    # Replace with actual storage cost calculation
    return 5  # Example storage cost

# Placeholder function to fetch future price data based on date
def get_future_price(date):
    # Replace with logic to fetch the appropriate future price
    return 120  # Example future price

# Placeholder function to get inflation rate for econometric modeling
def get_inflation_rate(date):
    # Replace with logic to retrieve the inflation rate for a specific date
    return 0.02  # Example inflation rate

# Placeholder function to get exchange rate for econometric modeling
def get_exchange_rate(date):
    # Replace with logic to retrieve the exchange rate for a specific date
    return 1.2  # Example exchange rate

# Placeholder function for calculating OECD compliant price for transfer pricing
def calculate_oecd_compliant_price(contract):
    # Replace with logic following OECD guidelines
    return 110  # Example OECD-compliant price


def comparative_benchmarking(contract):
    external_benchmark = get_external_benchmark_data()  # e.g., market reports, ARERA indices
    internal_benchmark = get_internal_benchmark_data(contract)  # Contracts within the group

    # Example comparison output
    return {
        "external": {
            "benchmark": external_benchmark,
            "comparison": "Above Benchmark" if contract.market_price > external_benchmark else "Below Benchmark"
        },
        "internal": {
            "benchmark": internal_benchmark,
            "comparison": "Above Internal Benchmark" if contract.market_price > internal_benchmark else "Below Internal Benchmark"
        }
    }


def cost_plus_analysis(contract):
    procurement_cost = contract.price  # Assuming this represents the base procurement cost
    transportation_cost = get_transportation_cost(contract)
    storage_cost = get_storage_cost(contract)

    # Add a profit margin
    reference_price = procurement_cost + transportation_cost + storage_cost + (procurement_cost * 0.1)  # 10% margin
    return {
        "reference_price": reference_price,
        "comparison": "Above Cost Plus" if contract.market_price > reference_price else "Below Cost Plus"
    }

def shadow_pricing(contract):
    future_price = get_future_price(contract.contract_date)  # TTF or another index
    return {
        "future_price": future_price,
        "comparison": "Above Shadow Price" if contract.market_price > future_price else "Below Shadow Price"
    }


def econometric_modeling(contract):
    inflation_rate = get_inflation_rate(contract.contract_date)
    exchange_rate = get_exchange_rate(contract.contract_date)

    # Simple example regression model
    predicted_price = (contract.price * 1.02) + (exchange_rate * 0.05) - (inflation_rate * 0.03)
    return {
        "predicted_price": predicted_price,
        "comparison": "Above Modeled Price" if contract.market_price > predicted_price else "Below Modeled Price"
    }

def transfer_pricing(contract):
    # Assume a function to verify OECD compliance for intra-group transactions
    oecd_compliant_price = calculate_oecd_compliant_price(contract)
    return {
        "oecd_compliant_price": oecd_compliant_price,
        "comparison": "Compliant" if contract.market_price == oecd_compliant_price else "Non-compliant"
    }


@phy_bp.route('/compare/<int:contract_id>', endpoint='compare_physical_contracts')
def compare_physical_contracts(contract_id):
    # Fetch the specific PhysicalContract by ID
    contract = PhysicalContract.query.get(contract_id)
    if not contract:
        flash("Contract not found.", "danger")
        return redirect(url_for('phy.add_contract'))

    # Perform multi-faceted comparative analysis
    results = {
        "comparative_benchmarking": comparative_benchmarking(contract),
        "cost_plus_analysis": cost_plus_analysis(contract),
        "shadow_pricing": shadow_pricing(contract),
        "econometric_modeling": econometric_modeling(contract),
        "transfer_pricing": transfer_pricing(contract),
    }

    # Render template with results
    return render_template('phy-dashboard/compare_physical_contracts.html', contract=contract, results=results)


@phy_bp.route('/search_contract', methods=['GET', 'POST'])
def search_contract():
    contract_id = request.args.get('contract_id')
    if contract_id:
        # Redirect to the compare_physical_contracts with the provided contract_id
        return redirect(url_for('phy.compare_physical_contracts', contract_id=contract_id))
    else:
        flash("Please enter a valid Contract ID.", "warning")
        return redirect(url_for('phy.phy_dashboard'))  # Redirect back to dashboard or appropriate page


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

        # Pass new_contract.id to the template for use with url_for
        return render_template('phy-dashboard/add_physical_contract.html', form=form, new_contract_id=new_contract.id)

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
        future_price = futures_prices_by_date.get(contract.expiration_date)

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

    session['show_spinner'] = False
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

