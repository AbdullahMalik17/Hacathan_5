"""
Enhanced monitoring and observability module for Customer Success Digital FTE.

This module provides:
- Structured logging with correlation IDs
- Application metrics collection
- Performance monitoring
- Business metrics tracking
"""

import logging
import time
import functools
from typing import Callable, Any
from contextvars import ContextVar
from datetime import datetime

from prometheus_client import Counter, Histogram, Gauge, Summary
import structlog

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default=None)

# Prometheus metrics
# Request metrics
REQUEST_COUNT = Counter(
    "fte_requests_total", 
    "Total requests processed", 
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "fte_request_duration_seconds", 
    "Request duration in seconds", 
    ["method", "endpoint"]
)

# Business metrics
CUSTOMER_INTERACTIONS = Counter(
    "fte_customer_interactions_total",
    "Total customer interactions processed",
    ["channel", "customer_id"]
)

TICKET_OPERATIONS = Counter(
    "fte_ticket_operations_total",
    "Total ticket operations",
    ["operation", "category", "priority"]
)

AGENT_THINKING_TIME = Histogram(
    "fte_agent_thinking_time_seconds",
    "Time spent by agent thinking/processing",
    ["operation"]
)

ACTIVE_CUSTOMERS = Gauge(
    "fte_active_customers",
    "Number of active customers"
)

BUSINESS_HOURS = Gauge(
    "fte_business_hours",
    "Indicator if it's business hours (1 = yes, 0 = no)"
)

# Error metrics
ERROR_COUNT = Counter(
    "fte_errors_total",
    "Total errors encountered",
    ["type", "component"]
)

PROCESSING_LATENCY = Summary(
    "fte_processing_latency_seconds",
    "Summary of processing latency",
    ["component", "operation"]
)


def get_structured_logger():
    """Initialize and return a structured logger."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def log_api_call(func: Callable) -> Callable:
    """Decorator to log API calls with structured logging and metrics."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        correlation_id = correlation_id_var.get()
        
        # Add context to structlog
        if correlation_id:
            structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        logger = get_structured_logger()
        
        try:
            # Log the start of the API call
            logger.info(
                "api_call_started",
                func_name=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful completion
            logger.info(
                "api_call_completed",
                func_name=func.__name__,
                duration=duration,
                result_type=type(result).__name__
            )
            
            # Record metrics
            REQUEST_DURATION.labels(
                method=getattr(func, '__name__', 'unknown'),
                endpoint=getattr(func, '__name__', 'unknown')
            ).observe(duration)
            
            REQUEST_COUNT.labels(
                method=getattr(func, '__name__', 'unknown'),
                endpoint=getattr(func, '__name__', 'unknown'),
                status="success"
            ).inc()
            
            return result
            
        except Exception as e:
            # Calculate duration even for failed calls
            duration = time.time() - start_time
            
            # Log the error
            logger.error(
                "api_call_failed",
                func_name=func.__name__,
                duration=duration,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Record error metrics
            ERROR_COUNT.labels(
                type=type(e).__name__,
                component=func.__module__
            ).inc()
            
            REQUEST_COUNT.labels(
                method=getattr(func, '__name__', 'unknown'),
                endpoint=getattr(func, '__name__', 'unknown'),
                status="error"
            ).inc()
            
            # Re-raise the exception
            raise
    
    return wrapper


def log_customer_interaction(channel: str, customer_id: str):
    """Log customer interaction with metrics."""
    logger = get_structured_logger()
    correlation_id = correlation_id_var.get()
    
    if correlation_id:
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    logger.info(
        "customer_interaction_logged",
        channel=channel,
        customer_id=customer_id,
        timestamp=datetime.utcnow().isoformat()
    )
    
    CUSTOMER_INTERACTIONS.labels(
        channel=channel,
        customer_id=customer_id
    ).inc()


def log_ticket_operation(operation: str, category: str, priority: str):
    """Log ticket operation with metrics."""
    logger = get_structured_logger()
    correlation_id = correlation_id_var.get()
    
    if correlation_id:
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    logger.info(
        "ticket_operation_logged",
        operation=operation,
        category=category,
        priority=priority,
        timestamp=datetime.utcnow().isoformat()
    )
    
    TICKET_OPERATIONS.labels(
        operation=operation,
        category=category,
        priority=priority
    ).inc()


def measure_agent_performance(operation: str):
    """Measure agent performance with timing."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            correlation_id = correlation_id_var.get()
            
            if correlation_id:
                structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
            
            logger = get_structured_logger()
            
            try:
                logger.info(
                    "agent_operation_started",
                    operation=operation,
                    func_name=func.__name__
                )
                
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                
                logger.info(
                    "agent_operation_completed",
                    operation=operation,
                    duration=duration,
                    func_name=func.__name__
                )
                
                AGENT_THINKING_TIME.labels(operation=operation).observe(duration)
                
                PROCESSING_LATENCY.labels(
                    component="agent",
                    operation=operation
                ).observe(duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    "agent_operation_failed",
                    operation=operation,
                    duration=duration,
                    error=str(e),
                    error_type=type(e).__name__
                )
                
                ERROR_COUNT.labels(
                    type=type(e).__name__,
                    component="agent"
                ).inc()
                
                raise
        
        return wrapper
    return decorator


def log_error(error_type: str, component: str, details: dict = None):
    """Log an error with metrics."""
    logger = get_structured_logger()
    correlation_id = correlation_id_var.get()
    
    if correlation_id:
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    logger.error(
        "system_error_logged",
        error_type=error_type,
        component=component,
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )
    
    ERROR_COUNT.labels(
        type=error_type,
        component=component
    ).inc()


def update_active_customers(count: int):
    """Update the gauge for active customers."""
    ACTIVE_CUSTOMERS.set(count)