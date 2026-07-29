from abc import ABC, abstractmethod


class ModelTrainer(ABC):
    """Common interface both classification and regression trainers implement,
    so the orchestrator and retraining job can treat every model uniformly."""

    model_name: str
    model_type: str  # "CLASSIFICATION" | "REGRESSION"

    @abstractmethod
    def prepare_training_data(self, features_df):
        """Returns (X, y) or (X, None) for unsupervised models."""
        raise NotImplementedError

    @abstractmethod
    def train(self, X, y=None):
        """Fits and returns the trained model object (and scaler, if used)."""
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, model, X, y=None) -> dict:
        """Returns a dict of evaluation metrics, type-appropriate."""
        raise NotImplementedError

    @abstractmethod
    def save_and_register(self, model, scaler, metrics: dict, version: str):
        """Serializes the artifact(s) and registers a CANDIDATE row in the Model Registry."""
        raise NotImplementedError