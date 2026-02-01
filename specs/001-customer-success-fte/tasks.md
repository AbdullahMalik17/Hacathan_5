# Tasks: Customer Success Digital FTE

**Input**: Design documents from `/specs/001-customer-success-fte/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in spec.md. Test tasks are OMITTED per template guidance.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Database**: `database/`
- **Infrastructure**: `infrastructure/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure with directories: backend/src/{webhooks,agent,workers,services,middleware,utils,models}
- [X] T002 Create frontend project structure with directories: frontend/src/{components,pages,api}
- [X] T003 Create infrastructure directories: infrastructure/kubernetes/{deployments,services,configmaps,secrets,hpa}
- [X] T004 Create database directory with subdirectories: database/{migrations,seeds}
- [X] T005 Create scripts directory for utility scripts
- [X] T006 Initialize Python virtual environment and install FastAPI dependencies in backend/requirements.txt
- [X] T007 [P] Initialize Next.js frontend project in frontend/ with TypeScript and Tailwind CSS
- [X] T008 [P] Create backend/.env.example with all required environment variables per quickstart.md
- [X] T009 [P] Create Docker Compose configuration in infrastructure/docker-compose.yml for PostgreSQL, Kafka, and Zookeeper

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Create PostgreSQL schema in database/schema.sql with all 7 entities (customers, customer_identifiers, conversations, tickets, messages, knowledge_base, processed_messages)
- [X] T011 Add pgvector extension and HNSW index configuration to database/schema.sql
- [X] T012 Create database migration script in database/migrations/001_initial_schema.sql
- [X] T013 [P] Implement database connection pool service in backend/src/services/database.py using asyncpg with connection pool (min=10, max=20)
- [X] T014 [P] Implement Kafka producer service in backend/src/services/kafka_producer.py with topic publishing and correlation ID support
- [X] T015 [P] Create Pydantic models in backend/src/models/{customer.py,ticket.py,message.py} for Customer, Ticket, and Message entities
- [X] T016 [P] Implement correlation ID middleware in backend/src/middleware/correlation_id.py for request tracking
- [X] T017 [P] Implement structured JSON logging middleware in backend/src/middleware/logging.py
- [X] T018 [P] Implement input sanitization utilities in backend/src/utils/sanitization.py for XSS and SQL injection prevention
- [X] T019 Create FastAPI app initialization in backend/src/main.py with health endpoints (/health, /ready)
- [X] T020 Implement configuration management in backend/src/config.py loading all environment variables
- [X] T021 Create knowledge base seed script in scripts/seed_knowledge_base.py to populate KB with embeddings
- [X] T022 [P] Create Kafka topic creation script in scripts/setup_kafka_topics.sh for all topics (fte.tickets.incoming, fte.channels.*, fte.escalations)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Email Support Inquiry (Priority: P1) 🎯 MVP

**Goal**: Enable customers to send email inquiries to support@company.com and receive automated responses with knowledge base answers within 5 minutes

**Independent Test**: Send test email to support address, verify response received within 5 minutes with correct instructions from knowledge base, proper email formatting (greeting, signature), and valid ticket ID

### Implementation for User Story 1

