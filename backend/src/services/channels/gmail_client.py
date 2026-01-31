"""
Gmail API client service for sending email responses.
Task: T024 - Implement Gmail API client service for sending email responses
Supports: FR-020, FR-024, FR-031, FR-032
"""

import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GmailClient:
    """Client for interacting with Gmail API."""

    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    def __init__(self):
        self._service = None
        self._credentials = None

    def _get_credentials(self):
        """Get service account credentials for Gmail API."""
        if self._credentials is None:
            try:
                credentials_path = Path(settings.GMAIL_SERVICE_ACCOUNT_PATH)
                if not credentials_path.exists():
                    logger.error(f"Gmail service account file not found: {credentials_path}")
                    raise FileNotFoundError(f"Service account file not found: {credentials_path}")

                self._credentials = service_account.Credentials.from_service_account_file(
                    str(credentials_path),
                    scopes=self.SCOPES
                )

                logger.info("Gmail service account credentials loaded")

            except Exception as e:
                logger.error(f"Failed to load Gmail credentials: {e}")
                raise

        return self._credentials

    def _get_service(self):
        """Get Gmail API service instance."""
        if self._service is None:
            try:
                credentials = self._get_credentials()
                self._service = build('gmail', 'v1', credentials=credentials)
                logger.info("Gmail API service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gmail service: {e}")
                raise

        return self._service

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None
    ) -> dict:
        """
        Send an email via Gmail API.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body_html: HTML email body
            body_text: Plain text email body (optional, defaults to stripped HTML)
            thread_id: Gmail thread ID for conversation continuity (FR-032)
            in_reply_to: Message-ID of the message being replied to
            references: References header for email threading

        Returns:
            Sent message details from Gmail API

        Example:
            await gmail_client.send_email(
                to_email="customer@example.com",
                subject="Re: Your Support Request",
                body_html="<p>Hello! Here's the answer...</p>",
                thread_id="thread_abc123"
            )
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['From'] = settings.GMAIL_SUPPORT_EMAIL
            message['Subject'] = subject

            # Add threading headers for conversation continuity (FR-032)
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
            if references:
                message['References'] = references

            # Attach plain text version
            if body_text:
                part_text = MIMEText(body_text, 'plain')
                message.attach(part_text)

            # Attach HTML version
            part_html = MIMEText(body_html, 'html')
            message.attach(part_html)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Prepare send request
            send_message = {
                'raw': raw_message
            }

            # Include thread_id if provided (for conversation continuity)
            if thread_id:
                send_message['threadId'] = thread_id

            # Send email
            service = self._get_service()
            sent_message = service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            logger.info(
                f"Email sent successfully: to={to_email}, "
                f"message_id={sent_message.get('id')}, "
                f"thread_id={sent_message.get('threadId')}"
            )

            return sent_message

        except HttpError as error:
            logger.error(f"Gmail API error sending email: {error}")
            raise
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise

    async def get_message(self, message_id: str) -> dict:
        """
        Retrieve a message by ID from Gmail.

        Args:
            message_id: Gmail message ID

        Returns:
            Message details
        """
        try:
            service = self._get_service()
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            logger.info(f"Retrieved message: {message_id}")
            return message

        except HttpError as error:
            logger.error(f"Gmail API error retrieving message {message_id}: {error}")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve message {message_id}: {e}")
            raise

    async def get_thread(self, thread_id: str) -> dict:
        """
        Retrieve an entire email thread by ID.

        Args:
            thread_id: Gmail thread ID

        Returns:
            Thread details with all messages
        """
        try:
            service = self._get_service()
            thread = service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()

            logger.info(f"Retrieved thread: {thread_id} with {len(thread.get('messages', []))} messages")
            return thread

        except HttpError as error:
            logger.error(f"Gmail API error retrieving thread {thread_id}: {error}")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve thread {thread_id}: {e}")
            raise


# Global Gmail client instance
gmail_client = GmailClient()


def get_gmail_client() -> GmailClient:
    """Get Gmail client instance for dependency injection."""
    return gmail_client
