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
    print(results)
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