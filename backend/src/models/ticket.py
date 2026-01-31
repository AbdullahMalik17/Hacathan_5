"""
Pydantic models for Ticket entity.
Task: T015 - Implement Pydantic models for Customer, Ticket, and Message entities
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TicketCategory(str, Enum):
    """Ticket categories for classification (FR-013)."""
    GENERAL = "general"
    TECHNICAL = "technical"
    BILLING = "billing"
    FEEDBACK = "feedback"
    BUG_REPORT = "bug_report"


class TicketPriority(str, Enum):
    """Ticket priority levels (FR-014)."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, Enum):
    """Ticket status values (FR-012)."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class SourceChannel(str, Enum):
    """Communication channels (FR-001)."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEBFORM = "webform"


class Ticket(BaseModel):
    """Ticket entity for support request tracking (FR-011 to FR-015)."""
    id: Optional[UUID] = None
    conversation_id: UUID
    customer_id: UUID
    source_channel: SourceChannel
    category: TicketCategory = TicketCategory.GENERAL
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    escalation_reason: Optional[str] = Field(None, max_length=100)
    resolution_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("escalation_reason")
    @classmethod
    def validate_escalation(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure escalation reason is provided for escalated tickets."""
        # This will be enforced at the service layer
        return v

    @property
    def is_escalated(self) -> bool:
        """Check if ticket is escalated."""
        return self.status == TicketStatus.ESCALATED

    @property
    def is_high_priority(self) -> bool:
        """Check if ticket requires urgent attention."""
        return self.priority == TicketPriority.HIGH


class TicketCreate(BaseModel):
    """Schema for creating a new ticket."""
    conversation_id: UUID
    customer_id: UUID
    source_channel: SourceChannel
    category: TicketCategory = TicketCategory.GENERAL
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketUpdate(BaseModel):
    """Schema for updating ticket information."""
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    escalation_reason: Optional[str] = Field(None, max_length=100)
    resolution_notes: Optional[str] = None


class TicketEscalate(BaseModel):
    """Schema for escalating a ticket (FR-025 to FR-030)."""
    reason: str = Field(..., min_length=1, max_length=100)
    context: Optional[dict] = None  # Full conversation context for human team

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Ensure escalation reason is not empty."""
        if not v.strip():
            raise ValueError("Escalation reason cannot be empty")
        return v.strip()


class TicketResponse(BaseModel):
    """Response model for ticket details (FR-036)."""
    id: UUID
    conversation_id: UUID
    customer_id: UUID
    source_channel: SourceChannel
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    escalation_reason: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    messages_count: int = 0  # Number of messages in ticket
