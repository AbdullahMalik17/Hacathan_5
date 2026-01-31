"""
Correlation ID middleware for request tracking across services.
Task: T016 - Implement correlation ID middleware for request tracking
Supports distributed tracing (NFR-016)
"""

import logging
from contextvars import ContextVar
from typing import Callable
from uuid import UUID, uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Context variable to store correlation ID for the current request
correlation_id_ctx: ContextVar[UUID] = ContextVar('correlation_id', default=None)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract or generate correlation IDs for request tracking.

    Correlation IDs enable distributed tracing across services:
    - Extracts correlation ID from request header if present
    - Generates new UUID if no correlation ID in request
    - Stores in context variable for access anywhere in request lifecycle
    - Adds correlation ID to response headers
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add correlation ID."""
        # Extract correlation ID from header or generate new one
        correlation_id_header = request.headers.get(
            settings.CORRELATION_ID_HEADER,
            request.headers.get('X-Request-ID')
        )

        if correlation_id_header:
            try:
                correlation_id = UUID(correlation_id_header)
            except ValueError:
                # Invalid UUID format, generate new one
                correlation_id = uuid4()
                logger.warning(
                    f"Invalid correlation ID format: {correlation_id_header}, "
                    f"generated new: {correlation_id}"
                )
        else:
            correlation_id = uuid4()

        # Store in context variable for access in request handlers
        correlation_id_ctx.set(correlation_id)

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers[settings.CORRELATION_ID_HEADER] = str(correlation_id)
        response.headers['X-Request-ID'] = str(correlation_id)

        return response


def get_correlation_id() -> UUID:
    """
    Get the correlation ID for the current request.

    Returns:
        UUID correlation ID

    Example:
        correlation_id = get_correlation_id()
        logger.info(f"Processing request {correlation_id}")
    """
    correlation_id = correlation_id_ctx.get()
    if correlation_id is None:
        # Fallback if called outside request context
        correlation_id = uuid4()
        correlation_id_ctx.set(correlation_id)
    return correlation_id
