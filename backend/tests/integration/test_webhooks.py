"""Integration tests for webhook handlers."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import json

from backend.src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.asyncio
class TestGmailWebhookIntegration:
    """Integration tests for Gmail webhook endpoint."""
    
    @patch('backend.src.webhooks.gmail.gmail_webhook_handler.handle_pubsub_notification')
    async def test_gmail_pubsub_webhook_success(self, mock_handle_notification, client):
        """Test successful Gmail Pub/Sub webhook request."""
        # Mock the handler response
        mock_handle_notification.return_value = {"status": "processed", "message": "OK"}
        
        # Sample Pub/Sub message
        pubsub_message = {
            "message": {
                "data": "eydleGFtcGxlJzogJ2RhdGEnfQ==",  # base64 encoded '{"example": "data"}'
                "messageId": "test-message-id",
                "publishTime": "2026-01-01T12:00:00Z"
            },
            "subscription": "projects/test-project/subscriptions/gmail-sub"
        }
        
        response = client.post(
            "/webhooks/gmail/pubsub",
            json=pubsub_message,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "received"
        assert "result" in response_data
        
        # Verify the handler was called
        mock_handle_notification.assert_called_once()
    
    @patch('backend.src.webhooks.gmail.gmail_webhook_handler.handle_pubsub_notification')
    async def test_gmail_pubsub_webhook_error_handling(self, mock_handle_notification, client):
        """Test Gmail Pub/Sub webhook error handling."""
        # Mock the handler to raise an exception
        mock_handle_notification.side_effect = Exception("Processing error")
        
        # Sample Pub/Sub message
        pubsub_message = {
            "message": {
                "data": "eydleGFtcGxlJzogJ2RhdGEnfQ==",
                "messageId": "test-message-id",
                "publishTime": "2026-01-01T12:00:00Z"
            },
            "subscription": "projects/test-project/subscriptions/gmail-sub"
        }
        
        response = client.post(
            "/webhooks/gmail/pubsub",
            json=pubsub_message,
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should still return 200 to avoid retries even if there's an error
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "error"
        assert "message" in response_data


@pytest.mark.asyncio
class TestTwilioWhatsAppWebhookIntegration:
    """Integration tests for Twilio WhatsApp webhook endpoint."""
    
    @patch('backend.src.webhooks.twilio.validate_twilio_signature')
    @patch('backend.src.webhooks.twilio.handle_whatsapp_message')
    async def test_twilio_whatsapp_webhook_success(self, mock_handle_message, mock_validate_signature, client):
        """Test successful Twilio WhatsApp webhook request."""
        # Mock validation and handler
        mock_validate_signature.return_value = True
        mock_handle_message.return_value = {"status": "received", "message_sid": "SMtest123"}
        
        # Sample form data
        form_data = {
            "MessageSid": "SMtest1234567890abcdef1234567890ab",
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+10987654321",
            "Body": "Hello, I need help with my account.",
            "ProfileName": "John Doe",
            "WaId": "1234567890",
            "NumMedia": "0"
        }
        
        # Convert form data to the format expected by TestClient
        form_data_str = "&".join([f"{key}={value}" for key, value in form_data.items()])
        
        response = client.post(
            "/webhooks/twilio/whatsapp",
            content=form_data_str,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Twilio-Signature": "test-signature"
            }
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "received"
        
        # Verify the validation and handler were called
        mock_validate_signature.assert_called_once()
        mock_handle_message.assert_called_once()
    
    @patch('backend.src.webhooks.twilio.validate_twilio_signature')
    async def test_twilio_whatsapp_webhook_invalid_signature(self, mock_validate_signature, client):
        """Test Twilio WhatsApp webhook with invalid signature."""
        # Mock validation to return False
        mock_validate_signature.return_value = False
        
        # Sample form data
        form_data = {
            "MessageSid": "SMtest1234567890abcdef1234567890ab",
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+10987654321",
            "Body": "Hello, I need help with my account.",
            "ProfileName": "John Doe",
            "WaId": "1234567890",
            "NumMedia": "0"
        }
        
        # Convert form data to the format expected by TestClient
        form_data_str = "&".join([f"{key}={value}" for key, value in form_data.items()])
        
        response = client.post(
            "/webhooks/twilio/whatsapp",
            content=form_data_str,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Twilio-Signature": "invalid-signature"
            }
        )
        
        # Should return 401 for invalid signature
        assert response.status_code == 401
        response_data = response.json()
        assert "Invalid signature" in response_data["detail"]
    
    @patch('backend.src.webhooks.twilio.validate_twilio_signature')
    async def test_twilio_whatsapp_webhook_missing_signature(self, mock_validate_signature, client):
        """Test Twilio WhatsApp webhook with missing signature."""
        # Sample form data
        form_data = {
            "MessageSid": "SMtest1234567890abcdef1234567890ab",
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+10987654321",
            "Body": "Hello, I need help with my account.",
            "ProfileName": "John Doe",
            "WaId": "1234567890",
            "NumMedia": "0"
        }
        
        # Convert form data to the format expected by TestClient
        form_data_str = "&".join([f"{key}={value}" for key, value in form_data.items()])
        
        response = client.post(
            "/webhooks/twilio/whatsapp",
            content=form_data_str,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
                # Missing X-Twilio-Signature header
            }
        )
        
        # Should return 401 for missing signature
        assert response.status_code == 401
        response_data = response.json()
        assert "Missing signature" in response_data["detail"]


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert response_data["service"] == "customer-success-fte"
    
    def test_readiness_endpoint(self, client):
        """Test the readiness check endpoint."""
        response = client.get("/ready")
        
        assert response.status_code == 200
        response_data = response.json()
        # The readiness check depends on actual DB and Kafka connections
        # In a real test environment, we'd mock these
        assert "status" in response_data
        assert "database" in response_data
        assert "kafka" in response_data
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["service"] == "Customer Success Digital FTE"
        assert response_data["version"] == "1.0.0"
        assert "channels" in response_data
        assert "email" in response_data["channels"]
        assert "whatsapp" in response_data["channels"]
        assert "webform" in response_data["channels"]