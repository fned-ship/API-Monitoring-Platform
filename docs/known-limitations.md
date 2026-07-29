# Known Limitations (Phase 2, as of Phase 2E)

- **Cold start per service**: a newly onboarded monitored API has no
  prediction coverage until enough of its own history accumulates —
  no transfer learning across services.
- **Single-service scope in current config**: SERVICE_NAME is hardcoded in
  the training entry points; multi-service training requires either looping
  the same scripts per service or extending them to accept a service list
  (not yet implemented).
- **Fixed horizon**: all regressors currently forecast a single 5-minute
  horizon (HORIZON_WINDOWS=5). Multiple horizons per metric would need
  separate registered models (e.g. latency_forecaster_5m,
  latency_forecaster_15m) — supported by the architecture, not yet done.
- **No cross-model correlation**: each model is evaluated independently;
  the platform doesn't yet combine "latency rising AND CPU rising AND
  error rate rising" into a single compound confidence score.
- **In-memory Kafka buffers**: kafka_consumer.py holds recent events in
  process memory (bounded deques) — an orchestrator.py restart loses the
  current window's in-flight buffer (not the historical data in
  PostgreSQL, which is unaffected).
- **contributing_features is a heuristic**, not a formal feature-importance
  explanation (e.g. SHAP) — accurate as a plain-language pointer, not as a
  precise ranked attribution.