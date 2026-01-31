<!--
Sync Impact Report:
- Version change: template → 1.0.0
- New constitution created with 8 core principles
- Added sections: Channel-Specific Standards, Operational Requirements
- Templates requiring updates:
  ✅ .specify/templates/spec-template.md (channel requirements added)
  ✅ .specify/templates/plan-template.md (constitution check updated)
  ✅ .specify/templates/tasks-template.md (testing discipline aligned)
- Follow-up TODOs: None
-->

# Customer Success Digital FTE Constitution

## Core Principles

### I. Multi-Channel Architecture

All customer interactions MUST support three communication channels with channel-specific
response formatting:

- **Email (Gmail)**: Formal, detailed responses with proper greeting and signature. Maximum
  500 words. Include ticket reference and clear next steps.
- **WhatsApp**: Concise, conversational tone. Prefer responses under 300 characters. Break
  longer responses into multiple messages at natural boundaries.
- **Web Form**: Semi-formal, helpful tone. Balance detail with readability. Maximum 300 words.

**Rationale**: Customers expect different communication styles based on channel. Email users
tolerate longer, formal responses; WhatsApp users expect instant, concise answers. Failing to
adapt tone creates friction and reduces satisfaction.

**Requirements**:
- All agent tools MUST accept `channel` parameter
- Response formatting MUST be channel-aware before delivery
- Message storage MUST track source channel for analytics
- Cross-channel conversation continuity MUST be maintained via unified customer ID

### II. Production-First Development

Build for 24/7 autonomous operation. All components MUST handle failures gracefully without
manual intervention.

**Non-Negotiable Requirements**:
- **Error Handling**: Every external API call MUST have try/catch with fallback behavior
- **Retry Logic**: Transient failures (network, rate limits) MUST retry with exponential
  backoff
- **Graceful Degradation**: If knowledge base unavailable, agent MUST escalate rather than
  hallucinate
- **Structured Logging**: All operations MUST log to stdout/stderr in JSON format with
  correlation IDs
- **Observability**: Expose metrics (latency, error rate, escalation rate) via /metrics
  endpoint

**Rationale**: A production FTE cannot rely on humans to restart failed processes or debug
issues. The system must self-heal or fail safely to human escalation.

### III. Event-Driven Design

Use Kafka for ALL inter-component communication to enable asynchronous processing, replay,
and horizontal scaling.

**Architecture Requirements**:
- All channel inputs (Gmail, WhatsApp, Web Form) MUST publish to Kafka topics
- Agent workers MUST consume from unified `fte.tickets.incoming` topic
- Responses MUST publish to channel-specific outbound topics for delivery workers
- Messages MUST be idempotent (safe to process multiple times)
- Each message MUST include correlation ID for distributed tracing

**Topic Schema**:
```
fte.tickets.incoming      # Unified intake from all channels
fte.channels.email.*      # Email-specific events
fte.channels.whatsapp.*   # WhatsApp-specific events
fte.channels.webform.*    # Web form-specific events
fte.escalations           # Human intervention required
fte.metrics               # Performance and business metrics
fte.dlq                   # Failed messages for investigation
```

**Rationale**: Synchronous request-response patterns create tight coupling and single points
of failure. Kafka enables replay for debugging, independent scaling of components, and
audit trail for compliance.

### IV. Database-as-CRM

PostgreSQL serves as the custom CRM/ticket management system. Track ALL customer
interactions across channels in a unified data model.

**Schema Requirements**:
- **Customers**: Unified table with unique ID, support multiple identifiers (email, phone)
- **Customer Identifiers**: Junction table for cross-channel matching (email, phone, WhatsApp)
- **Conversations**: Track dialogue threads with initial channel and any channel switches
- **Messages**: Store all inbound/outbound messages with channel metadata
- **Tickets**: Support tickets with source channel, category, priority, resolution status
- **Knowledge Base**: Product documentation with vector embeddings (pgvector) for semantic
  search

**Data Integrity Rules**:
- Customer email MUST be unique when present
- Every message MUST reference a conversation
- Every conversation MUST reference a customer
- Ticket creation MUST precede first agent response
- Channel message IDs (Gmail message ID, Twilio SID) MUST be stored for deduplication

