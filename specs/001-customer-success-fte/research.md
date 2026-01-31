# Technical Architecture Research: Customer Success Digital FTE

**Feature**: 001-customer-success-fte
**Date**: 2026-01-31
**Status**: Research Complete
**Next Phase**: Data Model Design (Phase 1)

## Executive Summary

Production-grade Customer Success Digital FTE operating 24/7 across three communication channels (Email, WhatsApp, Web Form). All decisions align with constitution's eight core principles and optimize for autonomous operation, reliability, and cost efficiency (<$2,000/year vs $75,000 human FTE).

## 1. OpenAI Agents SDK Architecture

### Decision
Use OpenAI Agents SDK with @function_tool decorators and Pydantic v2 models for all tool definitions.

### Rationale
- Constitution Principle V (Agent Autonomy with Guardrails) requires strict behavioral constraints
- SDK provides automatic schema generation, type safety, and validation
- Structured outputs eliminate manual parsing and improve reliability

### Implementation Pattern
```python
from openai_agents import Agent, function_tool
from pydantic import BaseModel

class TicketCreate(BaseModel):
    customer_id: str
    issue: str
    channel: str

@function_tool
def create_ticket(data: TicketCreate) -> str:
    """Create support ticket with automatic validation."""
    pass

agent = Agent(
    name="customer-success-fte",
    instructions="REQUIRED WORKFLOW: 1. create_ticket 2. get_customer_history 3. search_knowledge_base 4. send_response",
    tools=[create_ticket, get_customer_history, search_knowledge_base],
)
```

### Alternatives Rejected
- **LangChain**: Less structured output guarantees
- **Custom Agent Loop**: Reinventing validation and retry logic

## 2. PostgreSQL with pgvector

### Decision
PostgreSQL 16+ with pgvector extension. asyncpg driver with connection pooling (min=10, max=20).

### Rationale
- Constitution Principle IV (Database-as-CRM) mandates PostgreSQL
- pgvector HNSW index provides fast semantic search (<500ms p95)
- Unified storage for CRM data and vector embeddings

### Schema Highlights
```sql
CREATE EXTENSION vector;

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    primary_email TEXT UNIQUE,
    sentiment_history JSONB
);

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY,
    content TEXT,
    embedding vector(1536)
);

CREATE INDEX ON knowledge_base USING hnsw (embedding vector_cosine_ops);
```

### Performance Targets
- Customer lookup: <100ms p95
- Knowledge base search: <500ms p95 (pgvector HNSW)

## 3. Kafka Event Streaming

### Decision
Apache Kafka with domain-based topics (`fte.<subdomain>.<entity>`). JSON messages with correlation IDs. Partition by customer_id for ordering.

### Rationale
- Constitution Principle III (Event-Driven Design) mandates Kafka
- Enables replay, horizontal scaling, and audit trail
- Consumer groups allow parallel processing while preserving per-customer ordering

### Topic Schema
```
fte.tickets.incoming          # Unified intake
fte.channels.email.inbound
fte.channels.whatsapp.inbound
fte.channels.webform.inbound
fte.escalations
fte.metrics.agent
fte.dlq                       # Dead letter queue
```

### Partitioning
- **Key**: customer_id (preserves conversation order)
- **Partition Count**: 12 (matches max worker replicas)
- **Replication**: 3 (fault tolerance)

### Idempotency
Deduplication table in PostgreSQL:
```sql
CREATE TABLE processed_messages (
    message_id UUID PRIMARY KEY,
    processed_at TIMESTAMP
);
```

## 4. FastAPI Backend

### Decision
FastAPI 0.115+ with async handlers, Pydantic v2 validation, Prometheus metrics, structured logging.

### Project Structure
```
backend/
├── src/
│   ├── main.py              # FastAPI app
│   ├── webhooks/
│   │   ├── gmail.py
│   │   ├── twilio.py
│   │   └── webform.py
│   ├── services/
│   │   ├── kafka_producer.py
│   │   ├── database.py
│   │   └── auth.py          # Signature validation
│   └── middleware/
│       ├── correlation_id.py
│       └── logging.py
```

