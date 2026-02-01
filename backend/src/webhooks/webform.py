"""
Web form submission webhook handler.

Receives support requests from web form, validates input,
creates ticket, sends confirmation email, and publishes to Kafka.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field, EmailStr, field_validator

from ..services.kafka_producer import KafkaProducerService
from ..services.channels.gmail_client import gmail_client
from ..services.database import DatabaseService
from ..utils.sanitization import sanitize_input

logger = logging.getLogger(__name__)


# ============================================================================
# Task T063: Form validation schema (FR-035)
# ============================================================================

class WebFormSubmission(BaseModel):
    """
    Web form submission model with validation.

    Requirements (FR-035):
    - Email format validation
    - Required fields
    - Message length: 10-5000 characters
    """

    name: str = Field(..., min_length=2, max_length=100, description="Customer name")
    email: EmailStr = Field(..., description="Customer email address")
    subject: str = Field(..., min_length=5, max_length=200, description="Request subject")
    message: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Request message (10-5000 chars)",
    )
    priority: str = Field(default="normal", description="Request priority (normal or high)")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is either normal or high."""
        if v not in ["normal", "high"]:
            raise ValueError("Priority must be 'normal' or 'high'")
        return v

    @field_validator("name", "subject", "message")
    @classmethod
    def sanitize_text_fields(cls, v: str) -> str:
        """Sanitize text fields for XSS prevention."""
        return sanitize_input(v)


# ============================================================================
# Task T061: Web form webhook handler
# ============================================================================

async def handle_webform_submission(
    form_data: WebFormSubmission,
    kafka_producer: KafkaProducerService,
    db_service: DatabaseService,
) -> Dict[str, Any]:
    """
    Handle web form submission.

    Flow (FR-036, FR-037):
    1. Validate form data
    2. Create ticket immediately
    3. Send confirmation email within 30 seconds
    4. Publish to Kafka for agent processing
    5. Return ticket ID to frontend

    Args:
        form_data: Validated web form data
        kafka_producer: Kafka producer service
        db_service: Database service

    Returns:
        Dict with ticket_id and status
    """
    logger.info(
        f"Web form submission received",
        extra={
            "email": form_data.email,
            "subject": form_data.subject,
            "priority": form_data.priority,
        },
    )

    # ========================================================================
    # Task T065: Immediate ticket ID response (FR-036, FR-037)
    # ========================================================================

    # Create ticket immediately
    ticket_id = uuid4()

    # Get or create customer
    customer_query = """
        SELECT id FROM customers WHERE primary_email = $1
    """
    customer = await db_service.fetchrow(customer_query, form_data.email)

    if not customer:
        # Create new customer
        customer_id = uuid4()
        create_customer_query = """
            INSERT INTO customers (id, primary_email, name, created_at)
            VALUES ($1, $2, $3, NOW())
            RETURNING id
        """
        customer = await db_service.fetchrow(
            create_customer_query, customer_id, form_data.email, form_data.name
        )

        # Create email identifier
        create_identifier_query = """
            INSERT INTO customer_identifiers (id, customer_id, identifier_type, identifier_value, verified)
            VALUES ($1, $2, 'email', $3, TRUE)
        """
        await db_service.execute(
            create_identifier_query, uuid4(), customer_id, form_data.email
        )
    else:
        customer_id = customer["id"]

    # Create conversation
    conversation_id = uuid4()
    create_conversation_query = """
        INSERT INTO conversations (id, customer_id, initial_channel, status, started_at)
        VALUES ($1, $2, 'webform', 'active', NOW())
        RETURNING id
    """
    conversation = await db_service.fetchrow(
        create_conversation_query, conversation_id, customer_id
    )

    # Determine priority based on form selection (FR-014)
    # High priority: 5 min SLA, Normal priority: 10 min SLA
    priority_level = "high" if form_data.priority == "high" else "medium"

    # Create ticket
    create_ticket_query = """
        INSERT INTO tickets (
            id, conversation_id, customer_id, source_channel,
            category, priority, status, created_at
        )
        VALUES ($1, $2, $3, 'webform', 'general', $4, 'open', NOW())
        RETURNING id, created_at
    """
    ticket = await db_service.fetchrow(
        create_ticket_query,
        ticket_id,
        conversation_id,
        customer_id,
        priority_level,
    )

    # Store initial message
    message_id = uuid4()
    create_message_query = """
        INSERT INTO messages (
            id, conversation_id, channel, direction, role,
            content, created_at, metadata
        )
        VALUES ($1, $2, 'webform', 'inbound', 'customer', $3, NOW(), $4)
        RETURNING id
    """
    await db_service.execute(
        create_message_query,
        message_id,
        conversation_id,
        form_data.message,
        json.dumps({"subject": form_data.subject, "name": form_data.name}),
    )

    # ========================================================================
    # Task T066: Send confirmation email (FR-037)
    # ========================================================================

    try:
        confirmation_subject = f"We've received your request: {form_data.subject}"
        confirmation_body = f"""
Dear {form_data.name},

Thank you for contacting our support team. We have received your request and our AI support agent is processing it now.

**Your Ticket ID:** {ticket_id}

**Subject:** {form_data.subject}

**Expected Response Time:** {'5 minutes (High Priority)' if form_data.priority == 'high' else '10 minutes (Normal Priority)'}

You will receive a detailed response via email shortly. If you need to reference this request later, please save your ticket ID.

If you have any additional information to add, simply reply to this email.

Best regards,

Customer Success Team
support@company.com

---
This is an automated confirmation from our AI support system.
"""

        await gmail_client.send_email(
            to_email=form_data.email,
            subject=confirmation_subject,
            body_text=confirmation_body,
            body_html=None,  # Use text-only for confirmation
        )

        logger.info(
            f"Confirmation email sent",
            extra={"ticket_id": str(ticket_id), "email": form_data.email},
        )

    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        # Don't fail the request if confirmation email fails

    # ========================================================================
    # Task T067: Publish to Kafka (FR-037)
    # ========================================================================

    # Publish to Kafka for agent processing (Unified Ticket Ingestion)
    message_payload = {
        "channel": "webform",
        "channel_message_id": str(message_id),
        "customer_identifier": form_data.email,  # Use unified field name
        "customer_id": str(customer_id),
        "conversation_id": str(conversation_id),
        "ticket_id": str(ticket_id),
        "sender": {
            "email": form_data.email,
            "name": form_data.name,
        },
        "content": form_data.message,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "subject": form_data.subject,
            "priority": form_data.priority,
            "priority_level": priority_level,
        },
    }

    await kafka_producer.publish(
        topic="fte.tickets.incoming",
        message=message_payload,
        key=form_data.email,  # Partition by customer email
    )

    logger.info(
        f"Web form submission published to Kafka",
        extra={"ticket_id": str(ticket_id), "priority": form_data.priority},
    )

    # Return ticket ID immediately (FR-036)
    return {
        "ticket_id": str(ticket_id),
        "status": "received",
        "message": "Your support request has been received and is being processed.",
        "priority": form_data.priority,
        "expected_response_time": "5 minutes" if form_data.priority == "high" else "10 minutes",
    }


