import pandas as pd
from sqlalchemy import text
from db import engine

SERVICE_NAME = "travel-agency-api"
RISK_THRESHOLD = 0.5  # matches is_anomaly's effective cutoff


def load_predictions():
    query = text("""
        SELECT generated_at, risk_score, is_anomaly
        FROM prediction
        WHERE service_name = :service_name
        ORDER BY generated_at
    """)
    return pd.read_sql(query, engine, params={"service_name": SERVICE_NAME})


def load_alerts():
    query = text("""
        SELECT triggered_at, alert_type, severity
        FROM alert
        WHERE service_name = :service_name
        ORDER BY triggered_at
    """)
    return pd.read_sql(query, engine, params={"service_name": SERVICE_NAME})


def evaluate():
    predictions = load_predictions()
    alerts = load_alerts()

    if predictions.empty or alerts.empty:
        print("Not enough data — run simulate_incidents.py first, with both "
              "ai-prediction-service and alert-service running throughout.")
        return

    predictions["generated_at"] = pd.to_datetime(predictions["generated_at"], utc=True)
    alerts["triggered_at"] = pd.to_datetime(alerts["triggered_at"], utc=True)

    lead_times = []
    for _, alert_row in alerts.iterrows():
        # find AI predictions that flagged risk_score >= threshold BEFORE this alert fired
        prior_flags = predictions[
            (predictions["generated_at"] < alert_row["triggered_at"]) &
            (predictions["risk_score"] >= RISK_THRESHOLD)
        ]
        if not prior_flags.empty:
            first_flag_time = prior_flags.iloc[-1]["generated_at"]  # most recent qualifying flag before the alert
            lead_seconds = (alert_row["triggered_at"] - first_flag_time).total_seconds()
            lead_times.append(lead_seconds)
            print(f"Alert '{alert_row['alert_type']}' at {alert_row['triggered_at']} — "
                  f"AI flagged risk {lead_seconds:.0f}s earlier")
        else:
            print(f"Alert '{alert_row['alert_type']}' at {alert_row['triggered_at']} — "
                  f"no prior AI flag found (either coincided, or model missed it)")

    print(f"\n{len(lead_times)} / {len(alerts)} alerts were preceded by an AI risk flag.")
    if lead_times:
        avg_lead = sum(lead_times) / len(lead_times)
        print(f"Average lead time: {avg_lead:.0f} seconds")


if __name__ == "__main__":
    evaluate()