### Health Checks
```python
@app.get("/health")  # Liveness probe
@app.get("/ready")   # Readiness probe (checks DB + Kafka)
```

## 5. Channel Integrations

### Gmail
- **Method**: Gmail API + Pub/Sub push notifications
- **Authentication**: Service account with JWT validation
- **Real-time**: Pub/Sub eliminates polling latency

### Twilio WhatsApp
- **Method**: Twilio WhatsApp API webhooks
- **Security**: Validate X-Twilio-Signature header
- **Response**: Split messages >300 chars at sentence boundaries

### Web Form
- **Frontend**: React Hook Form + Zod validation
- **Backend**: FastAPI with Pydantic validation
- **Flow**: Immediate ticket ID display + async email notification

## 6. Kubernetes Deployment

### Architecture
```
Namespace: customer-success-fte
├── Deployment: api (FastAPI, 3 replicas)
├── Deployment: agent-workers (2-12 replicas with KEDA)
├── StatefulSet: postgresql (pgvector enabled)
├── StatefulSet: kafka (3 brokers)
├── ConfigMap: app-config
└── Secret: api-keys, database-credentials
```

### Autoscaling (KEDA)
```yaml
triggers:
- type: kafka
  metadata:
    topic: fte.tickets.incoming
    lagThreshold: "100"  # Scale up when lag >100
```

### Resource Allocation
- API pods: 500m-1000m CPU, 512Mi-1Gi memory
- Worker pods: 1000m-2000m CPU, 1Gi-2Gi memory
- PostgreSQL: 1000m-2000m CPU, 2Gi-4Gi memory

### Graceful Shutdown
```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 30"]
terminationGracePeriodSeconds: 60
```

## Constitution Compliance

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Multi-Channel Architecture | ✅ | Gmail/Twilio/Web Form handlers with channel-specific formatting |
| II. Production-First | ✅ | Health checks, retry logic, graceful degradation |
| III. Event-Driven | ✅ | Kafka topics, idempotency, correlation IDs |
| IV. Database-as-CRM | ✅ | PostgreSQL schema with pgvector |
| V. Agent Autonomy | ✅ | OpenAI SDK with explicit constraints |
| VI. Testing Discipline | ⚠️ Pending | Test strategy defined, implementation in tasks phase |
| VII. Channel Security | ✅ | Webhook signature validation, input sanitization |
| VIII. Deployment-Ready | ✅ | Kubernetes manifests, HPA with KEDA |

## Performance Budget

| Requirement | Target | Architecture Support |
|-------------|--------|---------------------|
| Agent Response | <3s | Async operations, connection pooling |
| KB Search | <500ms p95 | pgvector HNSW index |
| DB Queries | <100ms p95 | B-tree indexes, asyncpg pool |
| Kafka Lag | <10s | KEDA autoscaling on lag >100 |

## Cost Estimation

| Service | Configuration | Annual Cost |
|---------|--------------|-------------|
| Kubernetes | 3 nodes (4 vCPU, 16GB) | $500 |
| OpenAI API | ~500k tokens/month | $600 |
| Twilio WhatsApp | ~5k messages/month | $50 |
| Gmail API | Free tier | $0 |
| Domain + SSL | Standard | $50 |
| **Total** | | **$1,200/year** |

**vs. Human FTE**: $75,000/year → **98.4% cost reduction**

## Next Steps

### Phase 1: Data Model Design
1. Create detailed entity relationship diagrams
2. Define API contracts in contracts/
3. Write quickstart implementation guide

### Phase 2: Task Generation
1. Run /sp.tasks for actionable development tasks
2. Prioritize: DB schema → Kafka → FastAPI → Agent
3. Define test cases (unit, integration, E2E)

### Critical Files for Implementation
1. `backend/src/main.py` - FastAPI app entry point
2. `backend/src/services/database.py` - asyncpg pool + pgvector queries
3. `backend/src/agent/agent_worker.py` - OpenAI Agents SDK implementation
4. `infrastructure/kubernetes/agent-workers.yaml` - KEDA autoscaling config
5. `backend/src/webhooks/twilio.py` - Pattern for all webhook handlers
