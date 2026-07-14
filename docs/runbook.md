# Local Startup Runbook (No Docker)

Start in this order, each in its own terminal:

1. Kafka broker: `bin/kafka-server-start.sh config/kraft/server.properties`
2. PostgreSQL: already running as a local service (`brew services start postgresql@16` / `systemctl start postgresql`)
3. Grafana: already running as a local service
4. Build shared modules once per change: `mvn clean install` from the platform root
5. `mvn -pl monitored-apis/travel-agency-api spring-boot:run`
6. `mvn -pl metrics-storage-service spring-boot:run`
7. `mvn -pl alert-service spring-boot:run`
8. `mvn -pl dashboard-service spring-boot:run`
9. `mvn -pl api-gateway spring-boot:run`

Smoke test: `curl http://localhost:8080/api/bookings/1`, then check
`SELECT count(*) FROM api_metric;` in psql.

## Known local ports
| Service | Port |
|---|---|
| Kafka | 9092 |
| PostgreSQL | 5432 |
| Grafana | 3000 |
| Travel Agency API | 8090 |
| Metrics Storage Service | 8081 |
| Alert Service | 8082 |
| Dashboard Service | 8083 |
| API Gateway | 8080 |