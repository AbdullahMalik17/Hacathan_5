# Monitoring and Observability for Customer Success Digital FTE

This document describes the monitoring and observability setup for the Customer Success Digital FTE application.

## Components

### 1. Structured Logging
- Uses `structlog` for structured JSON logging
- Includes correlation IDs for distributed tracing
- Logs contain contextual information for debugging

### 2. Metrics Collection
- Uses Prometheus client for metric collection
- Exposes `/metrics` endpoint for scraping
- Tracks application, business, and system metrics

### 3. Alerting
- Predefined alerting rules for common issues
- Configured thresholds for error rates, response times, etc.
- Integration-ready with alert managers

### 4. Visualization
- Grafana dashboard for real-time monitoring
- Pre-configured panels for key metrics
- Historical trend analysis

## Metrics Collected

### HTTP Metrics
- `fte_http_requests_total` - Total HTTP requests processed
- `fte_http_request_duration_seconds` - Request duration histogram

### Customer Interaction Metrics
- `fte_customer_interactions_total` - Customer interactions by channel
- `fte_customer_response_time_seconds` - Response time histogram

### Ticket Metrics
- `fte_ticket_operations_total` - Ticket operations by type
- `fte_ticket_resolution_time_seconds` - Resolution time histogram

### Agent Metrics
- `fte_agent_thinking_time_seconds` - Agent processing time
- `fte_agent_tool_calls_total` - Tool call counts

### System Metrics
- `fte_active_conversations` - Active conversations gauge
- `fte_message_queue_size` - Message queue sizes
- `fte_system_uptime_seconds` - System uptime

### Error Metrics
- `fte_errors_total` - Error counts by type and component

### Business Metrics
- `fte_customer_satisfaction_score` - Satisfaction score summary
- `fte_escalations_total` - Escalations by reason

## Setup Instructions

### Local Development
1. Run the application normally
2. Access metrics at `http://localhost:8000/metrics`
3. View structured logs in the console

### Docker Compose Setup
1. Navigate to the monitoring directory:
   ```bash
   cd infrastructure/monitoring
   ```
2. Start the monitoring stack:
   ```bash
   docker-compose up -d
   ```
3. Access services:
   - Application: `http://localhost:8000`
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3000` (admin/admin)

### Alerting
Alerting rules are defined in `fte_alerting_rules.yml` and can be customized based on your requirements.

## Best Practices

1. Monitor error rates and response times regularly
2. Set up alerts for critical metrics
3. Review customer satisfaction scores
4. Track escalation patterns
5. Watch for performance degradation over time

## Troubleshooting

If metrics are not appearing:
1. Verify the `/metrics` endpoint is accessible
2. Check Prometheus configuration for correct target
3. Ensure the application is running and healthy

For logging issues:
1. Check log levels in configuration
2. Verify structured logging is enabled
3. Look for correlation IDs to trace requests