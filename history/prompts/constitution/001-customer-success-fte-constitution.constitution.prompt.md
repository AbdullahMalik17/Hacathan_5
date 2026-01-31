---
id: 001
title: Customer Success FTE Constitution
stage: constitution
date: 2026-01-31
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: developer
command: /sp.constitution
labels: ["constitution", "hackathon", "multi-channel", "production-architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitution document)
---

## Prompt

Create constitution for Customer Success FTE Hackathon Project with these principles:

1. **Multi-Channel Architecture**: All customer interactions must support three channels (Gmail, WhatsApp, Web Form) with channel-specific response formatting. Email responses are formal and detailed, WhatsApp is concise and conversational, Web Form is semi-formal.

2. **Production-First Development**: Build for 24/7 operation with proper error handling, retry logic, graceful degradation, and monitoring. All components must be production-ready with structured logging and observability.

3. **Event-Driven Design**: Use Kafka for all inter-component communication. All channel inputs publish to Kafka topics, agent workers consume from unified topics, maintain idempotency for message processing.

4. **Database-as-CRM**: PostgreSQL serves as the custom CRM/ticket management system. Track customers unified across channels, conversations with channel metadata, tickets with source channel, and knowledge base with vector embeddings for semantic search.

5. **Agent Autonomy with Guardrails**: OpenAI Agents SDK with strict constraints. NEVER discuss pricing or process refunds (escalate), NEVER promise features not in documentation, ALWAYS create ticket before responding, ALWAYS check customer history across all channels, escalate when sentiment negative or customer requests human.

6. **Testing Discipline**: Test-driven development with unit tests for tools, integration tests for channel handlers, end-to-end tests for multi-channel flows. Test edge cases discovered during incubation phase.

7. **Channel-Aware Security**: Validate all webhook signatures (Gmail Pub/Sub, Twilio). Sanitize inputs from all channels. Store credentials in environment variables. Never log sensitive customer data.

8. **Deployment-Ready Infrastructure**: Kubernetes-native design with health checks, resource limits, autoscaling. Docker containers with minimal attack surface. Infrastructure as code for reproducible deployments.

Project Name: Customer Success Digital FTE
Version: 1.0.0
Ratified: 2026-01-31

## Response snapshot

Created comprehensive constitution with 8 core principles, 2 additional sections (Channel-Specific Standards, Operational Requirements), and complete governance framework.

Constitution includes:
- **Principle I**: Multi-Channel Architecture (Gmail, WhatsApp, Web Form) with channel-specific formatting requirements
- **Principle II**: Production-First Development with error handling, retry logic, graceful degradation, structured logging
- **Principle III**: Event-Driven Design using Kafka for all inter-component communication with defined topic schema
- **Principle IV**: Database-as-CRM using PostgreSQL with unified customer tracking, conversations, tickets, knowledge base with pgvector
- **Principle V**: Agent Autonomy with Guardrails using OpenAI Agents SDK with hard constraints and required workflow
- **Principle VI**: Testing Discipline with TDD, unit/integration/E2E tests, 90% coverage targets
- **Principle VII**: Channel-Aware Security with webhook validation, input sanitization, credential management
- **Principle VIII**: Deployment-Ready Infrastructure with Kubernetes, health checks, autoscaling, monitoring

Additional sections:
- **Channel-Specific Standards**: Email/WhatsApp/Web Form SLAs, formatting, deduplication requirements
- **Operational Requirements**: Performance targets (<3s response), reliability (99.5% uptime), cost targets (<$2K/year)

Governance includes amendment process, versioning policy, compliance review requirements.

## Outcome

- ✅ Impact: Constitution v1.0.0 established with 8 production-ready principles for Customer Success FTE hackathon
- 🧪 Tests: N/A (governance document)
- 📁 Files: Created .specify/memory/constitution.md (305 lines)
- 🔁 Next prompts: /sp.specify to create feature specification based on constitutional principles
- 🧠 Reflection: Constitution provides clear architectural direction for multi-channel, production-grade agent system. All principles are testable and measurable. Ready to guide spec and plan creation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation - PASS (all placeholders filled, principles declarative and testable, version/dates correct)
- Prompt variant (if applicable): v1-initial-constitution
- Next experiment (smallest change to try): Create feature specification to validate constitutional principles apply cleanly to user stories
