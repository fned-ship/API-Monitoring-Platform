package com.travel.controller;

import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

@RestController
@RequestMapping("/api/bookings")
public class TravelAgencyController {

    @GetMapping("/{id}")
    public Map<String, Object> getBooking(@PathVariable String id) throws InterruptedException {
        // simulate variable response time so you have realistic latency data
        Thread.sleep(ThreadLocalRandom.current().nextInt(50, 300));
        return Map.of("bookingId", id, "destination", "Tunis", "status", "CONFIRMED");
    }

    @PostMapping
    public Map<String, Object> createBooking(@RequestBody Map<String, Object> request) {
        return Map.of("bookingId", "BK-1001", "status", "CREATED", "details", request);
    }

    @GetMapping("/fail")
    public Map<String, Object> simulateFailure() {
        throw new RuntimeException("Simulated payment gateway timeout");
    }

    @GetMapping("/slow")
    public Map<String, Object> simulateSlowResponse() throws InterruptedException {
        Thread.sleep(1500); // deliberately breaches the latency alert threshold (Step 6)
        return Map.of("status", "SLOW_RESPONSE_OK");
    }
}