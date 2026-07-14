# Kafka Event Contracts

| Topic | Producer | Consumers | Java type |
|---|---|---|---|
| api-request-metrics | monitoring-starter (in every monitored API) | Metrics Storage, Alert Service, Dashboard Service | com.monitoring.common.events.ApiMetricEvent |
| api-system-metrics  | monitoring-starter | Metrics Storage | com.monitoring.common.events.SystemMetricEvent |
| api-error-logs      | monitoring-starter | Metrics Storage, Alert Service | com.monitoring.common.events.ErrorLogEvent |
| api-alerts          | Alert Service | Dashboard Service | com.monitoring.common.events.AlertEvent |

These four types live in the `monitoring-common` module and are the single shared contract
between all services. Any breaking change here must be versioned and rolled out to every
consumer at once.