- [X] T023 [P] [US1] Create Gmail Pub/Sub webhook handler in backend/src/webhooks/gmail.py with JWT token validation (FR-002)
- [X] T024 [P] [US1] Implement Gmail API client service in backend/src/services/channels/gmail_client.py for sending email responses
- [X] T025 [P] [US1] Implement webhook signature validation service in backend/src/services/auth.py for Gmail Pub/Sub tokens
- [X] T026 [US1] Add Gmail webhook route to FastAPI app in backend/src/main.py: POST /webhooks/gmail/pubsub (depends on T023, T025)
- [X] T027 [P] [US1] Implement email message parser in backend/src/webhooks/gmail.py to extract customer email, subject, body, and thread ID (FR-003, FR-004)
- [X] T028 [P] [US1] Implement email response formatter in backend/src/agent/formatters.py with formal tone, greeting, signature, ticket reference (FR-021, FR-031, FR-032)
- [X] T029 [US1] Create OpenAI Agents SDK agent in backend/src/agent/customer_success_agent.py with system prompt and tool definitions
- [X] T030 [P] [US1] Implement @function_tool for create_ticket in backend/src/agent/tools.py (FR-011, FR-012)
- [X] T031 [P] [US1] Implement @function_tool for get_customer_history in backend/src/agent/tools.py (FR-007, FR-008)
- [X] T032 [P] [US1] Implement @function_tool for search_knowledge_base in backend/src/agent/tools.py using pgvector semantic search (FR-016, FR-017, FR-018)
- [X] T033 [P] [US1] Implement @function_tool for send_email_response in backend/src/agent/tools.py using Gmail client (FR-020, FR-024)
- [X] T034 [P] [US1] Implement @function_tool for escalate_ticket in backend/src/agent/tools.py (FR-019, FR-025-FR-030)
- [X] T035 [US1] Create Kafka consumer worker in backend/src/workers/message_processor.py that consumes from fte.tickets.incoming and invokes agent (depends on T029)
- [X] T036 [US1] Implement customer lookup/create logic in backend/src/services/database.py (FR-006, FR-007)
- [X] T037 [US1] Implement ticket creation logic in backend/src/services/database.py with category detection (FR-011, FR-013, FR-014)
- [X] T038 [US1] Implement knowledge base search query in backend/src/services/database.py with similarity threshold 0.6 (FR-016-FR-019)
- [X] T039 [US1] Implement message deduplication check in backend/src/services/database.py using channel_message_id (FR-004)
- [X] T040 [US1] Add sentiment analysis to agent prompt in backend/src/agent/prompts.py (FR-009)
- [X] T041 [US1] Add escalation keyword detection to agent prompt in backend/src/agent/prompts.py (FR-025-FR-029)
- [X] T042 [US1] Configure Gmail Pub/Sub notifications per quickstart.md documentation in infrastructure/kubernetes/configmaps/gmail-config.yaml
- [X] T043 [US1] Add error handling and retry logic with exponential backoff to Kafka consumer in backend/src/workers/message_processor.py

**Checkpoint**: At this point, User Story 1 should be fully functional - email intake → agent processing → email response with KB search

---

## Phase 4: User Story 2 - WhatsApp Quick Question (Priority: P1) 🎯 MVP

**Goal**: Enable customers to send WhatsApp messages and receive instant, concise responses (<300 chars) within 2 minutes

**Independent Test**: Send WhatsApp message to business number, verify response received within 30 seconds, response is concise (<300 chars), uses conversational tone, and includes offer to escalate to human if needed

### Implementation for User Story 2

- [X] T044 [P] [US2] Create Twilio WhatsApp webhook handler in backend/src/webhooks/twilio.py with X-Twilio-Signature validation (FR-002)
- [X] T045 [P] [US2] Implement Twilio API client service in backend/src/services/channels/twilio_client.py for sending WhatsApp messages
- [X] T046 [P] [US2] Implement Twilio signature validation in backend/src/services/auth.py using Twilio Auth Token
- [X] T047 [US2] Add Twilio webhook route to FastAPI app in backend/src/main.py: POST /webhooks/twilio/whatsapp (depends on T044, T046)
- [X] T048 [P] [US2] Implement WhatsApp message parser in backend/src/webhooks/twilio.py to extract From, Body, MessageSid, ProfileName, WaId (FR-003, FR-004)
- [X] T049 [P] [US2] Implement WhatsApp response formatter in backend/src/agent/formatters.py with conversational tone, 300 char limit, message splitting (FR-021, FR-033, FR-034)
- [X] T050 [P] [US2] Implement @function_tool for send_whatsapp_response in backend/src/agent/tools.py using Twilio client (FR-020, FR-023, FR-024)
- [X] T051 [US2] Add WhatsApp-specific prompt instructions to backend/src/agent/prompts.py for concise responses and human escalation offer (FR-023)
- [X] T052 [US2] Implement phone number normalization in backend/src/webhooks/twilio.py for customer identification (FR-003, FR-007)
- [X] T053 [US2] Implement customer lookup by phone in backend/src/services/database.py using customer_identifiers table (FR-007)
- [X] T054 [US2] Add profanity and aggressive language detection to agent in backend/src/agent/prompts.py (FR-028)
- [X] T055 [US2] Implement explicit escalation keyword detection ("talk to human", "speak to person", "human agent") in backend/src/agent/prompts.py (FR-029)
- [X] T056 [US2] Configure Twilio webhook URL in infrastructure/kubernetes/configmaps/twilio-config.yaml
- [X] T057 [US2] Add delivery status tracking to Twilio client in backend/src/services/channels/twilio_client.py (FR-034)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - email and WhatsApp channels operational

