"""
FastAPI application initialization for Customer Success Digital FTE.
Task: T019 - Create FastAPI app initialization with health endpoints
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .middleware.correlation_id import CorrelationIdMiddleware
from .middleware.logging import StructuredLoggingMiddleware, setup_logging
from .services.database import db_service
from .services.kafka_producer import kafka_producer

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle: startup and shutdown.

    Startup:
    - Initialize database connection pool
    - Initialize Kafka producer
    - Setup structured logging

    Shutdown:
    - Close database connections
    - Flush and close Kafka producer
    """
    # Startup
    logger.info("Starting Customer Success Digital FTE application")

    # Setup structured JSON logging
    setup_logging(settings.LOG_LEVEL)

    # Initialize database connection pool
    try:
        await db_service.connect()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Initialize Kafka producer
    try:
        kafka_producer.connect()
        logger.info("Kafka producer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        raise

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")

    # Close database connections
    await db_service.disconnect()
    logger.info("Database connections closed")

    # Close Kafka producer
    kafka_producer.disconnect()
    logger.info("Kafka producer closed")

    logger.info("Application shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title="Customer Success Digital FTE",
    description="AI-powered customer support agent handling Email, WhatsApp, and Web Form channels",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for web form integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add correlation ID middleware for distributed tracing (NFR-016)
app.add_middleware(CorrelationIdMiddleware)

# Add structured logging middleware (NFR-017)
app.add_middleware(StructuredLoggingMiddleware)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint.

    Returns 200 OK if the application is running.
    Used by load balancers and monitoring systems.
    """
    return {"status": "healthy", "service": "customer-success-fte"}


@app.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint.

    Returns 200 OK if the application is ready to serve traffic:
    - Database connection pool is healthy
    - Kafka producer is connected

    Returns 503 Service Unavailable if not ready.
    """
    # Check database connection
    db_ready = False
    try:
        await db_service.fetchval("SELECT 1")
        db_ready = True
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")

    # Check Kafka producer
    kafka_ready = kafka_producer._producer is not None

    # Overall readiness
    ready = db_ready and kafka_ready

    if ready:
        return {
            "status": "ready",
            "database": "connected",
            "kafka": "connected",
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "connected" if db_ready else "disconnected",
                "kafka": "connected" if kafka_ready else "disconnected",
            }
        )


# ============================================================================
# Root endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Customer Success Digital FTE",
        "version": "1.0.0",
        "description": "AI-powered customer support agent",
        "channels": ["email", "whatsapp", "webform"],
        "health_endpoints": {
            "health": "/health",
            "readiness": "/ready",
        }
    }


# ============================================================================
# Webhook Routes
# ============================================================================

@app.post("/webhooks/gmail/pubsub", status_code=status.HTTP_200_OK)
async def gmail_pubsub_webhook(request: Request):
    """
    Gmail Pub/Sub webhook endpoint (Task: T026 - User Story 1).

    Receives push notifications from Gmail when new emails arrive.
    Validates JWT token and processes the notification.

    Returns 200 OK to acknowledge receipt.
    """
    from .webhooks.gmail import gmail_webhook_handler

    try:
        # Get authorization token
        auth_header = request.headers.get("Authorization")

        # Parse Pub/Sub message
        body = await request.json()

        # Handle notification
        result = await gmail_webhook_handler.handle_pubsub_notification(
            pubsub_message=body,
            auth_token=auth_header
        )

        logger.info(f"Gmail Pub/Sub notification processed: {result}")

        return {"status": "received", "result": result}

    except Exception as e:
        logger.error(f"Failed to process Gmail webhook: {e}")
        # Return 200 to avoid retries for invalid messages
        return {"status": "error", "message": str(e)}


# TODO: Add remaining webhook routes in Phase 4+
# - POST /webhooks/twilio/whatsapp (User Story 2)
# - POST /api/support/submit (User Story 3)

# ============================================================================
# API Routes (will be added in Phase 3+)
# ============================================================================

# TODO: Add API routes in Phase 3
# - GET /api/ticket/{ticket_id} (User Story 3)


if __name__ == "__main__":
    import uvicorn

    # Run with: python -m backend.src.main
    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
