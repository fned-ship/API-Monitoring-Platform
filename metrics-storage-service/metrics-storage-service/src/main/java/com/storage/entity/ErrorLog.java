package com.storage.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "error_log")
public class ErrorLog {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String serviceName;
    private String endpoint;
    private int statusCode;
    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    @Column(columnDefinition = "TEXT")
    private String stackTrace;
    private Instant timestamp;

    public void setServiceName(String v) { this.serviceName = v; }
    public void setEndpoint(String v) { this.endpoint = v; }
    public void setStatusCode(int v) { this.statusCode = v; }
    public void setErrorMessage(String v) { this.errorMessage = v; }
    public void setStackTrace(String v) { this.stackTrace = v; }
    public void setTimestamp(Instant v) { this.timestamp = v; }
}