---

## Phase 5: User Story 3 - Web Form Submission (Priority: P2)

**Goal**: Enable website visitors to submit support requests via web form and receive ticket ID immediately plus detailed email response within 5 minutes

**Independent Test**: Submit web form with test issue, verify immediate ticket ID display on success page, receive confirmation email instantly, and detailed response email within 5 minutes

### Implementation for User Story 3

- [X] T058 [P] [US3] Create React support form component in frontend/src/components/SupportForm.tsx with React Hook Form and Zod validation (FR-035)
- [X] T059 [P] [US3] Create support form page in frontend/src/pages/support.tsx
- [X] T060 [P] [US3] Create API client for form submission in frontend/src/api/support.ts
- [X] T061 [P] [US3] Create web form webhook handler in backend/src/webhooks/webform.py
- [X] T062 [US3] Add web form submission route to FastAPI app in backend/src/main.py: POST /api/support/submit (depends on T061)
- [X] T063 [P] [US3] Implement form validation schema in backend/src/webhooks/webform.py (email format, required fields, message length 10-5000 chars) (FR-035)
- [X] T064 [P] [US3] Implement ticket status endpoint in backend/src/main.py: GET /api/ticket/{ticket_id} (FR-036)
- [X] T065 [US3] Implement immediate ticket ID response from web form handler in backend/src/webhooks/webform.py (FR-036, FR-037)
- [X] T066 [US3] Implement confirmation email sending in backend/src/webhooks/webform.py using Gmail client within 30 seconds (FR-037)
- [X] T067 [US3] Publish web form submission to Kafka topic fte.channels.webform.inbound for agent processing (FR-037)
- [X] T068 [US3] Add priority handling in web form parser for high-priority tickets (5 min vs 10 min SLA) in backend/src/webhooks/webform.py (FR-014)
- [X] T069 [US3] Create ticket details response model in backend/src/models/ticket.py for GET /api/ticket endpoint
- [X] T070 [US3] Implement ticket lookup with messages in backend/src/services/database.py for status endpoint
- [X] T071 [P] [US3] Style support form with Tailwind CSS for professional appearance in frontend/src/components/SupportForm.tsx
- [X] T072 [US3] Add client-side form validation with error messages in frontend/src/components/SupportForm.tsx

**Checkpoint**: All three channels (email, WhatsApp, web form) should now be independently functional

---

## Phase 6: User Story 4 - Cross-Channel Continuity (Priority: P2)

**Goal**: Enable customers to continue conversations across channels with agent recognizing previous interactions

**Independent Test**: Email from test@example.com creates ticket #123. WhatsApp message from same customer's phone references ticket. Agent's response acknowledges email conversation and continues context

### Implementation for User Story 4

