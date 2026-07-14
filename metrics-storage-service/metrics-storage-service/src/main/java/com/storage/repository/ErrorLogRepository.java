package com.storage.repository;

import com.storage.entity.ErrorLog;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ErrorLogRepository extends JpaRepository<ErrorLog, Long> {
    List<ErrorLog> findByServiceNameOrderByTimestampDesc(String serviceName);
}