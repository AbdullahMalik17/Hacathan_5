# Data Model: Customer Success Digital FTE

**Feature**: 001-customer-success-fte
**Date**: 2026-01-31
**Status**: Design Complete

## Entity Relationship Diagram

```
┌─────────────────┐
│    Customer     │
│─────────────────│
│ id (PK)         │
│ primary_email   │◄──────────┐
│ name            │            │
│ sentiment_hist  │            │
│ first_contact   │            │
│ total_interact  │            │
└─────────────────┘            │
         │                     │
         │ 1:N                 │
         ▼                     │
┌─────────────────────┐        │
│ Customer_Identifier │        │
│─────────────────────│        │
│ id (PK)             │        │
│ customer_id (FK)    │────────┘
│ identifier_type     │
│ identifier_value    │
│ verified            │
└─────────────────────┘

Customer 1:N Conversation 1:N Message
Customer 1:N Ticket 1:N Message
Conversation 1:1 Ticket

┌─────────────────┐
│  Conversation   │
│─────────────────│
│ id (PK)         │
│ customer_id(FK) │
│ initial_channel │
│ status          │
│ sentiment       │
│ started_at      │
│ ended_at        │
└─────────────────┘
         │ 1:N
         ▼
┌─────────────────┐
│    Message      │
│─────────────────│
│ id (PK)         │
│ conversation_id │
│ channel         │
│ direction       │
│ role            │
│ content         │
│ channel_msg_id  │ (for dedup)
│ delivery_status │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│     Ticket      │
│─────────────────│
│ id (PK)         │
│ conversation_id │
│ customer_id(FK) │
│ source_channel  │
│ category        │
│ priority        │
│ status          │
│ created_at      │
│ resolved_at     │
└─────────────────┘

┌─────────────────────┐
│   Knowledge_Base    │
│─────────────────────│
│ id (PK)             │
│ title               │
│ content             │
│ category            │
│ embedding (vector)  │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

## Core Entities

### Customer
**Purpose**: Unified identity across all communication channels

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique customer identifier |
| primary_email | TEXT | UNIQUE, NULLABLE | Primary contact email |
| name | TEXT | NULLABLE | Customer name |
| sentiment_history | JSONB | DEFAULT '[]' | Array of sentiment scores over time |
| first_contact_at | TIMESTAMPTZ | DEFAULT NOW() | When customer first contacted support |
| total_interactions | INT | DEFAULT 0 | Count of all interactions across channels |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- `PRIMARY KEY (id)`
- `UNIQUE INDEX (primary_email)` WHERE primary_email IS NOT NULL

**Business Rules**:
- Email uniqueness enforced when present
- Sentiment history stored as JSON array: `[{"date": "2026-01-31", "score": 0.8, "channel": "email"}]`
- Total interactions incremented on each new message

---

### Customer_Identifier
**Purpose**: Enable cross-channel customer matching (email, phone, WhatsApp)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier record ID |
| customer_id | UUID | FOREIGN KEY → Customer(id) | Parent customer |
| identifier_type | TEXT | CHECK IN ('email', 'phone', 'whatsapp') | Type of identifier |
| identifier_value | TEXT | NOT NULL | Actual identifier value |
| verified | BOOLEAN | DEFAULT FALSE | Whether identifier is verified |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | When identifier was added |

**Indexes**:
- `PRIMARY KEY (id)`
- `UNIQUE INDEX (identifier_type, identifier_value)`
- `INDEX (identifier_value)` for fast lookups

**Business Rules**:
- Combination of type + value must be unique
- Email identifiers auto-verified on first successful email exchange
- Phone identifiers verified on WhatsApp session validation
- Enables finding customer by email OR phone across channels

**Example Usage**:
```sql
-- Find customer by WhatsApp phone number
SELECT c.* FROM customers c
JOIN customer_identifiers ci ON ci.customer_id = c.id
WHERE ci.identifier_type = 'whatsapp' AND ci.identifier_value = '+14155551234';
```

---

### Conversation
**Purpose**: Dialogue thread tracking across channels

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique conversation ID |
| customer_id | UUID | FOREIGN KEY → Customer(id) | Participant customer |
| initial_channel | TEXT | NOT NULL | Channel where conversation started |
| status | TEXT | CHECK IN ('active', 'closed'), DEFAULT 'active' | Conversation status |
| overall_sentiment | FLOAT | CHECK BETWEEN -1.0 AND 1.0 | Aggregate sentiment across messages |
| started_at | TIMESTAMPTZ | DEFAULT NOW() | Conversation start time |
| ended_at | TIMESTAMPTZ | NULLABLE | When conversation closed |
| metadata | JSONB | DEFAULT '{}' | Channel switches, escalations |

**Indexes**:
- `PRIMARY KEY (id)`
- `INDEX (customer_id, status)`
- `INDEX (started_at DESC)` for recent conversations

**Business Rules**:
- Active conversations within 24 hours are reused
- Conversations auto-close after 24 hours of inactivity
- Sentiment computed as weighted average of message sentiments
- Metadata tracks channel switches: `{"switches": [{"from": "email", "to": "whatsapp", "at": "2026-01-31T12:00:00Z"}]}`

**State Transitions**:
```
[NEW] → active → closed
       active → active (ongoing)
