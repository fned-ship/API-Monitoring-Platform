package com.dashboard.consumer;

import com.monitoring.common.events.ApiMetricEvent;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

@Component
public class LiveMetricsConsumer {

    private final SimpMessagingTemplate messagingTemplate;

    public LiveMetricsConsumer(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @KafkaListener(
        topics = "api-request-metrics",
        groupId = "cg-dashboard",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.ApiMetricEvent"}
    )
    public void onMetric(ApiMetricEvent event) {
        messagingTemplate.convertAndSend("/topic/live-metrics", event);
    }
}