import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone


@dataclass
class MetricForecastEvent:
    forecast_id: str
    service_name: str
    target_metric: str
    current_value: float
    predicted_value: float
    predicted_change_pct: float
    horizon_seconds: int
    trend_direction: str          # RISING | FALLING | STABLE
    model_version: str
    window_timestamp: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def create(service_name: str, target_metric: str, current_value: float,
               predicted_value: float, horizon_seconds: int,
               model_version: str, window_timestamp: str) -> "MetricForecastEvent":
        change_pct = ((predicted_value - current_value) / current_value) if current_value else 0.0
        if change_pct > 0.05:
            trend = "RISING"
        elif change_pct < -0.05:
            trend = "FALLING"
        else:
            trend = "STABLE"

        return MetricForecastEvent(
            forecast_id=str(uuid.uuid4()),
            service_name=service_name,
            target_metric=target_metric,
            current_value=round(current_value, 2),
            predicted_value=round(predicted_value, 2),
            predicted_change_pct=round(change_pct, 4),
            horizon_seconds=horizon_seconds,
            trend_direction=trend,
            model_version=model_version,
            window_timestamp=window_timestamp,
        )

    def to_json_dict(self) -> dict:
        return asdict(self)