package com.dashboard.consumer;

import com.monitoring.common.events.AlertEvent;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

@Component
public class LiveAlertsConsumer {

    private final SimpMessagingTemplate messagingTemplate;

    public LiveAlertsConsumer(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @KafkaListener(
        topics = "api-alerts",
        groupId = "cg-dashboard",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.AlertEvent"}
    )
    public void onAlert(AlertEvent event) {
        messagingTemplate.convertAndSend("/topic/live-alerts", event);
    }
}