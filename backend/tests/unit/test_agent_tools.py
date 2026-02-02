"""Unit tests for agent tools."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID

from backend.src.agent.tools import (
    create_ticket,
    get_customer_history,
    search_knowledge_base,
    send_email_response,
    send_whatsapp_response,
    escalate_ticket
)


@pytest.mark.asyncio
class TestCreateTicketTool:
    """Test cases for create_ticket function."""
    
    @patch('backend.src.agent.tools.db_service')
    @patch('backend.src.agent.tools.uuid4')
    async def test_create_ticket_success(self, mock_uuid4, mock_db_service):
        """Test creating a ticket successfully."""
        # Mock UUID generation
        mock_uuid = MagicMock()
        mock_uuid.__str__.return_value = "123e4567-e89b-12d3-a456-426614174000"
        mock_uuid4.return_value = mock_uuid
        
        # Mock database response
        mock_result = {'id': mock_uuid, 'created_at': datetime.now()}
        mock_db_service.fetchrow.return_value = mock_result
        
        result = await create_ticket(
            customer_id="123e4567-e89b-12d3-a456-426614174000",
            conversation_id="123e4567-e89b-12d3-a456-426614174001",
            source_channel="email",
            category="technical",
            priority="high"
        )
        
        assert result["ticket_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert result["status"] == "open"
        assert result["category"] == "technical"
        assert result["priority"] == "high"
        
        # Verify database was called correctly
        mock_db_service.fetchrow.assert_called_once()
    
    @patch('backend.src.agent.tools.db_service')
    async def test_create_ticket_invalid_uuid(self, mock_db_service):
        """Test creating a ticket with invalid UUID."""
        result = await create_ticket(
            customer_id="invalid-uuid",
            conversation_id="123e4567-e89b-12d3-a456-426614174001",
            source_channel="email"
        )
        
        assert "error" in result
        assert result["ticket_id"] is None


@pytest.mark.asyncio
class TestGetCustomerHistoryTool:
    """Test cases for get_customer_history function."""
    
    @patch('backend.src.agent.tools.db_service')
    async def test_get_customer_history_success(self, mock_db_service):
        """Test retrieving customer history successfully."""
        # Mock customer data
        mock_customer = {
            'id': UUID('123e4567-e89b-12d3-a456-426614174000'),
            'name': 'John Doe',
            'primary_email': 'john@example.com',
            'primary_phone': '+1234567890',
            'sentiment_score': 0.8,
            'total_interactions': 5,
            'escalation_count': 0
        }
        
        # Mock tickets data
        mock_tickets = [
            {
                'id': UUID('123e4567-e89b-12d3-a456-426614174001'),
                'source_channel': 'email',
                'category': 'technical',
                'status': 'resolved',
                'created_at': datetime.now()
            }
        ]
        
        # Mock messages data
        mock_messages = [
            {
                'id': UUID('123e4567-e89b-12d3-a456-426614174002'),
                'channel': 'email',
                'direction': 'inbound',
                'content': 'Help with account',
                'created_at': datetime.now(),
                'conversation_id': UUID('123e4567-e89b-12d3-a456-426614174001')
            }
        ]
        
        # Setup mock return values
        mock_db_service.fetchrow.return_value = mock_customer
        mock_db_service.fetch.side_effect = [mock_tickets, mock_messages]
        
        result = await get_customer_history(
            customer_id="123e4567-e89b-12d3-a456-426614174000",
            limit=10
        )
        
        assert "customer" in result
        assert result["customer"]["name"] == "John Doe"
        assert len(result["recent_tickets"]) == 1
        assert len(result["recent_messages"]) == 1
        
        # Verify database was called correctly
        assert mock_db_service.fetchrow.call_count == 1
        assert mock_db_service.fetch.call_count == 2
    
    @patch('backend.src.agent.tools.db_service')
    async def test_get_customer_history_not_found(self, mock_db_service):
        """Test retrieving customer history for non-existent customer."""
        mock_db_service.fetchrow.return_value = None
        
        result = await get_customer_history(
            customer_id="123e4567-e89b-12d3-a456-426614174000",
            limit=10
        )
        
        assert result["error"] == "Customer not found"


@pytest.mark.asyncio
class TestSearchKnowledgeBaseTool:
    """Test cases for search_knowledge_base function."""
    
    @patch('backend.src.agent.tools.OpenAI')
    @patch('backend.src.agent.tools.get_settings')
    @patch('backend.src.agent.tools.db_service')
    async def test_search_knowledge_base_success(self, mock_db_service, mock_get_settings, mock_openai_class):
        """Test searching knowledge base successfully."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
        mock_get_settings.return_value = mock_settings
        
        # Mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock()]
        mock_embedding_response.data[0].embedding = [0.1, 0.2, 0.3]  # Mock embedding
        mock_openai_instance.embeddings.create.return_value = mock_embedding_response
        mock_openai_class.return_value = mock_openai_instance
        
        # Mock database response
        mock_results = [
            {
                'id': UUID('123e4567-e89b-12d3-a456-426614174000'),
                'title': 'Account Help',
                'content': 'Information about account management',
                'category': 'account',
                'similarity_score': 0.85
            }
        ]
        mock_db_service.fetch.return_value = mock_results
        
        result = await search_knowledge_base("account help", max_results=5)
        
        assert result["count"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Account Help"
        assert result["results"][0]["similarity_score"] == 0.85
        
        # Verify database was called correctly
        mock_db_service.fetch.assert_called_once()
    
    @patch('backend.src.agent.tools.OpenAI')
    @patch('backend.src.agent.tools.get_settings')
    @patch('backend.src.agent.tools.db_service')
    async def test_search_knowledge_base_no_results(self, mock_db_service, mock_get_settings, mock_openai_class):
        """Test searching knowledge base with no results."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
        mock_get_settings.return_value = mock_settings
        
        # Mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock()]
        mock_embedding_response.data[0].embedding = [0.1, 0.2, 0.3]  # Mock embedding
        mock_openai_instance.embeddings.create.return_value = mock_embedding_response
        mock_openai_class.return_value = mock_openai_instance
        
        # Mock database response - no results
        mock_db_service.fetch.return_value = []
        
        result = await search_knowledge_base("nonexistent topic", max_results=5)
        
        assert result["count"] == 0
        assert len(result["results"]) == 0
        assert "No relevant documentation found" in result["message"]


@pytest.mark.asyncio
class TestSendWhatsAppResponseTool:
    """Test cases for send_whatsapp_response function."""
    
    @patch('backend.src.agent.tools.WhatsAppResponseFormatter')
    @patch('backend.src.agent.tools.twilio_client')
    async def test_send_whatsapp_response_success(self, mock_twilio_client, mock_formatter):
        """Test sending WhatsApp response successfully."""
        # Mock formatter
        mock_formatter.add_escalation_offer.return_value = "Original content with escalation offer"
        mock_formatter.format_response.return_value = ["Formatted message"]
        
        # Mock Twilio response
        mock_twilio_response = {"message_sid": "SMtest1234567890abcdef1234567890ab"}
        mock_twilio_client.send_whatsapp_message.return_value = mock_twilio_response
        
        result = await send_whatsapp_response(
            customer_phone="+1234567890",
            content="Hello, how can I help you?",
            ticket_id="123e4567-e89b-12d3-a456-426614174000",
            add_escalation_offer=True
        )
        
        assert result["status"] == "sent"
        assert result["message_count"] == 1
        assert len(result["message_sids"]) == 1
        assert result["recipient"] == "+1234567890"
        
        # Verify formatter was called
        mock_formatter.add_escalation_offer.assert_called_once()
        mock_formatter.format_response.assert_called_once()
        
        # Verify Twilio was called
        mock_twilio_client.send_whatsapp_message.assert_called_once()
    
    @patch('backend.src.agent.tools.WhatsAppResponseFormatter')
    @patch('backend.src.agent.tools.twilio_client')
    async def test_send_whatsapp_response_failure(self, mock_twilio_client, mock_formatter):
        """Test sending WhatsApp response with failure."""
        # Mock formatter
        mock_formatter.add_escalation_offer.return_value = "Original content with escalation offer"
        mock_formatter.format_response.return_value = ["Formatted message"]
        
        # Mock Twilio to raise exception
        mock_twilio_client.send_whatsapp_message.side_effect = Exception("Twilio error")
        
        result = await send_whatsapp_response(
            customer_phone="+1234567890",
            content="Hello, how can I help you?",
            ticket_id="123e4567-e89b-12d3-a456-426614174000",
            add_escalation_offer=False
        )
        
        assert result["status"] == "failed"
        assert "Twilio error" in result["error"]
        assert result["recipient"] == "+1234567890"


@pytest.mark.asyncio
class TestEscalateTicketTool:
    """Test cases for escalate_ticket function."""
    
    @patch('backend.src.agent.tools.db_service')
    @patch('backend.src.agent.tools.kafka_producer')
    async def test_escalate_ticket_success(self, mock_kafka_producer, mock_db_service):
        """Test escalating ticket successfully."""
        # Mock UUID conversion
        from uuid import UUID
        mock_ticket_uuid = UUID('123e4567-e89b-12d3-a456-426614174000')
        
        # Mock database responses
        mock_updated_ticket = {
            'id': mock_ticket_uuid,
            'customer_id': UUID('123e4567-e89b-12d3-a456-426614174001'),
            'conversation_id': UUID('123e4567-e89b-12d3-a456-426614174002')
        }
        mock_db_service.fetchrow.return_value = mock_updated_ticket
        
        mock_ticket_context = {
            'customer_id': UUID('123e4567-e89b-12d3-a456-426614174001'),
            'name': 'John Doe',
            'primary_email': 'john@example.com',
            'sentiment_score': 0.2,
            'source_channel': 'email',
            'category': 'billing',
            'conversation_id': UUID('123e4567-e89b-12d3-a456-426614174002')
        }
        mock_db_service.fetchrow.side_effect = [mock_updated_ticket, mock_ticket_context]
        
        mock_messages = [
            {
                'channel': 'email',
                'direction': 'inbound',
                'role': 'customer',
                'content': 'I have a billing issue',
                'created_at': datetime.now()
            }
        ]
        mock_db_service.fetch.return_value = mock_messages
        
        # Mock Kafka producer
        mock_kafka_producer.publish.return_value = UUID('123e4567-e89b-12d3-a456-426614174003')
        
        result = await escalate_ticket(
            ticket_id="123e4567-e89b-12d3-a456-426614174000",
            reason="billing_issue",
            context='{"issue": "refund request"}',
            priority="high"
        )
        
        assert result["status"] == "escalated"
        assert result["ticket_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert result["reason"] == "billing_issue"
        assert result["priority"] == "high"
        
        # Verify database updates were called
        assert mock_db_service.execute.call_count >= 1  # At least the customer update