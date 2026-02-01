"""
Kafka consumer worker for processing customer messages.
Task: T035 - Create Kafka consumer worker that consumes from fte.tickets.incoming and invokes agent
Task: T043 - Add error handling and retry logic with exponential backoff
Supports: NFR-007, NFR-008
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict

from confluent_kafka import Consumer, KafkaError, KafkaException

from src.agent.customer_success_agent import get_agent
from src.config import get_settings
from src.models import InboundMessage
from src.services.database import db_service
from src.services.kafka_producer import kafka_producer

logger = logging.getLogger(__name__)
settings = get_settings()


class MessageProcessor:
    """
    Kafka consumer worker for processing incoming customer messages.

    Consumes from fte.tickets.incoming topic and invokes the AI agent
    for each message with error handling and retry logic.
    """

    def __init__(self):
        """Initialize the message processor."""
        self._consumer: Consumer = None
        self._running = False
        self._agent = get_agent()

    def _create_consumer(self) -> Consumer:
        """
        Create and configure Kafka consumer.

        Returns:
            Configured Kafka consumer
        """
        config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_CONSUMER_GROUP,
            'auto.offset.reset': 'earliest',  # Start from earliest unprocessed message
            'enable.auto.commit': False,  # Manual commit for at-least-once delivery
            'max.poll.interval.ms': 300000,  # 5 minutes max processing time
            'session.timeout.ms': 60000,  # 1 minute session timeout
        }

        consumer = Consumer(config)
        logger.info(f"Kafka consumer created: group={settings.KAFKA_CONSUMER_GROUP}")

        return consumer

    async def _check_message_deduplication(self, channel_message_id: str, channel: str) -> bool:
        """
        Check if message has already been processed (FR-004).

        Args:
            channel_message_id: External message ID from channel
            channel: Message channel

        Returns:
            True if message was already processed, False otherwise
        """
        try:
            query = """
                SELECT id FROM messages
                WHERE channel = $1 AND channel_message_id = $2
                LIMIT 1
            """
            result = await db_service.fetchrow(query, channel, channel_message_id)

            if result:
                logger.info(f"Duplicate message detected: {channel_message_id} on {channel}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking message deduplication: {e}")
            # On error, assume not duplicate to avoid losing messages
            return False

    async def _get_or_create_customer(self, identifier: str, identifier_type: str) -> str:
        """
        Get existing customer or create new one (FR-006, FR-007).

        Task: T036 - Implement customer lookup/create logic

        Args:
            identifier: Email or phone number
            identifier_type: Type of identifier (email, phone, whatsapp)

        Returns:
            Customer UUID as string
        """
        try:
            # First, try to find existing customer by identifier
            lookup_query = """
                SELECT customer_id
                FROM customer_identifiers
                WHERE identifier_type = $1 AND identifier_value = $2
                LIMIT 1
            """
            result = await db_service.fetchrow(lookup_query, identifier_type, identifier)

            if result:
                logger.info(f"Found existing customer: identifier={identifier}")
                return str(result['customer_id'])

            # Create new customer
            from uuid import uuid4
            customer_id = uuid4()

            create_customer_query = """
                INSERT INTO customers (id, primary_email, primary_phone, created_at)
                VALUES ($1, $2, $3, NOW())
                RETURNING id
            """

            # Set primary email or phone based on identifier type
            primary_email = identifier if identifier_type == 'email' else None
            primary_phone = identifier if identifier_type in ['phone', 'whatsapp'] else None

            await db_service.execute(
                create_customer_query,
                customer_id,
                primary_email,
                primary_phone
            )

            # Create identifier record
            create_identifier_query = """
                INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
                VALUES ($1, $2, $3)
            """
            await db_service.execute(
                create_identifier_query,
                customer_id,
                identifier_type,
                identifier
            )

            logger.info(f"Created new customer: {customer_id}, identifier={identifier}")

            return str(customer_id)

        except Exception as e:
            logger.error(f"Error in get_or_create_customer: {e}")
            raise

    async def _get_or_create_conversation(self, customer_id: str, channel: str) -> str:
        """
        Get active conversation or create new one.

        Args:
            customer_id: Customer UUID
            channel: Message channel

        Returns:
            Conversation UUID as string
        """
        try:
            from uuid import UUID, uuid4

            customer_uuid = UUID(customer_id)

            # Look for active conversation within last 24 hours (FR-008)
            lookup_query = """
                SELECT id
                FROM conversations
                WHERE customer_id = $1
                  AND status = 'active'
                  AND started_at > NOW() - INTERVAL '24 hours'
                ORDER BY started_at DESC
                LIMIT 1
            """
            result = await db_service.fetchrow(lookup_query, customer_uuid)

            if result:
                logger.info(f"Found active conversation: {result['id']}")
                return str(result['id'])

            # Create new conversation
            conversation_id = uuid4()
            create_query = """
                INSERT INTO conversations (id, customer_id, initial_channel, status, started_at)
                VALUES ($1, $2, $3, 'active', NOW())
                RETURNING id
            """
            await db_service.execute(create_query, conversation_id, customer_uuid, channel)

            logger.info(f"Created new conversation: {conversation_id}")

            return str(conversation_id)

        except Exception as e:
            logger.error(f"Error in get_or_create_conversation: {e}")
            raise

    async def _process_message(self, message_data: Dict[str, Any]) -> None:
        """
        Process a single customer message with the AI agent.

        Args:
            message_data: Parsed message data from Kafka

        Raises:
            Exception: If processing fails after retries
        """
        try:
            # Parse inbound message
            inbound_msg = InboundMessage(**message_data)

            # Check for duplicate (FR-004)
            is_duplicate = await self._check_message_deduplication(
                inbound_msg.channel_message_id,
                inbound_msg.channel.value
            )

            if is_duplicate:
                logger.info(f"Skipping duplicate message: {inbound_msg.channel_message_id}")
                return

            # Get or create customer (T036)
            identifier_type = 'email' if inbound_msg.channel.value == 'email' else 'phone'
            customer_id = await self._get_or_create_customer(
                inbound_msg.customer_identifier,
                identifier_type
            )

            # Get or create conversation
            conversation_id = await self._get_or_create_conversation(
                customer_id,
                inbound_msg.channel.value
            )

            # Invoke AI agent
            logger.info(
                f"Invoking agent: customer={customer_id}, "
                f"channel={inbound_msg.channel.value}"
            )

            result = await self._agent.process_message(
                customer_message=inbound_msg.content,
                channel=inbound_msg.channel.value,
                customer_id=customer_id,
                conversation_id=conversation_id,
                metadata=inbound_msg.metadata
            )

            if result['status'] == 'success':
                logger.info(f"Message processed successfully: customer={customer_id}")
            else:
                logger.error(f"Agent processing failed: {result.get('error')}")
                raise Exception(f"Agent processing failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    async def _retry_with_exponential_backoff(
        self,
        func,
        *args,
        max_retries: int = None,
        backoff_factor: int = None,
        **kwargs
    ):
        """
        Retry function with exponential backoff (NFR-007).

        Task: T043 - Error handling and retry logic with exponential backoff

        Args:
            func: Async function to retry
            *args: Function arguments
            max_retries: Maximum retry attempts (defaults to config)
            backoff_factor: Backoff multiplier (defaults to config)
            **kwargs: Function keyword arguments

        Raises:
            Exception: If all retries fail
        """
        if max_retries is None:
            max_retries = settings.MESSAGE_RETRY_MAX_ATTEMPTS

        if backoff_factor is None:
            backoff_factor = settings.MESSAGE_RETRY_BACKOFF_FACTOR

        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    logger.error(f"All {max_retries} retry attempts failed: {e}")
                    raise

                # Calculate exponential backoff delay
                delay = backoff_factor ** attempt
                logger.warning(
                    f"Retry attempt {attempt + 1}/{max_retries} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)

    async def _publish_to_dlq(self, message_data: Dict[str, Any], error: str):
        """
        Publish failed message to dead letter queue (NFR-008).

        Args:
            message_data: Original message data
            error: Error description
        """
        try:
            dlq_payload = {
                "original_message": message_data,
                "error": error,
                "failed_at": time.time(),
                "source": "message_processor"
            }

            await kafka_producer.publish(
                topic="fte.dlq",
                message=dlq_payload
            )

            logger.info("Failed message published to DLQ")

        except Exception as e:
            logger.error(f"Failed to publish to DLQ: {e}")

    async def start(self):
        """
        Start consuming messages from Kafka.

        Implements graceful shutdown handling.
        """
        self._consumer = self._create_consumer()
        self._consumer.subscribe(['fte.tickets.incoming'])

        self._running = True
        logger.info("Message processor started. Listening for messages...")

        try:
            while self._running:
                # Poll for message (with 1 second timeout)
                msg = self._consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition, not an error
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        continue

                try:
                    # Parse message
                    message_data = json.loads(msg.value().decode('utf-8'))

                    # Process with retry logic (T043)
                    await self._retry_with_exponential_backoff(
                        self._process_message,
                        message_data
                    )

                    # Commit offset after successful processing
                    self._consumer.commit(asynchronous=False)

                except Exception as e:
                    logger.error(f"Message processing failed after all retries: {e}")

                    # Publish to DLQ
                    await self._publish_to_dlq(message_data, str(e))

                    # Still commit to avoid reprocessing bad message
                    self._consumer.commit(asynchronous=False)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down...")

        finally:
            await self.stop()

    async def stop(self):
        """
        Gracefully stop the consumer (T108).

        Implements graceful shutdown for Kafka consumer.
        """
        self._running = False

        if self._consumer:
            logger.info("Closing Kafka consumer...")
            self._consumer.close()
            logger.info("Kafka consumer closed")


# Main entry point for worker process
async def main():
    """Main function to run message processor worker."""
    logger.info("Starting message processor worker...")

    # Initialize database connection
    await db_service.connect()

    # Initialize Kafka producer
    kafka_producer.connect()

    # Create and start processor
    processor = MessageProcessor()

    try:
        await processor.start()
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
        raise
    finally:
        await db_service.disconnect()
        kafka_producer.disconnect()


if __name__ == "__main__":
    # Run worker
    asyncio.run(main())
