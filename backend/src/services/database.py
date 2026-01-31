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
