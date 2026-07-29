import json
from sqlalchemy import text
from db import engine

INSERT_SQL = text("""
    INSERT INTO prediction
        (prediction_id, service_name, prediction_type, risk_score, severity,
         confidence, is_anomaly, contributing_features, model_version, window_timestamp)
    VALUES
        (:prediction_id, :service_name, :prediction_type, :risk_score, :severity,
         :confidence, :is_anomaly, :contributing_features, :model_version, :window_timestamp)
""")


def save_prediction(service_name: str, prediction_type: str, risk_score: float,
                     confidence: float, is_anomaly: bool, model_version: str,
                     window_timestamp: str, contributing_features: list = None):
    import uuid
    severity = "HIGH" if risk_score >= 0.75 else "MEDIUM" if risk_score >= 0.4 else "LOW"

    with engine.begin() as conn:
        conn.execute(INSERT_SQL, {
            "prediction_id": str(uuid.uuid4()),
            "service_name": service_name,
            "prediction_type": prediction_type,
            "risk_score": risk_score,
            "severity": severity,
            "confidence": confidence,
            "is_anomaly": is_anomaly,
            "contributing_features": json.dumps(contributing_features or []),
            "model_version": model_version,
            "window_timestamp": window_timestamp,
        })

def save_forecast(forecast_event_dict: dict):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO metric_forecast
                (forecast_id, service_name, target_metric, current_value, predicted_value,
                 predicted_change_pct, horizon_seconds, trend_direction, model_version, window_timestamp)
            VALUES
                (:forecast_id, :service_name, :target_metric, :current_value, :predicted_value,
                 :predicted_change_pct, :horizon_seconds, :trend_direction, :model_version, :window_timestamp)
        """), {
            "forecast_id": forecast_event_dict["forecast_id"],
            "service_name": forecast_event_dict["service_name"],
            "target_metric": forecast_event_dict["target_metric"],
            "current_value": forecast_event_dict["current_value"],
            "predicted_value": forecast_event_dict["predicted_value"],
            "predicted_change_pct": forecast_event_dict["predicted_change_pct"],
            "horizon_seconds": forecast_event_dict["horizon_seconds"],
            "trend_direction": forecast_event_dict["trend_direction"],
            "model_version": forecast_event_dict["model_version"],
            "window_timestamp": forecast_event_dict["window_timestamp"],
        })