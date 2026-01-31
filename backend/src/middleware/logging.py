"""
Structured JSON logging middleware.
Task: T017 - Implement structured JSON logging middleware
Supports observability requirements (NFR-017)
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings
from .correlation_id import get_correlation_id

settings = get_settings()


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with structured JSON output.

    Logs include:
    - HTTP method, path, status code
    - Request duration (latency)
    - Correlation ID for distributed tracing
    - Client IP address
    - User agent
    - Excludes PII per NFR-013, NFR-014
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log structured information."""
        start_time = time.time()

        # Get correlation ID for this request
        correlation_id = get_correlation_id()

        # Process request
        response = await call_next(request)

        # Calculate request duration
        duration_ms = (time.time() - start_time) * 1000

        # Structured log data (NFR-013: excludes PII)
        log_data = {
            "correlation_id": str(correlation_id),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Log at appropriate level based on status code
        logger = logging.getLogger(__name__)
        if response.status_code >= 500:
            logger.error("HTTP request failed", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("HTTP request error", extra=log_data)
        else:
            logger.info("HTTP request completed", extra=log_data)

        return response


def setup_logging(log_level: str = None) -> None:
    """
    Configure structured JSON logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR). Uses config default if not provided.
    """
    if log_level is None:
        log_level = settings.LOG_LEVEL

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add stdout handler with JSON formatter
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("confluent_kafka").setLevel(logging.WARNING)

    root_logger.info(f"Structured logging initialized at {log_level} level")
