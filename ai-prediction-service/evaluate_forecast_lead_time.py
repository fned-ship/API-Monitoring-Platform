import pandas as pd
from sqlalchemy import text
from db import engine

SERVICE_NAME = "travel-agency-api"
TARGET_METRIC = "avg_response_time_ms"
RISING_THRESHOLD_PCT = 0.15  # a forecast counts as "flagged rising" above this predicted change


def load_forecasts():
    query = text("""
        SELECT generated_at, horizon_seconds, current_value, predicted_value, predicted_change_pct
        FROM metric_forecast
        WHERE service_name = :service_name AND target_metric = :target_metric
        ORDER BY generated_at
    """)
    return pd.read_sql(query, engine, params={"service_name": SERVICE_NAME, "target_metric": TARGET_METRIC})


def load_actual_metrics():
    query = text("""
        SELECT timestamp, response_time_ms
        FROM api_metric
        WHERE service_name = :service_name
        ORDER BY timestamp
    """)
    return pd.read_sql(query, engine, params={"service_name": SERVICE_NAME})


def evaluate():
    forecasts = load_forecasts()
    actuals = load_actual_metrics()

    if forecasts.empty or actuals.empty:
        print("Not enough data yet — run the load test with a deliberate /slow spike first.")
        return

    forecasts["generated_at"] = pd.to_datetime(forecasts["generated_at"], utc=True)
    forecasts["target_time"] = forecasts["generated_at"] + pd.to_timedelta(forecasts["horizon_seconds"], unit="s")
    actuals["timestamp"] = pd.to_datetime(actuals["timestamp"], utc=True)

    rising_flags = forecasts[forecasts["predicted_change_pct"] >= RISING_THRESHOLD_PCT]
    print(f"Total forecasts: {len(forecasts)}")
    print(f"Forecasts flagging a rising trend (>= {RISING_THRESHOLD_PCT*100:.0f}%): {len(rising_flags)}")

    lead_times = []
    for _, forecast_row in rising_flags.iterrows():
        # find the first actual spike (response_time_ms notably above the forecast's current_value)
        # occurring after this forecast was generated
        spike_threshold = forecast_row["current_value"] * (1 + RISING_THRESHOLD_PCT)
        subsequent = actuals[
            (actuals["timestamp"] > forecast_row["generated_at"]) &
            (actuals["response_time_ms"] >= spike_threshold)
        ]
        if not subsequent.empty:
            actual_spike_time = subsequent.iloc[0]["timestamp"]
            lead_seconds = (actual_spike_time - forecast_row["generated_at"]).total_seconds()
            lead_times.append(lead_seconds)

    if lead_times:
        avg_lead = sum(lead_times) / len(lead_times)
        print(f"\nForecasts that correctly preceded an actual spike: {len(lead_times)} / {len(rising_flags)}")
        print(f"Average lead time: {avg_lead:.0f} seconds "
              f"(forecast horizon was configured at {forecasts['horizon_seconds'].iloc[0]}s)")
    else:
        print("\nNo rising-trend forecasts were followed by an actual spike in this dataset — "
              "either not enough test spikes were generated, or the model needs more training data.")


if __name__ == "__main__":
    evaluate()