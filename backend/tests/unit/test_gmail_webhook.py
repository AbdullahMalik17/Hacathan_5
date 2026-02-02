"""Unit tests for Gmail webhook handler."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.src.webhooks.gmail import GmailWebhookHandler


@pytest.mark.asyncio
class TestGmailWebhookHandler:
    """Test cases for GmailWebhookHandler class."""
    
    async def test_extract_email_address_with_angle_brackets(self):
        """Test extracting email address from header with angle brackets."""
        header_value = "John Doe <john.doe@example.com>"
        result = GmailWebhookHandler._extract_email_address(header_value)
        assert result == "john.doe@example.com"
    
    async def test_extract_email_address_without_angle_brackets(self):
        """Test extracting email address from header without angle brackets."""
        header_value = "john.doe@example.com"
        result = GmailWebhookHandler._extract_email_address(header_value)
        assert result == "john.doe@example.com"
    
    async def test_extract_email_address_with_spaces(self):
        """Test extracting email address from header with spaces."""
        header_value = " john.doe@example.com "
        result = GmailWebhookHandler._extract_email_address(header_value)
        assert result == "john.doe@example.com"
    
    async def test_decode_base64_success(self):
        """Test decoding base64 encoded data."""
        encoded_data = "SGVsbG8gV29ybGQh"  # "Hello World!" in base64
        result = GmailWebhookHandler._decode_base64(encoded_data)
        assert result == "Hello World!"
    
    async def test_decode_base64_url_safe(self):
        """Test decoding URL-safe base64 encoded data."""
        encoded_data = "SGVsbG8gV29ybGQh"  # Same as above, but URL-safe
        result = GmailWebhookHandler._decode_base64(encoded_data)
        assert result == "Hello World!"
    
    async def test_decode_base64_failure(self):
        """Test decoding invalid base64 data."""
        encoded_data = "invalid_base64_data"
        result = GmailWebhookHandler._decode_base64(encoded_data)
        assert result == ""
    
    async def test_get_header_value_found(self):
        """Test getting header value when it exists."""
        headers = [
            {"name": "Subject", "value": "Test Subject"},
            {"name": "From", "value": "sender@example.com"}
        ]
        result = GmailWebhookHandler._get_header_value(headers, "Subject")
        assert result == "Test Subject"
    
    async def test_get_header_value_not_found(self):
        """Test getting header value when it doesn't exist."""
        headers = [
            {"name": "Subject", "value": "Test Subject"},
            {"name": "From", "value": "sender@example.com"}
        ]
        result = GmailWebhookHandler._get_header_value(headers, "To")
        assert result is None
    
    async def test_get_header_value_case_insensitive(self):
        """Test getting header value with case insensitive matching."""
        headers = [
            {"name": "Subject", "value": "Test Subject"},
            {"name": "FROM", "value": "sender@example.com"}
        ]
        result = GmailWebhookHandler._get_header_value(headers, "from")
        assert result == "sender@example.com"


@pytest.mark.asyncio
class TestGmailWebhookHandlerIntegration:
    """Integration-style tests for Gmail webhook handler methods."""
    
    @patch('backend.src.webhooks.gmail.gmail_client')
    async def test_parse_email_message_success(self, mock_gmail_client):
        """Test parsing email message successfully."""
        # Mock the Gmail client response
        mock_gmail_client.get_message.return_value = {
            "id": "test_msg_123",
            "threadId": "test_thread_456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "customer@example.com"},
                    {"name": "Subject", "value": "Help needed"},
                ],
                "body": {
                    "data": "VGhpcyBpcyB0aGUgbWVzc2FnZSBib2R5Lg==",  # "This is the message body."
                    "size": 20
                }
            }
        }
        
        result = await GmailWebhookHandler.parse_email_message("test_msg_123")
        
        assert result["customer_email"] == "customer@example.com"
        assert result["subject"] == "Help needed"
        assert result["body"] == "This is the message body."
        assert result["thread_id"] == "test_thread_456"
        assert result["message_id"] == "test_msg_123"
    
    @patch('backend.src.webhooks.gmail.gmail_client')
    async def test_parse_email_message_missing_from_header(self, mock_gmail_client):
        """Test parsing email message with missing From header."""
        # Mock the Gmail client response with missing From header
        mock_gmail_client.get_message.return_value = {
            "id": "test_msg_123",
            "threadId": "test_thread_456",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Help needed"},
                ],
                "body": {
                    "data": "VGhpcyBpcyB0aGUgbWVzc2FnZSBib2R5Lg==",
                    "size": 20
                }
            }
        }
        
        with pytest.raises(ValueError, match="No From header found in email"):
            await GmailWebhookHandler.parse_email_message("test_msg_123")
    
    @patch('backend.src.webhooks.gmail.gmail_client')
    async def test_parse_email_message_with_parts(self, mock_gmail_client):
        """Test parsing email message with multipart content."""
        # Mock the Gmail client response with parts
        mock_gmail_client.get_message.return_value = {
            "id": "test_msg_123",
            "threadId": "test_thread_456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "customer@example.com"},
                    {"name": "Subject", "value": "Help needed"},
                ],
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": "VGhpcyBpcyB0aGUgcGxhaW4gdGV4dCBib2R5Lg=="  # "This is the plain text body."
                        }
                    },
                    {
                        "mimeType": "text/html",
                        "body": {
                            "data": "PGh0bWw+PHA+VGhpcyBpcyB0aGUgaHRtbCBib2R5LjwvcD48L2h0bWw+"  # "<html><p>This is the html body.</p></html>"
                        }
                    }
                ]
            }
        }
        
        result = await GmailWebhookHandler.parse_email_message("test_msg_123")
        
        assert result["customer_email"] == "customer@example.com"
        assert result["subject"] == "Help needed"
        assert result["body"] == "This is the plain text body."  # Plain text is preferred
        assert result["thread_id"] == "test_thread_456"
        assert result["message_id"] == "test_msg_123"