"""
Kafka producer service for publishing messages to topics.
Task: T014 - Implement Kafka producer service with topic publishing and correlation ID support
"""

import json
import logging
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from confluent_kafka import KafkaException, Producer

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class KafkaProducerService:
    """Manages Kafka message production with correlation ID tracking."""

    def __init__(self):
        self._producer: Optional[Producer] = None

    def connect(self) -> None:
        """Initialize Kafka producer with configured bootstrap servers."""
        if self._producer is not None:
            logger.warning("Kafka producer already initialized")
            return

        try:
            config = {
                'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
                'client.id': 'customer-success-agent',
                'acks': 'all',  # Wait for all replicas to acknowledge
                'retries': 3,  # Retry failed messages
                'max.in.flight.requests.per.connection': 1,  # Ensure ordering
                'compression.type': 'snappy',  # Compress messages
                'linger.ms': 10,  # Batch messages for 10ms
                'batch.size': 16384,  # 16KB batch size
                'security.protocol': settings.KAFKA_SECURITY_PROTOCOL,
            }

            # Add SASL settings if provided
            if settings.KAFKA_SASL_USERNAME:
                config['sasl.mechanism'] = settings.KAFKA_SASL_MECHANISM
                config['sasl.username'] = settings.KAFKA_SASL_USERNAME
                config['sasl.password'] = settings.KAFKA_SASL_PASSWORD

            self._producer = Producer(config)
            logger.info(f"Kafka producer initialized: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

    def disconnect(self) -> None:
        """Flush pending messages and close producer."""
        if self._producer is not None:
            self._producer.flush(timeout=30)  # Wait up to 30s for pending messages
            self._producer = None
            logger.info("Kafka producer closed")

    def _delivery_callback(self, err, msg):
        """Callback for message delivery reports."""
        if err:
            logger.error(f"Message delivery failed: {err}, topic={msg.topic()}")
        else:
            logger.debug(
                f"Message delivered: topic={msg.topic()}, "
                f"partition={msg.partition()}, offset={msg.offset()}"
            )

    async def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> UUID:
        """
        Publish a message to a Kafka topic with correlation ID.

        Args:
            topic: Kafka topic name
            message: Message payload (will be JSON serialized)
            key: Optional partition key for message ordering
            correlation_id: Optional correlation ID for request tracking
            headers: Optional message headers

        Returns:
            Correlation ID for the published message

        Example:
            await kafka_service.publish(
                topic="fte.tickets.incoming",
                message={"customer_id": "123", "content": "Help!"},
                key="customer-123",
                correlation_id=uuid4()
            )
        """
        if self._producer is None:
            raise RuntimeError("Kafka producer not initialized. Call connect() first.")

        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = uuid4()

        try:
            # Add correlation ID to message
            message_with_correlation = {
                **message,
                "correlation_id": str(correlation_id)
            }

            # Prepare headers
            kafka_headers = []
            if headers:
                kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]

            # Add correlation ID to headers
            kafka_headers.append(('correlation_id', str(correlation_id).encode('utf-8')))

            # Serialize message to JSON
            message_bytes = json.dumps(message_with_correlation).encode('utf-8')

            # Publish message
            self._producer.produce(
                topic=topic,
                value=message_bytes,
                key=key.encode('utf-8') if key else None,
                headers=kafka_headers,
                callback=self._delivery_callback
            )

            # Trigger delivery reports
            self._producer.poll(0)

            logger.info(
                f"Published message to topic={topic}, "
                f"correlation_id={correlation_id}, key={key}"
            )

            return correlation_id

        except KafkaException as e:
            logger.error(f"Failed to publish message to {topic}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error publishing to {topic}: {e}")
            raise

    def flush(self, timeout: float = 30.0) -> int:
        """
        Wait for all messages in the Producer queue to be delivered.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Number of messages still in queue
        """
        if self._producer is None:
            return 0
        return self._producer.flush(timeout=timeout)


# Global Kafka producer instance
kafka_producer = KafkaProducerService()


def get_kafka_producer() -> KafkaProducerService:
    """
    Dependency function for FastAPI to inject Kafka producer.

    Usage in FastAPI routes:
        @app.post("/webhook")
        async def webhook(
            kafka: KafkaProducerService = Depends(get_kafka_producer)
        ):
            await kafka.publish("fte.tickets.incoming", {"data": "..."})
    """
    return kafka_producer
