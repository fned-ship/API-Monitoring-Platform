package com.storage.repository;

import com.storage.entity.ApiMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ApiMetricRepository extends JpaRepository<ApiMetric, Long> {
    List<ApiMetric> findByServiceNameOrderByTimestampDesc(String serviceName);
}