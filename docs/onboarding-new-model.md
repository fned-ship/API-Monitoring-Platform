# Registering a New Prediction Model

Both classification and regression models are added the same way: one entry in
`model_definitions.py`, then a training run. No changes to `orchestrator.py`,
`retrain.py`, or the registry are needed for a new REGRESSION model using an
existing algorithm class. A new CLASSIFICATION algorithm, or a genuinely new
algorithm type, needs one small addition described below.

## Adding a new regression forecaster (e.g. a memory-pressure forecaster)

1. Confirm the target metric already exists in `FEATURE_COLUMNS` (features.py).
   If not, add it to the feature engineering pipeline first.
2. Add one entry to `MODEL_DEFINITIONS` in `model_definitions.py`:
   ```python
   {
       "model_name": "memory_forecaster",
       "model_type": "REGRESSION",
       "trainer_factory": lambda: MetricForecastTrainer("memory_forecaster", "memory_pressure"),
   },
   ```
3. Run `python retrain.py --once` (or wait for the next scheduled run).
4. Confirm it trained and promoted:
   ```bash
   psql -U monitoring -d monitoring_db -c "SELECT * FROM model_registry WHERE model_name='memory_forecaster';"
   ```
5. `orchestrator.py` picks it up automatically on its next registry refresh
   (within REGISTRY_REFRESH_INTERVAL) — no restart needed.
6. Optional: extend Dashboard/Grafana forecast panels to filter on the new
   target_metric, following the exact pattern used for latency/error-rate/CPU.

## Adding a new classification algorithm for an existing model_name

Requires one additional step beyond config, because the *predictor* side must
know how to call the new algorithm's prediction API (see the IsolationForest
vs. RandomForestClassifier branch in `inference.py`'s `HealthRiskPredictor.predict()`):

1. Implement a new `ModelTrainer` subclass (or extend the existing one) for the
   new algorithm, registered under the same `model_name` so it competes for the
   same ACTIVE slot via the normal evaluation gate in `retrain.py`.
2. Add a branch to `HealthRiskPredictor.predict()` in `inference.py` for the
   new `self.algorithm` value.
3. Everything else — registry, retraining, hot-swap, rollback — works unchanged.

## What you should NOT need to do

- Modify `orchestrator.py` to add a new regression model.
- Modify `retrain.py` beyond the `MODEL_DEFINITIONS` list.
- Touch the Kafka topics, `PredictionEvent`, or `MetricForecastEvent` schemas —
  a new model of an existing type reuses the existing event shape.