"""
Pydantic models for Customer entity.
Task: T015 - Implement Pydantic models for Customer, Ticket, and Message entities
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class IdentifierType(str, Enum):
    """Customer identifier types for cross-channel matching."""
    EMAIL = "email"
    PHONE = "phone"
    WHATSAPP = "whatsapp"


class CustomerIdentifier(BaseModel):
    """Customer identifier for cross-channel recognition (FR-007)."""
    id: Optional[UUID] = None
    customer_id: UUID
    identifier_type: IdentifierType
    identifier_value: str = Field(..., min_length=1, max_length=255)
    verified: bool = False
    created_at: Optional[datetime] = None

    @field_validator("identifier_value")
    @classmethod
    def validate_identifier_value(cls, v: str, info) -> str:
        """Validate identifier value based on type."""
        if not v or not v.strip():
            raise ValueError("Identifier value cannot be empty")
        return v.strip()


class Customer(BaseModel):
    """Customer entity with identity and sentiment tracking (FR-006 to FR-010)."""
    id: Optional[UUID] = None
    name: Optional[str] = Field(None, max_length=255)
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = Field(None, max_length=50)
    sentiment_score: float = Field(
        default=0.5,
        ge=-1.0,
        le=1.0,
        description="Sentiment score from -1.0 (negative) to +1.0 (positive)"
    )
    total_interactions: int = Field(default=0, ge=0)
    escalation_count: int = Field(default=0, ge=0)
    first_contact_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("sentiment_score")
    @classmethod
    def validate_sentiment(cls, v: float) -> float:
        """Ensure sentiment score is within valid range."""
        if v < -1.0 or v > 1.0:
            raise ValueError("Sentiment score must be between -1.0 and 1.0")
        return v

    @field_validator("primary_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize phone number format."""
        if v:
            # Remove common phone formatting characters
            cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
            return cleaned if cleaned else None
        return v

    @property
    def is_high_risk(self) -> bool:
        """Check if customer is high risk (negative sentiment or multiple escalations)."""
        return self.sentiment_score < 0.3 or self.escalation_count >= 2


class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""
    name: Optional[str] = Field(None, max_length=255)
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = Field(None, max_length=50)

    @field_validator("primary_email", "primary_phone")
    @classmethod
    def at_least_one_identifier(cls, v, info):
        """Ensure at least one identifier is provided."""
        # This will be validated at the service layer
        return v


class CustomerUpdate(BaseModel):
    """Schema for updating customer information."""
    name: Optional[str] = Field(None, max_length=255)
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = Field(None, max_length=50)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
