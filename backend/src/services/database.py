"""
Database connection pool service using asyncpg.
Task: T013 - Implement database connection pool service with asyncpg
Connection pool configuration: min=10, max=20 per requirements
"""

import asyncpg
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseService:
    """Manages PostgreSQL connection pool with asyncpg."""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """
        Initialize connection pool with configured parameters.
        Pool size: min=10, max=20 per NFR-003 requirements.
        """
        if self._pool is not None:
            logger.warning("Database pool already initialized")
            return

        try:
            # Parse DATABASE_URL - remove the +asyncpg suffix if present
            db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

            self._pool = await asyncpg.create_pool(
                dsn=db_url,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_QUERY_TIMEOUT,
                max_queries=50000,  # Number of queries before connection is replaced
                max_inactive_connection_lifetime=300.0,  # 5 minutes
            )
            logger.info(
                f"Database pool initialized: min={settings.DB_POOL_MIN_SIZE}, "
                f"max={settings.DB_POOL_MAX_SIZE}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    async def disconnect(self) -> None:
        """Close all connections in the pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            logger.info("Database pool closed")

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Acquire a connection from the pool.

        Usage:
            async with db_service.acquire() as conn:
                result = await conn.fetch("SELECT * FROM customers")
        """
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call connect() first.")

        async with self._pool.acquire() as connection:
            yield connection

    async def execute(self, query: str, *args) -> str:
        """
        Execute a query that doesn't return rows (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Query execution status
        """
        async with self.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list:
        """
        Fetch multiple rows from a query.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            List of records
        """
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Fetch a single row from a query.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Single record or None
        """
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """
        Fetch a single value from a query.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Single value
        """
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)

    # ========================================================================
    # Task T053: Customer lookup by phone (FR-007)
    # ========================================================================

    async def find_customer_by_phone(self, phone: str) -> Optional[asyncpg.Record]:
        """
        Find customer by phone number using customer_identifiers table.

        Args:
            phone: Phone number in E.164 format (+14155551234)

        Returns:
            Customer record or None if not found
        """
        query = """
            SELECT c.*
            FROM customers c
            JOIN customer_identifiers ci ON ci.customer_id = c.id
            WHERE ci.identifier_type = 'phone'
              AND ci.identifier_value = $1
            LIMIT 1
        """
        return await self.fetchrow(query, phone)

    async def find_customer_by_whatsapp(self, phone: str) -> Optional[asyncpg.Record]:
        """
        Find customer by WhatsApp number using customer_identifiers table.

        Args:
            phone: WhatsApp phone number in E.164 format

        Returns:
            Customer record or None if not found
        """
        query = """
            SELECT c.*
            FROM customers c
            JOIN customer_identifiers ci ON ci.customer_id = c.id
            WHERE ci.identifier_type = 'whatsapp'
              AND ci.identifier_value = $1
            LIMIT 1
        """
        return await self.fetchrow(query, phone)

    # ========================================================================
    # Task T039: Message deduplication (FR-004)
    # ========================================================================

    async def check_message_duplicate(
        self, channel: str, channel_message_id: str
    ) -> bool:
        """
        Check if message has already been processed (deduplication).

        Args:
            channel: Channel name (email, whatsapp, webform)
            channel_message_id: External message ID (Gmail ID, Twilio SID, etc.)

        Returns:
            True if message exists (duplicate), False otherwise
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM messages
                WHERE channel = $1 AND channel_message_id = $2
            ) AS is_duplicate
        """
        result = await self.fetchval(query, channel, channel_message_id)
        return bool(result)

    # ========================================================================
    # Task T073: Customer identifier creation/update (FR-007)
    # ========================================================================

    async def create_or_update_customer_identifier(
        self,
        customer_id,
        identifier_type: str,
        identifier_value: str,
        verified: bool = False,
    ) -> Optional[asyncpg.Record]:
        """
        Create or update customer identifier for cross-channel matching.

        Args:
            customer_id: Customer UUID
            identifier_type: Type (email, phone, whatsapp)
            identifier_value: Identifier value (email address, phone number)
            verified: Whether identifier is verified

        Returns:
            Identifier record
        """
        from uuid import uuid4

        query = """
            INSERT INTO customer_identifiers (id, customer_id, identifier_type, identifier_value, verified, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            ON CONFLICT (identifier_type, identifier_value)
            DO UPDATE SET verified = EXCLUDED.verified
            RETURNING id, customer_id, identifier_type, identifier_value, verified
        """
        return await self.fetchrow(
            query, uuid4(), customer_id, identifier_type, identifier_value, verified
        )

    # ========================================================================
    # Task T074: Cross-channel customer lookup (FR-007, FR-008)
    # ========================================================================

    async def find_customer_by_any_identifier(
        self, email: str = None, phone: str = None, whatsapp: str = None
    ) -> Optional[asyncpg.Record]:
        """
        Find customer by any identifier (email, phone, or WhatsApp).

        Enables cross-channel customer recognition.

        Args:
            email: Email address
            phone: Phone number
            whatsapp: WhatsApp number

        Returns:
            Customer record or None
        """
        query = """
            SELECT DISTINCT c.*
            FROM customers c
            LEFT JOIN customer_identifiers ci ON ci.customer_id = c.id
            WHERE c.primary_email = $1
               OR (ci.identifier_type = 'email' AND ci.identifier_value = $1)
               OR (ci.identifier_type = 'phone' AND ci.identifier_value = $2)
               OR (ci.identifier_type = 'whatsapp' AND ci.identifier_value = $3)
            LIMIT 1
        """
        return await self.fetchrow(query, email, phone, whatsapp)

    # ========================================================================
    # Task T075: Conversation merging (FR-008)
    # ========================================================================

    async def merge_conversations(
        self, primary_conversation_id, secondary_conversation_id
    ):
        """
        Merge two conversations when same customer uses multiple channels.

        Updates all messages from secondary conversation to primary.

        Args:
            primary_conversation_id: Target conversation UUID
            secondary_conversation_id: Source conversation UUID to merge
        """
        # Update messages to primary conversation
        update_messages_query = """
            UPDATE messages
            SET conversation_id = $1, updated_at = NOW()
            WHERE conversation_id = $2
        """
        await self.execute(update_messages_query, primary_conversation_id, secondary_conversation_id)

        # Update tickets to primary conversation
        update_tickets_query = """
            UPDATE tickets
            SET conversation_id = $1, updated_at = NOW()
            WHERE conversation_id = $2
        """
        await self.execute(update_tickets_query, primary_conversation_id, secondary_conversation_id)

        # Close secondary conversation
        close_query = """
            UPDATE conversations
            SET status = 'closed', ended_at = NOW()
            WHERE id = $1
        """
        await self.execute(close_query, secondary_conversation_id)

    # ========================================================================
    # Task T077: Channel switch tracking (FR-008)
    # ========================================================================

    async def track_channel_switch(
        self, conversation_id, from_channel: str, to_channel: str
    ):
        """
        Track when customer switches communication channels.

        Updates conversation metadata with channel switch event.

        Args:
            conversation_id: Conversation UUID
            from_channel: Previous channel (email, whatsapp, webform)
            to_channel: New channel
        """
        from datetime import datetime

        query = """
            UPDATE conversations
            SET metadata = COALESCE(metadata, '{}'::jsonb) ||
                jsonb_build_object(
                    'channel_switches',
                    COALESCE(metadata->'channel_switches', '[]'::jsonb) ||
                    jsonb_build_array(
                        jsonb_build_object(
                            'from', $2,
                            'to', $3,
                            'at', $4
                        )
                    )
                )
            WHERE id = $1
        """
        await self.execute(
            query,
            conversation_id,
            from_channel,
            to_channel,
            datetime.utcnow().isoformat(),
        )

    # ========================================================================
    # Task T079: Active conversation detection (FR-008)
    # ========================================================================

    async def find_active_conversation(
        self, customer_id, within_hours: int = 24
    ) -> Optional[asyncpg.Record]:
        """
        Find active conversation for customer within time window.

        Used to reuse conversations when customer returns within 24 hours.

        Args:
            customer_id: Customer UUID
            within_hours: Time window in hours (default 24)

        Returns:
            Active conversation record or None
        """
        query = """
            SELECT *
            FROM conversations
            WHERE customer_id = $1
              AND status = 'active'
              AND started_at > NOW() - INTERVAL '1 hour' * $2
            ORDER BY started_at DESC
            LIMIT 1
        """
        return await self.fetchrow(query, customer_id, within_hours)

    # ========================================================================
    # Task T080: Sentiment score propagation (FR-009, FR-010)
    # ========================================================================

    async def update_conversation_sentiment(
        self, conversation_id, sentiment_score: float
    ):
        """
        Update conversation sentiment score.

        Propagates sentiment across channels for same customer.

        Args:
            conversation_id: Conversation UUID
            sentiment_score: Sentiment score (-1.0 to 1.0)
        """
        query = """
            UPDATE conversations
            SET overall_sentiment = $2, updated_at = NOW()
            WHERE id = $1
        """
        await self.execute(query, conversation_id, sentiment_score)

    async def update_customer_sentiment_history(
        self, customer_id, sentiment_score: float, channel: str
    ):
        """
        Update customer sentiment history across all channels.

        Args:
            customer_id: Customer UUID
            sentiment_score: Sentiment score (-1.0 to 1.0)
            channel: Channel where sentiment was recorded
        """
        from datetime import datetime

        query = """
            UPDATE customers
            SET sentiment_history = COALESCE(sentiment_history, '[]'::jsonb) ||
                jsonb_build_array(
                    jsonb_build_object(
                        'date', $2,
                        'score', $3,
                        'channel', $4
                    )
                )
            WHERE id = $1
        """
        await self.execute(
            query,
            customer_id,
            datetime.utcnow().date().isoformat(),
            sentiment_score,
            channel,
        )


# Global database service instance
db_service = DatabaseService()


async def get_db() -> DatabaseService:
    """
    Dependency function for FastAPI to inject database service.

    Usage in FastAPI routes:
        @app.get("/customers")
        async def get_customers(db: DatabaseService = Depends(get_db)):
            customers = await db.fetch("SELECT * FROM customers")
            return customers
    """
    return db_service
