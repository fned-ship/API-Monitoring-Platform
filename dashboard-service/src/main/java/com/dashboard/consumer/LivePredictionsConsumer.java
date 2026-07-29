package com.dashboard.consumer;

import com.monitoring.common.events.PredictionEvent;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

@Component
public class LivePredictionsConsumer {

    private final SimpMessagingTemplate messagingTemplate;

    public LivePredictionsConsumer(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @KafkaListener(
        topics = "api-predictions",
        groupId = "cg-dashboard",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.PredictionEvent"}
    )
    public void onPrediction(PredictionEvent event) {
        messagingTemplate.convertAndSend("/topic/live-predictions", event);
    }
}