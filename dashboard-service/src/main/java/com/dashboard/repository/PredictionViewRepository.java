package com.dashboard.repository;

import com.dashboard.entity.PredictionView;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface PredictionViewRepository extends JpaRepository<PredictionView, Long> {
    List<PredictionView> findByServiceNameOrderByGeneratedAtDesc(String serviceName);
    List<PredictionView> findTop20ByOrderByGeneratedAtDesc();
    List<PredictionView> findBySeverityInOrderByGeneratedAtDesc(List<String> severities);
}