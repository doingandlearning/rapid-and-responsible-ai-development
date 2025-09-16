#!/usr/bin/env python3
"""
Step 2: Edinburgh Knowledge Base Schema Creation
Complete solution for creating optimized database schema.
"""

import psycopg
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

def create_edinburgh_schema():
    """
    Create optimized schema for Edinburgh knowledge base.
    
    This creates a production-ready table with:
    - Proper data types for all fields
    - Vector columns for embeddings  
    - Text search capabilities
    - Performance indexes
    - Automatic triggers for maintenance
    """
    print("📊 CREATING EDINBURGH KNOWLEDGE BASE SCHEMA")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Drop existing table if needed (careful in production!)
                cur.execute("DROP TABLE IF EXISTS edinburgh_docs CASCADE;")
                print("🗑️  Dropped existing table (if any)")
                
                # Create main documents table
                print("📋 Creating main documents table...")
                cur.execute("""
                    CREATE TABLE edinburgh_docs (
                        -- Primary key and basic info
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        content TEXT NOT NULL,
                        
                        -- Categorization
                        category VARCHAR(100) NOT NULL,
                        subcategory VARCHAR(100),
                        
                        -- Source and versioning
                        source_url VARCHAR(1000),
                        source_type VARCHAR(50) DEFAULT 'webpage', -- webpage, pdf, doc, etc.
                        last_updated DATE DEFAULT CURRENT_DATE,
                        content_hash VARCHAR(64), -- for deduplication
                        
                        -- Content metadata
                        word_count INTEGER,
                        char_count INTEGER,
                        language VARCHAR(10) DEFAULT 'en',
                        
                        -- Vector embeddings (BGE-M3 is 1024 dimensions)
                        title_embedding vector(1024),
                        content_embedding vector(1024),
                        
                        -- Text search optimization
                        content_tsvector tsvector, -- for hybrid text+vector search
                        
                        -- Quality and confidence metrics
                        embedding_model VARCHAR(50) DEFAULT 'bge-m3',
                        embedding_quality_score FLOAT, -- optional quality metric
                        
                        -- Audit trail
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(100) DEFAULT 'system',
                        
                        -- Constraints
                        CONSTRAINT valid_word_count CHECK (word_count >= 0),
                        CONSTRAINT valid_quality_score CHECK (embedding_quality_score IS NULL OR (embedding_quality_score >= 0 AND embedding_quality_score <= 1))
                    );
                """)
                print("✅ Main table 'edinburgh_docs' created")
                
                # Create indexes for performance
                print("📊 Creating performance indexes...")
                
                # Text search indexes
                indexes_to_create = [
                    ("idx_edinburgh_title", "CREATE INDEX idx_edinburgh_title ON edinburgh_docs (title);"),
                    ("idx_edinburgh_category", "CREATE INDEX idx_edinburgh_category ON edinburgh_docs (category, subcategory);"),
                    ("idx_edinburgh_updated", "CREATE INDEX idx_edinburgh_updated ON edinburgh_docs (last_updated);"),
                    ("idx_edinburgh_source", "CREATE INDEX idx_edinburgh_source ON edinburgh_docs (source_type);"),
                    ("idx_edinburgh_tsvector", "CREATE INDEX idx_edinburgh_tsvector ON edinburgh_docs USING gin(content_tsvector);"),
                    ("idx_edinburgh_hash", "CREATE UNIQUE INDEX idx_edinburgh_hash ON edinburgh_docs (content_hash) WHERE content_hash IS NOT NULL;"),
                ]
                
                for index_name, index_sql in indexes_to_create:
                    cur.execute(index_sql)
                    print(f"   ✅ {index_name}")
                
                print("✅ Text search indexes created")
                
                # Note: Vector indexes will be created after loading data
                print("⏳ Vector indexes will be created after data loading for efficiency")
                
                # Create trigger function for automatic maintenance
                print("🔧 Creating automatic maintenance triggers...")
                
                cur.execute("""
                    CREATE OR REPLACE FUNCTION maintain_document_metadata() 
                    RETURNS TRIGGER AS $$
                    BEGIN
                        -- Update text search vector
                        NEW.content_tsvector := to_tsvector('english', 
                            COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, ''));
                        
                        -- Update character count
                        NEW.char_count := LENGTH(NEW.content);
                        
                        -- Update word count if not provided
                        IF NEW.word_count IS NULL THEN
                            NEW.word_count := array_length(
                                string_to_array(trim(NEW.content), ' '), 1
                            );
                        END IF;
                        
                        -- Generate content hash if not provided
                        IF NEW.content_hash IS NULL THEN
                            NEW.content_hash := md5(NEW.title || NEW.content);
                        END IF;
                        
                        -- Update timestamp
                        NEW.updated_at := CURRENT_TIMESTAMP;
                        
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                cur.execute("""
                    CREATE TRIGGER maintain_metadata_trigger
                    BEFORE INSERT OR UPDATE ON edinburgh_docs
                    FOR EACH ROW EXECUTE FUNCTION maintain_document_metadata();
                """)
                
                print("✅ Automatic metadata maintenance configured")
                
                # Create helper functions for common queries
                print("🛠️  Creating helper functions...")
                
                cur.execute("""
                    CREATE OR REPLACE FUNCTION search_similar_documents(
                        query_embedding vector(1024),
                        similarity_threshold FLOAT DEFAULT 0.5,
                        max_results INTEGER DEFAULT 10,
                        category_filter VARCHAR DEFAULT NULL
                    ) RETURNS TABLE (
                        doc_id INTEGER,
                        title VARCHAR,
                        category VARCHAR,
                        subcategory VARCHAR,
                        similarity_score FLOAT,
                        word_count INTEGER,
                        last_updated DATE
                    ) AS $$
                    BEGIN
                        RETURN QUERY
                        SELECT 
                            ed.id,
                            ed.title,
                            ed.category,
                            ed.subcategory,
                            (1 - (ed.content_embedding <=> query_embedding)) as similarity,
                            ed.word_count,
                            ed.last_updated
                        FROM edinburgh_docs ed
                        WHERE 
                            (category_filter IS NULL OR ed.category = category_filter)
                            AND (1 - (ed.content_embedding <=> query_embedding)) >= similarity_threshold
                        ORDER BY ed.content_embedding <=> query_embedding
                        LIMIT max_results;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                print("✅ Helper function 'search_similar_documents' created")
                
                # Create view for common queries
                cur.execute("""
                    CREATE VIEW edinburgh_docs_summary AS
                    SELECT 
                        category,
                        subcategory,
                        COUNT(*) as document_count,
                        AVG(word_count) as avg_word_count,
                        MAX(last_updated) as most_recent_update,
                        MIN(last_updated) as oldest_update
                    FROM edinburgh_docs
                    WHERE content_embedding IS NOT NULL  -- Only count docs with embeddings
                    GROUP BY category, subcategory
                    ORDER BY category, subcategory;
                """)
                
                print("✅ Summary view 'edinburgh_docs_summary' created")
                
                conn.commit()
                
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        return False
    
    print("\n🎉 Edinburgh schema created successfully!")
    return True

def verify_schema():
    """Verify the created schema is correct."""
    print("\n🔍 VERIFYING CREATED SCHEMA")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check table structure
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'edinburgh_docs'
                    ORDER BY ordinal_position;
                """)
                columns = cur.fetchall()
                
                print(f"📊 Table structure ({len(columns)} columns):")
                for col_name, data_type, nullable, default in columns:
                    nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                    default_str = f" DEFAULT {default}" if default else ""
                    print(f"   {col_name}: {data_type} {nullable_str}{default_str}")
                
                # Check indexes
                cur.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = 'edinburgh_docs'
                    ORDER BY indexname;
                """)
                indexes = cur.fetchall()
                
                print(f"\n📊 Indexes ({len(indexes)} total):")
                for index_name, index_def in indexes:
                    # Truncate long index definitions
                    short_def = index_def[:80] + "..." if len(index_def) > 80 else index_def
                    print(f"   {index_name}: {short_def}")
                
                # Check functions
                cur.execute("""
                    SELECT proname, prorettype::regtype
                    FROM pg_proc
                    WHERE proname LIKE '%document%' OR proname LIKE '%maintain%'
                    ORDER BY proname;
                """)
                functions = cur.fetchall()
                
                print(f"\n🛠️  Helper functions ({len(functions)} total):")
                for func_name, return_type in functions:
                    print(f"   {func_name}() → {return_type}")
                
                # Check triggers
                cur.execute("""
                    SELECT trigger_name, event_manipulation, action_timing
                    FROM information_schema.triggers
                    WHERE event_object_table = 'edinburgh_docs'
                    ORDER BY trigger_name;
                """)
                triggers = cur.fetchall()
                
                print(f"\n⚡ Triggers ({len(triggers)} total):")
                for trigger_name, event, timing in triggers:
                    print(f"   {trigger_name}: {timing} {event}")
                
                # Test basic functionality
                print(f"\n🧪 Testing basic functionality...")
                
                # Test insert with trigger
                cur.execute("""
                    INSERT INTO edinburgh_docs (title, content, category, subcategory)
                    VALUES ('Test Document', 'This is a test document for schema verification.', 'Test', 'Verification')
                    RETURNING id, word_count, char_count, content_hash;
                """)
                test_result = cur.fetchone()
                test_id, word_count, char_count, content_hash = test_result
                
                print(f"   ✅ Insert successful (ID: {test_id})")
                print(f"   ✅ Word count auto-calculated: {word_count}")
                print(f"   ✅ Character count auto-calculated: {char_count}")
                print(f"   ✅ Content hash auto-generated: {content_hash[:16]}...")
                
                # Clean up test data
                cur.execute("DELETE FROM edinburgh_docs WHERE id = %s;", (test_id,))
                print(f"   🗑️  Test data cleaned up")
                
                conn.commit()
                
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False
    
    print("\n✅ Schema verification successful!")
    return True

