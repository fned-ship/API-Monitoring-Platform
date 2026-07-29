import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class PredictionEvent:
    prediction_id: str
    service_name: str
    prediction_type: str          # e.g. "ANOMALY_DETECTED", "LATENCY_DEGRADATION"
    risk_score: float             # normalized 0.0-1.0
    severity: str                 # "LOW" | "MEDIUM" | "HIGH"
    confidence: float             # raw model output, model-specific meaning
    contributing_features: list   # e.g. ["avg_response_time_ms +38%", "avg_cpu_usage_pct +22%"]
    model_version: str
    window_timestamp: str         # timestamp of the data window this prediction is based on
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def create(service_name: str, prediction_type: str, risk_score: float,
               confidence: float, contributing_features: list,
               model_version: str, window_timestamp: str) -> "PredictionEvent":
        severity = "HIGH" if risk_score >= 0.75 else "MEDIUM" if risk_score >= 0.4 else "LOW"
        return PredictionEvent(
            prediction_id=str(uuid.uuid4()),
            service_name=service_name,
            prediction_type=prediction_type,
            risk_score=round(risk_score, 4),
            severity=severity,
            confidence=round(confidence, 4),
            contributing_features=contributing_features,
            model_version=model_version,
            window_timestamp=window_timestamp,
        )

    def to_json_dict(self) -> dict:
        return asdict(self)