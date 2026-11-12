-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verification notice
COMMENT ON DATABASE doc_verify_db IS 'Meridian Bay Institutional Clinical Document Verification Database';
