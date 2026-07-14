package com.monitoring.starter.config;

import com.monitoring.starter.filter.RequestMetricsFilter;
import com.monitoring.starter.kafka.KafkaEventPublisher;
import com.monitoring.starter.metrics.SystemMetricsScheduler;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;

@Configuration
@EnableScheduling
@EnableConfigurationProperties(MonitoringProperties.class)
@ConditionalOnProperty(prefix = "monitoring", name = "enabled", havingValue = "true", matchIfMissing = true)
public class MonitoringAutoConfiguration {

    @Bean
    public KafkaEventPublisher kafkaEventPublisher(KafkaTemplate<String, Object> kafkaTemplate) {
        return new KafkaEventPublisher(kafkaTemplate);
    }

    @Bean
    public SystemMetricsScheduler systemMetricsScheduler(KafkaEventPublisher publisher,
                                                           MonitoringProperties properties) {
        return new SystemMetricsScheduler(publisher, properties);
    }

    @Bean
    public FilterRegistrationBean<RequestMetricsFilter> monitoringFilter(
            KafkaEventPublisher publisher, MonitoringProperties properties) {
        FilterRegistrationBean<RequestMetricsFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new RequestMetricsFilter(publisher, properties));
        registration.addUrlPatterns("/*");
        registration.setOrder(1);
        return registration;
    }
}