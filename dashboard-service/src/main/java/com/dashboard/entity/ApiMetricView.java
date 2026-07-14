package com.dashboard.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "api_metric")
public class ApiMetricView {
    @Id
    private Long id;
    private String serviceName;
    private int statusCode;
    private int responseTimeMs;
    private Instant timestamp;

    public String getServiceName() { return serviceName; }
    public int getStatusCode() { return statusCode; }
    public int getResponseTimeMs() { return responseTimeMs; }
    public Instant getTimestamp() { return timestamp; }
}