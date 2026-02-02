"""Unit tests for Twilio WhatsApp webhook handler."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.src.webhooks.twilio import normalize_phone_number, TwilioWhatsAppWebhook


class TestNormalizePhoneNumber:
    """Test cases for phone number normalization function."""
    
    def test_normalize_phone_number_with_whatsapp_prefix(self):
        """Test normalizing phone number with whatsapp: prefix."""
        phone = "whatsapp:+1234567890"
        result = normalize_phone_number(phone)
        assert result == "+1234567890"
    
    def test_normalize_phone_number_without_prefix(self):
        """Test normalizing phone number without whatsapp: prefix."""
        phone = "+1234567890"
        result = normalize_phone_number(phone)
        assert result == "+1234567890"
    
    def test_normalize_phone_number_us_format(self):
        """Test normalizing US phone number without country code."""
        phone = "2345678901"
        result = normalize_phone_number(phone)
        assert result == "+12345678901"
    
    def test_normalize_phone_number_with_extra_chars(self):
        """Test normalizing phone number with extra characters."""
        phone = "whatsapp:234-567-8901"
        result = normalize_phone_number(phone)
        assert result == "+12345678901"
    
    def test_normalize_phone_number_international(self):
        """Test normalizing international phone number."""
        phone = "447900000000"
        result = normalize_phone_number(phone)
        assert result == "+447900000000"


class TestTwilioWhatsAppWebhookModel:
    """Test cases for TwilioWhatsAppWebhook Pydantic model."""
    
    def test_valid_webhook_payload(self):
        """Test creating a valid webhook payload."""
        payload = {
            "MessageSid": "SMtest1234567890abcdef1234567890ab",
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+10987654321",
            "Body": "Hello, I need help with my account.",
            "ProfileName": "John Doe",
            "WaId": "1234567890",
            "NumMedia": "0"
        }
        
        webhook = TwilioWhatsAppWebhook(**payload)
        
        assert webhook.MessageSid == "SMtest1234567890abcdef1234567890ab"
        assert webhook.From == "whatsapp:+1234567890"
        assert webhook.To == "whatsapp:+10987654321"
        assert webhook.Body == "Hello, I need help with my account."
        assert webhook.ProfileName == "John Doe"
        assert webhook.WaId == "1234567890"
        assert webhook.NumMedia == "0"
    
    def test_webhook_payload_with_missing_optional_fields(self):
        """Test creating a webhook payload with missing optional fields."""
        payload = {
            "MessageSid": "SMtest1234567890abcdef1234567890ab",
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+10987654321",
            "Body": "Hello, I need help with my account.",
            "NumMedia": "0"
        }
        
        webhook = TwilioWhatsAppWebhook(**payload)
        
        assert webhook.MessageSid == "SMtest1234567890abcdef1234567890ab"
        assert webhook.From == "whatsapp:+1234567890"
        assert webhook.To == "whatsapp:+10987654321"
        assert webhook.Body == "Hello, I need help with my account."
        assert webhook.ProfileName is None
        assert webhook.WaId is None
        assert webhook.NumMedia == "0"
    
    def test_required_fields_validation(self):
        """Test validation of required fields."""
        payload = {
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+10987654321",
            "Body": "Hello, I need help with my account."
            # Missing MessageSid
        }
        
        with pytest.raises(ValueError):
            TwilioWhatsAppWebhook(**payload)