def show_usage_examples():
    """Show examples of how to use the created schema."""
    print("\n📖 USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        ("Insert a document", """
INSERT INTO edinburgh_docs (title, content, category, subcategory, source_url)
VALUES ('WiFi Setup Guide', 'Connect to EdUni network...', 'IT Support', 'Networking', 'https://ed.ac.uk/wifi');
        """),
        ("Search similar documents (after adding embeddings)", """
SELECT * FROM search_similar_documents(
    '[0.1,0.2,...]'::vector(1024),  -- query embedding
    0.7,  -- similarity threshold
    5,    -- max results  
    'IT Support'  -- category filter
);
        """),
        ("Hybrid text + vector search", """
SELECT title, category, 
       ts_rank(content_tsvector, query) as text_relevance,
       1 - (content_embedding <=> '[...]'::vector) as vector_similarity
FROM edinburgh_docs, plainto_tsquery('password reset') query
WHERE content_tsvector @@ query
ORDER BY (text_relevance + vector_similarity) DESC;
        """),
        ("Get category summary", """
SELECT * FROM edinburgh_docs_summary;
        """)
    ]
    
    for title, sql in examples:
        print(f"\n💡 {title}:")
        print(sql.strip())

def main():
    """Main schema creation workflow."""
    print("🚀 EDINBURGH KNOWLEDGE BASE SCHEMA CREATION")
    print("=" * 60)
    print("Creating production-ready database schema for Edinburgh's AI system.\n")
    
    # Create schema
    if not create_edinburgh_schema():
        print("❌ Schema creation failed!")
        return 1
    
    # Verify schema
    if not verify_schema():
        print("❌ Schema verification failed!")
        return 1
    
    # Show usage examples
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("✅ SCHEMA CREATION COMPLETE!")
    print("Your Edinburgh knowledge base is ready for documents and embeddings.")
    print("\n💡 Next steps:")
    print("   • Load sample Edinburgh documents")
    print("   • Generate and store embeddings")
    print("   • Create vector indexes for performance")
    print("   • Test search functionality")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)