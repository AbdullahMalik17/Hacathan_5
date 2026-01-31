-- Migration: 001_initial_schema
-- Task: T012 - Create database migration script
-- Description: Initial schema setup for Customer Success Digital FTE
-- Created: 2026-01-31
-- Author: AI Agent

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector"; -- pgvector for semantic search

-- Import the complete schema from schema.sql
-- This migration is idempotent and can be re-run safely
\i ../schema.sql

-- Migration metadata tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    description TEXT
);

-- Record this migration
INSERT INTO schema_migrations (version, description)
VALUES ('001', 'Initial schema with pgvector support')
ON CONFLICT (version) DO NOTHING;

-- Migration complete
