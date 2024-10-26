

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
def predict_future_trends(data, metrics, periods=4):
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    forecasts = {}
    for metric in metrics:
        if metric in df.columns and not df[metric].dropna().empty:
            try:
                # Prepare and fit the ARIMA model only if the metric has data
                model = ARIMA(df[metric].dropna(), order=(1, 1, 1))  # Handle non-null values only
                model_fit = model.fit()

                # Forecast for the specified number of periods
                forecast = model_fit.forecast(steps=periods)
                forecasts[metric] = forecast.tolist()  # Store forecast as list for each metric
            except Exception as e:
                print(f"Error fitting ARIMA model for metric {metric}: {e}")
                forecasts[metric] = []  # Handle any issues per metric
        else:
            print(f"Metric '{metric}' is missing or has insufficient data.")
            forecasts[metric] = []  # Mark as empty if no data is available

    return forecasts


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
def comparative_analysis(data, company_id, metrics):
    # Convert data to DataFrame and ensure all metrics are columns
    df = pd.DataFrame(data)
    df = df[["company_id"] + metrics].fillna(np.nan)  # Use NaN for missing metrics

    # Calculate percentile rank for each metric
    results = {}
    for metric in metrics:
        if metric in df.columns:
            df_metric = df[df[metric].notnull()]  # Filter for non-null values of the metric
            df[f'{metric}_percentile'] = df_metric[metric].rank(pct=True)
            # Store percentile values for the target company
            results[metric] = df.loc[df['company_id'] == company_id, [metric, f'{metric}_percentile']].to_dict(
                orient='records')

    # Flatten the results for rendering
    flattened_results = []
    for metric, values in results.items():
        for value in values:
            flattened_results.append({
                'metric': metric,
                'value': value[metric],
                'percentile': value[f'{metric}_percentile']
            })

    return flattened_results
