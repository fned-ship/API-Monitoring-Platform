package com.storage.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "system_metric")
public class SystemMetric {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String serviceName;
    private double cpuUsagePct;
    private double memoryUsedMb;
    private double memoryMaxMb;
    private Instant timestamp;

    public void setServiceName(String v) { this.serviceName = v; }
    public void setCpuUsagePct(double v) { this.cpuUsagePct = v; }
    public void setMemoryUsedMb(double v) { this.memoryUsedMb = v; }
    public void setMemoryMaxMb(double v) { this.memoryMaxMb = v; }
    public void setTimestamp(Instant v) { this.timestamp = v; }
}