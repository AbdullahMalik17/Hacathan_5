"""
Metrics collection module for Customer Success Digital FTE.

This module provides Prometheus metrics for monitoring system performance,
business operations, and customer interactions.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, Info
from prometheus_client.registry import CollectorRegistry
from fastapi import Request
from typing import Dict, Any
import time
from datetime import datetime


class MetricsCollector:
    """Centralized metrics collector for the Customer Success Digital FTE."""
    
    def __init__(self):
        # Initialize registry
        self.registry = CollectorRegistry()
        
        # Request metrics
        self.request_count = Counter(
            'fte_http_requests_total',
            'Total HTTP requests processed',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'fte_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Customer interaction metrics
        self.customer_interactions = Counter(
            'fte_customer_interactions_total',
            'Total customer interactions processed',
            ['channel', 'direction', 'status'],
            registry=self.registry
        )
        
        self.customer_response_time = Histogram(
            'fte_customer_response_time_seconds',
            'Time taken to respond to customer',
            ['channel'],
            registry=self.registry
        )
        
        # Ticket metrics
        self.ticket_operations = Counter(
            'fte_ticket_operations_total',
            'Total ticket operations',
            ['operation', 'category', 'priority', 'status'],
            registry=self.registry
        )
        
        self.ticket_resolution_time = Histogram(
            'fte_ticket_resolution_time_seconds',
            'Time taken to resolve tickets',
            ['category', 'priority'],
            registry=self.registry
        )
        
        # Agent metrics
        self.agent_thinking_time = Histogram(
            'fte_agent_thinking_time_seconds',
            'Time spent by agent thinking/processing',
            ['operation'],
            registry=self.registry
        )
        
        self.agent_tool_calls = Counter(
            'fte_agent_tool_calls_total',
            'Total agent tool calls',
            ['tool_name', 'status'],
            registry=self.registry
        )
        
        # System metrics
        self.active_conversations = Gauge(
            'fte_active_conversations',
            'Number of active conversations',
            registry=self.registry
        )
        
        self.message_queue_size = Gauge(
            'fte_message_queue_size',
            'Current size of message queue',
            ['queue_name'],
            registry=self.registry
        )
        
        self.system_uptime = Gauge(
            'fte_system_uptime_seconds',
            'System uptime in seconds',
            registry=self.registry
        )
        
        # Error metrics
        self.error_count = Counter(
            'fte_errors_total',
            'Total errors encountered',
            ['error_type', 'component', 'severity'],
            registry=self.registry
        )
        
        # Business metrics
        self.customer_satisfaction = Summary(
            'fte_customer_satisfaction_score',
            'Customer satisfaction scores',
            ['interaction_type'],
            registry=self.registry
        )
        
        self.escalation_rate = Counter(
            'fte_escalations_total',
            'Total escalations to human agents',
            ['reason', 'channel'],
            registry=self.registry
        )
        
        # Service info
        self.service_info = Info(
            'fte_service_info',
            'Service information',
            registry=self.registry
        )
        
        # Initialize service info
        self.service_info.info({
            'version': '1.0.0',
            'service': 'customer-success-digital-fte',
            'team': 'customer-success'
        })
        
        # Track start time for uptime
        self.start_time = time.time()
    
    def increment_request_count(self, method: str, endpoint: str, status_code: int):
        """Increment request counter."""
        self.request_count.labels(
            method=method.upper(),
            endpoint=endpoint,
            status_code=status_code
        ).inc()
    
    def record_request_duration(self, method: str, endpoint: str, duration: float):
        """Record request duration."""
        self.request_duration.labels(
            method=method.upper(),
            endpoint=endpoint
        ).observe(duration)
    
    def record_customer_interaction(self, channel: str, direction: str, status: str = "success"):
        """Record customer interaction."""
        self.customer_interactions.labels(
            channel=channel,
            direction=direction,
            status=status
        ).inc()
    
    def record_customer_response_time(self, channel: str, response_time: float):
        """Record customer response time."""
        self.customer_response_time.labels(
            channel=channel
        ).observe(response_time)
    
    def record_ticket_operation(self, operation: str, category: str, priority: str, status: str = "success"):
        """Record ticket operation."""
        self.ticket_operations.labels(
            operation=operation,
            category=category,
            priority=priority,
            status=status
        ).inc()
    
    def record_ticket_resolution_time(self, category: str, priority: str, resolution_time: float):
        """Record ticket resolution time."""
        self.ticket_resolution_time.labels(
            category=category,
            priority=priority
        ).observe(resolution_time)
    
    def record_agent_thinking_time(self, operation: str, thinking_time: float):
        """Record agent thinking time."""
        self.agent_thinking_time.labels(
            operation=operation
        ).observe(thinking_time)
    
    def record_agent_tool_call(self, tool_name: str, status: str = "success"):
        """Record agent tool call."""
        self.agent_tool_calls.labels(
            tool_name=tool_name,
            status=status
        ).inc()
    
    def set_active_conversations(self, count: int):
        """Set active conversations count."""
        self.active_conversations.set(count)
    
    def set_message_queue_size(self, queue_name: str, size: int):
        """Set message queue size."""
        self.message_queue_size.labels(queue_name=queue_name).set(size)
    
    def update_uptime(self):
        """Update system uptime."""
        current_uptime = time.time() - self.start_time
        self.system_uptime.set(current_uptime)
    
    def record_error(self, error_type: str, component: str, severity: str = "medium"):
        """Record an error."""
        self.error_count.labels(
            error_type=error_type,
            component=component,
            severity=severity
        ).inc()
    
    def record_customer_satisfaction(self, interaction_type: str, score: float):
        """Record customer satisfaction score."""
        self.customer_satisfaction.labels(
            interaction_type=interaction_type
        ).observe(score)
    
    def record_escalation(self, reason: str, channel: str):
        """Record escalation."""
        self.escalation_rate.labels(
            reason=reason,
            channel=channel
        ).inc()
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        from prometheus_client import generate_latest
        return generate_latest(self.registry).decode('utf-8')


# Global metrics collector instance
metrics_collector = MetricsCollector()


async def metrics_middleware(request: Request, call_next):
    """Middleware to collect metrics for each request."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Record metrics
    metrics_collector.increment_request_count(
        method=request.method,
        endpoint=str(request.url.path),
        status_code=response.status_code
    )
    
    metrics_collector.record_request_duration(
        method=request.method,
        endpoint=str(request.url.path),
        duration=duration
    )
    
    # Update uptime
    metrics_collector.update_uptime()
    
    return response


def track_customer_interaction(channel: str, direction: str, status: str = "success"):
    """Helper function to track customer interactions."""
    metrics_collector.record_customer_interaction(channel, direction, status)


def track_agent_operation(operation: str, duration: float):
    """Helper function to track agent operations."""
    metrics_collector.record_agent_thinking_time(operation, duration)


def track_ticket_operation(operation: str, category: str, priority: str, status: str = "success"):
    """Helper function to track ticket operations."""
    metrics_collector.record_ticket_operation(operation, category, priority, status)


def track_error(error_type: str, component: str, severity: str = "medium"):
    """Helper function to track errors."""
    metrics_collector.record_error(error_type, component, severity)