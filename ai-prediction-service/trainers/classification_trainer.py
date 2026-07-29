import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score

from trainers.base import ModelTrainer
from features import FEATURE_COLUMNS
from config import MODEL_DIR
from labels import derive_labels, has_enough_positive_samples
import registry


class HealthRiskClassificationTrainer(ModelTrainer):
    """Same model_name as the Isolation Forest version from Pre-Step 2C — the registry
    and orchestrator don't need to know or care that the algorithm underneath changed."""

    model_name = "health_risk_classifier"
    model_type = "CLASSIFICATION"

    def prepare_training_data(self, features_df, alerts_df=None):
        labels = derive_labels(features_df, alerts_df)
        if not has_enough_positive_samples(labels):
            raise RuntimeError(
                f"Only {int(labels.sum())} positive (degraded) samples found — need at least "
                f"{15}. Keep the platform running and generating occasional alerts, or lower "
                "the alert thresholds temporarily, then retry."
            )
        X = features_df[FEATURE_COLUMNS]
        return X, labels

    def train(self, X, y=None):
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = RandomForestClassifier(
            n_estimators=300, max_depth=8, class_weight="balanced", random_state=42
        )
        model.fit(X_scaled, y)
        return model, scaler

    def evaluate(self, model, X, y=None) -> dict:
        scaler = StandardScaler().fit(X)
        X_scaled = scaler.transform(X)
        predictions = model.predict(X_scaled)
        return {
            "precision": round(float(precision_score(y, predictions, zero_division=0)), 4),
            "recall": round(float(recall_score(y, predictions, zero_division=0)), 4),
            "f1": round(float(f1_score(y, predictions, zero_division=0)), 4),
            "n_samples": len(y),
            "n_positive": int(y.sum()),
        }

    def save_and_register(self, model, scaler, metrics: dict, version: str):
        os.makedirs(f"{MODEL_DIR}/{self.model_name}/{version}", exist_ok=True)
        model_path = f"{MODEL_DIR}/{self.model_name}/{version}/model.joblib"
        scaler_path = f"{MODEL_DIR}/{self.model_name}/{version}/scaler.joblib"
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)

        registry.register_candidate(
            model_name=self.model_name, model_type=self.model_type,
            algorithm="RandomForestClassifier", version=version,
            artifact_path=model_path, scaler_path=scaler_path,
            evaluation_metrics=metrics,
        )
        return model_path, scaler_path