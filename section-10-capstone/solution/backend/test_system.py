#!/usr/bin/env python3
"""
Test script for the improved RAG system
Demonstrates the modern psycopg approach with dataclasses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import database_manager, search_engine, llm_integration
from services.database_manager import SearchResult
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_operations():
    """Test database operations with modern psycopg approach"""
    print("🧪 Testing Database Operations")
    print("=" * 50)
    
    # Initialize database
    try:
        database_manager.initialize_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    # Test connection validation
    if database_manager.validate_database_connection():
        print("✅ Database connection validated")
    else:
        print("❌ Database connection validation failed")
        return False
    
    # Test document stats
    stats = database_manager.get_document_stats()
    print(f"📊 Document stats: {stats.get('total_chunks', 0)} chunks")
    
    return True

def test_search_functionality():
    """Test search functionality with SearchResult dataclasses"""
    print("\n🔍 Testing Search Functionality")
    print("=" * 50)
    
    # Test embedding generation
    test_query = "What are the main themes in this literature?"
    embedding = search_engine.get_embedding(test_query)
    
    if embedding:
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
    else:
        print("❌ Embedding generation failed")
        return False
    
    # Test search
    results = search_engine.search_documents(test_query, {
        'max_results': 3,
        'similarity_threshold': 0.3
    })
    
    print(f"🔍 Search results: {len(results)} found")
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.chunk_id} - {result.similarity_score:.3f}")
        print(f"      Content: {result.content[:100]}...")
        print(f"      Metadata: {result.metadata}")
        print()
    
    return True

def test_llm_integration():
    """Test LLM integration with SearchResult objects"""
    print("\n🤖 Testing LLM Integration")
    print("=" * 50)
    
    # Create mock search results
    mock_results = [
        SearchResult(
            chunk_id="test_001",
            content="This is a test document about literature and themes.",
            metadata={"themes": ["love", "death"], "characters": ["Hamlet"]},
            document_info={"title": "Test Document", "author": "Test Author"},
            processing_info={"chunk_index": 0},
            similarity_score=0.85
        )
    ]
    
    # Test context building
    context = llm_integration.build_context(mock_results)
    print(f"✅ Built context: {len(context)} characters")
    
    # Test source extraction
    sources = llm_integration.extract_sources(mock_results)
    print(f"✅ Extracted sources: {len(sources)} sources")
    
    for source in sources:
        print(f"   - {source['title']} by {source['author']} ({source['similarity_score']:.3f})")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Improved RAG System")
    print("=" * 60)
    print("Using modern psycopg with dataclasses and context managers")
    print()
    
    tests = [
        test_database_operations,
        test_search_functionality,
        test_llm_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! System is ready.")
    else:
        print("⚠️  Some tests failed. Check configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
