# 🌶️ Mild: Database Setup - Complete Working Code

**"I like to follow the recipe step-by-step"**

This guide gives you complete, working code for database operations. You can copy, paste, and understand every line!

## Step 1: Database Connection

Here's the complete working code for database connections:

```python
# services/database_manager.py
import psycopg
import psycopg.extras
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5050,
    'dbname': 'pgvector',
    'user': 'postgres',
    'password': 'postgres'
}

@dataclass
class SearchResult:
    """Represents a search result chunk with structured data."""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    document_info: Dict[str, Any]
    processing_info: Dict[str, Any]
    similarity_score: float

def get_db_connection():
    """
    Get database connection using psycopg with context manager.
    
    This function:
    1. Connects to PostgreSQL using our configuration
    2. Returns a connection object
    3. Handles connection errors gracefully
    """
    try:
        # Create connection using psycopg (psycopg3)
        conn = psycopg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        logger.info("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def initialize_database():
    """
    Initialize database tables and extensions.
    
    This function:
    1. Creates the pgvector extension
    2. Creates all necessary tables
    3. Sets up indexes for performance
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Enable pgvector extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # Create document_chunks table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id SERIAL PRIMARY KEY,
                        chunk_id VARCHAR(50) UNIQUE NOT NULL,
                        content TEXT NOT NULL,
                        embedding vector(1024),
                        
                        -- JSONB for flexible metadata storage
                        metadata JSONB NOT NULL DEFAULT '{}',
                        document_info JSONB NOT NULL DEFAULT '{}',
                        processing_info JSONB NOT NULL DEFAULT '{}',
                        
                        -- Extracted fields for performance
                        document_type VARCHAR(50),
                        author VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create query_analytics table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS query_analytics (
                        id SERIAL PRIMARY KEY,
                        query_text TEXT NOT NULL,
                        query_metadata JSONB DEFAULT '{}',
                        response_metadata JSONB DEFAULT '{}',
                        user_session JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create indexes for performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_metadata ON document_chunks USING gin (metadata);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_info ON document_chunks USING gin (document_info);")
                
                conn.commit()
                logger.info("Database initialized successfully")
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def store_chunk(chunk_data: Dict[str, Any], embedding: List[float]) -> bool:
    """
    Store a document chunk in the database.
    
    Args:
        chunk_data: Dictionary containing chunk information
        embedding: Vector embedding for the chunk
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO document_chunks 
                    (chunk_id, content, embedding, metadata, document_info, processing_info, document_type, author)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        document_info = EXCLUDED.document_info,
                        processing_info = EXCLUDED.processing_info,
                        document_type = EXCLUDED.document_type,
                        author = EXCLUDED.author
                """, (
                    chunk_data['chunk_id'],
                    chunk_data['content'],
                    embedding,
                    json.dumps(chunk_data['metadata']),
                    json.dumps(chunk_data['document_info']),
                    json.dumps(chunk_data['processing_info']),
                    chunk_data.get('document_type', 'unknown'),
                    chunk_data.get('author', 'Unknown')
                ))
                
                conn.commit()
                logger.info(f"Stored chunk: {chunk_data['chunk_id']}")
                return True
                
    except Exception as e:
        logger.error(f"Failed to store chunk {chunk_data.get('chunk_id', 'unknown')}: {e}")
        return False

def search_chunks(query_embedding: List[float], limit: int = 10, similarity_threshold: float = 0.4) -> List[SearchResult]:
    """
    Search for similar chunks using vector similarity.
    
    Args:
        query_embedding: Vector embedding of the search query
        limit: Maximum number of results to return
        similarity_threshold: Minimum similarity score (0-1)
        
    Returns:
        List of SearchResult objects
    """
    try:
        with get_db_connection() as conn:
            # Use RealDictCursor for named column access
            with conn.cursor(row_factory=psycopg.RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        chunk_id,
                        content,
                        metadata,
                        document_info,
                        processing_info,
                        1 - (embedding <=> %s) as similarity_score
                    FROM document_chunks
                    WHERE similarity_score > %s
                    ORDER BY similarity_score ASC
                    LIMIT %s
                """, (json.dumps(query_embedding),  similarity_threshold,  limit))
                
                results = []
                for row in cur.fetchall():
                    result = SearchResult(
                        chunk_id=row['chunk_id'],
                        content=row['content'],
                        metadata=row['metadata'],
                        document_info=row['document_info'],
                        processing_info=row['processing_info'],
                        similarity_score=float(row['similarity_score'])
                    )
                    results.append(result)
                
                logger.info(f"Found {len(results)} similar chunks")
                return results
                
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []

def validate_database_connection() -> bool:
    """
    Validate that database connection is working.
    
    Returns:
        bool: True if connection is working, False otherwise
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                return result is not None
    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        return False
```