# ============================================================================
# Task T064: Ticket status endpoint (FR-036)
# ============================================================================

async def get_ticket_details(
    ticket_id: str, db_service: DatabaseService
) -> Dict[str, Any]:
    """
    Get ticket details and conversation history.

    Args:
        ticket_id: Ticket UUID
        db_service: Database service

    Returns:
        Dict with ticket details and message history

    Raises:
        ValueError: If ticket not found
    """
    from uuid import UUID

    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise ValueError("Invalid ticket ID format")

    # Get ticket details
    ticket_query = """
        SELECT
            t.id,
            t.status,
            t.category,
            t.priority,
            t.source_channel,
            t.created_at,
            t.resolved_at,
            c.primary_email,
            c.name
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
        WHERE t.id = $1
    """
    ticket = await db_service.fetchrow(ticket_query, ticket_uuid)

    if not ticket:
        raise ValueError(f"Ticket not found: {ticket_id}")

    # Get conversation messages
    messages_query = """
        SELECT
            m.role,
            m.content,
            m.channel,
            m.direction,
            m.created_at
        FROM messages m
        JOIN tickets t ON m.conversation_id = t.conversation_id
        WHERE t.id = $1
        ORDER BY m.created_at ASC
    """
    messages = await db_service.fetch(messages_query, ticket_uuid)

    return {
        "ticket_id": str(ticket["id"]),
        "status": ticket["status"],
        "category": ticket["category"],
        "priority": ticket["priority"],
        "source_channel": ticket["source_channel"],
        "created_at": ticket["created_at"].isoformat(),
        "resolved_at": ticket["resolved_at"].isoformat() if ticket["resolved_at"] else None,
        "customer": {
            "email": ticket["primary_email"],
            "name": ticket["name"],
        },
        "messages": [
            {
                "role": msg["role"],
                "content": msg["content"],
                "channel": msg["channel"],
                "direction": msg["direction"],
                "created_at": msg["created_at"].isoformat(),
            }
            for msg in messages
        ],
    }