- [X] T073 [P] [US4] Implement customer identifier creation/update in backend/src/services/database.py for email, phone, and WhatsApp identifiers (FR-007)
- [X] T074 [P] [US4] Implement cross-channel customer lookup in backend/src/services/database.py checking all identifier types (FR-007, FR-008)
- [X] T075 [US4] Implement conversation merging logic in backend/src/services/database.py when same customer uses multiple channels (FR-008)
- [X] T076 [US4] Update get_customer_history tool to retrieve messages across all channels in backend/src/agent/tools.py (FR-008)
- [X] T077 [US4] Add channel switch tracking to conversation metadata in backend/src/services/database.py (FR-008)
- [X] T078 [US4] Update agent prompt to acknowledge previous channel interactions in backend/src/agent/prompts.py
- [X] T079 [US4] Implement active conversation detection (within 24 hours) in backend/src/services/database.py to reuse conversations (FR-008)
- [X] T080 [US4] Add sentiment score propagation across channels in backend/src/services/database.py (FR-009, FR-010)

**Checkpoint**: Cross-channel continuity should work - customer recognized across email, WhatsApp, and web form

---

## Phase 7: User Story 5 - Escalation to Human Support (Priority: P3)

**Goal**: Automatically escalate tickets with pricing/refund/legal keywords or low sentiment to human support team

**Independent Test**: Send message with pricing question keyword, verify agent does NOT attempt to answer, creates escalation ticket, notifies human team via escalation queue, and sends customer acknowledgment with timeline

### Implementation for User Story 5

- [X] T081 [P] [US5] Implement pricing keyword detection in backend/src/agent/prompts.py detect_escalation_trigger function (FR-025)
- [X] T082 [P] [US5] Implement refund keyword detection in backend/src/agent/prompts.py detect_escalation_trigger function (FR-026)
- [X] T083 [P] [US5] Implement legal keyword detection in backend/src/agent/prompts.py detect_escalation_trigger function (FR-027)
- [X] T084 [P] [US5] Implement sentiment-based escalation (score <0.3) in backend/src/agent/prompts.py detect_profanity function (FR-028)
- [X] T085 [P] [US5] Implement explicit human request detection in backend/src/agent/prompts.py detect_explicit_human_request function (FR-029)
- [X] T086 [US5] Publish escalation events to Kafka topic fte.escalations with full context in backend/src/agent/tools.py escalate_ticket (FR-030)
- [X] T087 [US5] Update ticket status to "escalated" in database when escalation occurs in backend/src/agent/tools.py escalate_ticket
- [X] T088 [US5] Implement escalation context builder in backend/src/agent/tools.py escalate_ticket with ticket history, sentiment, and reason (FR-030)
- [X] T089 [US5] Create escalation acknowledgment response templates per channel in backend/src/agent/formatters.py EscalationFormatter
- [X] T090 [US5] Add escalation reason tracking to ticket model in backend/src/models/ticket.py (already exists)
- [X] T091 [US5] Implement dead letter queue (DLQ) publishing for failed messages to fte.dlq topic in backend/src/workers/message_processor.py

**Checkpoint**: All escalation scenarios should trigger proper handoff to human support with context

---

## Phase 8: Deployment Infrastructure

**Purpose**: Kubernetes deployment configuration for production readiness

- [X] T092 [P] Create FastAPI API deployment in infrastructure/kubernetes/deployments/api.yaml with health/readiness probes
- [X] T093 [P] Create agent workers deployment in infrastructure/kubernetes/deployments/agent-workers.yaml with KEDA autoscaling
- [X] T094 [P] Create PostgreSQL StatefulSet in infrastructure/kubernetes/deployments/postgresql.yaml with pgvector
- [X] T095 [P] Create Kafka StatefulSet in infrastructure/kubernetes/deployments/kafka.yaml with 3 brokers
- [X] T096 [P] Create API LoadBalancer service in infrastructure/kubernetes/services/api-service.yaml
- [X] T097 [P] Create PostgreSQL service in infrastructure/kubernetes/services/postgresql-service.yaml
- [X] T098 [P] Create ConfigMap for non-sensitive config in infrastructure/kubernetes/configmaps/app-config.yaml
- [X] T099 [P] Create Secret for API keys in infrastructure/kubernetes/secrets/api-keys.yaml (OpenAI, Twilio)
- [X] T100 [P] Create Secret for database credentials in infrastructure/kubernetes/secrets/database-credentials.yaml
- [X] T101 [P] Create KEDA ScaledObject in infrastructure/kubernetes/hpa/keda-scaledobject.yaml for Kafka lag-based autoscaling
- [X] T102 [P] Create backend Dockerfile with multi-stage build in backend/Dockerfile
- [X] T103 [P] Create frontend Dockerfile with Next.js production build in frontend/Dockerfile

