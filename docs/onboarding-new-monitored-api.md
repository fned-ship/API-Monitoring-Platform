# Onboarding a New Monitored API

Any Spring Boot 3.3.x REST API can be plugged into this platform in three steps.

## 1. Add the dependency
'''xml
<dependency>
    <groupId>com.monitoring</groupId>
    <artifactId>monitoring-starter</artifactId>
    <version>1.0.0</version>
</dependency>
'''
Requires `monitoring-common` and `monitoring-starter` to already be installed locally
(`mvn clean install` from the platform root).

## 2. Configure two properties
'''yaml
monitoring:
  service-name: <your-service-name>   # must be unique across the platform
  enabled: true

spring:
  kafka:
    bootstrap-servers: localhost:9092
'''

## 3. Point the API Gateway at it
In `api-gateway/src/main/resources/application.yml`, update the `monitored-api` route's
`uri` to your service's host:port. No other service needs to change.

## What you get automatically
- Every HTTP request/response is timed and published to `api-request-metrics`.
- Every HTTP 500 is published to `api-error-logs`.
- CPU/memory is sampled every 15s (configurable via `monitoring.system-metrics-interval-ms`)
  and published to `api-system-metrics`.
- Alert Service evaluates latency and error-rate thresholds on your traffic automatically —
  no per-service alert configuration needed for the default rules.

## What you must NOT do
- Do not publish to any `api-*` topic directly from your API — always go through the starter,
  so the event contract below stays the single source of truth.
- Do not change field names/types in `monitoring-common` without bumping its version and
  coordinating with every consumer (Storage, Alert, Dashboard, and any future AI service).