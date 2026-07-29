import os
import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from trainers.base import ModelTrainer
from features import FEATURE_COLUMNS
from config import MODEL_DIR
import registry

MIN_USABLE_WINDOWS=5

class MetricForecastTrainer(ModelTrainer):
    """Generic regression trainer for any target metric already present in FEATURE_COLUMNS.
    One class, many registered models — this is what makes adding a new forecaster
    (Step 2C.5) a config change rather than a new class."""

    model_type = "REGRESSION"

    def __init__(self, model_name: str, target_metric: str, horizon_windows: int = 5):
        self.model_name = model_name
        self.target_metric = target_metric
        self.horizon_windows = horizon_windows

    def prepare_training_data(self, features_df):
        df = features_df.copy().reset_index(drop=True)

        df["target"] = df[self.target_metric].shift(-self.horizon_windows)
        df["target_request_count"] = df["request_count"].shift(-self.horizon_windows)
        df = df.dropna(subset=["target", "target_request_count"])

        # exclude windows where either end had no traffic — undefined signal, not a real value
        df = df[(df["request_count"] > 0) & (df["target_request_count"] > 0)]

        if len(df) < MIN_USABLE_WINDOWS:
            raise RuntimeError(
                f"Only {len(df)} usable windows for '{self.model_name}' after filtering — "
                "generate more continuous traffic before training."
            )

        X = df[FEATURE_COLUMNS]
        y = df["target"]
        return X, y

    def train(self, X, y=None):
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)
        model.fit(X_scaled, y)
        return model, scaler

    def evaluate(self, model, X, y=None) -> dict:
        scaler = StandardScaler().fit(X)
        X_scaled = scaler.transform(X)
        predictions = model.predict(X_scaled)

        mae = mean_absolute_error(y, predictions)
        rmse = float(np.sqrt(mean_squared_error(y, predictions)))
        actual_direction = np.sign(y.values - X[self.target_metric].values)
        predicted_direction = np.sign(predictions - X[self.target_metric].values)
        directional_accuracy = float((actual_direction == predicted_direction).mean())

        return {
            "mae": round(mae, 4), "rmse": round(rmse, 4),
            "directional_accuracy": round(directional_accuracy, 4), "n_samples": len(y),
        }

    def save_and_register(self, model, scaler, metrics: dict, version: str):
        os.makedirs(f"{MODEL_DIR}/{self.model_name}/{version}", exist_ok=True)
        model_path = f"{MODEL_DIR}/{self.model_name}/{version}/model.joblib"
        scaler_path = f"{MODEL_DIR}/{self.model_name}/{version}/scaler.joblib"
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)

        registry.register_candidate(
            model_name=self.model_name, model_type=self.model_type,
            target_metric=self.target_metric, algorithm="GradientBoostingRegressor",
            version=version, artifact_path=model_path, scaler_path=scaler_path,
            evaluation_metrics=metrics,
        )
        return model_path, scaler_path