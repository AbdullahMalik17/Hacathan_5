# Implementation Plan: Customer Success Digital FTE

**Branch**: `001-customer-success-fte` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-customer-success-fte/spec.md`

## Summary

Build production-grade Customer Success Digital FTE operating 24/7 across three communication channels (Email via Gmail, WhatsApp via Twilio, Web Form). Technical approach: FastAPI webhooks → Kafka event streaming → OpenAI Agents SDK workers → PostgreSQL with pgvector → Channel-specific responses. Deploy on Kubernetes with KEDA autoscaling.

**Key Metrics**: <3s response time, 80% autonomous resolution, 99.5% uptime, <$2K/year cost

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.115+, OpenAI Agents SDK, asyncpg, confluent-kafka, Pydantic v2
**Storage**: PostgreSQL 16+ with pgvector extension
**Testing**: pytest with async support, pytest-asyncio
**Target Platform**: Kubernetes (Minikube local, cloud production)
**Project Type**: Web application (backend API + frontend form)
**Performance Goals**: <3s agent processing, <500ms knowledge base search, 1000 concurrent conversations
**Constraints**: <100ms DB queries (p95), <10s Kafka lag, channel-specific response times (2min WhatsApp, 5min email)
**Scale/Scope**: 10,000 tickets/month, 100+ knowledge base articles, 12 max concurrent agent workers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Multi-Channel Architecture
✅ **PASS**: Three channels (Gmail, WhatsApp, Web Form) with dedicated handlers in `backend/src/webhooks/`. Channel-specific formatters in `backend/src/agent/formatters.py`.

### Principle II: Production-First Development
✅ **PASS**: Health checks (`/health`, `/ready`), structured logging (JSON to stdout), retry logic (exponential backoff), graceful degradation (escalate on KB failure).

### Principle III: Event-Driven Design
✅ **PASS**: Kafka topics defined (`fte.tickets.incoming`, `fte.channels.*`), idempotency via `processed_messages` table, correlation IDs in all messages.

### Principle IV: Database-as-CRM
✅ **PASS**: PostgreSQL schema with `customers`, `customer_identifiers`, `conversations`, `tickets`, `messages`, `knowledge_base`. pgvector for semantic search.

### Principle V: Agent Autonomy with Guardrails
✅ **PASS**: OpenAI Agents SDK with explicit workflow constraints. Hard-coded escalation triggers (pricing, refund, legal keywords). Required tool execution order enforced.

### Principle VI: Testing Discipline
⚠️ **PENDING**: Test strategy defined (unit, integration, E2E). Implementation deferred to task generation phase (`/sp.tasks`).

### Principle VII: Channel-Aware Security
✅ **PASS**: Webhook signature validation (Gmail JWT, Twilio X-Twilio-Signature). Input sanitization in `backend/src/utils/sanitization.py`. Environment variables for all secrets.

### Principle VIII: Deployment-Ready Infrastructure
✅ **PASS**: Kubernetes manifests in `infrastructure/kubernetes/`. KEDA autoscaling on Kafka lag. Health/readiness probes. ConfigMaps/Secrets for config management.

**Overall Status**: ✅ **7/8 PASS**, 1 pending (Testing implementation in tasks phase)

## Project Structure

### Documentation (this feature)

```text
specs/001-customer-success-fte/
├── spec.md              # Feature requirements (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Technical architecture research (completed)
├── data-model.md        # Entity relationship design (completed)
├── quickstart.md        # Local development guide (completed)
├── contracts/
│   └── openapi.yaml     # API contract definitions (completed)
├── checklists/
│   └── requirements.md  # Spec quality validation (completed)
└── tasks.md             # Actionable development tasks (next: /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                      # FastAPI app initialization
│   ├── config.py                    # Environment configuration
│   ├── webhooks/
│   │   ├── __init__.py
│   │   ├── gmail.py                 # Gmail Pub/Sub webhook handler
│   │   ├── twilio.py                # Twilio WhatsApp webhook handler
│   │   └── webform.py               # Web form submission endpoint
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── customer_success_agent.py  # OpenAI Agents SDK implementation
│   │   ├── tools.py                 # @function_tool definitions
│   │   ├── prompts.py               # Agent system prompts
│   │   └── formatters.py            # Channel-specific response formatting
│   ├── workers/
│   │   ├── __init__.py
│   │   └── message_processor.py     # Kafka consumer + agent runner
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py              # asyncpg connection pool + queries
│   │   ├── kafka_producer.py        # Kafka message publishing
│   │   ├── auth.py                  # Webhook signature validation
│   │   └── channels/
│   │       ├── gmail_client.py      # Gmail API integration
│   │       └── twilio_client.py     # Twilio API integration
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── correlation_id.py        # Request correlation ID injection
│   │   └── logging.py               # Structured JSON logging
│   ├── utils/
│   │   ├── __init__.py
│   │   └── sanitization.py          # Input sanitization (XSS, SQL injection)
│   └── models/
│       ├── __init__.py
│       ├── customer.py              # Pydantic models
│       ├── ticket.py
│       └── message.py
├── tests/
│   ├── unit/
│   │   ├── test_tools.py
│   │   ├── test_formatters.py
│   │   └── test_sanitization.py
│   ├── integration/
│   │   ├── test_gmail_handler.py
│   │   ├── test_twilio_handler.py
│   │   └── test_database.py
│   └── e2e/
│       └── test_multi_channel_flow.py
├── requirements.txt
├── Dockerfile
└── .env.example

