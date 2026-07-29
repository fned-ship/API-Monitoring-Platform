# AI Prediction Service — Onboarding

## What it does
Consumes api-request-metrics, api-system-metrics, api-error-logs from Kafka,
computes windowed features, and runs two kinds of models:
- Classification (health_risk_classifier): is this service degraded right now?
- Regression (latency_forecaster, error_rate_forecaster, cpu_forecaster):
  what will this metric's value be ~5 minutes from now?

Publishes PredictionEvent -> api-predictions and MetricForecastEvent ->
api-metric-forecasts. Both are consumed by Dashboard Service and visualized
in Grafana, following the same pattern as every other consumer in the platform.

## Running it locally (no Docker)
1. Kafka + PostgreSQL running (Phase 1 Step 1).
2. `pip install -r requirements.txt` inside a venv.
3. Train at least one model per track: `python train_classification.py`,
   `python train_regression.py` (trains all registered regressors).
4. `python orchestrator.py` — runs continuously, logs each window's results.
5. `python retrain.py --interval-hours 24` (or an OS-scheduled `--once` run)
   for ongoing retraining.

## Minimum data requirements (cold start)
- Regression models: work from day one — self-supervised, no labels needed —
  but need at least ~30-50 non-empty (traffic > 0) windows to train reliably.
- Classification model starts as an Isolation Forest (unsupervised, same
  minimum as above) and only upgrades to a Random Forest once at least 15
  positive (degraded) labeled windows have accumulated, derived from
  threshold breaches and real AlertEvent history. Until then, Isolation
  Forest keeps serving — this fallback is automatic via the evaluation gate
  in retrain.py, not something you need to manage manually.
- A newly onboarded monitored API (per Phase 1's pluggability design) starts
  with ZERO history — expect all four models to be unusable for it until
  enough traffic has accumulated. There is currently no cross-service transfer
  learning; each service's models are trained independently on its own history.