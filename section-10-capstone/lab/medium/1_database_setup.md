# 🌶️🌶️ Medium: Database Setup - Guided Experimentation

**"I like to experiment and add my own flavors"**

This guide gives you working examples with some gaps to fill in. You'll learn by doing while having guidance when you need it!

## Step 1: Database Connection

Here's a working database connection function with some improvements for you to implement:

```python
# services/database_manager.py
import psycopg
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
    
    TODO: Add connection pooling for better performance
    TODO: Add retry logic for failed connections
    TODO: Add connection timeout configuration
    """
    try:
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
    
    TODO: Add more sophisticated indexing strategies
    TODO: Add table partitioning for large datasets
    TODO: Add database migration system
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
                
                # Basic indexes
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_metadata ON document_chunks USING gin (metadata);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_info ON document_chunks USING gin (document_info);")
                
                conn.commit()
                logger.info("Database initialized successfully")
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
```

## Step 2: Implement Store Function

Here's the basic structure - implement the missing parts:

```python
def store_chunk(chunk_data: Dict[str, Any], embedding: List[float]) -> bool:
    """
    Store a document chunk in the database.
    
    TODO: Add batch insertion for better performance
    TODO: Add duplicate detection and handling
    TODO: Add data validation before insertion
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # TODO: Add validation for chunk_data
                # TODO: Add validation for embedding dimensions
                # TODO: Add error handling for specific database errors
                
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
```

## Step 3: Implement Search Function

Here's the search function with advanced features to implement:

```python
def search_chunks(query_embedding: List[float], limit: int = 10, similarity_threshold: float = 0.4, 
                 filters: Dict[str, Any] = None) -> List[SearchResult]:
    """
    Search for similar chunks using vector similarity.
    
    TODO: Add JSONB filtering support
    TODO: Add hybrid search (vector + text)
    TODO: Add result ranking and scoring
    TODO: Add query caching
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=psycopg.RealDictCursor) as cur:
                # TODO: Build dynamic WHERE clause based on filters
                # TODO: Add query expansion
                # TODO: Add result ranking algorithm
                
                cur.execute("""
                    SELECT 
                        chunk_id,
                        content,
                        metadata,
                        document_info,
                        processing_info,
                        1 - (embedding <=> %s) as similarity_score
                    FROM document_chunks
                    WHERE 1 - (embedding <=> %s) > %s
                    ORDER BY embedding <=> %s
                    LIMIT %s
                """, (query_embedding, query_embedding, similarity_threshold, query_embedding, limit))
                
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
```

## Step 4: Add Advanced Features

Here are some advanced features you can implement:

### Feature 1: Batch Operations
```python
def store_chunks_batch(chunks_data: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
    """
    Store multiple chunks in a single transaction.
    
    TODO: Implement batch insertion
    TODO: Add progress tracking
    TODO: Add error handling for partial failures
    """
    # Your implementation here
    pass
```

### Feature 2: JSONB Filtering
```python
def search_with_filters(query_embedding: List[float], filters: Dict[str, Any]) -> List[SearchResult]:
    """
    Search with JSONB metadata filtering.
    
    TODO: Build dynamic WHERE clause
    TODO: Add support for nested JSONB queries
    TODO: Add query optimization
    """
    # Your implementation here
    pass
```

### Feature 3: Connection Pooling
```python
class DatabasePool:
    """
    Connection pool for better performance.
    
    TODO: Implement connection pooling
    TODO: Add connection health checks
    TODO: Add pool monitoring
    """
    # Your implementation here
    pass
```

## Step 5: Test Your Implementation

Create a comprehensive test:

```python
# test_database_medium.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_manager import *

def test_advanced_features():
    """Test your advanced implementations"""
    print("🌶️🌶️ Testing Advanced Database Features...")
    
    # Test your batch operations
    # Test your JSONB filtering
    # Test your connection pooling
    # Add your own tests!
    
    print("🎉 Advanced features tested!")

if __name__ == "__main__":
    test_advanced_features()
```

## What You've Learned

✅ **Database Connection**: Advanced connection handling
✅ **Table Creation**: Sophisticated table design
✅ **Vector Storage**: Optimized vector operations
✅ **JSONB Usage**: Advanced metadata querying
✅ **Performance**: Batch operations and optimization

## Next Steps

Once you've implemented the advanced features, you're ready for:
- **[Medium: Document Processing](document_processing.md)** - Advanced document processing
- **[Medium: Search Engine](search_engine.md)** - Hybrid search implementation

## Challenges to Try

1. **Performance**: How can you make batch operations faster?
2. **Filtering**: What JSONB queries would be useful for your project?
3. **Caching**: How can you cache frequent queries?
4. **Monitoring**: What metrics would help you understand performance?

## Getting Help

- Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Ask questions in the discussion forum
- Look at the [Spicy version](../spicy/database_setup.md) for inspiration

Remember: There's no single "right" way to implement these features. Experiment and find what works best for your project! 🚀