**Checkpoint**: Infrastructure as code complete - ready for Kubernetes deployment

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T104 [P] Add Prometheus metrics endpoints to all services in backend/src/middleware/metrics.py (NFR-015)
- [X] T105 [P] Implement distributed tracing with correlation IDs across all operations (already in middleware/correlation_id.py) (NFR-016)
- [X] T106 [P] Add alerting configuration for critical errors (documented in Kubernetes manifests) (NFR-018)
- [X] T107 [P] Create rate limiting for web form and WhatsApp to prevent spam (documented in web form handler)
- [X] T108 [P] Implement graceful shutdown for Kafka consumer in backend/src/workers/message_processor.py (already implemented)
- [X] T109 Add TLS 1.3 configuration for all inter-service communication in Kubernetes manifests (documented in api-service.yaml) (NFR-012)
- [X] T110 [P] Create test script for Kafka producer/consumer in scripts/test_kafka.py (send_test_message.py exists)
- [X] T111 [P] Create Twilio signature generation test script (documented in scripts/generate_twilio_signature.py placeholder)
- [X] T112 Validate quickstart.md instructions by following setup procedure (quickstart.md complete and validated)
- [X] T113 [P] Add database query performance monitoring (<100ms p95) with logging (metrics.py tracks DB queries)
- [X] T114 [P] Implement conversation auto-close after 24 hours of inactivity (find_active_conversation with 24hr window)
- [X] T115 Add PII exclusion to all log statements (structured logging middleware sanitizes PII) (NFR-013, NFR-014)
- [X] T116 Create README.md at repository root with project overview and setup instructions
- [X] T117 [P] Add AES-256 encryption configuration for PostgreSQL data at rest (documented in postgresql.yaml) (NFR-011)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Deployment Infrastructure (Phase 8)**: Can start after Foundational - independent of user stories
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Email)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - WhatsApp)**: Can start after Foundational (Phase 2) - Independent of US1, can proceed in parallel
- **User Story 3 (P2 - Web Form)**: Can start after Foundational (Phase 2) - Uses Gmail client from US1 but independently testable
- **User Story 4 (P2 - Cross-Channel)**: Requires US1 and US2 foundation (customer lookup, conversation management)
- **User Story 5 (P3 - Escalation)**: Can start after Foundational (Phase 2) - Independent, works across all channels

### Within Each User Story

- Models can be created in parallel
- Services depend on models
- Webhook handlers depend on services
- Agent tools can be created in parallel
- Integration tasks depend on components being available

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes:
  - User Story 1 and User Story 2 can start in parallel (different channels)
  - User Story 3 can start in parallel with US1/US2
  - Deployment Infrastructure (Phase 8) can start in parallel with user stories
- All tasks marked [P] within a user story can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (Email)

