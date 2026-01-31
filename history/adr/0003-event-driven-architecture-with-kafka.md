# ADR-0003: Event-Driven Architecture with Kafka

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-31
- **Feature:** 001-customer-success-fte
- **Context:** System must decouple webhook intake from agent processing to enable horizontal scaling, replay capabilities, and audit trails. Constitution Principle III (Event-Driven Design) mandates Kafka for async messaging. Requirements include <10s message lag, idempotent processing, and per-customer message ordering for conversation coherence.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core system integration pattern
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - RabbitMQ, Redis Streams, SQS, direct DB polling
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all services and scaling characteristics
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use **Apache Kafka** with the following event-driven architecture:

- **Message Broker**: Apache Kafka (3 broker cluster with replication factor 3)
- **Topic Schema**: Domain-based naming `fte.<subdomain>.<entity>` for all events
- **Message Format**: JSON with correlation IDs for distributed tracing
- **Partitioning Strategy**: Partition by customer_id to preserve per-customer message ordering
- **Partition Count**: 12 partitions (matches max agent worker replicas for parallel processing)
- **Consumer Groups**: Single consumer group per service for parallel consumption
- **Idempotency**: Deduplication via processed_messages table in PostgreSQL
- **Dead Letter Queue**: fte.dlq topic for failed messages after 5 retry attempts
- **Producer Library**: confluent-kafka-python with at-least-once delivery semantics

**Topic Structure**:
```
fte.tickets.incoming          # Unified intake from all channels
fte.channels.email.inbound    # Gmail webhook events
fte.channels.whatsapp.inbound # Twilio webhook events
fte.channels.webform.inbound  # Web form submissions
fte.escalations               # Human escalation events
fte.metrics.agent             # Agent performance metrics
fte.dlq                       # Dead letter queue for failures
```

**Idempotency Pattern**:
```sql
-- Check before processing
SELECT EXISTS(
  SELECT 1 FROM processed_messages
  WHERE message_id = '<kafka_message_id>'
) AS already_processed;

-- Store after successful processing
INSERT INTO processed_messages (message_id, processed_at)
VALUES ('<kafka_message_id>', NOW());
```

## Consequences

### Positive

- **Decoupling**: Webhook handlers immediately return 200 OK after publishing to Kafka, agent processing happens async (eliminates webhook timeouts)
- **Horizontal Scaling**: KEDA autoscaler adds agent worker replicas based on Kafka consumer lag (2-12 replicas, lag threshold 100 messages)
- **Message Ordering**: Partitioning by customer_id guarantees conversation coherence (all messages from same customer processed sequentially)
- **Replay Capability**: 7-day retention enables reprocessing messages for debugging or schema migrations
- **Audit Trail**: Kafka logs provide immutable record of all customer interactions for compliance
- **Fault Tolerance**: 3x replication ensures no message loss if single broker fails
- **Load Spike Handling**: Kafka buffers messages during traffic spikes, workers process at sustainable rate
- **Constitution Alignment**: Directly mandated by Principle III (Event-Driven Design)

### Negative

- **Operational Complexity**: Requires managing Kafka cluster (3 brokers, ZooKeeper/KRaft, monitoring, disk management)
- **Resource Usage**: Kafka cluster requires ~1.5GB RAM + 50GB disk minimum (vs lightweight queue like Redis)
- **Learning Curve**: Team must learn Kafka concepts (partitions, consumer groups, offsets, rebalancing)
- **Latency Overhead**: Kafka adds 50-100ms network round-trip vs direct function calls
- **Duplicate Processing Risk**: At-least-once semantics means idempotency logic required in all consumers
- **Rebalancing Delays**: Consumer group rebalancing on worker scale-up/down pauses processing for 5-10 seconds

## Alternatives Considered

### Alternative A: RabbitMQ with Topic Exchanges
- **Stack**: RabbitMQ + Topic exchanges for routing + Manual DLQ
- **Why Rejected**:
  - No built-in message replay (once consumed, message is gone)
  - Weaker partitioning guarantees make per-customer ordering harder to implement
  - Constitution explicitly mandates Kafka (Principle III)
  - Less mature autoscaling integrations (KEDA supports Kafka better than RabbitMQ)
  - Disk-based durability slower than Kafka's append-only log design

### Alternative B: Redis Streams
- **Stack**: Redis Streams + Consumer groups + XACK acknowledgment
- **Why Rejected**:
  - Limited to single Redis instance (no horizontal scaling of message broker itself)
  - 7-day retention requires large Redis memory (vs Kafka's disk-based storage)
  - Weaker durability guarantees (Redis persistence modes RDB/AOF less robust than Kafka replication)
  - Smaller ecosystem for monitoring and tooling compared to Kafka
  - Constitution mandates Kafka specifically

### Alternative C: AWS SQS + SNS
- **Stack**: SQS queues per channel + SNS for pub/sub + DLQ built-in
- **Why Rejected**:
  - No message ordering guarantees (SQS FIFO queues limited to 300 TPS per queue, too low for our scale)
  - Vendor lock-in to AWS prevents multi-cloud or on-prem deployment
  - Higher cost at scale ($0.40 per 1M requests vs self-hosted Kafka ~$500/year for 100M+ messages)
  - No replay capability (messages deleted after consumption)
  - Constitution requires self-hosted Kafka

### Alternative D: Direct Database Polling
- **Stack**: PostgreSQL + Polling worker queries messages table every 1s
- **Why Rejected**:
  - Database becomes bottleneck under high load (polling queries strain PostgreSQL)
  - No horizontal scaling of message intake (single DB write path)
  - Missing audit trail and replay capabilities
  - Higher latency (1-2s polling interval vs Kafka's immediate push)
  - Violates Constitution Principle III (Event-Driven Design with Kafka)

## References

- Feature Spec: specs/001-customer-success-fte/spec.md (FR-004: Message Deduplication, FR-005: Message Normalization)
- Implementation Plan: specs/001-customer-success-fte/plan.md (Phase 0: Research - Section 3, Path 2: Event Streaming Layer)
- Research Document: specs/001-customer-success-fte/research.md (Section 3: Kafka Event Streaming)
- Related ADRs: ADR-0001 (AI Agent Architecture) for worker integration, ADR-0004 (Deployment Strategy) for KEDA autoscaling
- Constitution: .specify/memory/constitution.md (Principle III: Event-Driven Design)
