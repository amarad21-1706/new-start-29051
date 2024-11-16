# physical contracts routes and defs
import os

from fredapi import Fred

import requests
from models.user import (
        FuturesPrice, ExchangeRate, InflationData, HistoricalPrice, BenchmarkData
        )

import os
from werkzeug.utils import secure_filename

from flask_login import current_user
from datetime import datetime, timedelta

from flask import Blueprint, render_template, session
from flask import jsonify, redirect, url_for, render_template, request, redirect
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

from finvizfinance.quote import finvizfinance

from saxo_openapi import openapi
from saxo_openapi.contrib.auth import AuthorizationCodeAuth
import json

# ai_bp = Blueprint('ai', __name__, url_prefix='/ai-dashboard')
market_api_bp = Blueprint('market_api', __name__)



@market_api_bp.route('/api-dashboard')
def dashboard():
    session['show_spinner'] = False
    return render_template('api-dashboard/api_dashboard.html')

@market_api_bp.route('/api-dashboard/fetch_financial_data/<ticker>')
def fetch_financial_data(ticker):
    # Fetch stock data using Finviz
    stock = finvizfinance(ticker)
    data = stock.TickerFundament()
    return jsonify(data)

@market_api_bp.route('/api-dashboard/fetch_fx_data')
def fetch_fx_data():
    # Fetch FX data using Saxo Bank API
    params = {"AssetType": "FxSpot", "Uic": 21}  # EUR/USD
    response = saxo_client.reference_data.instruments.get(params=params)
    fx_data = response.json()
    return jsonify(fx_data)




# Example: Fetching financial data for a specific stock (e.g., Apple)
stock = finvizfinance('AAPL')
financial_data = stock.TickerFundament()  # Fetching fundamental data
print(financial_data)



# Replace with your Saxo Bank app's details
client_key = 'your_client_key'
client_secret = 'your_client_secret'
redirect_uri = 'your_redirect_uri'

# Authenticate with Saxo Bank API
auth = AuthorizationCodeAuth(client_key, client_secret, redirect_uri)
client = openapi.OpenAPI(auth)

# Example: Fetching data for a specific instrument (e.g., EURUSD)
params = {
    "AssetType": "FxSpot",
    "Uic": 21  # EUR/USD
}
response = client.reference_data.instruments.get(params=params)
instrument_data = json.loads(response.text)
print(instrument_data)

