package com.storage.repository;

import com.storage.entity.SystemMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SystemMetricRepository extends JpaRepository<SystemMetric, Long> {
    List<SystemMetric> findByServiceNameOrderByTimestampDesc(String serviceName);
}