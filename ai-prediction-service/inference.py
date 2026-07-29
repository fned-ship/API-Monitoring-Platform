import joblib
import numpy as np
from features import FEATURE_COLUMNS
import registry
import pandas as pd  


class RegistryBackedPredictor:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.version = None
        self.algorithm = None
        self.target_metric = None
        self._load_active()

    def _load_active(self):
        entry = registry.get_active_model(self.model_name)
        if entry is None:
            print(f"[inference] WARNING: no ACTIVE model for '{self.model_name}' yet — "
                  f"this track will be skipped until one is trained and promoted.")
            return
        self.model = joblib.load(entry["artifact_path"])
        self.scaler = joblib.load(entry["scaler_path"]) if entry["scaler_path"] else None
        self.version = entry["version"]
        self.algorithm = entry["algorithm"]
        self.target_metric = entry.get("target_metric")

    def is_ready(self) -> bool:
        return self.model is not None

    def reload(self):
        self._load_active()


class HealthRiskPredictor(RegistryBackedPredictor):
    def __init__(self):
        super().__init__("health_risk_classifier")

    def predict(self, feature_row: dict) -> dict:
        import pandas as pd
        X = pd.DataFrame([{col: feature_row.get(col, 0.0) for col in FEATURE_COLUMNS}])
        X_scaled = self.scaler.transform(X)

        if self.algorithm == "IsolationForest":
            raw_prediction = self.model.predict(X_scaled)[0]        # -1 = anomaly, 1 = normal
            raw_score = self.model.decision_function(X_scaled)[0]   # lower = more anomalous
            is_anomaly = bool(raw_prediction == -1)
            risk_score = float(np.clip(0.5 - raw_score, 0.0, 1.0))

        elif self.algorithm == "RandomForestClassifier":
            # predict_proba returns [[P(class 0), P(class 1)]] — class 1 is "degraded"
            proba = self.model.predict_proba(X_scaled)[0]
            positive_class_idx = list(self.model.classes_).index(1)
            risk_score = float(proba[positive_class_idx])
            raw_score = risk_score
            is_anomaly = risk_score >= 0.5

        else:
            raise RuntimeError(f"Unsupported classification algorithm: {self.algorithm}")

        return {
            "is_anomaly": is_anomaly, "raw_score": float(raw_score),
            "risk_score": risk_score, "model_version": self.version,
        }


class LatencyForecastPredictor(RegistryBackedPredictor):
    def __init__(self):
        super().__init__("latency_forecaster")

    def predict(self, feature_row: dict) -> dict:
        X = pd.DataFrame([{col: feature_row.get(col, 0.0) for col in FEATURE_COLUMNS}])
        X_scaled = self.scaler.transform(X)
        predicted_value = float(self.model.predict(X_scaled)[0])
        current_value = float(feature_row.get("avg_response_time_ms", 0.0))
        return {"predicted_value": predicted_value, "current_value": current_value,
                "model_version": self.version, "target_metric": self.target_metric}

class MetricForecastPredictor(RegistryBackedPredictor):
    def __init__(self, model_name: str):
        super().__init__(model_name)

    def predict(self, feature_row: dict) -> dict:
        import pandas as pd
        X = pd.DataFrame([{col: feature_row.get(col, 0.0) for col in FEATURE_COLUMNS}])
        X_scaled = self.scaler.transform(X)
        predicted_value = float(self.model.predict(X_scaled)[0])
        current_value = float(feature_row.get(self.target_metric, 0.0))
        return {
            "predicted_value": predicted_value, "current_value": current_value,
            "model_version": self.version, "target_metric": self.target_metric,
        }