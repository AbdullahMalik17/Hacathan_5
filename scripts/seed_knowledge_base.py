#!/usr/bin/env python3
"""
Knowledge base seeding script with embeddings generation.
Task: T021 - Create knowledge base seed script to populate KB with embeddings

This script:
1. Reads knowledge base articles from a JSON file or inline data
2. Generates embeddings using OpenAI text-embedding-3-small
3. Stores articles with embeddings in PostgreSQL using pgvector

Usage:
    python scripts/seed_knowledge_base.py
    python scripts/seed_knowledge_base.py --file kb_articles.json
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

import asyncpg
from openai import OpenAI

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


# Sample knowledge base articles for initial seeding
SAMPLE_ARTICLES = [
    {
        "title": "How to Reset Your Password",
        "content": """To reset your password:
        1. Go to the login page
        2. Click on "Forgot Password" link
        3. Enter your email address
        4. Check your email for the password reset link
        5. Click the link and enter your new password
        6. Confirm your new password
        Your password must be at least 8 characters and include uppercase, lowercase, and numbers.""",
        "category": "account_management"
    },
    {
        "title": "Business Hours and Contact Information",
        "content": """Our business hours are:
        Monday - Friday: 9:00 AM - 6:00 PM EST
        Saturday: 10:00 AM - 4:00 PM EST
        Sunday: Closed

        You can reach us through:
        - Email: support@company.com
        - WhatsApp: +1 (415) 555-1234
        - Web Form: company.com/support

        For urgent issues outside business hours, please use our emergency hotline.""",
        "category": "general"
    },
    {
        "title": "How to Update Your Account Information",
        "content": """To update your account information:
        1. Log in to your account
        2. Click on your profile icon in the top right
        3. Select "Account Settings"
        4. Update your name, email, phone number, or other details
        5. Click "Save Changes"
        Changes take effect immediately.""",
        "category": "account_management"
    },
    {
        "title": "Troubleshooting Login Issues",
        "content": """If you're having trouble logging in:
        1. Verify you're using the correct email address
        2. Check that Caps Lock is off when entering your password
        3. Clear your browser cache and cookies
        4. Try using a different browser or incognito mode
        5. Reset your password if you've forgotten it
        6. Contact support if issues persist

        Common login errors:
        - "Invalid credentials": Check email and password spelling
        - "Account locked": Too many failed attempts, wait 15 minutes
        - "Session expired": Log in again""",
        "category": "technical"
    },
    {
        "title": "How to Cancel or Modify an Order",
        "content": """To cancel or modify an order:
        1. Orders can be cancelled within 24 hours of placement
        2. Log in to your account and go to "Order History"
        3. Find your order and click "Cancel Order" or "Modify Order"
        4. For orders already shipped, you'll need to process a return
        5. Refunds typically process within 5-7 business days

        Note: Once an order ships, it cannot be cancelled. You can refuse delivery or return the item.""",
        "category": "billing"
    },
    {
        "title": "Product Return and Refund Policy",
        "content": """Our return policy:
        - 30-day return window from delivery date
        - Items must be unused and in original packaging
        - Free returns for defective or incorrect items
        - $5.99 restocking fee for buyer's remorse returns

        Refund timeline:
        1. Initiate return through your account
        2. Print return label and ship within 7 days
        3. We process refund within 3-5 business days of receiving item
        4. Refund appears in your account within 5-7 business days

        Non-returnable items: Gift cards, digital downloads, personalized items""",
        "category": "billing"
    },
    {
        "title": "How to Track Your Order",
        "content": """To track your order:
        1. Check your order confirmation email for tracking number
        2. Visit the carrier's website (UPS, FedEx, USPS)
        3. Enter your tracking number
        4. Or log in to your account and view order status

        Shipping timeline:
        - Standard shipping: 5-7 business days
        - Express shipping: 2-3 business days
        - Overnight shipping: 1 business day

        Note: Tracking information updates within 24 hours of shipment.""",
        "category": "general"
    },
    {
        "title": "How to Report a Bug or Technical Issue",
        "content": """To report a technical issue:
        1. Note what you were doing when the issue occurred
        2. Take a screenshot if possible
        3. Contact support with:
           - Your account email
           - Description of the issue
           - Steps to reproduce
           - Browser and device information
           - Screenshot if available
        4. Our technical team will investigate and respond within 24 hours

        For urgent issues affecting your account security, contact us immediately.""",
        "category": "technical"
    },
    {
        "title": "Account Security Best Practices",
        "content": """Keep your account secure:
        1. Use a strong, unique password (at least 12 characters)
        2. Enable two-factor authentication (2FA)
        3. Never share your password with anyone
        4. Don't use the same password across multiple sites
        5. Log out when using shared computers
        6. Monitor your account for suspicious activity
        7. Update your password every 90 days

        If you suspect unauthorized access, change your password immediately and contact support.""",
        "category": "account_management"
    },
    {
        "title": "Payment Methods and Billing",
        "content": """Accepted payment methods:
        - Credit cards: Visa, Mastercard, American Express, Discover
        - Debit cards
        - PayPal
        - Apple Pay
        - Google Pay

        Billing information:
        - Charges appear as "COMPANY_NAME" on your statement
        - You'll receive a receipt via email after each purchase
        - View billing history in your account under "Billing"

        Payment issues: Verify card details, expiration date, and billing address match your bank records.""",
        "category": "billing"
    },
]


async def generate_embedding(client: OpenAI, text: str) -> List[float]:
    """
    Generate embedding vector for text using OpenAI.

    Args:
        client: OpenAI client instance
        text: Text to embed

    Returns:
        1536-dimensional embedding vector
    """
    try:
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise


async def seed_knowledge_base(articles: List[Dict], conn: asyncpg.Connection):
    """
    Seed knowledge base with articles and embeddings.

    Args:
        articles: List of article dictionaries
        conn: Database connection
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    logger.info(f"Seeding {len(articles)} knowledge base articles...")

    for idx, article in enumerate(articles, 1):
        try:
            # Generate embedding for article content
            logger.info(f"Processing article {idx}/{len(articles)}: {article['title']}")
            embedding = await generate_embedding(client, article['content'])

            # Insert article with embedding
            await conn.execute(
                """
                INSERT INTO knowledge_base (title, content, category, embedding)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                """,
                article['title'],
                article['content'],
                article['category'],
                str(embedding)
            )

            logger.info(f"✓ Seeded: {article['title']}")

        except Exception as e:
            logger.error(f"Failed to seed article '{article['title']}': {e}")
            continue

    logger.info("Knowledge base seeding complete!")


async def main():
    """Main execution function."""
    # Check for OpenAI API key
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
        logger.error("OPENAI_API_KEY not set in environment variables")
        sys.exit(1)

    # Connect to database
    try:
        db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(db_url)
        logger.info("Connected to database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

    try:
        # Use sample articles or load from file
        articles = SAMPLE_ARTICLES

        # Check if file argument provided
        if len(sys.argv) > 1 and sys.argv[1] == "--file":
            if len(sys.argv) < 3:
                logger.error("Usage: python seed_knowledge_base.py --file <json_file>")
                sys.exit(1)

            file_path = Path(sys.argv[2])
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                sys.exit(1)

            with open(file_path, 'r') as f:
                articles = json.load(f)
                logger.info(f"Loaded {len(articles)} articles from {file_path}")

        # Seed knowledge base
        await seed_knowledge_base(articles, conn)

        # Verify seeding
        count = await conn.fetchval("SELECT COUNT(*) FROM knowledge_base")
        logger.info(f"Total articles in knowledge base: {count}")

    finally:
        await conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
