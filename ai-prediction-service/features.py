import pandas as pd
from windowing import resample_api_metrics, resample_system_metrics, resample_error_logs

ROLLING_WINDOWS = 5  # number of buckets used for rolling trend features


def build_feature_frame(api_df: pd.DataFrame, system_df: pd.DataFrame, error_df: pd.DataFrame) -> pd.DataFrame:
    api_w = resample_api_metrics(api_df)
    sys_w = resample_system_metrics(system_df)
    err_w = resample_error_logs(error_df)

    if api_w.empty:
        return pd.DataFrame()

    # sys_w / err_w can legitimately be empty (e.g. zero errors in this window) —
    # that's normal, not a data problem. Backfill with zero-valued rows aligned
    # to api_w's timestamps so the merge always has a join key.
    if sys_w.empty:
        sys_w = pd.DataFrame({"timestamp": api_w["timestamp"]})
        for col in ["avg_cpu_usage_pct", "max_cpu_usage_pct", "avg_memory_used_mb", "max_memory_used_mb"]:
            sys_w[col] = 0.0

    if err_w.empty:
        err_w = pd.DataFrame({"timestamp": api_w["timestamp"]})
        for col in ["error_count", "distinct_error_types"]:
            err_w[col] = 0

    merged = api_w.merge(sys_w, on="timestamp", how="left").merge(err_w, on="timestamp", how="left")
    merged = merged.fillna(0.0).sort_values("timestamp").reset_index(drop=True)

    # trend / rate-of-change features
    merged["latency_trend"] = merged["avg_response_time_ms"].diff().fillna(0.0)
    merged["cpu_trend"] = merged["avg_cpu_usage_pct"].diff().fillna(0.0)
    merged["error_trend"] = merged["error_count"].diff().fillna(0.0)

    # rolling volatility / averages
    merged["latency_rolling_std"] = (
        merged["avg_response_time_ms"].rolling(ROLLING_WINDOWS, min_periods=1).std().fillna(0.0)
    )
    merged["cpu_rolling_std"] = (
        merged["avg_cpu_usage_pct"].rolling(ROLLING_WINDOWS, min_periods=1).std().fillna(0.0)
    )

    # lag features — short-term memory without a recurrent model
    for lag in (1, 2, 3):
        merged[f"latency_lag_{lag}"] = merged["avg_response_time_ms"].shift(lag).fillna(0.0)

    # interaction feature: latency rising while CPU also rising is a stronger signal than either alone
    merged["latency_cpu_interaction"] = merged["latency_trend"] * merged["cpu_trend"]

    # memory pressure ratio
    merged["memory_pressure"] = (
        merged["avg_memory_used_mb"] / merged["max_memory_used_mb"].replace(0, pd.NA)
    ).fillna(0.0)

    return merged


def filter_active_windows(df: pd.DataFrame) -> pd.DataFrame:
    """Drops windows with zero requests — these have undefined/meaningless latency,
    not genuinely 'fast' latency, and must not be treated as valid targets or features."""
    return df[df["request_count"] > 0].reset_index(drop=True)


FEATURE_COLUMNS = [
    "request_count", "avg_response_time_ms", "p95_response_time_ms", "std_response_time_ms",
    "error_ratio_5xx", "avg_cpu_usage_pct", "max_cpu_usage_pct", "avg_memory_used_mb",
    "memory_pressure", "error_count", "distinct_error_types",
    "latency_trend", "cpu_trend", "error_trend",
    "latency_rolling_std", "cpu_rolling_std",
    "latency_lag_1", "latency_lag_2", "latency_lag_3",
    "latency_cpu_interaction",
]