## Step 2: Test Your Database Setup

Create this test file to verify everything works:

```python
# test_database.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_manager import initialize_database, validate_database_connection, store_chunk, search_chunks

def test_database():
    """Test all database functions"""
    print("🌶️ Testing Database Setup...")
    
    # Test 1: Validate connection
    print("1. Testing database connection...")
    if validate_database_connection():
        print("   ✅ Database connection successful!")
    else:
        print("   ❌ Database connection failed!")
        return False
    
    # Test 2: Initialize database
    print("2. Initializing database...")
    try:
        initialize_database()
        print("   ✅ Database initialized successfully!")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return False
    
    # Test 3: Store a test chunk
    print("3. Storing test chunk...")
    test_chunk = {
        'chunk_id': 'test_chunk_001',
        'content': 'This is a test document chunk for the RAG system.',
        'metadata': {'test': True, 'word_count': 10},
        'document_info': {'title': 'Test Document', 'author': 'Test Author'},
        'processing_info': {'chunk_index': 0, 'total_chunks': 1},
        'document_type': 'test',
        'author': 'Test Author'
    }
    
    test_embedding = [0.1] * 1024  # Dummy embedding
    
    if store_chunk(test_chunk, test_embedding):
        print("   ✅ Test chunk stored successfully!")
    else:
        print("   ❌ Failed to store test chunk!")
        return False
    
    # Test 4: Search for chunks
    print("4. Testing search...")
    results = search_chunks(test_embedding, limit=5)
    if results:
        print(f"   ✅ Found {len(results)} results!")
        print(f"   Top result: {results[0].content[:50]}...")
    else:
        print("   ❌ No search results found!")
        return False
    
    print("\n🎉 All database tests passed! You're ready for the next step!")
    return True

if __name__ == "__main__":
    test_database()
```

## Step 3: Run the Test

```bash
cd backend
python test_database.py
```

## What You've Learned

✅ **Database Connection**: How to connect to PostgreSQL with psycopg3
✅ **Table Creation**: How to create tables with JSONB columns
✅ **Vector Storage**: How to store and query vector embeddings
✅ **JSONB Usage**: How to store flexible metadata
✅ **Error Handling**: How to handle database errors gracefully

## Next Steps

Once your database tests pass, you're ready for:
- **[Mild: Document Processing](document_processing.md)** - Process documents into chunks
- **[Mild: Search Engine](search_engine.md)** - Create vector embeddings and search

## Troubleshooting

**If database connection fails:**
- Make sure PostgreSQL is running: `docker ps | grep postgres`
- Check if port 5050 is available
- Verify database credentials in `DB_CONFIG`

**If table creation fails:**
- Make sure you have permission to create tables
- Check if pgvector extension is available
- Look at the error message for specific issues

**If search returns no results:**
- Check if you have data in the database
- Verify the embedding vector has 1024 dimensions
- Try lowering the similarity threshold

Need help? Ask questions - we're here to support you! 🤝
