CREATE TABLE monitored_service (
    id              BIGSERIAL PRIMARY KEY,
    service_name    VARCHAR(100) UNIQUE NOT NULL,
    description     VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT now()
);

CREATE TABLE api_metric (
    id               BIGSERIAL PRIMARY KEY,
    service_id       BIGINT REFERENCES monitored_service(id),
    endpoint         VARCHAR(255) NOT NULL,
    http_method      VARCHAR(10) NOT NULL,
    status_code      INT NOT NULL,
    response_time_ms INT NOT NULL,
    request_count    INT DEFAULT 1,
    timestamp        TIMESTAMP NOT NULL,
    created_at       TIMESTAMP DEFAULT now()
);
CREATE INDEX idx_api_metric_service_time ON api_metric (service_id, timestamp);

CREATE TABLE system_metric (
    id              BIGSERIAL PRIMARY KEY,
    service_id      BIGINT REFERENCES monitored_service(id),
    cpu_usage_pct   DOUBLE PRECISION,
    memory_used_mb  DOUBLE PRECISION,
    memory_max_mb   DOUBLE PRECISION,
    timestamp       TIMESTAMP NOT NULL,
    created_at      TIMESTAMP DEFAULT now()
);

CREATE TABLE error_log (
    id              BIGSERIAL PRIMARY KEY,
    service_id      BIGINT REFERENCES monitored_service(id),
    endpoint        VARCHAR(255),
    status_code     INT,
    error_message   TEXT,
    stack_trace     TEXT,
    timestamp       TIMESTAMP NOT NULL,
    created_at      TIMESTAMP DEFAULT now()
);

CREATE TABLE alert (
    id              BIGSERIAL PRIMARY KEY,
    service_id      BIGINT REFERENCES monitored_service(id),
    alert_type      VARCHAR(50) NOT NULL,
    severity        VARCHAR(20) NOT NULL,
    message         TEXT NOT NULL,
    threshold_value DOUBLE PRECISION,
    observed_value  DOUBLE PRECISION,
    status          VARCHAR(20) DEFAULT 'OPEN',
    triggered_at    TIMESTAMP NOT NULL,
    resolved_at     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT now()
);