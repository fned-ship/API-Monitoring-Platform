API Monitoring Platform is a distributed monitoring solution built with Spring Boot and Apache Kafka.

The platform provides plug-and-play monitoring for any Spring Boot API through a custom Monitoring Starter. Every HTTP request is automatically captured, published to Kafka, processed by dedicated microservices, stored in PostgreSQL, analyzed for anomalies, and visualized in Grafana through real-time dashboards.

Features:
• Automatic request and system metrics collection
• Kafka-based event-driven architecture
• Real-time dashboards using Grafana
• Alert generation for high latency and server errors
• Live WebSocket dashboard updates
• Modular microservice architecture
• Easy integration with new APIs using the Monitoring Starter

This project was designed as the foundation for a future AI-powered prediction service capable of forecasting API failures and infrastructure issues using Large Language Models (LLMs).