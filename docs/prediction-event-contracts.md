# Prediction Event Contracts

## PredictionEvent (topic: api-predictions)
Classification/anomaly track. Fields: prediction_id, service_name,
prediction_type, risk_score (0-1), severity (LOW/MEDIUM/HIGH), confidence,
contributing_features (list of strings), model_version, window_timestamp,
generated_at.

Published only when risk_score crosses ANOMALY_RISK_THRESHOLD (0.4) AND
the debouncer allows it (severity increase or cooldown expired). Every
windowed evaluation is persisted to the `prediction` table regardless of
whether it was published.

## MetricForecastEvent (topic: api-metric-forecasts)
Regression/forecasting track. Fields: forecast_id, service_name,
target_metric, current_value, predicted_value, predicted_change_pct,
horizon_seconds, trend_direction (RISING/FALLING/STABLE), model_version,
window_timestamp, generated_at.

Published every window, for every ACTIVE regression model, unconditionally
(no debouncing) — a forecast's value comes from being a continuous trend
line, unlike an anomaly flag.

## Breaking-change policy
Both schemas are shared across ai-prediction-service (Python) and
monitoring-common (Java, used by Dashboard Service). Any field change must
be applied to both sides in the same change, and any field removal or type
change should be versioned (e.g. a new event type) rather than silently
changed, since Dashboard Service's JSON deserialization will fail on an
incompatible payload.