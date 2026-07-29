import pandas as pd
from config import WINDOW_SECONDS


def resample_api_metrics(df: pd.DataFrame, window_seconds: int = WINDOW_SECONDS) -> pd.DataFrame:
    """Aggregate raw request-level rows into fixed time windows."""
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp")

    freq = f"{window_seconds}s"
    grouped = df.resample(freq)

    windowed = grouped.agg(
        request_count=("response_time_ms", "count"),
        avg_response_time_ms=("response_time_ms", "mean"),
        p95_response_time_ms=("response_time_ms", lambda x: x.quantile(0.95) if len(x) else None),
        std_response_time_ms=("response_time_ms", "std"),
    )

    # status code ratios per window
    total = df["status_code"].resample(freq).count().replace(0, pd.NA)
    err5xx = df[df["status_code"] >= 500]["status_code"].resample(freq).count()
    windowed["error_ratio_5xx"] = (err5xx / total).fillna(0.0)

    windowed = windowed.fillna(0.0)
    windowed["service_name"] = df["service_name"].iloc[0] if not df.empty else None
    return windowed.reset_index()


def resample_system_metrics(df: pd.DataFrame, window_seconds: int = WINDOW_SECONDS) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp")

    freq = f"{window_seconds}s"
    windowed = df.resample(freq).agg(
        avg_cpu_usage_pct=("cpu_usage_pct", "mean"),
        max_cpu_usage_pct=("cpu_usage_pct", "max"),
        avg_memory_used_mb=("memory_used_mb", "mean"),
        max_memory_used_mb=("memory_used_mb", "max"),
    )
    windowed = windowed.ffill().fillna(0.0)  # system metrics are sampled every 15s, forward-fill small gaps
    return windowed.reset_index()


def resample_error_logs(df: pd.DataFrame, window_seconds: int = WINDOW_SECONDS) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp")

    freq = f"{window_seconds}s"
    windowed = df.resample(freq).agg(
        error_count=("status_code", "count"),
        distinct_error_types=("error_message", "nunique"),
    )
    return windowed.fillna(0).reset_index()