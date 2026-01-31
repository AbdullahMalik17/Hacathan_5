-- Customer Success Digital FTE Database Schema
-- PostgreSQL 16+ with pgvector extension
-- Created: 2026-01-31

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: customers
-- Purpose: Unified customer identity across all channels
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    primary_email TEXT UNIQUE,
    name TEXT,
    sentiment_history JSONB DEFAULT '[]'::jsonb,
    first_contact_at TIMESTAMPTZ DEFAULT NOW(),
    total_interactions INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for customers table
CREATE UNIQUE INDEX idx_customers_primary_email ON customers(primary_email) WHERE primary_email IS NOT NULL;
CREATE INDEX idx_customers_created_at ON customers(created_at DESC);

-- Table: customer_identifiers
-- Purpose: Cross-channel customer matching (email, phone, whatsapp)
CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type TEXT NOT NULL CHECK (identifier_type IN ('email', 'phone', 'whatsapp')),
    identifier_value TEXT NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

-- Indexes for customer_identifiers table
CREATE INDEX idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX idx_customer_identifiers_customer_id ON customer_identifiers(customer_id);

-- Table: conversations
-- Purpose: Dialogue threads with customers
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    initial_channel TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'closed')) DEFAULT 'active',
    overall_sentiment FLOAT CHECK (overall_sentiment BETWEEN -1.0 AND 1.0),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for conversations table
CREATE INDEX idx_conversations_customer_id_status ON conversations(customer_id, status);
CREATE INDEX idx_conversations_started_at ON conversations(started_at DESC);

-- Table: tickets
-- Purpose: Support request tracking with categorization
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    source_channel TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved', 'escalated')) DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT
);

-- Indexes for tickets table
CREATE INDEX idx_tickets_status_created_at ON tickets(status, created_at DESC);
CREATE INDEX idx_tickets_customer_id_created_at ON tickets(customer_id, created_at DESC);
CREATE INDEX idx_tickets_conversation_id ON tickets(conversation_id);

-- Table: messages
-- Purpose: All inbound/outbound messages with deduplication
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    channel TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    role TEXT NOT NULL CHECK (role IN ('customer', 'agent', 'system')),
    content TEXT NOT NULL,
    channel_message_id TEXT,
    delivery_status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for messages table
CREATE INDEX idx_messages_conversation_id_created_at ON messages(conversation_id, created_at);
CREATE UNIQUE INDEX idx_messages_channel_message_id ON messages(channel, channel_message_id) WHERE channel_message_id IS NOT NULL;

-- Table: knowledge_base
-- Purpose: Product documentation with semantic search
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    embedding vector(1536) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast vector similarity search
CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);
CREATE INDEX idx_knowledge_base_category ON knowledge_base(category);

-- Table: processed_messages
-- Purpose: Idempotency - prevent duplicate processing on Kafka retry
CREATE TABLE processed_messages (
    message_id UUID PRIMARY KEY,
    processed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for cleanup queries
CREATE INDEX idx_processed_messages_processed_at ON processed_messages(processed_at);

-- Cleanup function for processed_messages (delete records older than 7 days)
CREATE OR REPLACE FUNCTION cleanup_processed_messages()
RETURNS void AS $$
BEGIN
    DELETE FROM processed_messages
    WHERE processed_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE customers IS 'Unified customer identity across all communication channels';
COMMENT ON TABLE customer_identifiers IS 'Cross-channel customer matching via email/phone/whatsapp';
COMMENT ON TABLE conversations IS 'Dialogue threads with sentiment tracking';
COMMENT ON TABLE tickets IS 'Support requests with categorization and status';
COMMENT ON TABLE messages IS 'All inbound/outbound messages with deduplication';
COMMENT ON TABLE knowledge_base IS 'Product documentation with vector embeddings for semantic search';
COMMENT ON TABLE processed_messages IS 'Idempotency table to prevent duplicate Kafka message processing';

-- Grant permissions (adjust user as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
