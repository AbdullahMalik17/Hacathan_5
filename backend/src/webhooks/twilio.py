"""
Twilio WhatsApp webhook handler.

Receives incoming WhatsApp messages via Twilio webhook,
validates X-Twilio-Signature, and publishes to Kafka.
"""

import logging
from typing import Dict, Any
from fastapi import Request, HTTPException, Header
from pydantic import BaseModel, Field

from ..services.kafka_producer import KafkaProducerService
from ..services.auth import validate_twilio_signature
from ..utils.sanitization import sanitize_input
from ..services.database import DatabaseService

logger = logging.getLogger(__name__)


class TwilioWhatsAppWebhook(BaseModel):
    """Twilio WhatsApp webhook payload model."""

    MessageSid: str = Field(..., description="Twilio message SID")
    From: str = Field(..., description="Sender WhatsApp number with whatsapp: prefix")
    To: str = Field(..., description="Recipient WhatsApp number with whatsapp: prefix")
    Body: str = Field(..., description="Message text content")
    ProfileName: str | None = Field(None, description="Sender's WhatsApp profile name")
    WaId: str | None = Field(None, description="WhatsApp user ID (phone number)")
    NumMedia: str = Field(default="0", description="Number of media items")


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number for consistent customer identification.

    Args:
        phone: Phone number (may include whatsapp: prefix)

    Returns:
        Normalized phone number in E.164 format (+14155551234)
    """
    # Remove whatsapp: prefix if present
    if phone.startswith("whatsapp:"):
        phone = phone.replace("whatsapp:", "")

    # Remove all non-digit characters except leading +
    normalized = phone.strip()
    if not normalized.startswith("+"):
        # Assume US number if no country code
        if len(normalized) == 10:
            normalized = f"+1{normalized}"
        else:
            normalized = f"+{normalized}"

    return normalized


async def handle_whatsapp_message(
    request: Request,
    form_data: Dict[str, str],
    x_twilio_signature: str | None = None,
    kafka_producer: KafkaProducerService = None,
    db_service: DatabaseService = None,
) -> Dict[str, Any]:
    """
    Handle incoming WhatsApp message from Twilio webhook.

    Validates signature, parses message, checks for duplicates,
    and publishes to Kafka for agent processing.

    Args:
        request: FastAPI request object
        form_data: Form-encoded webhook data
        x_twilio_signature: Twilio signature header
        kafka_producer: Kafka producer service
        db_service: Database service

    Returns:
        Response dict with status

    Raises:
        HTTPException: If signature validation fails or message is duplicate
    """
    # Validate Twilio signature (FR-002)
    if not x_twilio_signature:
        logger.error("Missing X-Twilio-Signature header")
        raise HTTPException(status_code=401, detail="Missing signature")

    is_valid = await validate_twilio_signature(
        request_url=str(request.url),
        form_data=form_data,
        signature=x_twilio_signature,
    )

    if not is_valid:
        logger.error("Invalid Twilio signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse webhook payload (FR-003)
    try:
        webhook = TwilioWhatsAppWebhook(**form_data)
    except Exception as e:
        logger.error(f"Failed to parse Twilio webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    # Extract and normalize phone number (FR-003, FR-007)
    sender_phone = normalize_phone_number(webhook.From)
    sender_name = webhook.ProfileName or "WhatsApp User"
    message_body = sanitize_input(webhook.Body)

    logger.info(
        f"WhatsApp message received",
        extra={
            "message_sid": webhook.MessageSid,
            "from": sender_phone,
            "body_length": len(message_body),
        },
    )

    # Check for duplicate message (FR-004)
    is_duplicate = await db_service.check_message_duplicate(
        channel="whatsapp",
        channel_message_id=webhook.MessageSid,
    )

    if is_duplicate:
        logger.info(f"Duplicate WhatsApp message ignored: {webhook.MessageSid}")
        return {"status": "duplicate", "message_sid": webhook.MessageSid}

    # Publish to Kafka for agent processing
    message = {
        "channel": "whatsapp",
        "channel_message_id": webhook.MessageSid,
        "sender": {
            "phone": sender_phone,
            "name": sender_name,
            "wa_id": webhook.WaId or sender_phone.replace("+", ""),
        },
        "content": message_body,
        "metadata": {
            "num_media": int(webhook.NumMedia),
            "to": webhook.To,
        },
    }

    await kafka_producer.publish(
        topic="fte.channels.whatsapp.inbound",
        message=message,
        key=sender_phone,  # Partition by customer for ordering
    )

    logger.info(
        f"WhatsApp message published to Kafka",
        extra={"message_sid": webhook.MessageSid, "phone": sender_phone},
    )

    # Return 200 OK to Twilio (empty TwiML response)
    return {"status": "received"}