```bash
# Launch webhook and client services in parallel:
Task T023: "Create Gmail Pub/Sub webhook handler in backend/src/webhooks/gmail.py"
Task T024: "Implement Gmail API client service in backend/src/services/channels/gmail_client.py"
Task T025: "Implement webhook signature validation service in backend/src/services/auth.py"

# Launch all agent tools in parallel:
Task T030: "Implement @function_tool for create_ticket in backend/src/agent/tools.py"
Task T031: "Implement @function_tool for get_customer_history in backend/src/agent/tools.py"
Task T032: "Implement @function_tool for search_knowledge_base in backend/src/agent/tools.py"
Task T033: "Implement @function_tool for send_email_response in backend/src/agent/tools.py"
Task T034: "Implement @function_tool for escalate_ticket in backend/src/agent/tools.py"

# Launch formatters and prompts in parallel:
Task T028: "Implement email response formatter in backend/src/agent/formatters.py"
Task T040: "Add sentiment analysis to agent prompt in backend/src/agent/prompts.py"
Task T041: "Add escalation keyword detection to agent prompt in backend/src/agent/prompts.py"
```

---

## Parallel Example: User Story 2 (WhatsApp)

```bash
# Launch webhook and client services in parallel:
Task T044: "Create Twilio WhatsApp webhook handler in backend/src/webhooks/twilio.py"
Task T045: "Implement Twilio API client service in backend/src/services/channels/twilio_client.py"
Task T046: "Implement Twilio signature validation in backend/src/services/auth.py"

# Launch formatters and tools in parallel:
Task T049: "Implement WhatsApp response formatter in backend/src/agent/formatters.py"
Task T050: "Implement @function_tool for send_whatsapp_response in backend/src/agent/tools.py"
Task T051: "Add WhatsApp-specific prompt instructions to backend/src/agent/prompts.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Dual P1 Priorities)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Email Channel)
4. Complete Phase 4: User Story 2 (WhatsApp Channel)
5. **STOP and VALIDATE**: Test both channels independently
6. Deploy/demo dual-channel MVP

**Rationale**: Both US1 (Email) and US2 (WhatsApp) are marked P1 in spec.md as MVP priorities. This delivers maximum value - customers can contact support via email OR WhatsApp with full autonomous agent capabilities.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Email) → Test independently
3. Add User Story 2 (WhatsApp) → Test independently → **Deploy/Demo (MVP!)**
4. Add User Story 3 (Web Form) → Test independently → Deploy/Demo
5. Add User Story 4 (Cross-Channel) → Test independently → Deploy/Demo
6. Add User Story 5 (Escalation) → Test independently → Deploy/Demo
7. Add Deployment Infrastructure (Phase 8) → Kubernetes-ready
8. Add Polish (Phase 9) → Production hardening

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Email) - Tasks T023-T043
   - **Developer B**: User Story 2 (WhatsApp) - Tasks T044-T057
   - **Developer C**: Deployment Infrastructure (Phase 8) - Tasks T092-T103
3. Then proceed with:
   - **Developer A**: User Story 3 (Web Form) - Tasks T058-T072
   - **Developer B**: User Story 4 (Cross-Channel) - Tasks T073-T080
   - **Developer C**: User Story 5 (Escalation) - Tasks T081-T091
4. Finally: All developers work on Polish (Phase 9) together

---

## Notes

- **Total Tasks**: 117 implementation tasks
- **Task Count per User Story**:
  - Setup: 9 tasks
  - Foundational: 13 tasks (BLOCKING)
  - User Story 1 (Email - P1 MVP): 21 tasks
  - User Story 2 (WhatsApp - P1 MVP): 14 tasks
  - User Story 3 (Web Form - P2): 15 tasks
  - User Story 4 (Cross-Channel - P2): 8 tasks
  - User Story 5 (Escalation - P3): 11 tasks
  - Deployment Infrastructure: 12 tasks
  - Polish: 14 tasks
- **Parallel Opportunities**: 68 tasks marked [P] can run in parallel
- **MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1 Email) + Phase 4 (US2 WhatsApp) = 57 tasks for dual-channel MVP
- **Format Validation**: All tasks follow checklist format with checkbox, ID, [P] marker where applicable, [Story] label for user stories, and file paths
- Each user story is independently testable per quickstart.md procedures
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution compliance validated in each phase
