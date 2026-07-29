import joblib
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from db import load_api_metrics, load_system_metrics, load_error_logs
from features import build_feature_frame, FEATURE_COLUMNS
from config import MODEL_DIR, ISOLATION_FOREST_MODEL_PATH, SCALER_PATH

SERVICE_NAME = "travel-agency-api"
CONTAMINATION = 0.05  # expected proportion of anomalous windows; tune based on manual validation below


def train():
    api_df = load_api_metrics(SERVICE_NAME, since_hours=168)
    sys_df = load_system_metrics(SERVICE_NAME, since_hours=168)
    err_df = load_error_logs(SERVICE_NAME, since_hours=168)

    features = build_feature_frame(api_df, sys_df, err_df)
    if features.empty or len(features) < 20:
        raise RuntimeError(
            f"Not enough historical data to train ({len(features)} windows). "
            "Generate more traffic via the Phase 1 load test first."
        )

    X = features[FEATURE_COLUMNS]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION,
        random_state=42,
    )
    model.fit(X_scaled)

    # -1 = anomaly, 1 = normal (scikit-learn's Isolation Forest convention)
    predictions = model.predict(X_scaled)
    scores = model.decision_function(X_scaled)  # higher = more normal, lower/negative = more anomalous

    features["is_anomaly"] = predictions == -1
    features["anomaly_score"] = scores

    print(f"Total windows: {len(features)}")
    print(f"Flagged anomalies: {features['is_anomaly'].sum()}")
    print("\nTop 10 most anomalous windows:")
    print(
        features.sort_values("anomaly_score")
        .head(10)[["timestamp", "avg_response_time_ms", "error_ratio_5xx", "avg_cpu_usage_pct", "anomaly_score"]]
    )

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, ISOLATION_FOREST_MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"\nModel saved to {ISOLATION_FOREST_MODEL_PATH}")


if __name__ == "__main__":
    train()