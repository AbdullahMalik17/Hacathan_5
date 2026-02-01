"""
Twilio API client for sending WhatsApp messages.

Handles WhatsApp message sending via Twilio API with
delivery status tracking.
"""

import logging
import os
from typing import Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class TwilioClient:
    """
    Twilio API client for WhatsApp messaging.

    Attributes:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        whatsapp_number: Twilio WhatsApp-enabled number
        client: Twilio REST client
    """

    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        whatsapp_number: str | None = None,
    ):
        """
        Initialize Twilio client.

        Args:
            account_sid: Twilio Account SID (defaults to env var)
            auth_token: Twilio Auth Token (defaults to env var)
            whatsapp_number: Twilio WhatsApp number (defaults to env var)
        """
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = whatsapp_number or os.getenv(
            "TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"
        )

        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio credentials not configured")

        self.client = Client(self.account_sid, self.auth_token)
        logger.info(f"Twilio client initialized with number {self.whatsapp_number}")

    async def send_whatsapp_message(
        self, to: str, body: str, status_callback: str | None = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message via Twilio.

        Args:
            to: Recipient phone number (with whatsapp: prefix or will be added)
            body: Message text (max 1600 chars for WhatsApp)
            status_callback: Optional URL for delivery status callbacks

        Returns:
            Dict with message SID and delivery status

        Raises:
            TwilioRestException: If message sending fails
        """
        # Ensure whatsapp: prefix
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"

        # Validate message length (FR-033)
        if len(body) > 1600:
            logger.warning(f"WhatsApp message truncated from {len(body)} to 1600 chars")
            body = body[:1597] + "..."

        try:
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                to=to,
                body=body,
                status_callback=status_callback,
            )

            logger.info(
                f"WhatsApp message sent",
                extra={
                    "message_sid": message.sid,
                    "to": to,
                    "status": message.status,
                },
            )

            return {
                "message_sid": message.sid,
                "status": message.status,
                "to": to,
                "body_length": len(body),
                "error_code": message.error_code,
                "error_message": message.error_message,
            }

        except TwilioRestException as e:
            logger.error(
                f"Failed to send WhatsApp message",
                extra={"to": to, "error_code": e.code, "error": str(e)},
            )
            raise

    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get delivery status for a sent message (FR-034).

        Args:
            message_sid: Twilio message SID

        Returns:
            Dict with message status details

        Statuses: queued, sending, sent, delivered, undelivered, failed, read
        """
        try:
            message = self.client.messages(message_sid).fetch()

            return {
                "message_sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent,
                "date_updated": message.date_updated,
            }

        except TwilioRestException as e:
            logger.error(f"Failed to fetch message status: {e}")
            return {"message_sid": message_sid, "status": "unknown", "error": str(e)}

    async def send_whatsapp_message_split(
        self, to: str, body: str, max_length: int = 300
    ) -> list[Dict[str, Any]]:
        """
        Send long WhatsApp message as multiple messages (FR-034).

        Splits message at sentence boundaries when possible.

        Args:
            to: Recipient phone number
            body: Message text (can exceed max_length)
            max_length: Maximum chars per message (default 300 for concise responses)

        Returns:
            List of message send results
        """
        if len(body) <= max_length:
            result = await self.send_whatsapp_message(to, body)
            return [result]

        # Split at sentence boundaries
        sentences = body.replace("! ", "!|").replace(". ", ".|").replace("? ", "?|").split("|")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Send each chunk
        results = []
        for i, chunk in enumerate(chunks):
            prefix = f"({i+1}/{len(chunks)}) " if len(chunks) > 1 else ""
            result = await self.send_whatsapp_message(to, prefix + chunk)
            results.append(result)

        logger.info(f"WhatsApp message split into {len(chunks)} parts for {to}")
        return results