frontend/
├── src/
│   ├── components/
│   │   └── SupportForm.tsx          # React Hook Form + Zod validation
│   ├── pages/
│   │   └── support.tsx              # Support form page
│   └── api/
│       └── support.ts               # API client
├── public/
├── package.json
├── tsconfig.json
└── next.config.js

database/
├── schema.sql                       # PostgreSQL schema with pgvector
├── migrations/
│   └── 001_initial_schema.sql
└── seeds/
    └── knowledge_base_seed.sql      # Sample product documentation

infrastructure/
├── kubernetes/
│   ├── deployments/
│   │   ├── api.yaml                 # FastAPI webhook server
│   │   ├── agent-workers.yaml       # Kafka consumers with KEDA scaling
│   │   ├── postgresql.yaml          # StatefulSet with pgvector
│   │   └── kafka.yaml               # StatefulSet with 3 brokers
│   ├── services/
│   │   ├── api-service.yaml         # LoadBalancer for webhooks
│   │   └── postgresql-service.yaml
│   ├── configmaps/
│   │   └── app-config.yaml          # Non-sensitive configuration
│   ├── secrets/
│   │   ├── api-keys.yaml            # OpenAI, Twilio (encrypted)
│   │   └── database-credentials.yaml
│   └── hpa/
│       └── keda-scaledobject.yaml   # KEDA autoscaling config
└── docker-compose.yml               # Local development infrastructure

