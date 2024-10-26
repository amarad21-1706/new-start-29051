

from scipy.stats import zscore
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from textblob import TextBlob
import numpy as np

'''
Integrating Results into the React Dashboard
For each AI feature, set up specific endpoints in Flask, and call these endpoints from React to fetch and display the results:

Anomaly Detection: Call /api/anomalies to fetch flagged data and highlight anomalies in charts.
Predictive Modeling: Call /api/predict to fetch forecasted values and display them as a future trend line.
Sentiment Analysis: If feedback data is available, call /api/sentiment and show a pie chart or bar chart summarizing sentiments.
Comparative Analysis: Fetch peer comparisons via /api/comparative and display relative performance, perhaps with a percentile or rank-based chart.
'''

# anomaly detection

def detect_anomalies(data):
    # Convert data to DataFrame for processing
    df = pd.DataFrame(data)

    # Calculate Z-scores for selected metrics
    df['volume_zscore'] = zscore(df['total_volume'])
    df['percentage_zscore'] = zscore(df['average_percentage'])

    # Flag anomalies where Z-score is greater than threshold (e.g., abs(z) > 2)
    df['is_anomaly_volume'] = df['volume_zscore'].abs() > 2
    df['is_anomaly_percentage'] = df['percentage_zscore'].abs() > 2

    # Return only rows where anomalies are detected
    anomalies = df[(df['is_anomaly_volume']) | (df['is_anomaly_percentage'])]
    return anomalies.to_dict(orient='records')


# Predictive Modeling for Time Series Data

def predict_future_trends(data, metric_column, periods=4):
    # Convert data to DataFrame and check if it's non-empty
    df = pd.DataFrame(data)

    # Ensure metric_column exists and has data
    if metric_column not in df or df[metric_column].empty:
        raise ValueError(f"The specified metric column '{metric_column}' is missing or has no data.")

    try:
        # Fit the ARIMA model
        model = ARIMA(df[metric_column], order=(1, 1, 1))
        model_fit = model.fit()

        # Forecast the next few periods
        forecast = model_fit.forecast(steps=periods)
        return forecast.tolist()  # Return as list for easy JSON serialization
    except Exception as e:
        print("Error fitting ARIMA model:", e)
        return []


# 3. Sentiment Analysis for Customer Feedback


def analyze_sentiment(feedback_text):
    analysis = TextBlob(feedback_text)
    sentiment = analysis.sentiment.polarity
    if sentiment > 0:
        return 'Positive'
    elif sentiment < 0:
        return 'Negative'
    else:
        return 'Neutral'


# 4. Comparative Analysis Across Companies

def comparative_analysis(data, company_id, metric):
    df = pd.DataFrame(data)

    # Calculate percentile rank for each company in the metric
    df[f'{metric}_percentile'] = df[metric].rank(pct=True)
    target_company = df[df['company_id'] == company_id]

    return target_company[[metric, f'{metric}_percentile']].to_dict(orient='records')

