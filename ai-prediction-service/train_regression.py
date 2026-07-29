from datetime import datetime, timezone
from db import load_api_metrics, load_system_metrics, load_error_logs
from features import build_feature_frame
from trainers.regression_trainer import MetricForecastTrainer
import registry

SERVICE_NAME = "travel-agency-api"
TEST_FRACTION = 0.2

# Adding a new forecaster is exactly one line here — no other code changes.
REGRESSOR_DEFINITIONS = [
    {"model_name": "latency_forecaster", "target_metric": "avg_response_time_ms"},
    {"model_name": "error_rate_forecaster", "target_metric": "error_ratio_5xx"},
    {"model_name": "cpu_forecaster", "target_metric": "avg_cpu_usage_pct"},
]


def train_one(definition: dict, features_df):
    trainer = MetricForecastTrainer(**definition)
    try:
        X, y = trainer.prepare_training_data(features_df)
    except RuntimeError as e:
        print(f"[{definition['model_name']}] skipped: {e}")
        return

    split_idx = int(len(X) * (1 - TEST_FRACTION))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model, scaler = trainer.train(X_train, y_train)
    metrics = trainer.evaluate(model, X_test, y_test)
    print(f"[{definition['model_name']}] evaluation: {metrics}")

    version = datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    trainer.save_and_register(model, scaler, metrics, version)
    registry.promote(trainer.model_name, version)
    print(f"[{definition['model_name']}] promoted {version} to ACTIVE")


def main():
    api_df = load_api_metrics(SERVICE_NAME, since_hours=168)
    sys_df = load_system_metrics(SERVICE_NAME, since_hours=168)
    err_df = load_error_logs(SERVICE_NAME, since_hours=168)
    features = build_feature_frame(api_df, sys_df, err_df)

    if features.empty:
        raise RuntimeError("No historical data available.")

    for definition in REGRESSOR_DEFINITIONS:
        train_one(definition, features)


if __name__ == "__main__":
    main()