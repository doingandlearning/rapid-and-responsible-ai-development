-- Capstone RAG System Database Schema
-- PostgreSQL with pgvector and JSONB support

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Document chunks table with rich JSONB metadata
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(50) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1024),
    
    -- JSONB fields for flexible metadata storage
    metadata JSONB NOT NULL DEFAULT '{}',
    document_info JSONB NOT NULL DEFAULT '{}',
    processing_info JSONB NOT NULL DEFAULT '{}',
    
    -- Extracted fields for performance
    document_type VARCHAR(50),
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query analytics table
CREATE TABLE IF NOT EXISTS query_analytics (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_metadata JSONB DEFAULT '{}',
    response_metadata JSONB DEFAULT '{}',
    user_session JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document relationships table (for literature/research projects)
CREATE TABLE IF NOT EXISTS document_relationships (
    id SERIAL PRIMARY KEY,
    source_doc_id VARCHAR(50),
    target_doc_id VARCHAR(50),
    relationship_type VARCHAR(50),
    relationship_data JSONB DEFAULT '{}',
    confidence_score FLOAT
);

-- Create indexes for JSONB fields
CREATE INDEX IF NOT EXISTS idx_chunks_metadata 
ON document_chunks USING gin(metadata);

CREATE INDEX IF NOT EXISTS idx_chunks_document_info 
ON document_chunks USING gin(document_info);

CREATE INDEX IF NOT EXISTS idx_analytics_query_metadata 
ON query_analytics USING gin(query_metadata);

-- Create vector similarity index
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw 
ON document_chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Create fallback IVFFlat index
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_ivfflat 
ON document_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document_type 
ON document_chunks (document_type);

CREATE INDEX IF NOT EXISTS idx_chunks_author 
ON document_chunks (author);

CREATE INDEX IF NOT EXISTS idx_analytics_created_at 
ON query_analytics (created_at);

-- Sample data for testing (optional)
INSERT INTO document_chunks (
    chunk_id, 
    content, 
    metadata, 
    document_info, 
    processing_info, 
    document_type, 
    author
) VALUES (
    'sample_001',
    'This is a sample document chunk for testing the RAG system. It contains example content that can be used to verify the search and retrieval functionality.',
    '{"chunk_type": "sample", "word_count": 25, "has_numbers": false}',
    '{"title": "Sample Document", "author": "Test Author", "work_type": "sample"}',
    '{"chunk_index": 0, "total_chunks": 1, "processing_timestamp": "2024-01-01T00:00:00Z"}',
    'sample',
    'Test Author'
) ON CONFLICT (chunk_id) DO NOTHING;