**Rationale**: External CRMs (Salesforce, HubSpot) add cost and integration complexity. A
custom PostgreSQL schema provides full control, enables vector search for AI, and teaches
fundamental data modeling.

### V. Agent Autonomy with Guardrails

Use OpenAI Agents SDK with strict behavioral constraints to prevent harmful actions.

**Hard Constraints (NEVER violate)**:
- NEVER discuss pricing → escalate immediately with reason "pricing_inquiry"
- NEVER process refunds → escalate with reason "refund_request"
- NEVER promise features not in documentation
- NEVER share internal processes, system architecture, or database details
- NEVER respond without using `send_response` tool (ensures channel formatting)
- NEVER exceed response length limits per channel

**Required Workflow (ALWAYS follow in order)**:
1. FIRST: Call `create_ticket` to log interaction (includes channel)
2. THEN: Call `get_customer_history` to check prior context across ALL channels
3. THEN: Call `search_knowledge_base` if product questions arise
4. FINALLY: Call `send_response` to reply via appropriate channel

**Escalation Triggers (MUST escalate when detected)**:
- Customer mentions "lawyer", "legal", "sue", or "attorney"
- Customer uses profanity or aggressive language (sentiment < 0.3)
- Cannot find relevant information after 2 search attempts
- Customer explicitly requests human help ("talk to a person", "human agent")
- WhatsApp customer sends "human", "agent", or "representative"

**Rationale**: Autonomous agents without guardrails can cause business harm (incorrect
pricing quotes, legal liability). Explicit constraints prevent these failure modes while
maintaining high autonomy for routine tasks.

### VI. Testing Discipline

Test-driven development with comprehensive test coverage across all layers.

**Testing Requirements**:
- **Unit Tests**: All `@function_tool` definitions MUST have unit tests with mocked
  dependencies
- **Integration Tests**: Channel handlers (Gmail, WhatsApp, Web Form) MUST have integration
  tests with real API calls to staging environments
- **End-to-End Tests**: Complete multi-channel flows MUST be tested (message in → agent
  processing → response out)
- **Edge Case Tests**: All edge cases discovered during incubation phase MUST have
  regression tests

**Test Phases**:
1. **Red**: Write failing test for new functionality
2. **Green**: Implement minimum code to pass test
3. **Refactor**: Improve code while keeping tests green

**Coverage Targets**:
- Tool functions: 90% coverage minimum
- Channel handlers: 80% coverage minimum
- Agent workflows: Critical paths must have E2E tests

**Rationale**: Production systems without tests accumulate technical debt and fear of
changing code. TDD ensures confidence when iterating and prevents regressions.

### VII. Channel-Aware Security

Validate all external inputs and protect sensitive customer data across all channels.

**Security Requirements**:
- **Webhook Validation**: MUST verify signatures on all webhooks (Gmail Pub/Sub, Twilio)
- **Input Sanitization**: MUST sanitize all customer inputs from all channels before
  processing
- **Credential Management**: MUST store all API keys/secrets in environment variables, NEVER
  in code
- **Data Protection**: MUST NOT log sensitive data (full email content, phone numbers, PII)
- **Channel Isolation**: MUST prevent cross-channel data leakage (WhatsApp message cannot
  leak into email response)

**Audit Requirements**:
- Log all authentication attempts (webhook signature verification)
- Log all escalations with sanitized context
- Log all tool calls with sanitized inputs/outputs

**Rationale**: Multi-channel systems have larger attack surface. Each channel (email,
WhatsApp, web form) is a potential entry point for malicious input. Defense-in-depth
prevents single-point security failures.

### VIII. Deployment-Ready Infrastructure

Kubernetes-native design for production deployment, scaling, and reliability.

**Infrastructure Requirements**:
- **Health Checks**: All services MUST expose `/health` endpoint (liveness) and `/ready`
  (readiness)
- **Resource Limits**: All pods MUST define CPU/memory requests and limits
- **Autoscaling**: Agent workers MUST support horizontal pod autoscaling based on Kafka lag
- **Graceful Shutdown**: All services MUST handle SIGTERM and complete in-flight work
- **Container Security**: Use minimal base images (Alpine, distroless), run as non-root user

