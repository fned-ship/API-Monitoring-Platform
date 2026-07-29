from trainers.classification_trainer import HealthRiskClassificationTrainer
from trainers.regression_trainer import MetricForecastTrainer

# The single place that defines "which models exist." Adding a new model means
# adding one entry here — nothing else in the retraining job changes.
MODEL_DEFINITIONS = [
    {
        "model_name": "health_risk_classifier",
        "model_type": "CLASSIFICATION",
        "trainer_factory": lambda: HealthRiskClassificationTrainer(),
    },
    {
        "model_name": "latency_forecaster",
        "model_type": "REGRESSION",
        "trainer_factory": lambda: MetricForecastTrainer("latency_forecaster", "avg_response_time_ms"),
    },
    {
        "model_name": "error_rate_forecaster",
        "model_type": "REGRESSION",
        "trainer_factory": lambda: MetricForecastTrainer("error_rate_forecaster", "error_ratio_5xx"),
    },
    {
        "model_name": "cpu_forecaster",
        "model_type": "REGRESSION",
        "trainer_factory": lambda: MetricForecastTrainer("cpu_forecaster", "avg_cpu_usage_pct"),
    },
]