```

---

### Ticket
**Purpose**: Support request tracking with categorization

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique ticket ID |
| conversation_id | UUID | FOREIGN KEY → Conversation(id) | Parent conversation |
| customer_id | UUID | FOREIGN KEY → Customer(id) | Ticket owner |
| source_channel | TEXT | NOT NULL | Channel where ticket originated |
| category | TEXT | DEFAULT 'general' | Ticket category |
| priority | TEXT | CHECK IN ('low', 'medium', 'high'), DEFAULT 'medium' | Urgency level |
| status | TEXT | CHECK IN ('open', 'in_progress', 'resolved', 'escalated'), DEFAULT 'open' | Ticket state |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Ticket creation time |
| resolved_at | TIMESTAMPTZ | NULLABLE | When ticket was resolved |
| resolution_notes | TEXT | NULLABLE | How ticket was resolved |

**Indexes**:
- `PRIMARY KEY (id)`
- `INDEX (status, created_at DESC)` for queue views
- `INDEX (customer_id, created_at DESC)` for customer history

**Categories**: general, technical, billing, feedback, bug_report

**Business Rules**:
- One ticket per conversation (1:1 relationship)
- Tickets created BEFORE first agent response (per constitution)
- Auto-escalate if unresolved >24 hours (configurable SLA)
- Resolution notes required when status changes to 'resolved'

**State Transitions**:
```
[NEW] → open → in_progress → resolved
              → in_progress → escalated
              → escalated → resolved (human handoff)
```

---

### Message
**Purpose**: All inbound/outbound messages with deduplication

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique message ID |
| conversation_id | UUID | FOREIGN KEY → Conversation(id) | Parent conversation |
| channel | TEXT | NOT NULL | Communication channel |
| direction | TEXT | CHECK IN ('inbound', 'outbound') | Message direction |
| role | TEXT | CHECK IN ('customer', 'agent', 'system') | Message author |
| content | TEXT | NOT NULL | Message text |
| channel_message_id | TEXT | NULLABLE | External message ID (Gmail, Twilio SID) |
| delivery_status | TEXT | NULLABLE | queued, sent, delivered, read |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Message timestamp |
| metadata | JSONB | DEFAULT '{}' | Channel-specific data |

**Indexes**:
- `PRIMARY KEY (id)`
- `UNIQUE INDEX (channel, channel_message_id)` WHERE channel_message_id IS NOT NULL (deduplication)
- `INDEX (conversation_id, created_at)` for chronological ordering

**Business Rules**:
- Deduplication via channel_message_id prevents webhook retries
- Metadata stores channel-specific fields: `{"from": "user@example.com", "subject": "Help", "thread_id": "gmail-thread-123"}`
- Content sanitized before storage (no XSS, SQL injection)
- System messages for escalations: `{"role": "system", "content": "Ticket escalated to human support"}`

**Deduplication Query**:
```sql
-- Check if message already processed
SELECT EXISTS(
  SELECT 1 FROM messages
  WHERE channel = 'email' AND channel_message_id = 'gmail-msg-abc123'
) AS already_processed;
```

---

### Knowledge_Base
**Purpose**: Product documentation with semantic search

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique article ID |
| title | TEXT | NOT NULL | Article title |
| content | TEXT | NOT NULL | Full article text |
| category | TEXT | NULLABLE | Documentation category |
| embedding | vector(1536) | NOT NULL | OpenAI embedding for semantic search |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Article creation |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last modification |

**Indexes**:
- `PRIMARY KEY (id)`
- `HNSW INDEX (embedding vector_cosine_ops)` WITH (m=16, ef_construction=64)
- `INDEX (category)` for filtered search

**Business Rules**:
- Embeddings generated via OpenAI text-embedding-3-small (1536 dimensions)
- HNSW index provides <500ms p95 search latency
- Similarity threshold: >=0.7 highly relevant, 0.5-0.7 moderately relevant, <0.5 not relevant
- Articles updated triggers embedding regeneration

**Semantic Search Query**:
```sql
SELECT id, title, content,
       1 - (embedding <=> $1::vector) AS similarity_score
