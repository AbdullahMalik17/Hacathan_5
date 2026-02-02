"""Test configuration and fixtures for Customer Success Digital FTE."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from backend.src.main import app
from backend.src.services.database import DatabaseService
from backend.src.services.kafka_producer import KafkaProducerService


@pytest.fixture
def mock_db_service():
    """Mock database service for testing."""
    mock = AsyncMock(spec=DatabaseService)
    
    # Mock common database methods
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock.fetchrow = AsyncMock()
    mock.fetch = AsyncMock()
    mock.execute = AsyncMock()
    
    return mock


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer service for testing."""
    mock = MagicMock(spec=KafkaProducerService)
    mock.connect = MagicMock()
    mock.disconnect = MagicMock()
    mock.publish = AsyncMock(return_value="test-correlation-id")
    
    return mock


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "sentiment_score": 0.8,
        "total_interactions": 5
    }


@pytest.fixture
def sample_ticket_data():
    """Sample ticket data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "conversation_id": "123e4567-e89b-12d3-a456-426614174002",
        "customer_id": "123e4567-e89b-12d3-a456-426614174000",
        "source_channel": "email",
        "category": "technical",
        "priority": "medium",
        "status": "open"
    }


@pytest.fixture
def sample_email_webhook_data():
    """Sample Gmail webhook data for testing."""
    return {
        "message": {
            "data": "eydleGFtcGxlJzogJ2RhdGEnfQ==",  # base64 encoded '{"example": "data"}'
            "messageId": "test-message-id",
            "publishTime": "2026-01-01T12:00:00Z"
        },
        "subscription": "projects/test-project/subscriptions/gmail-sub"
    }


@pytest.fixture
def sample_whatsapp_webhook_data():
    """Sample WhatsApp webhook data for testing."""
    return {
        "MessageSid": "SMtest1234567890abcdef1234567890ab",
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+10987654321",
        "Body": "Hello, I need help with my account.",
        "ProfileName": "John Doe",
        "WaId": "1234567890",
        "NumMedia": "0"
    }