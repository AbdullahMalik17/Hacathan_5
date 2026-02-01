"""
Response formatters for different channels with channel-specific formatting.
Task: T028 - Implement email response formatter with formal tone, greeting, signature, ticket reference
Supports: FR-021, FR-031, FR-032, FR-033, FR-034
"""

import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class EmailResponseFormatter:
    """
    Format agent responses for email channel.

    Requirements (FR-031):
    - Professional, formal tone
    - Proper greeting
    - Detailed answer
    - Professional signature
    - Ticket reference
    """

    @staticmethod
    def format_response(
        content: str,
        customer_name: Optional[str] = None,
        ticket_id: Optional[UUID] = None,
        subject: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Format agent response for email delivery.

        Args:
            content: Agent's response content
            customer_name: Customer's name for personalized greeting
            ticket_id: Ticket ID for reference
            subject: Original email subject for reply subject line

        Returns:
            Tuple of (html_body, text_body)

        Example:
            html, text = EmailResponseFormatter.format_response(
                content="Here are the password reset instructions...",
                customer_name="John Doe",
                ticket_id=uuid4(),
                subject="Password Reset Help"
            )
        """
        # Greeting (FR-031)
        if customer_name:
            greeting = f"Dear {customer_name},"
        else:
            greeting = "Hello,"

        # Ticket reference (FR-022)
        ticket_ref = ""
        if ticket_id:
            ticket_ref = f"\n\n**Ticket Reference:** {ticket_id}\n"

        # Professional signature (FR-031)
        signature = """
Best regards,

Customer Success Team
support@company.com

---
This is an automated response from our AI support agent.
If you need further assistance, please reply to this email.
"""

        # Generate plain text version
        text_body = f"""{greeting}

{content}
{ticket_ref}
{signature}
"""

        # Generate HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .greeting {{
            margin-bottom: 20px;
        }}
        .content {{
            margin-bottom: 30px;
            white-space: pre-wrap;
        }}
        .ticket-ref {{
            background-color: #f5f5f5;
            padding: 10px;
            border-left: 4px solid #007bff;
            margin: 20px 0;
        }}
        .signature {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="greeting">{greeting}</div>

    <div class="content">{content}</div>

    {f'<div class="ticket-ref"><strong>Ticket Reference:</strong> {ticket_id}</div>' if ticket_id else ''}

    <div class="signature">
        <p>Best regards,<br><br>
        <strong>Customer Success Team</strong><br>
        support@company.com</p>
    </div>

    <div class="footer">
        This is an automated response from our AI support agent.
        If you need further assistance, please reply to this email.
    </div>
</body>
</html>
"""

        logger.info(f"Formatted email response: length={len(content)} chars, ticket_id={ticket_id}")

        return html_body.strip(), text_body.strip()

    @staticmethod
    def format_reply_subject(original_subject: str) -> str:
        """
        Format reply subject line.

        Args:
            original_subject: Original email subject

        Returns:
            Reply subject with "Re:" prefix if not already present
        """
        if not original_subject:
            return "Re: Your Support Request"

        # Add Re: if not already present
        if not original_subject.lower().startswith("re:"):
            return f"Re: {original_subject}"

        return original_subject


class WhatsAppResponseFormatter:
    """
    Format agent responses for WhatsApp channel.

    Requirements (FR-033, FR-034):
    - Conversational tone
    - Under 300 characters preferred
    - Split longer messages at sentence boundaries
    - Track delivery status
    """

    @staticmethod
    def format_response(
        content: str,
        max_length: int = 300
    ) -> list[str]:
        """
        Format agent response for WhatsApp delivery.

        Args:
            content: Agent's response content
            max_length: Maximum length per message (default 300)

        Returns:
            List of message chunks (may be split if content is too long)

        Example:
            messages = WhatsAppResponseFormatter.format_response(
                content="Our business hours are Monday-Friday 9AM-6PM. "
                        "You can reach us via email at support@company.com.",
                max_length=300
            )
            # Returns: ["Our business hours are Monday-Friday 9AM-6PM. "
            #           "You can reach us via email at support@company.com."]
        """
        # If content fits in one message, return as-is
        if len(content) <= max_length:
            return [content]

        # Split into sentences
        import re
        sentences = re.split(r'(?<=[.!?])\s+', content)

        messages = []
        current_message = ""

        for sentence in sentences:
            # If single sentence is longer than max_length, force split
            if len(sentence) > max_length:
                if current_message:
                    messages.append(current_message.strip())
                    current_message = ""

                # Split long sentence at word boundaries
                words = sentence.split()
                for word in words:
                    if len(current_message) + len(word) + 1 <= max_length:
                        current_message += " " + word if current_message else word
                    else:
                        messages.append(current_message.strip())
                        current_message = word
            else:
                # Try to add sentence to current message
                test_message = current_message + " " + sentence if current_message else sentence

                if len(test_message) <= max_length:
                    current_message = test_message
                else:
                    # Current message is full, start new one
                    if current_message:
                        messages.append(current_message.strip())
                    current_message = sentence

        # Add remaining content
        if current_message:
            messages.append(current_message.strip())

        logger.info(f"Formatted WhatsApp response: {len(messages)} message(s), total length={len(content)}")

        return messages

    @staticmethod
    def add_escalation_offer(content: str) -> str:
        """
        Add human escalation offer to WhatsApp message (FR-023).

        Args:
            content: Message content

        Returns:
            Content with escalation offer appended
        """
        escalation_text = "\n\nReply 'human' if you'd like to speak with our team."
        return content + escalation_text


class WebFormResponseFormatter:
    """
    Format agent responses for web form channel.

    Requirements:
    - Semi-formal tone
    - Maximum 300 words
    - Clear and concise
    """

    @staticmethod
    def format_response(
        content: str,
        ticket_id: Optional[UUID] = None
    ) -> str:
        """
        Format agent response for web form delivery.

        Args:
            content: Agent's response content
            ticket_id: Ticket ID for reference

        Returns:
            Formatted response

        Example:
            response = WebFormResponseFormatter.format_response(
                content="Here's how to track your order...",
                ticket_id=uuid4()
            )
        """
        # Add ticket reference if provided
        if ticket_id:
            content = f"{content}\n\n**Ticket Reference:** {ticket_id}"

        # Truncate to reasonable length (approximate 300 words = 1800 characters)
        max_chars = 1800
        if len(content) > max_chars:
            content = content[:max_chars] + "..."
            logger.warning(f"Web form response truncated to {max_chars} characters")

        return content


# ============================================================================
# Task T089: Escalation acknowledgment response templates per channel
# ============================================================================

class EscalationFormatter:
    """
    Format escalation acknowledgment messages per channel.

    Requirements: FR-025-FR-030
    """

    @staticmethod
    def format_email_escalation(reason: str, ticket_id: Optional[UUID] = None) -> str:
        """
        Format escalation acknowledgment for email channel.

        Args:
            reason: Escalation reason
            ticket_id: Ticket reference ID

        Returns:
            Formatted email escalation message
        """
        reason_messages = {
            "pricing_inquiry": "pricing-related questions require review by our sales team",
            "refund_request": "refund requests are handled by our billing department",
            "legal_matter": "legal matters require immediate attention from our legal team",
            "negative_sentiment": "we take your concerns very seriously",
            "explicit_human_request": "you've requested to speak with a team member",
            "no_documentation_found": "your inquiry requires specialized expertise",
            "profanity_aggressive_language": "we want to ensure you receive the best possible support",
        }

        message_detail = reason_messages.get(reason, "your request requires specialized attention")

        ticket_ref = f"\n\n**Ticket Reference:** {ticket_id}" if ticket_id else ""

        return f"""Your request has been escalated to our support team.

{message_detail.capitalize()}, so I've forwarded your request to a specialist who will contact you within 2 hours.

You will receive an email from our team shortly with next steps.{ticket_ref}

Thank you for your patience."""

    @staticmethod
    def format_whatsapp_escalation(reason: str) -> str:
        """
        Format escalation acknowledgment for WhatsApp channel.

        Args:
            reason: Escalation reason

        Returns:
            Formatted WhatsApp escalation message (concise)
        """
        reason_messages = {
            "pricing_inquiry": "I've escalated your pricing question to our sales team.",
            "refund_request": "I've escalated your refund request to our billing team.",
            "legal_matter": "I've escalated this to our legal team immediately.",
            "negative_sentiment": "I've escalated your concern to a senior agent.",
            "explicit_human_request": "I've connected you with our support team.",
            "no_documentation_found": "I've escalated this to a specialist.",
            "profanity_aggressive_language": "I've escalated your request to our team.",
        }

        message = reason_messages.get(reason, "I've escalated your request to our team.")

        return f"{message} Someone will reach out within 2 hours. Thanks for your patience!"

    @staticmethod
    def format_webform_escalation(reason: str, ticket_id: Optional[UUID] = None) -> str:
        """
        Format escalation acknowledgment for web form channel.

        Args:
            reason: Escalation reason
            ticket_id: Ticket reference ID

        Returns:
            Formatted web form escalation message
        """
        reason_messages = {
            "pricing_inquiry": "Pricing questions are handled by our sales team",
            "refund_request": "Refund requests are processed by our billing department",
            "legal_matter": "Legal matters receive immediate attention from our legal team",
            "negative_sentiment": "Your concerns are being reviewed by a senior agent",
            "explicit_human_request": "You've been connected with our support team",
            "no_documentation_found": "Your inquiry requires specialized expertise",
            "profanity_aggressive_language": "Your request is being handled by our support team",
        }

        message_detail = reason_messages.get(reason, "Your request requires specialized attention")

        ticket_ref = f"\n\n**Ticket Reference:** {ticket_id}" if ticket_id else ""

        return f"""**Request Escalated**

{message_detail}. A specialist will contact you within 2 hours via email.

You will receive updates at the email address you provided.{ticket_ref}"""
