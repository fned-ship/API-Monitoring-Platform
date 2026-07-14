package com.monitoring.starter.filter;

import com.monitoring.common.events.ApiMetricEvent;
import com.monitoring.common.events.ErrorLogEvent;
import com.monitoring.starter.config.MonitoringProperties;
import com.monitoring.starter.kafka.KafkaEventPublisher;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.time.Instant;

public class RequestMetricsFilter extends OncePerRequestFilter {

    private final KafkaEventPublisher publisher;
    private final MonitoringProperties properties;

    public RequestMetricsFilter(KafkaEventPublisher publisher, MonitoringProperties properties) {
        this.publisher = publisher;
        this.properties = properties;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                     FilterChain filterChain) throws ServletException, IOException {
        long start = System.currentTimeMillis();
        try {
            filterChain.doFilter(request, response);
        } finally {
            long durationMs = System.currentTimeMillis() - start;
            int status = response.getStatus();

            publisher.publishMetric(ApiMetricEvent.of(
                    properties.getServiceName(),
                    request.getRequestURI(),
                    request.getMethod(),
                    status,
                    durationMs
            ));

            if (status >= 500) {
                publisher.publishErrorLog(new ErrorLogEvent(
                        java.util.UUID.randomUUID(),
                        properties.getServiceName(),
                        request.getRequestURI(),
                        status,
                        "HTTP " + status + " on " + request.getRequestURI(),
                        null,
                        Instant.now()
                ));
            }
        }
    }
}