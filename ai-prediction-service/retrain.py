import json
import time
import argparse
from datetime import datetime, timezone

from db import load_api_metrics, load_system_metrics, load_error_logs, load_alerts
from features import build_feature_frame
from model_definitions import MODEL_DEFINITIONS
import registry

SERVICE_NAME = "travel-agency-api"
TEST_FRACTION = 0.2
MIN_CLASSIFICATION_F1 = 0.4
REGRESSION_MAE_TOLERANCE = 1.05  # allow up to 5% worse MAE than current before rejecting


def _is_better(model_type: str, new_metrics: dict, current_metrics: dict | None) -> bool:
    """Type-appropriate comparison — this is what keeps a bad retrain of one model
    from ever affecting another, since each comparison is self-contained per model_type."""
    if current_metrics is None:
        # no ACTIVE model yet for this model_name — promote if it clears the absolute bar
        if model_type == "CLASSIFICATION":
            return new_metrics["f1"] >= MIN_CLASSIFICATION_F1
        return True  # first-ever regressor for this target: promote if it trained at all

    if model_type == "CLASSIFICATION":
        return new_metrics["f1"] >= current_metrics.get("f1", 0.0)

    if model_type == "REGRESSION":
        current_mae = current_metrics.get("mae") or current_metrics.get("mae_ms")
        new_mae = new_metrics.get("mae") or new_metrics.get("mae_ms")
        if current_mae is None or new_mae is None:
            return True
        return new_mae <= current_mae * REGRESSION_MAE_TOLERANCE

    return False


def retrain_one(definition: dict, features_df, alerts_df=None):
    model_name = definition["model_name"]
    model_type = definition["model_type"]
    trainer = definition["trainer_factory"]()

    try:
        if model_type == "CLASSIFICATION":
            X, y = trainer.prepare_training_data(features_df, alerts_df)
        else:
            X, y = trainer.prepare_training_data(features_df)
    except RuntimeError as e:
        print(f"[{model_name}] skipped — {e}")
        return

    split_idx = int(len(X) * (1 - TEST_FRACTION))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model, scaler = trainer.train(X_train, y_train)
    new_metrics = trainer.evaluate(model, X_test, y_test)
    print(f"[{model_name}] new candidate metrics: {new_metrics}")

    version = datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    trainer.save_and_register(model, scaler, new_metrics, version)

    current = registry.get_active_model(model_name)
    current_metrics = json.loads(current["evaluation_metrics"]) if current else None

    if _is_better(model_type, new_metrics, current_metrics):
        registry.promote(model_name, version)
        print(f"[{model_name}] promoted {version} to ACTIVE "
              f"(previous: {current_metrics if current_metrics else 'none'})")
    else:
        print(f"[{model_name}] candidate {version} did NOT beat current ACTIVE "
              f"({current_metrics}) — left as CANDIDATE for manual review")


def run_once(service_name: str = SERVICE_NAME):
    print(f"\n=== Retraining run started: {datetime.now(timezone.utc).isoformat()} ===")
    api_df = load_api_metrics(service_name, since_hours=168)
    sys_df = load_system_metrics(service_name, since_hours=168)
    err_df = load_error_logs(service_name, since_hours=168)
    alerts_df = load_alerts(service_name, since_hours=168)
    features = build_feature_frame(api_df, sys_df, err_df)

    if features.empty:
        print("No historical data available — skipping this retraining run.")
        return

    for definition in MODEL_DEFINITIONS:
        retrain_one(definition, features, alerts_df)

    print(f"=== Retraining run finished: {datetime.now(timezone.utc).isoformat()} ===\n")


def run_scheduled(interval_hours: int):
    print(f"Retraining job running on a schedule: every {interval_hours}h. Ctrl+C to stop.")
    while True:
        run_once()
        time.sleep(interval_hours * 3600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single retraining pass and exit.")
    parser.add_argument("--interval-hours", type=int, default=24, help="Hours between scheduled runs.")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_scheduled(args.interval_hours)