**Deployment Artifacts**:
- Dockerfile with multi-stage builds (build → runtime)
- Kubernetes manifests (Deployment, Service, ConfigMap, Secret)
- Helm charts for parameterized deployments (dev, staging, prod)
- CI/CD pipelines for automated testing and deployment

**Monitoring Requirements**:
- Prometheus metrics for all services
- Distributed tracing with correlation IDs
- Structured logging aggregated to central system (ELK, Loki)

**Rationale**: Manual deployments and lacking observability prevent scaling beyond demo
phase. Kubernetes provides production-grade orchestration, and proper monitoring enables
troubleshooting in production.

## Channel-Specific Standards

### Email (Gmail) Standards

- **Response Time SLA**: Initial response within 5 minutes, full resolution within 24 hours
- **Formatting**: Use proper email etiquette (greeting, body, signature, ticket reference)
- **Threading**: Preserve email threads via `thread_id` to maintain conversation context
- **Attachments**: Support parsing attachments (receipts, screenshots) for context
- **Deduplication**: Check `channel_message_id` (Gmail message ID) to prevent duplicate
  processing

### WhatsApp Standards

- **Response Time SLA**: Initial response within 2 minutes (users expect instant messaging)
- **Message Length**: Prefer responses under 300 characters; split longer content into
  multiple messages
- **Formatting**: Use WhatsApp formatting (bold, italic, lists) for clarity
- **Read Receipts**: Track message delivery status (queued, sent, delivered, read)
- **Session Timeout**: 24-hour session window for free-form responses; use templates after
  expiry

### Web Form Standards

- **Response Time SLA**: Acknowledge submission within 30 seconds, initial response within
  5 minutes
- **Ticket ID**: Provide ticket ID immediately after submission for customer reference
- **Email Notification**: Send email notification with response even though submitted via web
- **Status Tracking**: Provide status endpoint `/ticket/{ticket_id}` for customers to check
  progress
- **Validation**: Validate all form inputs (email format, required fields, length limits)
  before acceptance

## Operational Requirements

### Performance Targets

- **Agent Response Time**: <3 seconds processing time (not including external API latency)
- **Knowledge Base Search**: <500ms for semantic vector search (p95)
- **Database Queries**: <100ms for customer/ticket lookups (p95)
- **Kafka Message Lag**: <10 seconds under normal load
- **Overall SLA**: 95% of customer messages handled within channel-specific SLA

### Reliability Targets

- **Uptime**: 99.5% uptime (43.8 hours downtime per year allowed)
- **Error Rate**: <1% of messages result in processing errors
- **Escalation Rate**: <20% of conversations escalated to humans (target: autonomous
  resolution)
- **Accuracy**: >85% of agent responses marked helpful by customers

### Cost Targets

- **Model Costs**: <$1,000/year for OpenAI API usage (vs $75,000/year human FTE)
- **Infrastructure**: <$500/year for Kubernetes cluster (dev/staging/prod)
- **Total**: <$2,000/year operational costs

## Governance

### Amendment Process

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Validate change against current principles and production systems
3. **Version Bump**: Update version per semantic versioning (MAJOR.MINOR.PATCH)
4. **Template Sync**: Update all dependent templates (spec, plan, tasks)
5. **Migration Plan**: If existing code affected, create migration tasks
6. **Approval**: Document approval with date and approver
7. **Commit**: Update constitution with version bump and amendment date

### Versioning Policy

- **MAJOR**: Backward-incompatible governance changes (removing principles, changing core
  architecture)
- **MINOR**: New principles added or material expansions to existing guidance
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

### Compliance Review

- All feature specifications MUST reference relevant constitutional principles
- All implementation plans MUST include "Constitution Check" section validating compliance
- All pull requests MUST verify adherence to principles before merge
- Violations MUST be justified with "Complexity Tracking" section documenting why simpler
  alternatives were rejected

### Guidance

For detailed development workflows, see:
- `.claude/commands/sp.*.md` for SDD command documentation
- `CLAUDE.md` for agent-specific development guidelines
- `README.md` for quickstart and architecture overview

**Version**: 1.0.0 | **Ratified**: 2026-01-31 | **Last Amended**: 2026-01-31
