"""
Customer Success AI Agent using OpenAI Agents SDK.
Task: T029 - Create OpenAI Agents SDK agent with system prompt and tool definitions
Implements autonomous customer support across email, WhatsApp, and web form channels.
"""

import logging
from typing import Any, Dict, Optional

from agents import Agent, ModelSettings, Runner

from ..config import get_settings
from .prompts import get_full_system_prompt
from .tools import (
    create_ticket,
    escalate_ticket,
    get_customer_history,
    search_knowledge_base,
    send_email_response,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class CustomerSuccessAgent:
    """
    AI Agent for autonomous customer support.

    Features:
    - Multi-channel support (email, WhatsApp, web form)
    - Knowledge base search with semantic similarity
    - Sentiment analysis and escalation detection
    - Conversation continuity across channels
    - Automated ticket management
    """

    def __init__(self):
        """Initialize the customer success agent with tools and configuration."""
        self._agent: Optional[Agent] = None
        self._initialize_agent()

    def _initialize_agent(self):
        """Create and configure the OpenAI agent with tools."""
        try:
            # Get base system prompt
            system_prompt = get_full_system_prompt(channel="email")

            # Create agent with all tools
            self._agent = Agent(
                name="Customer Success Agent",
                instructions=system_prompt,
                model=settings.OPENAI_MODEL,
                tools=[
                    create_ticket,
                    get_customer_history,
                    search_knowledge_base,
                    send_email_response,
                    escalate_ticket,
                ],
                model_settings=ModelSettings(
                    temperature=0.7,  # Balanced creativity and consistency
                    max_tokens=1000,  # Limit response length
                ),
            )

            logger.info(f"Customer Success Agent initialized with model: {settings.OPENAI_MODEL}")

        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    async def process_message(
        self,
        customer_message: str,
        channel: str,
        customer_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        customer_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process customer message and generate response.

        Args:
            customer_message: The customer's message content
            channel: Communication channel (email, whatsapp, webform)
            customer_id: UUID of the customer (if known)
            conversation_id: UUID of the conversation (if exists)
            customer_name: Customer's name for personalization
            metadata: Additional context (e.g., email thread_id, subject)

        Returns:
            Dictionary with agent response and processing details

        Example:
            result = await agent.process_message(
                customer_message="How do I reset my password?",
                channel="email",
                customer_id="123e4567-e89b-12d3-a456-426614174000",
                customer_name="John Doe",
                metadata={
                    "subject": "Password Reset Help",
                    "thread_id": "thread_abc123"
                }
            )
        """
        try:
            # Update agent instructions with channel-specific guidelines
            channel_prompt = get_full_system_prompt(channel=channel)
            self._agent.instructions = channel_prompt

            # Build context for the agent
            context_message = f"""
New customer message received:

**Channel:** {channel}
**Customer ID:** {customer_id or 'Unknown (new customer)'}
**Customer Name:** {customer_name or 'Unknown'}
**Message:** {customer_message}

"""

            if metadata:
                context_message += "\n**Additional Context:**\n"
                for key, value in metadata.items():
                    context_message += f"- {key}: {value}\n"

            context_message += """
Please process this customer message following these steps:
1. Search the knowledge base for relevant information
2. Create a support ticket if one doesn't exist
3. Check customer history for context
4. Analyze sentiment (score -1.0 to 1.0)
5. Check for escalation triggers (pricing, refund, legal, negative sentiment, human request)
6. If escalation needed: Use escalate_ticket tool
7. If no escalation: Formulate helpful response using knowledge base information
8. Send response using the appropriate channel tool

Remember to:
- Only use information from knowledge base (no hallucinations)
- Be empathetic and professional
- Escalate when uncertain
- Include ticket reference in response
"""

            # Run agent
            logger.info(f"Processing message for customer {customer_id} on {channel}")

            result = await Runner.run(
                self._agent,
                input=context_message
            )

            # Extract agent response
            agent_response = result.final_output

            logger.info(
                f"Agent processing complete: customer={customer_id}, "
                f"channel={channel}, response_length={len(agent_response)}"
            )

            return {
                "status": "success",
                "agent_response": agent_response,
                "channel": channel,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "processing_time_ms": 0,  # TODO: Add timing
            }

        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_response": None,
                "channel": channel,
                "customer_id": customer_id
            }

    async def handle_email_message(
        self,
        customer_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
        message_id: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle inbound email message.

        Args:
            customer_email: Customer's email address
            subject: Email subject line
            body: Email body content
            thread_id: Gmail thread ID for continuity
            message_id: Gmail message ID for deduplication
            customer_name: Customer's name

        Returns:
            Processing result
        """
        metadata = {
            "email": customer_email,
            "subject": subject,
            "thread_id": thread_id,
            "message_id": message_id,
        }

        return await self.process_message(
            customer_message=body,
            channel="email",
            customer_name=customer_name,
            metadata=metadata
        )

    async def handle_whatsapp_message(
        self,
        customer_phone: str,
        message: str,
        customer_name: Optional[str] = None,
        whatsapp_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle inbound WhatsApp message.

        Args:
            customer_phone: Customer's phone number
            message: WhatsApp message content
            customer_name: Customer's name from WhatsApp profile
            whatsapp_id: WhatsApp user ID

        Returns:
            Processing result
        """
        metadata = {
            "phone": customer_phone,
            "whatsapp_id": whatsapp_id,
        }

        return await self.process_message(
            customer_message=message,
            channel="whatsapp",
            customer_name=customer_name,
            metadata=metadata
        )


# Global agent instance
customer_success_agent = CustomerSuccessAgent()


def get_agent() -> CustomerSuccessAgent:
    """Get the global customer success agent instance."""
    return customer_success_agent
