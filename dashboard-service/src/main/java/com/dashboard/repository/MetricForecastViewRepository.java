package com.dashboard.repository;

import com.dashboard.entity.MetricForecastView;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface MetricForecastViewRepository extends JpaRepository<MetricForecastView, Long> {
    List<MetricForecastView> findByServiceNameAndTargetMetricOrderByGeneratedAtDesc(
            String serviceName, String targetMetric);
    List<MetricForecastView> findByTrendDirectionOrderByGeneratedAtDesc(String trendDirection);
}