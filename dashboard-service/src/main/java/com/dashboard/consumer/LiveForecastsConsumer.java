package com.dashboard.consumer;

import com.monitoring.common.events.MetricForecastEvent;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

@Component
public class LiveForecastsConsumer {

    private final SimpMessagingTemplate messagingTemplate;

    public LiveForecastsConsumer(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @KafkaListener(
        topics = "api-metric-forecasts",
        groupId = "cg-dashboard",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.MetricForecastEvent"}
    )
    public void onForecast(MetricForecastEvent event) {
        messagingTemplate.convertAndSend("/topic/live-forecasts", event);
    }
}