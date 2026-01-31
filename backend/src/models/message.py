"""
Pydantic models for Message entity.
Task: T015 - Implement Pydantic models for Customer, Ticket, and Message entities
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MessageChannel(str, Enum):
    """Communication channels for messages (FR-001)."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEBFORM = "webform"


class MessageDirection(str, Enum):
    """Message direction (inbound from customer or outbound to customer)."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageRole(str, Enum):
    """Message sender role."""
    CUSTOMER = "customer"
    AGENT = "agent"
    SYSTEM = "system"


class DeliveryStatus(str, Enum):
    """Message delivery status (FR-034)."""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(BaseModel):
    """Message entity for storing all communications (FR-015)."""
    id: Optional[UUID] = None
    conversation_id: UUID
    channel: MessageChannel
    direction: MessageDirection
    role: MessageRole
    content: str = Field(..., min_length=1)
    channel_message_id: Optional[str] = Field(
        None,
        max_length=255,
        description="External message ID for deduplication (FR-004)"
    )
    correlation_id: Optional[UUID] = None
    delivery_status: Optional[DeliveryStatus] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure message content is not empty."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure metadata is a valid dict."""
        if v is None:
            return {}
        return v

    @property
    def is_inbound(self) -> bool:
        """Check if message is from customer."""
        return self.direction == MessageDirection.INBOUND

    @property
    def is_outbound(self) -> bool:
        """Check if message is to customer."""
        return self.direction == MessageDirection.OUTBOUND


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    conversation_id: UUID
    channel: MessageChannel
    direction: MessageDirection
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=10000)
    channel_message_id: Optional[str] = Field(None, max_length=255)
    correlation_id: Optional[UUID] = None
    delivery_status: Optional[DeliveryStatus] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageUpdate(BaseModel):
    """Schema for updating message delivery status."""
    delivery_status: Optional[DeliveryStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class InboundMessage(BaseModel):
    """Schema for incoming messages from webhooks (FR-003, FR-004, FR-005)."""
    channel: MessageChannel
    customer_identifier: str = Field(..., description="Email or phone number")
    content: str = Field(..., min_length=1, max_length=10000)
    channel_message_id: str = Field(..., description="External message ID for deduplication")
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("customer_identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """Ensure customer identifier is not empty."""
        if not v or not v.strip():
            raise ValueError("Customer identifier cannot be empty")
        return v.strip()


class OutboundMessage(BaseModel):
    """Schema for outbound messages to customers (FR-020 to FR-024)."""
    channel: MessageChannel
    customer_id: UUID
    content: str = Field(..., min_length=1)
    correlation_id: UUID
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, v: str, info) -> str:
        """Validate content length based on channel."""
        # WhatsApp preferred length is 300 chars (FR-033)
        # This is a preference, not a hard limit
        return v.strip()
