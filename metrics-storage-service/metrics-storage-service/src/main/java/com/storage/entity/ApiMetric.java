package com.storage.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "api_metric")
public class ApiMetric {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String serviceName;
    private String endpoint;
    private String httpMethod;
    private int statusCode;
    private int responseTimeMs;
    private Instant timestamp;

    public Long getId() { return id; }
    public String getServiceName() { return serviceName; }
    public void setServiceName(String v) { this.serviceName = v; }
    public void setEndpoint(String v) { this.endpoint = v; }
    public void setHttpMethod(String v) { this.httpMethod = v; }
    public void setStatusCode(int v) { this.statusCode = v; }
    public int getStatusCode() { return statusCode; }
    public void setResponseTimeMs(int v) { this.responseTimeMs = v; }
    public void setTimestamp(Instant v) { this.timestamp = v; }
    public Instant getTimestamp() { return timestamp; }
    public int getResponseTimeMs() { return responseTimeMs; }
    public String getHttpMethod() { return httpMethod; }
    public String getEndpoint() { return endpoint; }
}