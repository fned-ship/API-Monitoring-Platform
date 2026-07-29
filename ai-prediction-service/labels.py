import pandas as pd
from config import WINDOW_SECONDS

LATENCY_THRESHOLD_MS = 1000
ERROR_RATIO_THRESHOLD = 0.05
MIN_POSITIVE_SAMPLES = 5  # 15 # below this, supervised training isn't reliable yet


def derive_labels(features_df: pd.DataFrame, alerts_df: pd.DataFrame) -> pd.Series:
    """Two label sources, combined:
    1. Threshold-derived: reuses Alert Service's own thresholds, so the classifier
       starts out learning the same signal the reactive alerts already use.
    2. Alert-derived: any window overlapping an actual triggered AlertEvent is
       labeled positive — reflects what the system already considered noteworthy,
       independent of the exact threshold values.
    """
    df = features_df.copy()
    df["label"] = 0

    threshold_mask = (
        (df["avg_response_time_ms"] > LATENCY_THRESHOLD_MS) |
        (df["error_ratio_5xx"] > ERROR_RATIO_THRESHOLD)
    )
    df.loc[threshold_mask, "label"] = 1

    if not alerts_df.empty:
        window_delta = pd.Timedelta(seconds=WINDOW_SECONDS)
        alert_timestamps = pd.to_datetime(alerts_df["triggered_at"], utc=True)
        for alert_ts in alert_timestamps:
            overlapping = (df["timestamp"] <= alert_ts) & (df["timestamp"] > alert_ts - window_delta)
            df.loc[overlapping, "label"] = 1

    return df["label"]


def has_enough_positive_samples(labels: pd.Series) -> bool:
    return int(labels.sum()) >= MIN_POSITIVE_SAMPLES