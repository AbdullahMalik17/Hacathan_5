# ADR-0002: Data Architecture with PostgreSQL and Vector Search

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-31
- **Feature:** 001-customer-success-fte
- **Context:** System requires unified storage for CRM data (customers, tickets, conversations) and knowledge base with semantic search capabilities. Constitution Principle IV (Database-as-CRM) mandates PostgreSQL as the single source of truth. Performance requirements include <100ms customer lookups and <500ms knowledge base searches at p95.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core data persistence and search
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Separate vector DB, NoSQL, other RDBMS
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all services and data access patterns
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use **PostgreSQL 16+** with the following integrated data stack:

- **Database Engine**: PostgreSQL 16+ (single source of truth for all data)
- **Vector Search**: pgvector extension with HNSW index for semantic search
- **Async Driver**: asyncpg with connection pooling (min=10, max=20 connections)
- **Schema Design**: Normalized relational model with 7 core entities (customers, customer_identifiers, conversations, tickets, messages, knowledge_base, processed_messages)
- **Indexing Strategy**:
  - B-tree indexes for UUID lookups, timestamps, status fields
  - HNSW vector index for knowledge_base embeddings (m=16, ef_construction=64)
  - Unique indexes for deduplication (channel_message_id)
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions) stored as vector(1536)
- **Connection Management**: asyncpg pool with 30s query timeout for vector searches

**Schema Highlights**:
```sql
CREATE EXTENSION vector;

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    primary_email TEXT UNIQUE,
    sentiment_history JSONB,
    first_contact_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(id),
    identifier_type TEXT CHECK (identifier_type IN ('email', 'phone', 'whatsapp')),
    identifier_value TEXT NOT NULL,
    UNIQUE(identifier_type, identifier_value)
);

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL
);

CREATE INDEX ON knowledge_base USING hnsw (embedding vector_cosine_ops)
    WITH (m=16, ef_construction=64);
```

## Consequences

### Positive

- **Unified Storage**: Single database for CRM data and vector embeddings eliminates data synchronization complexity
- **ACID Compliance**: Transactions ensure consistency for cross-channel customer identification and conversation merging
- **Fast Vector Search**: pgvector HNSW index achieves <500ms p95 latency for semantic search (validated in benchmarks)
- **Cost Efficiency**: No separate vector database licensing or hosting costs (~$500/year saved vs Pinecone/Weaviate)
- **Operational Simplicity**: Single backup/restore process, single monitoring stack, familiar SQL tooling
- **Schema Evolution**: PostgreSQL migrations (Alembic) provide versioned, rollback-safe schema changes
- **Connection Pooling**: asyncpg async driver enables 1000+ concurrent conversations without connection exhaustion
- **Constitution Alignment**: Directly mandated by Principle IV (Database-as-CRM)

### Negative

- **Scaling Limits**: pgvector HNSW index performance degrades beyond 1M+ vectors (current KB has 100+ articles, growth to 10k articles acceptable)
- **Index Build Time**: HNSW index creation takes 30-60 seconds for 1000+ vectors, blocking writes during rebuild
- **Memory Usage**: Vector indexes require 2-4GB RAM for 10k documents with 1536-dim embeddings
- **Extension Dependency**: Requires pgvector extension (not available on all managed PostgreSQL providers like older AWS RDS versions)
- **Query Complexity**: Vector similarity queries are less intuitive than traditional SQL for developers unfamiliar with embeddings

## Alternatives Considered

### Alternative A: PostgreSQL + Separate Vector Database (Pinecone/Weaviate)
- **Stack**: PostgreSQL for CRM + Pinecone for knowledge base embeddings
- **Why Rejected**:
  - Data synchronization complexity (dual writes, eventual consistency issues)
  - Customer lookup in PostgreSQL followed by vector search in Pinecone adds 100-200ms latency
  - Additional $300-600/year cost for Pinecone hosting
  - Two backup/restore processes to maintain
  - Violates Constitution Principle IV (Database-as-CRM as single source of truth)

### Alternative B: MongoDB with Atlas Vector Search
- **Stack**: MongoDB Atlas with native vector search
- **Why Rejected**:
  - Constitution explicitly mandates PostgreSQL (Principle IV)
  - Weaker ACID guarantees for cross-channel customer merging transactions
  - Team lacks MongoDB operational expertise
  - Atlas Vector Search pricing ($0.10/GB RAM/hour) more expensive than self-hosted PostgreSQL
  - Schema-less design contradicts requirement for strict data validation

### Alternative C: MySQL 9.0 with Vector Extension
- **Stack**: MySQL 9.0 with experimental vector support
- **Why Rejected**:
  - Vector extension is preview/experimental (not production-ready as of 2026-01)
  - Weaker JSON support (JSONB) compared to PostgreSQL for sentiment_history storage
  - asyncpg driver for PostgreSQL has better async performance than aiomysql
  - pgvector has 2+ years of production usage vs MySQL's new vector feature

### Alternative D: PostgreSQL + Elasticsearch for Search
- **Stack**: PostgreSQL for CRM + Elasticsearch for semantic search
- **Why Rejected**:
  - Elasticsearch semantic search requires plugin (OpenSearch k-NN) adding complexity
  - Dual indexing overhead (PostgreSQL + Elasticsearch) slows writes
  - pgvector simpler for MVP scope (100-10k documents)
  - Additional $200-400/year hosting cost for Elasticsearch cluster

## References

- Feature Spec: specs/001-customer-success-fte/spec.md (FR-006 to FR-019: Customer Identity & Knowledge Base)
- Implementation Plan: specs/001-customer-success-fte/plan.md (Phase 0: Research - Section 2)
- Data Model: specs/001-customer-success-fte/data-model.md (Complete schema with 7 entities)
- Research Document: specs/001-customer-success-fte/research.md (Section 2: PostgreSQL with pgvector)
- Related ADRs: ADR-0001 (AI Agent Architecture) for knowledge base search tool integration
- Constitution: .specify/memory/constitution.md (Principle IV: Database-as-CRM)
