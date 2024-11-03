

from scipy.stats import zscore
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from textblob import TextBlob
import numpy as np
from models.user import Company, Area, Subarea

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
'''
Percentile Rank: This ranks each company relative to others for each metric on a scale from 0 to 1.
A percentile near 0 indicates the company ranks low in that metric compared to peers.
A percentile near 1 indicates the company ranks high in that metric.
Metric Value: This shows the actual value of the metric for the company.
'''


def comparative_analysis(data, metrics):
    import numpy as np
    import pandas as pd

    # Convert data to DataFrame and ensure all required columns are present
    df = pd.DataFrame(data)
    df = df[["company_id", "area_id", "subarea_id"] + metrics].infer_objects()  # Type inference for better handling

    # Fetch names for company, area, and subarea
    company_ids = [int(id) for id in df["company_id"].unique()]
    area_ids = [int(id) for id in df["area_id"].unique()]
    subarea_ids = [int(id) for id in df["subarea_id"].unique()]

    # Fetch and map names to IDs
    company_names = {c.id: c.name for c in Company.query.filter(Company.id.in_(company_ids)).all()}
    area_names = {a.id: a.name for a in Area.query.filter(Area.id.in_(area_ids)).all()}
    subarea_names = {s.id: s.name for s in Subarea.query.filter(Subarea.id.in_(subarea_ids)).all()}

    df["company_name"] = df["company_id"].map(company_names)
    df["area_name"] = df["area_id"].map(area_names)
    df["subarea_name"] = df["subarea_id"].map(subarea_names)

    # Calculate percentile ranks for each metric, grouped by company, area, and subarea
    results = []
    for metric in metrics:
        if metric in df.columns:
            # Calculate the percentile rank only for non-null metric values using .loc
            df_metric = df.loc[df[metric].notnull(), :]
            df.loc[df[metric].notnull(), f"{metric}_percentile"] = df_metric[metric].rank(pct=True)

            # Append each combination result to results list
            for _, row in df.loc[df[metric].notnull(), :].iterrows():
                results.append({
                    "company_name": row["company_name"],
                    "area_name": row["area_name"],
                    "subarea_name": row["subarea_name"],
                    "metric": metric,
                    "value": row[metric],
                    "percentile": row[f"{metric}_percentile"]
                })

    return results
