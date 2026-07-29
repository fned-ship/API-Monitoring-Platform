import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL

engine = create_engine(DB_URL)


def load_api_metrics(service_name: str, since_hours: int = 168) -> pd.DataFrame:
    query = """
        SELECT service_name, endpoint, http_method, status_code,
               response_time_ms, timestamp
        FROM api_metric
        WHERE service_name = %(service_name)s
          AND timestamp > now() - (%(since_hours)s || ' hours')::interval
        ORDER BY timestamp
    """
    return pd.read_sql(query, engine, params={"service_name": service_name, "since_hours": since_hours})


def load_system_metrics(service_name: str, since_hours: int = 168) -> pd.DataFrame:
    query = """
        SELECT service_name, cpu_usage_pct, memory_used_mb, memory_max_mb, timestamp
        FROM system_metric
        WHERE service_name = %(service_name)s
          AND timestamp > now() - (%(since_hours)s || ' hours')::interval
        ORDER BY timestamp
    """
    return pd.read_sql(query, engine, params={"service_name": service_name, "since_hours": since_hours})


def load_error_logs(service_name: str, since_hours: int = 168) -> pd.DataFrame:
    query = """
        SELECT service_name, endpoint, status_code, error_message, timestamp
        FROM error_log
        WHERE service_name = %(service_name)s
          AND timestamp > now() - (%(since_hours)s || ' hours')::interval
        ORDER BY timestamp
    """
    return pd.read_sql(query, engine, params={"service_name": service_name, "since_hours": since_hours})



def load_alerts(service_name: str, since_hours: int = 168) -> pd.DataFrame:
    query = """
        SELECT service_name, alert_type, severity, triggered_at
        FROM alert
        WHERE service_name = %(service_name)s
          AND triggered_at > now() - (%(since_hours)s || ' hours')::interval
        ORDER BY triggered_at
    """
    return pd.read_sql(query, engine, params={"service_name": service_name, "since_hours": since_hours})
