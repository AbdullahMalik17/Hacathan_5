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


@app.post("/webhooks/twilio/whatsapp", status_code=status.HTTP_200_OK)
async def twilio_whatsapp_webhook(request: Request):
    """
    Twilio WhatsApp webhook endpoint (Task: T047 - User Story 2).

    Receives incoming WhatsApp messages via Twilio webhook.
    Validates X-Twilio-Signature and processes the message.

    Returns 200 OK with empty TwiML response.
    """
    from .webhooks.twilio import handle_whatsapp_message

    try:
        # Get signature header
        signature = request.headers.get("X-Twilio-Signature")

        # Parse form data
        form_data = await request.form()
        form_dict = dict(form_data)

        # Handle WhatsApp message
        result = await handle_whatsapp_message(
            request=request,
            form_data=form_dict,
            x_twilio_signature=signature,
            kafka_producer=kafka_producer,
            db_service=db_service,
        )

        logger.info(f"Twilio WhatsApp webhook processed: {result}")

        # Return empty response (Twilio expects 200 OK)
        return result

    except Exception as e:
        logger.error(f"Failed to process Twilio webhook: {e}")
        # Return 200 to avoid retries for invalid messages
        return {"status": "error", "message": str(e)}


# ============================================================================
# API Routes (Phase 5: User Story 3 - Web Form)
# ============================================================================

@app.post("/api/support/submit", status_code=status.HTTP_200_OK)
async def submit_support_request(request: Request):
    """
    Web form submission endpoint (Task: T062 - User Story 3).

    Validates form data, creates ticket immediately, sends confirmation email,
    and publishes to Kafka for agent processing.

    Returns immediate ticket ID for customer tracking (FR-036).
    """
    from .webhooks.webform import WebFormSubmission, handle_webform_submission

    try:
        # Parse JSON body
        body = await request.json()

        # Validate form data
        form_data = WebFormSubmission(**body)

        # Handle submission
        result = await handle_webform_submission(
            form_data=form_data,
            kafka_producer=kafka_producer,
            db_service=db_service,
        )

        logger.info(f"Web form submission processed: {result['ticket_id']}")

        return result

    except Exception as e:
        logger.error(f"Failed to process web form submission: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(e), "status": "error"}
        )


@app.get("/api/ticket/{ticket_id}", status_code=status.HTTP_200_OK)
async def get_ticket_status(ticket_id: str):
    """
    Ticket status endpoint (Task: T064 - User Story 3).

    Returns ticket details and conversation history for tracking (FR-036).
    """
    from .webhooks.webform import get_ticket_details

    try:
        ticket_details = await get_ticket_details(
            ticket_id=ticket_id,
            db_service=db_service,
        )

        logger.info(f"Ticket status retrieved: {ticket_id}")

        return ticket_details

    except ValueError as e:
        logger.error(f"Ticket not found: {ticket_id}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e), "status": "not_found"}
        )
    except Exception as e:
        logger.error(f"Failed to retrieve ticket status: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e), "status": "error"}
        )


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
