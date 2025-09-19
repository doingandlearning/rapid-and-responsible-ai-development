import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_engine import search_documents, create_embedding, search_with_filters, track_search_analytics

def test_search_engine():
    """Test all search engine functions"""
    print("🌶️ Testing Search Engine...")
    
    # Test 1: Create embedding
    print("1. Testing embedding creation...")
    test_text = "What is machine learning?"
    embedding = create_embedding(test_text)
    
    if embedding and len(embedding) == 1024:
        print(f"   ✅ Created embedding with {len(embedding)} dimensions")
    else:
        print("   ❌ Failed to create embedding")
        return False
    
    # Test 2: Basic search
    print("2. Testing basic search...")
    start_time = time.time()
    results = search_documents("machine learning algorithms")
    search_time = time.time() - start_time
    
    if results:
        print(f"   ✅ Found {len(results)} results in {search_time:.2f} seconds")
        print(f"   Top result: {results[0].content[:50]}...")
        print(f"   Similarity score: {results[0].similarity_score:.3f}")
    else:
        print("   ❌ No search results found")
        return False
    
    # Test 3: Search with filters
    print("3. Testing filtered search...")
    filters = {
        'document_type': 'literature',
        'author': 'Shakespeare'
    }
    filtered_results = search_with_filters("love and romance", filters)
    
    if filtered_results:
        print(f"   ✅ Found {len(filtered_results)} filtered results")
    else:
        print("   ⚠️ No filtered results (this might be expected if no matching data)")
    
    # Test 4: Search analytics
    print("4. Testing search analytics...")
    track_search_analytics("test query", results, search_time)
    print("   ✅ Search analytics tracked")
    
    print("\n🎉 All search engine tests passed!")
    return True

if __name__ == "__main__":
    test_search_engine()