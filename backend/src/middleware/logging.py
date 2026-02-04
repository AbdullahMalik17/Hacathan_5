"""
Enhanced structured logging middleware with monitoring capabilities.
"""

import logging
import time
import traceback
from typing import Dict, Any
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask

import structlog
from ..monitoring.logger import get_structured_logger, correlation_id_var
from ..monitoring.metrics import metrics_collector, track_error


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced structured logging middleware with metrics collection."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_structured_logger()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        correlation_id_var.set(correlation_id)
        
        # Add correlation ID to structlog context
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        # Log request start
        self.logger.info(
            "request_started",
            method=request.method,
            path=str(request.url.path),
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful response
            self.logger.info(
                "request_completed",
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration=duration,
                content_length=response.headers.get("content-length", 0),
            )
            
            # Collect metrics
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
            metrics_collector.update_uptime()
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as exc:
            # Calculate duration for failed requests
            duration = time.time() - start_time
            
            # Log the error
            self.logger.error(
                "request_failed",
                method=request.method,
                path=str(request.url.path),
                duration=duration,
                error=str(exc),
                traceback=traceback.format_exc(),
            )
            
            # Collect error metrics
            metrics_collector.increment_request_count(
                method=request.method,
                endpoint=str(request.url.path),
                status_code=500
            )
            metrics_collector.record_request_duration(
                method=request.method,
                endpoint=str(request.url.path),
                duration=duration
            )
            track_error(
                error_type=type(exc).__name__,
                component="middleware",
                severity="high"
            )
            metrics_collector.update_uptime()
            
            # Re-raise the exception
            raise


def setup_logging(log_level: str = "INFO"):
    """Setup structured logging configuration."""
    # Configure standard logging to use structlog
    logging.basicConfig(
        level=log_level.upper(),
        format="%(message)s",
        handlers=[logging.StreamHandler()]
    )
    
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