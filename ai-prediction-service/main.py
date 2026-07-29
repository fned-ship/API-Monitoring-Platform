# ====================================================================
# PYTHON 3.13 KAFKA SELECTOR PATCH
# ====================================================================
import selectors
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Save reference to original unregister behavior
_orig_unregister = selectors.BaseSelector.unregister

def _safe_unregister(self, fileobj):
    try:
        return _orig_unregister(self, fileobj)
    except ValueError as e:
        # If Python 3.13 complains about a dead -1 socket descriptor, bypass it safely
        if "Invalid file descriptor: -1" in str(e):
            return None
        raise

# Apply safe fallback globally to all network socket selectors
selectors.BaseSelector.unregister = _safe_unregister
# ====================================================================


import time
import pandas as pd
from datetime import datetime, timezone

from config import WINDOW_SECONDS
from kafka_consumer import start_consumers, get_recent_events, known_services
from features import build_feature_frame
from inference import AnomalyPredictor
from prediction_event import PredictionEvent
from kafka_producer import make_producer, publish_prediction
from debounce import Debouncer
from persistence import save_prediction

MODEL_VERSION = "isolation_forest_v1"
ANOMALY_RISK_THRESHOLD = 0.4  # below this, don't even consider publishing


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
    """Simple, explainable summary of what stood out in this window — full SHAP-based
    explanations are a later refinement (Phase 2c); this is enough to be useful now."""
    notes = []
    if latest_window.get("latency_trend", 0) > 100:
        notes.append(f"latency rising ({latest_window['latency_trend']:.0f}ms over last window)")
    if latest_window.get("error_ratio_5xx", 0) > 0.05:
        notes.append(f"5xx error ratio at {latest_window['error_ratio_5xx']*100:.1f}%")
    if latest_window.get("cpu_trend", 0) > 10:
        notes.append(f"CPU usage rising ({latest_window['cpu_trend']:.1f}pp over last window)")
    if latest_window.get("avg_cpu_usage_pct", 0) > 80:
        notes.append(f"CPU usage high ({latest_window['avg_cpu_usage_pct']:.1f}%)")
    return notes or ["no single dominant factor — flagged by overall pattern deviation"]


def run_inference_loop():
    predictor = AnomalyPredictor()
    producer = make_producer()
    debouncer = Debouncer()

    while True:
        time.sleep(WINDOW_SECONDS)
        services = known_services()
        if not services:
            print("[main] no services observed yet — waiting for traffic...")
            continue

        for service_name in services:
            api_df = _rename_for_windowing(_events_to_df(get_recent_events("api-request-metrics", service_name)), "metric")
            sys_df = _rename_for_windowing(_events_to_df(get_recent_events("api-system-metrics", service_name)), "system")
            err_df = _rename_for_windowing(_events_to_df(get_recent_events("api-error-logs", service_name)), "error")

            features = build_feature_frame(api_df, sys_df, err_df)
            if features.empty:
                continue

            latest_window = features.iloc[-1].to_dict()
            result = predictor.predict(latest_window)

            window_ts = latest_window.get("timestamp")
            window_ts_str = window_ts.isoformat() if hasattr(window_ts, "isoformat") else str(window_ts)

            # persist every prediction for later evaluation (Step 11), regardless of threshold
            save_prediction(
                service_name=service_name,
                prediction_type="ANOMALY_DETECTED",
                risk_score=result["risk_score"],
                confidence=result["raw_score"],
                is_anomaly=result["is_anomaly"],
                model_version=MODEL_VERSION,
                window_timestamp=window_ts_str,
            )

            if result["risk_score"] < ANOMALY_RISK_THRESHOLD:
                continue

            severity = "HIGH" if result["risk_score"] >= 0.75 else "MEDIUM" if result["risk_score"] >= 0.4 else "LOW"
            if not debouncer.should_publish(service_name, "ANOMALY_DETECTED", severity):
                continue

            event = PredictionEvent.create(
                service_name=service_name,
                prediction_type="ANOMALY_DETECTED",
                risk_score=result["risk_score"],
                confidence=result["raw_score"],
                contributing_features=_contributing_features(latest_window),
                model_version=MODEL_VERSION,
                window_timestamp=window_ts_str,
            )
            publish_prediction(producer, event.to_json_dict())
            print(f"[main] published PredictionEvent: {event.prediction_id} "
                  f"service={service_name} severity={severity} risk={result['risk_score']:.3f}")


if __name__ == "__main__":
    print("Starting AI Prediction Service (Phase 2b — publishing to Kafka + persisting)")
    start_consumers()
    time.sleep(5)
    run_inference_loop()