FROM knowledge_base
WHERE 1 - (embedding <=> $1::vector) > 0.5
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

---

## Supporting Tables

### Processed_Messages (Idempotency)
**Purpose**: Prevent duplicate processing on Kafka retry

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| message_id | UUID | PRIMARY KEY | Kafka message ID |
| processed_at | TIMESTAMPTZ | DEFAULT NOW() | Processing timestamp |

**Indexes**:
- `PRIMARY KEY (message_id)`
- `INDEX (processed_at)` for cleanup cron

**Cleanup**: Delete records older than 7 days (Kafka retention period)

---

## Data Integrity Rules

1. **Customer Email Uniqueness**: Enforced via UNIQUE constraint
2. **Message → Conversation**: Every message MUST reference a conversation (FK constraint)
3. **Conversation → Customer**: Every conversation MUST reference a customer (FK constraint)
4. **Ticket Creation Before Response**: Application enforces (not DB constraint)
5. **Channel Message ID Deduplication**: UNIQUE index prevents duplicate webhook processing

---

## Data Migration Strategy

### Phase 1: Initial Schema
```sql
-- Run all CREATE TABLE statements
-- Run all CREATE INDEX statements
-- INSERT sample knowledge base articles
```

### Phase 2: Seed Data
```sql
-- Insert test customers
-- Insert sample conversations
-- Generate embeddings for knowledge base
```

### Phase 3: Production Migration
- Use `pg_dump` for backup before changes
- Run migrations with `alembic` or custom SQL scripts
- Validate FK constraints after data load
- Reindex knowledge_base after bulk embedding updates

---

## Query Patterns

### 1. Find Customer by Any Identifier
```sql
SELECT DISTINCT c.*
FROM customers c
LEFT JOIN customer_identifiers ci ON ci.customer_id = c.id
WHERE c.primary_email = $1
   OR (ci.identifier_type = 'phone' AND ci.identifier_value = $2)
   OR (ci.identifier_type = 'whatsapp' AND ci.identifier_value = $3);
```

### 2. Get Customer History Across All Channels
```sql
SELECT c.initial_channel, c.started_at, c.status,
       m.content, m.role, m.channel, m.created_at
FROM conversations c
JOIN messages m ON m.conversation_id = c.id
WHERE c.customer_id = $1
ORDER BY m.created_at DESC
LIMIT 20;
```

### 3. Check for Active Conversation
```sql
SELECT id FROM conversations
WHERE customer_id = $1
  AND status = 'active'
  AND started_at > NOW() - INTERVAL '24 hours'
ORDER BY started_at DESC
LIMIT 1;
```

### 4. Knowledge Base Semantic Search
```sql
SELECT id, title, content,
       1 - (embedding <=> $1::vector) AS similarity
FROM knowledge_base
WHERE 1 - (embedding <=> $1::vector) > 0.5
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

---

## Performance Considerations

### Index Strategy
- **B-tree indexes**: UUIDs, timestamps, status fields
- **HNSW vector index**: knowledge_base.embedding
- **Unique indexes**: Deduplication (channel_message_id)
- **Partial indexes**: WHERE clauses for filtered queries

### Connection Pooling
- **asyncpg pool size**: min=10, max=20
- **Connection timeout**: 60 seconds
- **Query timeout**: 30 seconds for vector search

### Partitioning (Future Optimization)
- **messages table**: Partition by created_at (monthly)
- **conversations table**: Partition by started_at (quarterly)
- Benefits: Faster queries on recent data, easier archival

---

## Validation Rules

### Customer
- Email format validation: RFC 5322
- Sentiment score range: -1.0 to 1.0

### Ticket
- Priority: low | medium | high
- Status: open | in_progress | resolved | escalated
- Category: general | technical | billing | feedback | bug_report

### Message
- Direction: inbound | outbound
- Role: customer | agent | system
- Channel: email | whatsapp | web_form

### Conversation
- Status: active | closed
- Sentiment: -1.0 to 1.0

---

## Next Steps

1. **Create PostgreSQL schema SQL script** (database/schema.sql)
2. **Generate seed data** for knowledge base (100+ articles)
3. **Define API contracts** in contracts/ directory
4. **Write quickstart guide** for local development setup
