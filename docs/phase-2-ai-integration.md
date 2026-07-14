# Adding the AI Prediction Service (Phase 2) — Integration Notes

The AI Prediction Service should be added as a new Spring Boot module, following the exact
same pattern as Metrics Storage / Alert / Dashboard:

1. New Kafka consumer group, e.g. `cg-ai-prediction`.
2. Subscribe to the existing topics: `api-request-metrics`, `api-system-metrics`,
   `api-error-logs`, and optionally `api-alerts`.
3. Read historical data from the same PostgreSQL tables (`api_metric`, `system_metric`,
   `error_log`, `alert`) for training/feature data — read-only access is sufficient.
4. Publish predictions as a new topic, e.g. `api-predictions`, using a new event type added
   to `monitoring-common` (additive change, does not touch the four existing event types).

No changes are required to:
- monitoring-starter or any monitored API,
- existing topics or their schemas,
- Metrics Storage, Alert, or Dashboard services.

This is the direct payoff of keeping every service decoupled through Kafka topics only,
established from Phase 1 Step 3 onward.