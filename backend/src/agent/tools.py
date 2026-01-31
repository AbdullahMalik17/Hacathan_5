"""
Agent function tools using OpenAI Agents SDK.
Tasks: T030-T034 - Implement agent tools for ticket management, customer history, KB search, responses, and escalation
Supports: FR-007, FR-008, FR-011, FR-012, FR-016-FR-020, FR-024, FR-025-FR-030
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from agents import function_tool

from ..models import (
    MessageChannel,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStatus,
)
from ..services.channels.gmail_client import gmail_client
from ..services.database import db_service
from ..services.kafka_producer import kafka_producer
from .formatters import EmailResponseFormatter

logger = logging.getLogger(__name__)


# ============================================================================
# T030: Create Ticket Tool (FR-011, FR-012)
# ============================================================================

@function_tool
async def create_ticket(
    customer_id: str,
    conversation_id: str,
    source_channel: str,
    category: str = "general",
    priority: str = "medium"
) -> Dict[str, Any]:
    """Create a support ticket for the customer.

    Args:
        customer_id: UUID of the customer
        conversation_id: UUID of the conversation
        source_channel: Channel source (email, whatsapp, webform)
        category: Ticket category (general, technical, billing, feedback, bug_report)
        priority: Ticket priority (low, medium, high)

    Returns:
        Dictionary with ticket details including ticket_id
    """
    try:
        # Validate UUIDs
        customer_uuid = UUID(customer_id)
        conversation_uuid = UUID(conversation_id)

        # Create ticket in database
        ticket_id = uuid4()

        query = """
            INSERT INTO tickets (
                id, conversation_id, customer_id, source_channel,
                category, priority, status, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            RETURNING id, created_at
        """

        result = await db_service.fetchrow(
            query,
            ticket_id,
            conversation_uuid,
            customer_uuid,
            source_channel,
            category,
            priority,
            "open"
        )

        logger.info(f"Ticket created: {ticket_id} for customer {customer_id}")

        return {
            "ticket_id": str(result['id']),
            "status": "open",
            "category": category,
            "priority": priority,
            "created_at": result['created_at'].isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        return {"error": str(e), "ticket_id": None}


# ============================================================================
# T031: Get Customer History Tool (FR-007, FR-008)
# ============================================================================

@function_tool
async def get_customer_history(customer_id: str, limit: int = 10) -> Dict[str, Any]:
    """Retrieve customer's past interactions and tickets across all channels.

    Args:
        customer_id: UUID of the customer
        limit: Maximum number of recent interactions to return

    Returns:
        Dictionary with customer history including past tickets and messages
    """
    try:
        customer_uuid = UUID(customer_id)

        # Get customer info
        customer_query = """
            SELECT id, name, primary_email, primary_phone,
                   sentiment_score, total_interactions, escalation_count
            FROM customers
            WHERE id = $1
        """
        customer = await db_service.fetchrow(customer_query, customer_uuid)

        if not customer:
            return {"error": "Customer not found"}

        # Get recent tickets
        tickets_query = """
            SELECT id, source_channel, category, priority, status,
                   created_at, resolved_at
            FROM tickets
            WHERE customer_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        tickets = await db_service.fetch(tickets_query, customer_uuid, limit)

        # Get recent messages across all channels
        messages_query = """
            SELECT m.id, m.channel, m.direction, m.content,
                   m.created_at, c.id as conversation_id
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.customer_id = $1
            ORDER BY m.created_at DESC
            LIMIT $2
        """
        messages = await db_service.fetch(messages_query, customer_uuid, limit)

        history = {
            "customer": {
                "id": str(customer['id']),
                "name": customer['name'],
                "email": customer['primary_email'],
                "phone": customer['primary_phone'],
                "sentiment_score": customer['sentiment_score'],
                "total_interactions": customer['total_interactions'],
                "escalation_count": customer['escalation_count']
            },
            "recent_tickets": [
                {
                    "id": str(t['id']),
                    "channel": t['source_channel'],
                    "category": t['category'],
                    "status": t['status'],
                    "created": t['created_at'].isoformat()
                }
                for t in tickets
            ],
            "recent_messages": [
                {
                    "channel": m['channel'],
                    "direction": m['direction'],
                    "content": m['content'][:100] + "..." if len(m['content']) > 100 else m['content'],
                    "timestamp": m['created_at'].isoformat()
                }
                for m in messages
            ]
        }

        logger.info(f"Retrieved history for customer {customer_id}: {len(tickets)} tickets, {len(messages)} messages")

        return history

    except Exception as e:
        logger.error(f"Failed to get customer history: {e}")
        return {"error": str(e)}


# ============================================================================
# T032: Search Knowledge Base Tool (FR-016, FR-017, FR-018)
# ============================================================================

@function_tool
async def search_knowledge_base(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search product documentation using semantic search with pgvector.

    Args:
        query: Search query text
        max_results: Maximum number of results to return (default 5)

    Returns:
        Dictionary with search results and similarity scores
    """
    try:
        # Generate embedding for query using OpenAI
        from openai import OpenAI
        from ..config import get_settings

        settings = get_settings()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Generate query embedding
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=query
        )
        query_embedding = response.data[0].embedding

        # Search knowledge base using pgvector cosine similarity
        search_query = """
            SELECT id, title, content, category,
                   1 - (embedding <=> $1::vector) AS similarity_score
            FROM knowledge_base
            WHERE 1 - (embedding <=> $1::vector) >= $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
        """

        # Use similarity threshold of 0.6 (FR-018)
        similarity_threshold = 0.6

        results = await db_service.fetch(
            search_query,
            query_embedding,
            similarity_threshold,
            max_results
        )

        if not results:
            logger.warning(f"No knowledge base results found for query: {query}")
            return {
                "results": [],
                "count": 0,
                "message": "No relevant documentation found. Consider escalating to human support."
            }

        formatted_results = [
            {
                "title": r['title'],
                "content": r['content'],
                "category": r['category'],
                "similarity_score": float(r['similarity_score']),
                "relevance": "high" if r['similarity_score'] >= 0.7 else "moderate"
            }
            for r in results
        ]

        logger.info(f"Knowledge base search: query='{query}', found {len(results)} results")

        return {
            "results": formatted_results,
            "count": len(results),
            "query": query
        }

    except Exception as e:
        logger.error(f"Failed to search knowledge base: {e}")
        return {
            "error": str(e),
            "results": [],
            "message": "Knowledge base search failed. Escalating to human support."
        }


# ============================================================================
# T033: Send Email Response Tool (FR-020, FR-024)
# ============================================================================

@function_tool
async def send_email_response(
    customer_email: str,
    content: str,
    customer_name: Optional[str] = None,
    ticket_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    original_subject: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None
) -> Dict[str, Any]:
    """Send formatted email response to customer.

    Args:
        customer_email: Customer's email address
        content: Response content from agent
        customer_name: Customer's name for personalized greeting
        ticket_id: Ticket reference ID
        thread_id: Gmail thread ID for conversation continuity
        original_subject: Original email subject for reply
        in_reply_to: Message-ID being replied to
        references: References header for threading

    Returns:
        Dictionary with send status and message ID
    """
    try:
        # Format response using email formatter (T028)
        ticket_uuid = UUID(ticket_id) if ticket_id else None
        html_body, text_body = EmailResponseFormatter.format_response(
            content=content,
            customer_name=customer_name,
            ticket_id=ticket_uuid,
            subject=original_subject
        )

        # Format subject line
        subject = EmailResponseFormatter.format_reply_subject(original_subject or "Your Support Request")

        # Send email via Gmail API
        sent_message = await gmail_client.send_email(
            to_email=customer_email,
            subject=subject,
            body_html=html_body,
            body_text=text_body,
            thread_id=thread_id,
            in_reply_to=in_reply_to,
            references=references
        )

        logger.info(f"Email sent: to={customer_email}, message_id={sent_message.get('id')}")

        return {
            "status": "sent",
            "message_id": sent_message.get('id'),
            "thread_id": sent_message.get('threadId'),
            "recipient": customer_email
        }

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "recipient": customer_email
        }


# ============================================================================
# T034: Escalate Ticket Tool (FR-019, FR-025-FR-030)
# ============================================================================

@function_tool
async def escalate_ticket(
    ticket_id: str,
    reason: str,
    context: Optional[str] = None,
    priority: str = "high"
) -> Dict[str, Any]:
    """Escalate ticket to human support team.

    Args:
        ticket_id: UUID of the ticket to escalate
        reason: Escalation reason (pricing_inquiry, refund_request, legal_matter,
                negative_sentiment, explicit_human_request, no_documentation_found)
        context: Additional context as JSON string including conversation history and customer sentiment
        priority: Escalation priority (high or urgent)

    Returns:
        Dictionary with escalation status
    """
    try:
        ticket_uuid = UUID(ticket_id)
        
        # Parse context if provided
        import json
        context_data = {}
        if context:
            try:
                context_data = json.loads(context)
            except Exception:
                logger.warning("Failed to parse escalation context JSON")

        # Update ticket status to escalated
        update_query = """
            UPDATE tickets
            SET status = 'escalated',
                escalation_reason = $1,
                priority = $2,
                updated_at = NOW()
            WHERE id = $3
            RETURNING id, customer_id, conversation_id
        """

        ticket = await db_service.fetchrow(
            update_query,
            reason,
            priority,
            ticket_uuid
        )

        if not ticket:
            return {"error": "Ticket not found"}

        # Get full ticket context
        context_query = """
            SELECT
                c.id as customer_id,
                c.name,
                c.primary_email,
                c.sentiment_score,
                t.source_channel,
                t.category,
                conv.id as conversation_id
            FROM tickets t
            JOIN customers c ON t.customer_id = c.id
            JOIN conversations conv ON t.conversation_id = conv.id
            WHERE t.id = $1
        """
        ticket_context = await db_service.fetchrow(context_query, ticket_uuid)

        # Get conversation messages
        messages_query = """
            SELECT channel, direction, role, content, created_at
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
        """
        messages = await db_service.fetch(messages_query, UUID(str(ticket_context['conversation_id'])))

        # Build escalation payload
        escalation_payload = {
            "ticket_id": str(ticket_uuid),
            "escalation_reason": reason,
            "priority": priority,
            "customer": {
                "id": str(ticket_context['customer_id']),
                "name": ticket_context['name'],
                "email": ticket_context['primary_email'],
                "sentiment_score": ticket_context['sentiment_score']
            },
            "ticket_info": {
                "channel": ticket_context['source_channel'],
                "category": ticket_context['category']
            },
            "conversation_history": [
                {
                    "channel": m['channel'],
                    "direction": m['direction'],
                    "role": m['role'],
                    "content": m['content'],
                    "timestamp": m['created_at'].isoformat()
                }
                for m in messages
            ],
            "escalated_at": datetime.utcnow().isoformat(),
            "additional_context": context_data
        }

        # Publish escalation to Kafka topic (FR-030)
        correlation_id = await kafka_producer.publish(
            topic="fte.escalations",
            message=escalation_payload,
            key=f"ticket-{ticket_id}"
        )

        # Update customer escalation count
        await db_service.execute(
            "UPDATE customers SET escalation_count = escalation_count + 1 WHERE id = $1",
            UUID(str(ticket_context['customer_id']))
        )

        logger.info(
            f"Ticket escalated: ticket_id={ticket_id}, reason={reason}, "
            f"correlation_id={correlation_id}"
        )

        return {
            "status": "escalated",
            "ticket_id": str(ticket_uuid),
            "reason": reason,
            "priority": priority,
            "correlation_id": str(correlation_id),
            "message": "Ticket has been escalated to our support team. They will contact you within 2 hours."
        }

    except Exception as e:
        logger.error(f"Failed to escalate ticket: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "ticket_id": ticket_id
        }
