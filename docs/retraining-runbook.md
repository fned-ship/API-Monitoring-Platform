# Retraining Runbook

## Normal operation
`retrain.py` runs on a schedule (cron/Task Scheduler, see Phase 2D) and
evaluates every model in MODEL_DEFINITIONS against a time-based holdout.
Promotion only happens if the new candidate is at least as good as the
currently ACTIVE model of the same model_name (F1 for classification,
MAE with 5% tolerance for regression). A rejected candidate is kept in the
registry with status CANDIDATE for manual review, not deleted.

## Checking current state
SELECT model_name, version, status, promoted_at FROM model_registry
WHERE status = 'ACTIVE';

## Manual rollback
python rollback_model.py <model_name>
Verify via the query above — promoted_at should update, and a running
orchestrator.py picks up the change within REGISTRY_REFRESH_INTERVAL (60s),
no restart required.

## If retraining keeps rejecting candidates
Check evaluation_metrics in model_registry for the CANDIDATE rows — if F1/MAE
is consistently worse than ACTIVE, the likely causes are: not enough new
training data since the last successful promotion, a recent traffic pattern
change the model hasn't adapted to yet, or (for classification specifically)
too few new positive-labeled windows. This is expected and safe behavior,
not a bug — the ACTIVE model keeps serving unaffected.

## If orchestrator.py has been down and just restarted
It will load whatever is currently ACTIVE per model_name — no special
recovery steps needed. Kafka consumer groups resume from `latest` offset
(live data only), so no backlog replay occurs; historical gaps are simply
not backfilled into predictions (they remain fully captured in Metrics
Storage's tables regardless, per Phase 1).