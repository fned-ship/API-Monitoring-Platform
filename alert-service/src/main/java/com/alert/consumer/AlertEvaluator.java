package com.alert.consumer;

import com.alert.entity.Alert;
import com.alert.repository.AlertRepository;
import com.alert.rules.ErrorRateRule;
import com.alert.rules.LatencyThresholdRule;
import com.monitoring.common.events.ApiMetricEvent;
import com.monitoring.common.events.AlertEvent;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class AlertEvaluator {

    private final LatencyThresholdRule latencyRule;
    private final ErrorRateRule errorRateRule;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final AlertRepository alertRepository;

    public AlertEvaluator(LatencyThresholdRule latencyRule, ErrorRateRule errorRateRule,
                           KafkaTemplate<String, Object> kafkaTemplate,
                           AlertRepository alertRepository) {
        this.latencyRule = latencyRule;
        this.errorRateRule = errorRateRule;
        this.kafkaTemplate = kafkaTemplate;
        this.alertRepository = alertRepository;
    }

    @KafkaListener(
        topics = "api-request-metrics",
        groupId = "cg-alert-engine",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.ApiMetricEvent"}
    )
    public void onMetric(ApiMetricEvent event) {
        latencyRule.evaluate(event).ifPresent(this::raise);
        errorRateRule.evaluate(event).ifPresent(this::raise);
    }

    private void raise(AlertEvent alertEvent) {
        // 1. persist
        Alert alert = new Alert();
        alert.setServiceName(alertEvent.serviceName());
        alert.setAlertType(alertEvent.alertType());
        alert.setSeverity(alertEvent.severity());
        alert.setMessage(alertEvent.message());
        alert.setThresholdValue(alertEvent.thresholdValue());
        alert.setObservedValue(alertEvent.observedValue());
        alert.setTriggeredAt(alertEvent.triggeredAt());
        alertRepository.save(alert);

        // 2. publish so Dashboard Service (and later AI Service) can react in real time
        kafkaTemplate.send("api-alerts", alertEvent.serviceName(), alertEvent);
    }
}