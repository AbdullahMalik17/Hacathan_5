"""
Prometheus metrics middleware for all services.
Task: T104 - Add Prometheus metrics endpoints (NFR-015)
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ============================================================================
# Metrics Definitions (NFR-015)
# ============================================================================

# HTTP Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method", "endpoint"]
)

# Agent processing metrics
agent_messages_processed_total = Counter(
    "agent_messages_processed_total",
    "Total messages processed by agent",
    ["channel", "status"]
)

agent_processing_duration_seconds = Histogram(
    "agent_processing_duration_seconds",
    "Agent processing time in seconds",
    ["channel"],
    buckets=(0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0, 60.0, 120.0)
)

# Knowledge base metrics
kb_searches_total = Counter(
    "kb_searches_total",
    "Total knowledge base searches",
    ["result"]
)

kb_search_duration_seconds = Histogram(
    "kb_search_duration_seconds",
    "Knowledge base search duration in seconds",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0)
)

# Database metrics
db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"]
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

db_connections_active = Gauge(
    "db_connections_active",
    "Active database connections"
)

# Kafka metrics
kafka_messages_produced_total = Counter(
    "kafka_messages_produced_total",
    "Total Kafka messages produced",
    ["topic", "status"]
)

kafka_messages_consumed_total = Counter(
    "kafka_messages_consumed_total",
    "Total Kafka messages consumed",
    ["topic", "status"]
)

kafka_consumer_lag = Gauge(
    "kafka_consumer_lag",
    "Kafka consumer lag",
    ["topic", "partition"]
)

# Escalation metrics
escalations_total = Counter(
    "escalations_total",
    "Total escalations",
    ["reason"]
)

# Error metrics
errors_total = Counter(
    "errors_total",
    "Total errors",
    ["error_type", "endpoint"]
)


# ============================================================================
# Metrics Middleware
# ============================================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect HTTP metrics for Prometheus.

    Tracks:
    - Request count by method, endpoint, status
    - Request duration by method, endpoint
    - Requests in progress by method, endpoint
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and collect metrics.

        Args:
            request: FastAPI request
            call_next: Next middleware/route handler

        Returns:
            Response from route handler
        """
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()
        status_code = 500  # Default to error if something goes wrong

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as e:
            # Track errors
            errors_total.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            raise

        finally:
            # Record metrics
            duration = time.time() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint
            ).dec()


# ============================================================================
# Metrics Endpoint
# ============================================================================

async def metrics_endpoint():
    """
    Prometheus metrics endpoint.

    Returns:
        Prometheus-formatted metrics
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================================================
# Helper Functions
# ============================================================================

def track_agent_processing(channel: str, duration: float, status: str):
    """
    Track agent message processing metrics.

    Args:
        channel: Message channel (email, whatsapp, webform)
        duration: Processing time in seconds
        status: Processing status (success, error, escalated)
    """
    agent_messages_processed_total.labels(
        channel=channel,
        status=status
    ).inc()

    agent_processing_duration_seconds.labels(
        channel=channel
    ).observe(duration)


def track_kb_search(duration: float, results_found: bool):
    """
    Track knowledge base search metrics.

    Args:
        duration: Search duration in seconds
        results_found: Whether results were found
    """
    kb_searches_total.labels(
        result="found" if results_found else "not_found"
    ).inc()

    kb_search_duration_seconds.observe(duration)


def track_db_query(operation: str, table: str, duration: float):
    """
    Track database query metrics.

    Args:
        operation: Query operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration: Query duration in seconds
    """
    db_queries_total.labels(
        operation=operation,
        table=table
    ).inc()

    db_query_duration_seconds.labels(
        operation=operation,
        table=table
    ).observe(duration)


def track_kafka_message(topic: str, produced: bool, status: str):
    """
    Track Kafka message metrics.

    Args:
        topic: Kafka topic
        produced: True if producing, False if consuming
        status: Message status (success, error)
    """
    if produced:
        kafka_messages_produced_total.labels(
            topic=topic,
            status=status
        ).inc()
    else:
        kafka_messages_consumed_total.labels(
            topic=topic,
            status=status
        ).inc()


def track_escalation(reason: str):
    """
    Track escalation metrics.

    Args:
        reason: Escalation reason
    """
    escalations_total.labels(reason=reason).inc()
