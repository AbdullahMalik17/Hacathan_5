"""
Pydantic models for Customer Success Digital FTE.
Exports all entity models for easy importing.
"""

from .customer import (
    Customer,
    CustomerCreate,
    CustomerIdentifier,
    CustomerUpdate,
    IdentifierType,
)
from .message import (
    DeliveryStatus,
    InboundMessage,
    Message,
    MessageChannel,
    MessageCreate,
    MessageDirection,
    MessageRole,
    MessageUpdate,
    OutboundMessage,
)
from .ticket import (
    SourceChannel,
    Ticket,
    TicketCategory,
    TicketCreate,
    TicketEscalate,
    TicketPriority,
    TicketResponse,
    TicketStatus,
    TicketUpdate,
)

__all__ = [
    # Customer models
    "Customer",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerIdentifier",
    "IdentifierType",
    # Ticket models
    "Ticket",
    "TicketCreate",
    "TicketUpdate",
    "TicketEscalate",
    "TicketResponse",
    "TicketCategory",
    "TicketPriority",
    "TicketStatus",
    "SourceChannel",
    # Message models
    "Message",
    "MessageCreate",
    "MessageUpdate",
    "InboundMessage",
    "OutboundMessage",
    "MessageChannel",
    "MessageDirection",
    "MessageRole",
    "DeliveryStatus",
]