scripts/
├── seed_knowledge_base.py           # Populate KB with embeddings
├── test_kafka.py                    # Kafka producer/consumer test
└── generate_twilio_signature.py     # Test signature generation
```

**Structure Decision**: Web application structure (backend + frontend) selected because requirements specify:
- Backend API for webhooks (Gmail, Twilio, Web Form)
- Frontend web form component (React/Next.js)
- Clear separation of concerns: API layer, agent processing, database access

## Complexity Tracking

*No violations - all architecture decisions align with constitution principles.*

## Phase 0: Research (COMPLETED)

**Artifacts**: [research.md](./research.md)

**Key Decisions Documented**:
1. ✅ OpenAI Agents SDK with @function_tool decorators
2. ✅ PostgreSQL 16+ with pgvector HNSW index
3. ✅ Kafka event streaming with 12 partitions (customer_id keying)
4. ✅ FastAPI with async handlers and Pydantic v2 validation
5. ✅ Gmail Pub/Sub, Twilio webhooks, React Hook Form
6. ✅ Kubernetes with KEDA autoscaling on Kafka lag

## Phase 1: Design (COMPLETED)

### Data Model
**Artifact**: [data-model.md](./data-model.md)

**Entities Designed**:
- ✅ Customer (unified identity across channels)
- ✅ Customer_Identifier (cross-channel matching)
- ✅ Conversation (dialogue threads with sentiment)
- ✅ Ticket (support requests with categorization)
- ✅ Message (all inbound/outbound with deduplication)
- ✅ Knowledge_Base (documentation with vector embeddings)
- ✅ Processed_Messages (idempotency table)

**Query Patterns**: Optimized for customer lookup, history retrieval, semantic search

### API Contracts
**Artifact**: [contracts/openapi.yaml](./contracts/openapi.yaml)

**Endpoints Defined**:
- ✅ `POST /webhooks/gmail/pubsub` - Gmail push notifications
- ✅ `POST /webhooks/twilio/whatsapp` - Twilio WhatsApp incoming
- ✅ `POST /api/support/submit` - Web form submission
- ✅ `GET /api/ticket/{ticket_id}` - Ticket status lookup
- ✅ `GET /health` - Liveness probe
- ✅ `GET /ready` - Readiness probe

### Quickstart Guide
**Artifact**: [quickstart.md](./quickstart.md)

**Local Development Setup**:
- ✅ Prerequisites listed (Python 3.11+, Docker, API keys)
- ✅ Environment variable configuration
- ✅ Docker Compose for PostgreSQL + Kafka
- ✅ Backend API startup instructions
- ✅ Agent worker execution
- ✅ Frontend development server
- ✅ Testing procedures for all three channels

## Phase 2: Implementation Tasks (NEXT)

**Command**: `/sp.tasks`

**Expected Output**: `specs/001-customer-success-fte/tasks.md` with:
- Setup tasks (project initialization, dependencies)
- Foundational tasks (database schema, Kafka topics)
- User Story 1 tasks (Email channel - P1 MVP)
- User Story 2 tasks (WhatsApp channel - P1 MVP)
- User Story 3 tasks (Web form - P2)
- User Story 4 tasks (Cross-channel continuity - P2)
- User Story 5 tasks (Escalation handling - P3)
- Testing tasks (unit, integration, E2E)
- Deployment tasks (Kubernetes manifests, KEDA config)

**Task Prioritization**: MVP first (US1 + US2 for email and WhatsApp channels), then web form, then cross-channel features

## Post-Phase 1 Constitution Re-Check

*Re-evaluating gates after design completion:*

### Principle I: Multi-Channel Architecture
✅ **PASS**: Confirmed via webhook handlers in project structure, channel formatters in data model

### Principle II: Production-First Development
✅ **PASS**: Confirmed via health endpoints in API contract, graceful shutdown in Kubernetes manifests

### Principle III: Event-Driven Design
✅ **PASS**: Confirmed via Kafka topic schema in research.md, idempotency table in data-model.md

### Principle IV: Database-as-CRM
✅ **PASS**: Confirmed via complete schema in data-model.md with all required entities

### Principle V: Agent Autonomy with Guardrails
✅ **PASS**: Confirmed via OpenAI Agents SDK pattern in research.md, escalation triggers in spec.md

### Principle VI: Testing Discipline
⚠️ **PENDING**: Test directory structure defined, test cases pending task generation

### Principle VII: Channel-Aware Security
✅ **PASS**: Confirmed via webhook signature validation in API contracts, sanitization utility in project structure

### Principle VIII: Deployment-Ready Infrastructure
✅ **PASS**: Confirmed via complete Kubernetes manifests structure, KEDA autoscaling defined

**Overall Post-Design Status**: ✅ **7/8 PASS**, 1 pending (unchanged from pre-research)

## Critical Implementation Paths

### Path 1: Core Agent Infrastructure (Weeks 1-2)
**Dependencies**: None (foundational)
**Files**:
1. `database/schema.sql` - PostgreSQL schema creation
2. `backend/src/services/database.py` - asyncpg connection pool
3. `backend/src/agent/tools.py` - @function_tool definitions
4. `backend/src/agent/customer_success_agent.py` - OpenAI Agents SDK agent

**Why Critical**: All other components depend on working database and agent logic

### Path 2: Event Streaming Layer (Weeks 2-3)
**Dependencies**: Path 1 (database for idempotency)
**Files**:
1. `backend/src/services/kafka_producer.py` - Message publishing
2. `backend/src/workers/message_processor.py` - Kafka consumer + agent runner
3. `infrastructure/docker-compose.yml` - Kafka cluster setup

**Why Critical**: Decouples webhook intake from agent processing, enables scaling

### Path 3: Channel Integrations (Weeks 3-4)
**Dependencies**: Path 2 (Kafka for message routing)
**Files**:
1. `backend/src/webhooks/gmail.py` - Gmail Pub/Sub handler
2. `backend/src/webhooks/twilio.py` - Twilio WhatsApp handler
3. `backend/src/webhooks/webform.py` - Web form submission
4. `frontend/src/components/SupportForm.tsx` - React form

**Why Critical**: User-facing entry points, must be production-ready

### Path 4: Deployment Infrastructure (Weeks 4-5)
**Dependencies**: Paths 1-3 (working application)
**Files**:
1. `infrastructure/kubernetes/deployments/api.yaml`
2. `infrastructure/kubernetes/deployments/agent-workers.yaml`
3. `infrastructure/kubernetes/hpa/keda-scaledobject.yaml`
4. `Dockerfile` - Multi-stage build

**Why Critical**: Enables 24/7 operation, autoscaling, fault tolerance

## Risk Mitigation Strategies

| Risk | Mitigation Approach | Implementation |
|------|-------------------|----------------|
| Knowledge base returns irrelevant results | Similarity threshold + feedback loop | Set threshold 0.7, escalate if <0.6, track escalation reasons |
| OpenAI API rate limits delay processing | Request queuing + fallback models | Implement exponential backoff, fallback to GPT-3.5-turbo |
| Kafka rebalancing disrupts message flow | Partition strategy + cooldown | Max replicas = partitions (12), 5min cooldown period |
| Cross-channel matching fails | Probabilistic matching + manual merge | Confidence scores >0.8 for auto-merge, UI for manual review |
| Webhook delivery failures | Health monitoring + polling fallback | Alert on-call team, implement polling as backup |

## Performance Validation Criteria

**Before Production Deployment**, validate against constitution NFRs:

- [ ] **NFR-001**: p95 message processing latency <3 seconds (load test with 100 concurrent messages)
- [ ] **NFR-002**: p95 knowledge base search <500ms (test with 1000+ documents)
- [ ] **NFR-003**: p95 database queries <100ms (test customer lookup across channels)
- [ ] **NFR-004**: System handles 1000 concurrent conversations (stress test with JMeter)
- [ ] **NFR-005**: Kafka message lag <10 seconds under normal load (monitor with Prometheus)

**Validation Tools**:
- Locust for load testing
- Prometheus + Grafana for metrics monitoring
- OpenTelemetry for distributed tracing
- pgBench for PostgreSQL performance testing

## Success Metrics (Aligned with Spec)

**Launch Criteria** (from spec.md Success Criteria):

- [ ] **SC-001**: Response SLAs met (Email 5min, WhatsApp 2min, Web Form 5min)
- [ ] **SC-002**: 80% autonomous resolution rate (measured over 100 test tickets)
- [ ] **SC-003**: Agent processing <3s (p95 latency)
- [ ] **SC-004**: 95% customer satisfaction (feedback mechanism required)
- [ ] **SC-005**: 99.5% uptime (health checks + alerts configured)
- [ ] **SC-006**: 95% cross-channel identification accuracy (test with 50 cross-channel scenarios)
- [ ] **SC-007**: Knowledge base relevance 90% (similarity >=0.7 for product questions)
- [ ] **SC-008**: Human escalation acknowledged <15min (queue monitoring required)
- [ ] **SC-009**: Operating costs <$1,000/year AI + <$2,000/year total (track monthly)
- [ ] **SC-010**: 1000 concurrent conversations supported (load test validated)
- [ ] **SC-011**: Zero data leakage incidents (security audit passed)
- [ ] **SC-012**: 90% ticket tracking via ticket ID (API endpoint functional)

## Next Actions

1. ✅ **Phase 0 Complete**: Research document created with all architectural decisions
2. ✅ **Phase 1 Complete**: Data model, API contracts, quickstart guide created
3. ⏭️ **Run `/sp.tasks`**: Generate actionable development tasks from this plan
4. ⏭️ **Create ADRs**: Document significant decisions (OpenAI SDK, Kafka, Kubernetes)
5. ⏭️ **Begin Implementation**: Start with Path 1 (Core Agent Infrastructure)

---

**Plan Status**: ✅ **COMPLETE** - Ready for task generation phase
**Constitution Compliance**: 7/8 principles validated, 1 pending implementation
**Performance Budget**: Defined and measurable
**Risk Mitigation**: Identified and documented
**Next Command**: `/sp.tasks` to generate implementation tasks
