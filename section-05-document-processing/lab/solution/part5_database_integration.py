"""
Part 5: Database Integration - Solution
======================================

This solution shows how to store document chunks with embeddings
in a PostgreSQL + pgvector database.
"""

import psycopg
import requests
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Configuration
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

@dataclass
class DocumentChunk:
    """Represents a chunk of a document with metadata."""
    id: str
    document_id: str
    document_title: str
    text: str
    page_number: int
    chunk_index: int
    word_count: int
    character_count: int
    section_title: str = None
    created_at: str = None

def get_embedding(text: str, max_retries: int = 3) -> Optional[List[float]]:
    """
    Generate embedding for text using Ollama BGE-M3 model.
    
    Args:
        text: Text to embed
        max_retries: Maximum number of retry attempts
        
    Returns:
        Embedding vector or None if failed
    """
    for attempt in range(max_retries):
        try:
            payload = {
                "model": EMBEDDING_MODEL,
                "input": text
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get("embeddings", [])
            
            if embedding and len(embedding[0]) == 1024:
                return embedding[0]
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"⚠️  Embedding failed for text: {text[:50]}... Error: {e}")
            time.sleep(1)
    
    return None

def setup_document_chunks_table():
    """
    Create enhanced table for document chunks with vector support.
    
    Returns:
        True if successful, False otherwise
    """
    print("🗄️  Setting up document chunks table...")
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Enable pgvector extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # Drop existing table if needed
                cur.execute("DROP TABLE IF EXISTS document_chunks CASCADE;")
                
                # Create enhanced table
                cur.execute("""
                    CREATE TABLE document_chunks (
                        id UUID PRIMARY KEY,
                        document_id TEXT NOT NULL,
                        document_title TEXT NOT NULL,
                        text TEXT NOT NULL,
                        embedding vector(1024),
                        page_number INTEGER,
                        section_title TEXT,
                        chunk_index INTEGER,
                        word_count INTEGER,
                        character_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create indexes for efficient querying
                cur.execute("CREATE INDEX idx_doc_chunks_document_id ON document_chunks (document_id);")
                cur.execute("CREATE INDEX idx_doc_chunks_page ON document_chunks (page_number);")
                cur.execute("CREATE INDEX idx_doc_chunks_section ON document_chunks (section_title);")
                
                # Create vector similarity index (only if pgvector is available)
                try:
                    cur.execute("""
                        CREATE INDEX idx_doc_chunks_embedding 
                        ON document_chunks 
                        USING hnsw (embedding vector_cosine_ops);
                    """)
                    print("✅ Vector similarity index created")
                except Exception as e:
                    print(f"⚠️  Could not create vector index: {e}")
                    print("   Vector similarity search may be slower")
                
                print("✅ Table and indexes created successfully")
                conn.commit()
                
    except Exception as e:
        print(f"❌ Table setup failed: {e}")
        return False
    
    return True

def store_chunks_in_database(chunks: List[DocumentChunk], batch_size: int = 10) -> int:
    """
    Store document chunks with embeddings in database.
    
    Args:
        chunks: List of DocumentChunk objects
        batch_size: Number of chunks to process at once
        
    Returns:
        Number of chunks successfully stored
    """
    print(f"💾 Storing {len(chunks)} chunks in database...")
    
    stored_count = 0
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    print(f"🧠 Generating embedding for chunk {i+1}/{len(chunks)}...", end=" ")
                    
                    embedding = get_embedding(chunk.text)
                    if not embedding:
                        print("❌ Failed")
                        continue
                    
                    # Store in database with properly formatted vector
                    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                    cur.execute("""
                        INSERT INTO document_chunks
                        (id, document_id, document_title, text, embedding,
                         page_number, section_title, chunk_index, word_count, character_count, created_at)
                        VALUES (%s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s, %s)
                    """, (
                        chunk.id,
                        chunk.document_id,
                        chunk.document_title,
                        chunk.text,
                        embedding_str,
                        chunk.page_number,
                        chunk.section_title,
                        chunk.chunk_index,
                        chunk.word_count,
                        chunk.character_count,
                        chunk.created_at
                    ))
                    
                    stored_count += 1
                    print("✅")
                    
                    # Commit in batches
                    if (i + 1) % batch_size == 0:
                        conn.commit()
                        print(f"💾 Committed batch {i+1-batch_size+1}-{i+1}")
                        time.sleep(0.5)  # Be nice to Ollama
                
                # Final commit
                conn.commit()
                print(f"✅ Stored {stored_count} chunks successfully")
                
    except Exception as e:
        print(f"❌ Database storage failed: {e}")
    
    return stored_count

def verify_chunk_storage() -> Dict[str, Any]:
    """
    Verify that chunks are stored correctly in the database.
    
    Returns:
        Dictionary with verification results
    """
    print("\n✅ VERIFYING CHUNK STORAGE")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Count total chunks
                cur.execute("SELECT COUNT(*) FROM document_chunks;")
                total_chunks = cur.fetchone()[0]
                print(f"📊 Total chunks stored: {total_chunks}")
                
                # Count chunks with embeddings
                cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
                chunks_with_embeddings = cur.fetchone()[0]
                print(f"🧠 Chunks with embeddings: {chunks_with_embeddings}/{total_chunks}")
                
                # Show document breakdown
                cur.execute("""
                    SELECT
                        document_title,
                        COUNT(*) as chunk_count,
                        AVG(word_count) as avg_words,
                        COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings
                    FROM document_chunks
                    GROUP BY document_title
                    ORDER BY document_title;
                """)
                
                results = cur.fetchall()
                print(f"\n📄 Document breakdown:")
                for title, count, avg_words, embeddings in results:
                    print(f"   • {title}")
                    print(f"     Chunks: {count}, Avg words: {avg_words:.1f}, Embeddings: {embeddings}")
                
                # Sample chunk verification
                cur.execute("""
                    SELECT text, word_count, page_number, section_title
                    FROM document_chunks
                    ORDER BY created_at
                    LIMIT 2;
                """)
                
                samples = cur.fetchall()
                print(f"\n📖 Sample chunks:")
                for i, (text, words, page, section) in enumerate(samples, 1):
                    section_info = f", Section: {section}" if section else ""
                    print(f"   {i}. Page {page}{section_info} ({words} words)")
                    print(f"      '{text[:120]}...'")
                
                # Check vector dimensions
                cur.execute("SELECT vector_dims(embedding) FROM document_chunks WHERE embedding IS NOT NULL LIMIT 1;")
                result = cur.fetchone()
                if result:
                    dims = result[0]
                    print(f"\n🔢 Embedding dimensions: {dims} (should be 1024 for BGE-M3)")
                    if dims == 1024:
                        print("   ✅ Embeddings are correct size")
                    else:
                        print("   ⚠️  Unexpected embedding size")
                
                return {
                    'total_chunks': total_chunks,
                    'chunks_with_embeddings': chunks_with_embeddings,
                    'document_breakdown': results,
                    'embedding_dimensions': dims if result else None
                }
                
    except Exception as e:
        print(f"❌ Storage verification failed: {e}")
        return {'error': str(e)}

def test_vector_similarity_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Test vector similarity search on stored chunks.
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        List of search results
    """
    print(f"\n🔍 Testing Vector Similarity Search")
    print(f"Query: '{query}'")
    print("=" * 50)
    
    try:
        # Generate embedding for query
        query_embedding = get_embedding(query)
        if not query_embedding:
            print("❌ Failed to generate query embedding")
            return []
        
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Perform similarity search with properly formatted vector
                try:
                    # Convert embedding to proper vector format
                    embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
                    
                    cur.execute("""
                        SELECT 
                            document_title,
                            text,
                            page_number,
                            section_title,
                            embedding <=> %s::vector as distance
                        FROM document_chunks
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (embedding_str, embedding_str, limit))
                except Exception as vector_error:
                    print(f"⚠️  Vector similarity not available: {vector_error}")
                    print("   Falling back to text search...")
                    
                    # Fallback to text search
                    cur.execute("""
                        SELECT 
                            document_title,
                            text,
                            page_number,
                            section_title,
                            0.0 as distance
                        FROM document_chunks
                        WHERE text ILIKE %s
                        ORDER BY document_title, page_number
                        LIMIT %s
                    """, (f"%{query}%", limit))
                
                results = cur.fetchall()
                
                print(f"📊 Found {len(results)} similar chunks:")
                for i, (title, text, page, section, distance) in enumerate(results, 1):
                    similarity = 1 - distance  # Convert distance to similarity
                    section_info = f" - {section}" if section else ""
                    print(f"\n   {i}. {title} (Page {page}{section_info})")
                    print(f"      Similarity: {similarity:.3f}")
                    print(f"      Text: {text[:100]}...")
                
                return results
                
    except Exception as e:
        print(f"❌ Similarity search failed: {e}")
        return []

def process_input_files_to_chunks(input_dir: str = "input") -> List[DocumentChunk]:
    """
    Process files from input directory and create chunks.
    
    Args:
        input_dir: Directory containing input files
        
    Returns:
        List of DocumentChunk objects
    """
    print(f"📁 Processing files from {input_dir} directory...")
    
    # Import text extraction and chunking functions
    from part1_text_extraction import process_all_input_files
    from part3_content_aware_chunking import create_content_aware_chunks
    
    # Process all files in input directory
    documents = process_all_input_files(input_dir)
    
    if not documents:
        print(f"⚠️  No files found in {input_dir} directory")
        return []
    
    all_chunks = []
    
    for filename, doc_data in documents.items():
        print(f"\n📄 Processing: {doc_data['title']}")
        
        # Create chunks using content-aware strategy
        doc_chunks = create_content_aware_chunks(
            doc_data, 
            max_chunk_size=400
        )
        
        print(f"   Created {len(doc_chunks)} chunks")
        all_chunks.extend(doc_chunks)
    
    print(f"\n📝 Total chunks created: {len(all_chunks)}")
    return all_chunks

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Database Integration")
    print("=" * 50)
    
    # Set up database table
    if not setup_document_chunks_table():
        print("❌ Failed to set up database table")
        exit(1)
    
    # Process input files and create chunks
    input_chunks = process_input_files_to_chunks("input")
    
    if not input_chunks:
        print("❌ No chunks created from input files")
        exit(1)
    
    # Store chunks in database
    stored_count = store_chunks_in_database(input_chunks)
    
    if stored_count > 0:
        print(f"\n🎉 Successfully stored {stored_count} chunks!")
        
        # Verify storage
        verification = verify_chunk_storage()
        
        # Test similarity search
        search_results = test_vector_similarity_search("university VPN access", limit=3)
        
        print(f"\n🎉 Database integration complete!")
        print(f"Next step: Implement verification and testing in Part 6")
    else:
        print("❌ Failed to store chunks in database")
