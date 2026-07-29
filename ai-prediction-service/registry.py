import json
from datetime import datetime, timezone
from sqlalchemy import text
from db import engine


def register_candidate(model_name: str, model_type: str, algorithm: str, version: str,
                        artifact_path: str, evaluation_metrics: dict,
                        target_metric: str = None, scaler_path: str = None):
    """Inserts a new CANDIDATE row. Does not affect the currently ACTIVE model."""
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO model_registry
                (model_name, model_type, target_metric, algorithm, version,
                 artifact_path, scaler_path, status, evaluation_metrics, trained_at)
            VALUES
                (:model_name, :model_type, :target_metric, :algorithm, :version,
                 :artifact_path, :scaler_path, 'CANDIDATE', :evaluation_metrics, :trained_at)
        """), {
            "model_name": model_name, "model_type": model_type, "target_metric": target_metric,
            "algorithm": algorithm, "version": version, "artifact_path": artifact_path,
            "scaler_path": scaler_path, "evaluation_metrics": json.dumps(evaluation_metrics),
            "trained_at": datetime.now(timezone.utc),
        })


def promote(model_name: str, version: str):
    now = datetime.now(timezone.utc)
    
    with engine.begin() as conn:
        # 1. Demote any currently ACTIVE model for this model_name
        conn.execute(
            text("""
                UPDATE model_registry 
                SET status = 'ARCHIVED' 
                WHERE model_name = :model_name AND status = 'ACTIVE'
            """),
            {"model_name": model_name}
        )
        
        # 2. Promote the target version regardless of whether it's CANDIDATE or ARCHIVED
        result = conn.execute(
            text("""
                UPDATE model_registry 
                SET status = 'ACTIVE', promoted_at = :now 
                WHERE model_name = :model_name AND version = :version
            """),
            {"model_name": model_name, "version": version, "now": now}
        )
        
        if result.rowcount == 0:
            raise RuntimeError(
                f"Cannot promote version '{version}' for model '{model_name}': "
                f"No record found in model_registry matching version='{version}'."
            )


def get_active_model(model_name: str) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT model_name, model_type, target_metric, algorithm, version,
                   artifact_path, scaler_path, evaluation_metrics, trained_at, promoted_at
            FROM model_registry
            WHERE model_name = :model_name AND status = 'ACTIVE'
        """), {"model_name": model_name}).mappings().first()
        return dict(row) if row else None


def list_active_models() -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT model_name, model_type, target_metric, algorithm, version,
                   artifact_path, scaler_path
            FROM model_registry
            WHERE status = 'ACTIVE'
        """)).mappings().all()
        return [dict(r) for r in rows]


def rollback(model_name: str):
    """Promotes the most recently ARCHIVED version back to ACTIVE (simple one-step rollback)."""
    with engine.connect() as conn:
        previous = conn.execute(text("""
            SELECT version FROM model_registry
            WHERE model_name = :model_name AND status = 'ARCHIVED'
            ORDER BY promoted_at DESC NULLS LAST, trained_at DESC
            LIMIT 1
        """), {"model_name": model_name}).mappings().first()
    if not previous:
        raise RuntimeError(f"No archived version to roll back to for '{model_name}'")
    promote(model_name, previous["version"])