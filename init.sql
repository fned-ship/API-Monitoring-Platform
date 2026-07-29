-- CREATE TABLE monitored_service (
--     id              BIGSERIAL PRIMARY KEY,
--     service_name    VARCHAR(100) UNIQUE NOT NULL,
--     description     VARCHAR(255),
--     is_active       BOOLEAN DEFAULT TRUE,
--     created_at      TIMESTAMP DEFAULT now()
-- );

-- CREATE TABLE api_metric (
--     id               BIGSERIAL PRIMARY KEY,
--     service_id       BIGINT REFERENCES monitored_service(id),
--     endpoint         VARCHAR(255) NOT NULL,
--     http_method      VARCHAR(10) NOT NULL,
--     status_code      INT NOT NULL,
--     response_time_ms INT NOT NULL,
--     request_count    INT DEFAULT 1,
--     timestamp        TIMESTAMP NOT NULL,
--     created_at       TIMESTAMP DEFAULT now()
-- );
-- CREATE INDEX idx_api_metric_service_time ON api_metric (service_id, timestamp);

-- CREATE TABLE system_metric (
--     id              BIGSERIAL PRIMARY KEY,
--     service_id      BIGINT REFERENCES monitored_service(id),
--     cpu_usage_pct   DOUBLE PRECISION,
--     memory_used_mb  DOUBLE PRECISION,
--     memory_max_mb   DOUBLE PRECISION,
--     timestamp       TIMESTAMP NOT NULL,
--     created_at      TIMESTAMP DEFAULT now()
-- );

-- CREATE TABLE error_log (
--     id              BIGSERIAL PRIMARY KEY,
--     service_id      BIGINT REFERENCES monitored_service(id),
--     endpoint        VARCHAR(255),
--     status_code     INT,
--     error_message   TEXT,
--     stack_trace     TEXT,
--     timestamp       TIMESTAMP NOT NULL,
--     created_at      TIMESTAMP DEFAULT now()
-- );

-- CREATE TABLE alert (
--     id              BIGSERIAL PRIMARY KEY,
--     service_id      BIGINT REFERENCES monitored_service(id),
--     alert_type      VARCHAR(50) NOT NULL,
--     severity        VARCHAR(20) NOT NULL,
--     message         TEXT NOT NULL,
--     threshold_value DOUBLE PRECISION,
--     observed_value  DOUBLE PRECISION,
--     status          VARCHAR(20) DEFAULT 'OPEN',
--     triggered_at    TIMESTAMP NOT NULL,
--     resolved_at     TIMESTAMP,
--     created_at      TIMESTAMP DEFAULT now()
-- );

-- CREATE TABLE prediction (
--     id                    BIGSERIAL PRIMARY KEY,
--     prediction_id         UUID NOT NULL,
--     service_name          VARCHAR(100) NOT NULL,
--     prediction_type       VARCHAR(50) NOT NULL,
--     risk_score            DOUBLE PRECISION NOT NULL,
--     severity              VARCHAR(20) NOT NULL,
--     confidence            DOUBLE PRECISION,
--     is_anomaly            BOOLEAN NOT NULL,
--     contributing_features TEXT,              -- JSON-encoded list
--     model_version         VARCHAR(50) NOT NULL,
--     window_timestamp      TIMESTAMP NOT NULL,
--     generated_at          TIMESTAMP DEFAULT now()
-- );
-- CREATE INDEX idx_prediction_service_time ON prediction (service_name, generated_at);

-- CREATE TABLE model_registry (
--     id                 BIGSERIAL PRIMARY KEY,
--     model_name         VARCHAR(100) NOT NULL,
--     model_type         VARCHAR(20) NOT NULL,       -- CLASSIFICATION | REGRESSION
--     target_metric      VARCHAR(50),                 -- null for classification
--     algorithm          VARCHAR(50) NOT NULL,
--     version            VARCHAR(50) NOT NULL,
--     artifact_path      VARCHAR(255) NOT NULL,
--     scaler_path        VARCHAR(255),
--     status             VARCHAR(20) NOT NULL,        -- ACTIVE | CANDIDATE | ARCHIVED
--     evaluation_metrics TEXT,                         -- JSON-encoded metrics dict
--     trained_at         TIMESTAMP NOT NULL,
--     promoted_at        TIMESTAMP
-- );
-- CREATE UNIQUE INDEX idx_model_registry_active
--     ON model_registry (model_name)
--     WHERE status = 'ACTIVE';


CREATE TABLE metric_forecast (
    id                    BIGSERIAL PRIMARY KEY,
    forecast_id           UUID NOT NULL,
    service_name          VARCHAR(100) NOT NULL,
    target_metric         VARCHAR(50) NOT NULL,
    current_value         DOUBLE PRECISION NOT NULL,
    predicted_value       DOUBLE PRECISION NOT NULL,
    predicted_change_pct  DOUBLE PRECISION,
    horizon_seconds       INT NOT NULL,
    trend_direction       VARCHAR(20) NOT NULL,
    model_version         VARCHAR(50) NOT NULL,
    window_timestamp      TIMESTAMP NOT NULL,
    generated_at          TIMESTAMP DEFAULT now()
);
CREATE INDEX idx_metric_forecast_service_metric_time
    ON metric_forecast (service_name, target_metric, generated_at);