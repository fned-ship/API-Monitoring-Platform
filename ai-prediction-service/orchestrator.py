import time
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

from config import WINDOW_SECONDS
from kafka_consumer import start_consumers, get_recent_events, known_services
from kafka_producer import make_producer, publish_event
from features import build_feature_frame
from inference import HealthRiskPredictor, MetricForecastPredictor
from prediction_event import PredictionEvent
from metric_forecast_event import MetricForecastEvent
from debounce import Debouncer
from persistence import save_prediction, save_forecast
import registry

ANOMALY_RISK_THRESHOLD = 0.4
FORECAST_HORIZON_SECONDS = WINDOW_SECONDS * 5
REGISTRY_REFRESH_INTERVAL = 60  # re-check for newly promoted/retrained models every N seconds
HEARTBEAT_FILE = Path("orchestrator.heartbeat")

def _events_to_df(events: list) -> pd.DataFrame:
    return pd.DataFrame(events) if events else pd.DataFrame()


def _rename_for_windowing(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    if df.empty:
        return df
    if kind == "metric":
        return df.rename(columns={"serviceName": "service_name", "statusCode": "status_code",
                                   "responseTimeMs": "response_time_ms"})
    if kind == "system":
        return df.rename(columns={"serviceName": "service_name", "cpuUsagePercent": "cpu_usage_pct",
                                   "memoryUsedMb": "memory_used_mb", "memoryMaxMb": "memory_max_mb"})
    if kind == "error":
        return df.rename(columns={"serviceName": "service_name", "statusCode": "status_code",
                                   "errorMessage": "error_message"})
    return df


def _contributing_features(latest_window: dict) -> list:
    notes = []
    if latest_window.get("latency_trend", 0) > 100:
        notes.append(f"latency rising ({latest_window['latency_trend']:.0f}ms over last window)")
    if latest_window.get("error_ratio_5xx", 0) > 0.05:
        notes.append(f"5xx error ratio at {latest_window['error_ratio_5xx']*100:.1f}%")
    if latest_window.get("cpu_trend", 0) > 10:
        notes.append(f"CPU usage rising ({latest_window['cpu_trend']:.1f}pp over last window)")
    return notes or ["no single dominant factor — flagged by overall pattern deviation"]


def _load_active_regression_predictors() -> dict:
    predictors = {}
    for entry in registry.list_active_models():
        if entry["model_type"] == "REGRESSION":
            p = MetricForecastPredictor(entry["model_name"])
            if p.is_ready():
                predictors[entry["model_name"]] = p
    return predictors


#############
def run():
    print("Starting AI Prediction Service — Phase 2E: hardened")
    start_consumers()
    time.sleep(5)

    health_predictor = HealthRiskPredictor()
    regression_predictors = _load_active_regression_predictors()
    print(f"Active regression models: {list(regression_predictors.keys())}")

    producer = make_producer()
    debouncer = Debouncer()
    last_registry_refresh = time.time()

    while True:
        time.sleep(WINDOW_SECONDS)

        try:
            if time.time() - last_registry_refresh > REGISTRY_REFRESH_INTERVAL:
                health_predictor.reload()
                regression_predictors = _load_active_regression_predictors()
                last_registry_refresh = time.time()
        except Exception as e:
            print(f"[orchestrator] registry refresh failed, keeping previous models loaded: {e}")

        for service_name in known_services():
            try:
                _process_service_window(
                    service_name, health_predictor, regression_predictors, producer, debouncer
                )
            except Exception as e:
                # log and move on — one service's bad window must never stop the others
                print(f"[orchestrator] ERROR processing service='{service_name}': {e!r} — skipping this window")
                
        HEARTBEAT_FILE.write_text(datetime.now(timezone.utc).isoformat())


def _process_service_window(service_name, health_predictor, regression_predictors, producer, debouncer):
    api_df = _rename_for_windowing(_events_to_df(get_recent_events("api-request-metrics", service_name)), "metric")
    sys_df = _rename_for_windowing(_events_to_df(get_recent_events("api-system-metrics", service_name)), "system")
    err_df = _rename_for_windowing(_events_to_df(get_recent_events("api-error-logs", service_name)), "error")

    features = build_feature_frame(api_df, sys_df, err_df)
    if features.empty:
        return

    latest_window = features.iloc[-1].to_dict()
    window_ts = latest_window.get("timestamp")
    window_ts_str = window_ts.isoformat() if hasattr(window_ts, "isoformat") else str(window_ts)

    # --- classification track ---
    try:
        if health_predictor.is_ready():
            health_result = health_predictor.predict(latest_window)
            save_prediction(
                service_name=service_name, prediction_type="ANOMALY_DETECTED",
                risk_score=health_result["risk_score"], confidence=health_result["raw_score"],
                is_anomaly=health_result["is_anomaly"], model_version=health_result["model_version"],
                window_timestamp=window_ts_str,
            )
            if health_result["risk_score"] >= ANOMALY_RISK_THRESHOLD:
                severity = "HIGH" if health_result["risk_score"] >= 0.75 else "MEDIUM"
                if debouncer.should_publish(service_name, "ANOMALY_DETECTED", severity):
                    event = PredictionEvent.create(
                        service_name=service_name, prediction_type="ANOMALY_DETECTED",
                        risk_score=health_result["risk_score"], confidence=health_result["raw_score"],
                        contributing_features=_contributing_features(latest_window),
                        model_version=health_result["model_version"], window_timestamp=window_ts_str,
                    )
                    publish_event(producer, "api-predictions", service_name, event.to_json_dict())
                    print(f"[classification] published: service={service_name} severity={severity} "
                          f"risk={health_result['risk_score']:.3f}")
    except Exception as e:
        print(f"[classification] ERROR for service='{service_name}': {e!r} — skipping this track this window")

    # --- regression track: each forecaster isolated from the others ---
    for model_name, predictor in regression_predictors.items():
        try:
            result = predictor.predict(latest_window)
            forecast_event = MetricForecastEvent.create(
                service_name=service_name, target_metric=result["target_metric"],
                current_value=result["current_value"], predicted_value=result["predicted_value"],
                horizon_seconds=FORECAST_HORIZON_SECONDS, model_version=result["model_version"],
                window_timestamp=window_ts_str,
            )
            forecast_dict = forecast_event.to_json_dict()
            save_forecast(forecast_dict)
            publish_event(producer, "api-metric-forecasts", service_name, forecast_dict)
        except Exception as e:
            print(f"[regression:{model_name}] ERROR for service='{service_name}': {e!r} — skipping")

####


if __name__ == "__main__":
    run()