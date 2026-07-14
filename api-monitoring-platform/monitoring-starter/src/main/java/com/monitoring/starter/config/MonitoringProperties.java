package com.monitoring.starter.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "monitoring")
public class MonitoringProperties {
    private String serviceName;
    private boolean enabled = true;
    private long systemMetricsIntervalMs = 15000;

    public String getServiceName() { return serviceName; }
    public void setServiceName(String serviceName) { this.serviceName = serviceName; }
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public long getSystemMetricsIntervalMs() { return systemMetricsIntervalMs; }
    public void setSystemMetricsIntervalMs(long v) { this.systemMetricsIntervalMs = v; }
}