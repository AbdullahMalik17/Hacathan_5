"""
Gmail Pub/Sub webhook handler with email message parser.
Task: T023 - Create Gmail Pub/Sub webhook handler with JWT token validation
Task: T027 - Implement email message parser to extract customer email, subject, body, thread ID
Supports: FR-002, FR-003, FR-004
"""

import base64
import email
import logging
import re
from typing import Dict, Optional, Tuple
from uuid import uuid4

from fastapi import HTTPException, status

from ..models import InboundMessage, MessageChannel
from ..services.auth import auth_service
from ..services.channels.gmail_client import gmail_client
from ..services.kafka_producer import kafka_producer
from ..utils.sanitization import sanitize_customer_input

logger = logging.getLogger(__name__)


class GmailWebhookHandler:
    """Handler for Gmail Pub/Sub notifications."""

    @staticmethod
    def _extract_email_address(header_value: str) -> str:
        """
        Extract email address from email header (From, To, etc.).

        Args:
            header_value: Email header value (e.g., "John Doe <john@example.com>")

        Returns:
            Email address

        Example:
            >>> _extract_email_address("John Doe <john@example.com>")
            'john@example.com'
        """
        # Match email pattern in angle brackets or standalone
        match = re.search(r'<([^>]+)>|([^\s]+@[^\s]+)', header_value)
        if match:
            return match.group(1) or match.group(2)
        return header_value.strip()

    @staticmethod
    def _decode_base64(data: str) -> str:
        """
        Decode base64 encoded email content.

        Args:
            data: Base64 encoded string

        Returns:
            Decoded string
        """
        try:
            # Gmail uses URL-safe base64 encoding
            decoded_bytes = base64.urlsafe_b64decode(data)
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to decode base64 data: {e}")
            return ""

    @staticmethod
    def _extract_email_body(message: dict) -> Tuple[str, str]:
        """
        Extract plain text and HTML body from Gmail message.

        Args:
            message: Gmail message object

        Returns:
            Tuple of (plain_text, html_text)
        """
        plain_text = ""
        html_text = ""

        payload = message.get('payload', {})

        # Check if message has parts (multipart)
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                body_data = part.get('body', {}).get('data', '')

                if mime_type == 'text/plain' and not plain_text:
                    plain_text = GmailWebhookHandler._decode_base64(body_data)
                elif mime_type == 'text/html' and not html_text:
                    html_text = GmailWebhookHandler._decode_base64(body_data)

                # Handle nested parts (multipart/alternative)
                if 'parts' in part:
                    for nested_part in part['parts']:
                        nested_mime = nested_part.get('mimeType', '')
                        nested_data = nested_part.get('body', {}).get('data', '')

                        if nested_mime == 'text/plain' and not plain_text:
                            plain_text = GmailWebhookHandler._decode_base64(nested_data)
                        elif nested_mime == 'text/html' and not html_text:
                            html_text = GmailWebhookHandler._decode_base64(nested_data)

        # Single part message
        else:
            mime_type = payload.get('mimeType', '')
            body_data = payload.get('body', {}).get('data', '')

            if mime_type == 'text/plain':
                plain_text = GmailWebhookHandler._decode_base64(body_data)
            elif mime_type == 'text/html':
                html_text = GmailWebhookHandler._decode_base64(body_data)

        return plain_text, html_text

    @staticmethod
    def _get_header_value(headers: list, name: str) -> Optional[str]:
        """
        Get header value by name from Gmail headers list.

        Args:
            headers: List of header dictionaries
            name: Header name to search for

        Returns:
            Header value or None
        """
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value', '')
        return None

    @staticmethod
    async def parse_email_message(message_id: str) -> Dict:
        """
        Parse Gmail message and extract relevant information.

        Task: T027 - Extract customer email, subject, body, and thread ID (FR-003, FR-004)

        Args:
            message_id: Gmail message ID from Pub/Sub notification

        Returns:
            Dictionary with parsed email data

        Example:
            parsed = await parse_email_message("msg_abc123")
            # Returns: {
            #     "customer_email": "customer@example.com",
            #     "subject": "Help needed",
            #     "body": "I need assistance with...",
            #     "thread_id": "thread_xyz789",
            #     "message_id": "msg_abc123",
            #     "in_reply_to": "<previous@msg.id>",
            #     "references": "<ref1@msg.id> <ref2@msg.id>"
            # }
        """
        try:
            # Retrieve full message from Gmail API
            message = await gmail_client.get_message(message_id)

            # Extract headers
            headers = message.get('payload', {}).get('headers', [])

            # Extract customer email (From header) - FR-003
            from_header = GmailWebhookHandler._get_header_value(headers, 'From')
            if not from_header:
                raise ValueError("No From header found in email")

            customer_email = GmailWebhookHandler._extract_email_address(from_header)

            # Extract subject
            subject = GmailWebhookHandler._get_header_value(headers, 'Subject') or "(No Subject)"

            # Extract thread ID for conversation continuity
            thread_id = message.get('threadId')

            # Extract In-Reply-To and References for email threading (FR-032)
            in_reply_to = GmailWebhookHandler._get_header_value(headers, 'In-Reply-To')
            references = GmailWebhookHandler._get_header_value(headers, 'References')

            # Extract email body
            plain_text, html_text = GmailWebhookHandler._extract_email_body(message)

            # Prefer plain text, fallback to HTML
            body = plain_text or html_text or "(Empty message)"

            # Sanitize body content (FR-038)
            body = sanitize_customer_input(body, max_length=10000)

            parsed_data = {
                "customer_email": customer_email,
                "subject": subject,
                "body": body,
                "thread_id": thread_id,
                "message_id": message_id,  # For deduplication (FR-004)
                "in_reply_to": in_reply_to,
                "references": references,
                "metadata": {
                    "has_html": bool(html_text),
                    "has_plain_text": bool(plain_text),
                    "original_subject": subject
                }
            }

            logger.info(
                f"Parsed email: from={customer_email}, "
                f"subject={subject[:50]}, thread_id={thread_id}"
            )

            return parsed_data

        except Exception as e:
            logger.error(f"Failed to parse email message {message_id}: {e}")
            raise

    @staticmethod
    async def handle_pubsub_notification(
        pubsub_message: dict,
        auth_token: Optional[str] = None
    ) -> dict:
        """
        Handle Gmail Pub/Sub notification.

        Task: T023 - JWT token validation and message processing (FR-002)

        Args:
            pubsub_message: Pub/Sub message payload
            auth_token: JWT token from Authorization header (optional for testing)

        Returns:
            Processing result

        Example Pub/Sub message:
            {
                "message": {
                    "data": "base64_encoded_data",
                    "messageId": "pubsub_msg_id",
                    "publishTime": "2024-01-01T12:00:00Z"
                },
                "subscription": "projects/project/subscriptions/gmail-sub"
            }
        """
        try:
            # Validate JWT token if provided (FR-002)
            if auth_token:
                token_payload = auth_service.verify_gmail_pubsub_token(auth_token)
                logger.info(f"Authenticated Gmail Pub/Sub from: {token_payload.get('email')}")

            # Extract message data
            message_data = pubsub_message.get('message', {})
            encoded_data = message_data.get('data', '')

            # Decode message data
            if encoded_data:
                decoded_data = base64.b64decode(encoded_data).decode('utf-8')
                notification_data = eval(decoded_data)  # Gmail sends Python dict as string
                gmail_message_id = notification_data.get('emailAddress')
                history_id = notification_data.get('historyId')

                logger.info(f"Gmail Pub/Sub notification: history_id={history_id}")

                # For MVP, we'll parse the notification to get message ID
                # In production, you'd use Gmail History API to get new messages
                # For now, we'll extract the message ID from the notification
                # This is a simplified implementation

                return {
                    "status": "notification_received",
                    "history_id": history_id
                }

            else:
                logger.warning("Empty Pub/Sub message data")
                return {"status": "empty_notification"}

        except Exception as e:
            logger.error(f"Failed to handle Gmail Pub/Sub notification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process notification: {str(e)}"
            )

    @staticmethod
    async def process_inbound_email(message_id: str) -> None:
        """
        Process inbound email and publish to Kafka.

        Args:
            message_id: Gmail message ID

        Returns:
            None (publishes to Kafka)
        """
        try:
            # Parse email message (T027)
            parsed_email = await GmailWebhookHandler.parse_email_message(message_id)

            # Create inbound message object
            inbound_message = InboundMessage(
                channel=MessageChannel.EMAIL,
                customer_identifier=parsed_email["customer_email"],
                content=parsed_email["body"],
                channel_message_id=parsed_email["message_id"],
                timestamp=datetime.utcnow(),
                metadata={
                    "subject": parsed_email["subject"],
                    "thread_id": parsed_email["thread_id"],
                    "in_reply_to": parsed_email["in_reply_to"],
                    "references": parsed_email["references"],
                    **parsed_email["metadata"]
                }
            )

            # Publish to Kafka for agent processing
            correlation_id = await kafka_producer.publish(
                topic="fte.tickets.incoming",
                message=inbound_message.model_dump(mode='json'),
                key=f"email-{parsed_email['customer_email']}"
            )

            logger.info(
                f"Email published to Kafka: message_id={message_id}, "
                f"correlation_id={correlation_id}"
            )

        except Exception as e:
            logger.error(f"Failed to process inbound email {message_id}: {e}")
            # Publish to DLQ for retry
            await kafka_producer.publish(
                topic="fte.dlq",
                message={
                    "message_id": message_id,
                    "error": str(e),
                    "source": "gmail_webhook"
                }
            )
            raise


# Add missing import
from datetime import datetime


# Global webhook handler instance
gmail_webhook_handler = GmailWebhookHandler()
