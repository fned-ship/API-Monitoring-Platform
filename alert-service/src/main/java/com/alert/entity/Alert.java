package com.alert.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "alert")
public class Alert {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String serviceName;
    private String alertType;
    private String severity;
    @Column(columnDefinition = "TEXT")
    private String message;
    private Double thresholdValue;
    private Double observedValue;
    private String status = "OPEN";
    private Instant triggeredAt;
    private Instant resolvedAt;

    public void setServiceName(String v) { this.serviceName = v; }
    public void setAlertType(String v) { this.alertType = v; }
    public void setSeverity(String v) { this.severity = v; }
    public void setMessage(String v) { this.message = v; }
    public void setThresholdValue(Double v) { this.thresholdValue = v; }
    public void setObservedValue(Double v) { this.observedValue = v; }
    public void setTriggeredAt(Instant v) { this.triggeredAt = v; }
    public Long getId() { return id; }
    public String getStatus() { return status; }
    public void setStatus(String v) { this.status = v; }
    public void setResolvedAt(Instant v) { this.resolvedAt = v; }
}