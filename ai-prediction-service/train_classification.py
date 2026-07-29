from datetime import datetime, timezone
from sklearn.model_selection import train_test_split

from db import load_api_metrics, load_system_metrics, load_error_logs, load_alerts
from features import build_feature_frame
from trainers.classification_trainer import HealthRiskClassificationTrainer
import registry

SERVICE_NAME = "travel-agency-api"
MIN_F1_TO_PROMOTE = 0.4  # below this, keep as CANDIDATE for manual review rather than auto-promoting


def main():
    api_df = load_api_metrics(SERVICE_NAME, since_hours=168)
    sys_df = load_system_metrics(SERVICE_NAME, since_hours=168)
    err_df = load_error_logs(SERVICE_NAME, since_hours=168)
    alerts_df = load_alerts(SERVICE_NAME, since_hours=168)
    features = build_feature_frame(api_df, sys_df, err_df)

    if features.empty or len(features) < 50:
        raise RuntimeError(f"Not enough historical data ({len(features)} windows).")

    trainer = HealthRiskClassificationTrainer()
    X, y = trainer.prepare_training_data(features, alerts_df)

    # time-based split, same discipline as regression training
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model, scaler = trainer.train(X_train, y_train)
    metrics = trainer.evaluate(model, X_test, y_test)
    print(f"Evaluation on held-out data: {metrics}")

    version = datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    trainer.save_and_register(model, scaler, metrics, version)

    if metrics["f1"] >= MIN_F1_TO_PROMOTE:
        registry.promote(trainer.model_name, version)
        print(f"F1={metrics['f1']} >= {MIN_F1_TO_PROMOTE} — promoted {trainer.model_name} {version} to ACTIVE.")
    else:
        print(f"F1={metrics['f1']} below {MIN_F1_TO_PROMOTE} — registered as CANDIDATE only, "
              f"the previous ACTIVE model (Isolation Forest, if promoted earlier) stays live.")


if __name__ == "__main__":
    main()