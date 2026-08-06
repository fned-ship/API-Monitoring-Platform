package com.dashboard.repository;

import com.dashboard.entity.ApiMetricView;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface ApiMetricViewRepository extends JpaRepository<ApiMetricView, Long> {
    List<ApiMetricView> findByServiceNameOrderByTimestampDesc(String serviceName);
    List<ApiMetricView> findTop50ByOrderByTimestampDesc();

    @Query("SELECT DISTINCT a.serviceName FROM ApiMetricView a ORDER BY a.serviceName")
    List<String> findDistinctServiceNames();
}