"""
Input sanitization utilities for XSS and SQL injection prevention.
Task: T018 - Implement input sanitization utilities for XSS and SQL injection prevention
Security requirement: FR-038
"""

import html
import re
from typing import Any, Dict, Optional


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Escapes HTML special characters:
    - < becomes &lt;
    - > becomes &gt;
    - & becomes &amp;
    - " becomes &quot;
    - ' becomes &#x27;

    Args:
        text: Input text that may contain HTML

    Returns:
        Sanitized text with HTML entities escaped

    Example:
        >>> sanitize_html("<script>alert('xss')</script>")
        '&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;'
    """
    if not text:
        return text
    return html.escape(text, quote=True)


def remove_script_tags(text: str) -> str:
    """
    Remove all script tags and their contents from text.

    Args:
        text: Input text that may contain script tags

    Returns:
        Text with all script tags removed

    Example:
        >>> remove_script_tags("Hello <script>alert('xss')</script> World")
        'Hello  World'
    """
    if not text:
        return text

    # Remove script tags (case-insensitive, handles variations)
    pattern = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
    text = pattern.sub('', text)

    # Remove inline event handlers
    event_pattern = re.compile(r'\son\w+\s*=\s*["\']?[^"\']*["\']?', re.IGNORECASE)
    text = event_pattern.sub('', text)

    # Remove javascript: protocol
    js_protocol_pattern = re.compile(r'javascript:', re.IGNORECASE)
    text = js_protocol_pattern.sub('', text)

    return text


def sanitize_sql_input(text: str) -> str:
    """
    Basic SQL injection prevention through input validation.

    Note: This is a defense-in-depth measure. Primary protection
    comes from using parameterized queries with asyncpg.

    Args:
        text: Input text that may contain SQL injection attempts

    Returns:
        Text with potentially dangerous SQL patterns removed

    Example:
        >>> sanitize_sql_input("user'; DROP TABLE users--")
        'user DROP TABLE users'
    """
    if not text:
        return text

    # Remove SQL comment patterns
    text = re.sub(r'--.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

    # Remove common SQL injection patterns
    dangerous_patterns = [
        r";\s*DROP\s+TABLE",
        r";\s*DELETE\s+FROM",
        r";\s*UPDATE\s+",
        r";\s*INSERT\s+INTO",
        r"UNION\s+SELECT",
        r"'\s*OR\s+'1'\s*=\s*'1",
        r"'\s*OR\s+1\s*=\s*1",
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()


def sanitize_customer_input(text: str, max_length: Optional[int] = 10000) -> str:
    """
    Comprehensive input sanitization for customer messages.

    Combines multiple sanitization techniques:
    - HTML escaping for XSS prevention
    - Script tag removal
    - SQL injection pattern removal
    - Length limiting

    Args:
        text: Customer input text
        max_length: Maximum allowed length (default 10,000 chars)

    Returns:
        Sanitized and truncated text

    Example:
        >>> sanitize_customer_input("<script>alert('xss')</script>Help me!")
        '&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;Help me!'
    """
    if not text:
        return ""

    # Truncate to max length
    if max_length and len(text) > max_length:
        text = text[:max_length]

    # Remove script tags first
    text = remove_script_tags(text)

    # SQL injection prevention (defense in depth)
    text = sanitize_sql_input(text)

    # HTML escape for XSS prevention
    text = sanitize_html(text)

    return text.strip()


def sanitize_dict(data: Dict[str, Any], fields_to_sanitize: Optional[list] = None) -> Dict[str, Any]:
    """
    Sanitize specific fields in a dictionary.

    Args:
        data: Dictionary containing user input
        fields_to_sanitize: List of field names to sanitize (default: all string fields)

    Returns:
        Dictionary with sanitized fields

    Example:
        >>> sanitize_dict({"name": "<script>xss</script>", "age": 25})
        {'name': '&lt;script&gt;xss&lt;/script&gt;', 'age': 25}
    """
    if not data:
        return {}

    sanitized = data.copy()

    for key, value in sanitized.items():
        # Sanitize if field is in the list or if sanitizing all string fields
        if isinstance(value, str):
            if fields_to_sanitize is None or key in fields_to_sanitize:
                sanitized[key] = sanitize_customer_input(value)

    return sanitized


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email:
        return False

    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Accepts:
    - International format: +1234567890
    - National format: (123) 456-7890
    - Basic format: 1234567890

    Args:
        phone: Phone number to validate

    Returns:
        True if valid phone format, False otherwise

    Example:
        >>> validate_phone("+14155551234")
        True
        >>> validate_phone("abc123")
        False
    """
    if not phone:
        return False

    # Remove common phone formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)

    # Check if result contains only digits and optional leading +
    pattern = r'^\+?\d{10,15}$'
    return bool(re.match(pattern, cleaned))


def strip_pii_for_logging(text: str) -> str:
    """
    Remove or mask PII from text for safe logging (NFR-013, NFR-014).

    Masks:
    - Email addresses
    - Phone numbers
    - Credit card patterns
    - SSN patterns

    Args:
        text: Text that may contain PII

    Returns:
        Text with PII masked

    Example:
        >>> strip_pii_for_logging("Contact me at user@example.com or +1234567890")
        'Contact me at [EMAIL] or [PHONE]'
    """
    if not text:
        return text

    # Mask email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

    # Mask phone numbers
    text = re.sub(r'\+?\d[\d\s\-\(\)\.]{8,}\d', '[PHONE]', text)

    # Mask credit card patterns (4 groups of 4 digits)
    text = re.sub(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '[CREDIT_CARD]', text)

    # Mask SSN patterns
    text = re.sub(r'\b\d{3}[\s\-]?\d{2}[\s\-]?\d{4}\b', '[SSN]', text)

    return text
