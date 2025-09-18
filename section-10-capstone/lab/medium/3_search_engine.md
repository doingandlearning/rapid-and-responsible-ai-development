# 🌶️🌶️ Medium: Search Engine - Guided Experimentation

**"I like to experiment and add my own flavors"**

This guide gives you working examples with some gaps to fill in. You'll learn by doing while having guidance when you need it!

## Step 1: Core Search Engine

Here's the working structure with some improvements for you to implement:

```python
# services/search_engine.py
import requests
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from . import database_manager
from .database_manager import SearchResult

logger = logging.getLogger(__name__)

# Configuration
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"

def search_documents(query: str, options: Dict[str, Any] = None) -> List[SearchResult]:
    """
    Search for relevant documents using vector similarity.
    
    TODO: Add query expansion
    TODO: Add result caching
    TODO: Add performance monitoring
    TODO: Add advanced ranking algorithms
    """
    if not options:
        options = {}
    
    logger.info(f"Searching for: {query}")
    
    try:
        # TODO: Add query preprocessing
        processed_query = preprocess_query(query)
        
        # Create embedding
        query_embedding = create_embedding(processed_query)
        if not query_embedding:
            logger.error("Failed to create query embedding")
            return []
        
        # TODO: Add hybrid search (vector + text)
        search_results = perform_hybrid_search(query, query_embedding, options)
        
        # TODO: Add advanced ranking
        ranked_results = advanced_ranking(search_results, query, options)
        
        # TODO: Add result post-processing
        final_results = post_process_results(ranked_results, options)
        
        logger.info(f"Found {len(final_results)} relevant documents")
        return final_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []

def preprocess_query(query: str) -> str:
    """
    Preprocess search query for better results.
    
    TODO: Implement query expansion
    TODO: Add query normalization
    TODO: Add stopword removal
    TODO: Add synonym expansion
    """
    # TODO: Your query preprocessing implementation
    # - Remove stopwords
    # - Expand synonyms
    # - Normalize text
    # - Add query suggestions
    
    return query

def perform_hybrid_search(query: str, query_embedding: List[float], options: Dict[str, Any]) -> List[SearchResult]:
    """
    Perform hybrid search combining vector and text search.
    
    TODO: Implement vector search
    TODO: Implement text search
    TODO: Combine results intelligently
    TODO: Add query expansion
    """
    # TODO: Your hybrid search implementation
    # - Vector similarity search
    # - Text-based keyword search
    # - Result combination strategy
    # - Query expansion techniques
    
    pass

def advanced_ranking(results: List[SearchResult], query: str, options: Dict[str, Any]) -> List[SearchResult]:
    """
    Advanced ranking algorithm for search results.
    
    TODO: Implement multiple ranking factors
    TODO: Add learning-to-rank features
    TODO: Add personalization
    TODO: Add diversity ranking
    """
    # TODO: Your advanced ranking implementation
    # - Multiple ranking signals
    # - Learning-to-rank features
    # - Personalization based on user history
    # - Diversity to avoid duplicate results
    
    pass

def post_process_results(results: List[SearchResult], options: Dict[str, Any]) -> List[SearchResult]:
    """
    Post-process search results.
    
    TODO: Add result deduplication
    TODO: Add result clustering
    TODO: Add result summarization
    TODO: Add result highlighting
    """
    # TODO: Your post-processing implementation
    # - Remove duplicate results
    # - Cluster similar results
    # - Add result summaries
    # - Highlight matching terms
    
    pass
```

## Step 2: Implement Advanced Embedding Features

Here are some advanced embedding features to implement:

```python
def create_embedding(text: str, model: str = None) -> List[float]:
    """
    Create embedding with advanced features.
    
    TODO: Add embedding caching
    TODO: Add multiple model support
    TODO: Add embedding normalization
    TODO: Add error handling and retries
    """
    if not model:
        model = EMBEDDING_MODEL
    
    # TODO: Check cache first
    cached_embedding = get_cached_embedding(text, model)
    if cached_embedding:
        return cached_embedding
    
    try:
        # TODO: Add retry logic
        # TODO: Add timeout handling
        # TODO: Add batch processing
        
        payload = {
            "model": model,
            "prompt": text
        }
        
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get('embedding')
            
            if embedding and len(embedding) == 1024:
                # TODO: Normalize embedding
                normalized_embedding = normalize_embedding(embedding)
                
                # TODO: Cache embedding
                cache_embedding(text, model, normalized_embedding)
                
                return normalized_embedding
            else:
                logger.error(f"Invalid embedding format")
                return []
        else:
            logger.error(f"Ollama request failed: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")
        return []

def normalize_embedding(embedding: List[float]) -> List[float]:
    """
    Normalize embedding vector.
    
    TODO: Implement L2 normalization
    TODO: Add other normalization techniques
    TODO: Add embedding validation
    """
    # TODO: Your normalization implementation
    # - L2 normalization
    # - Min-max normalization
    # - Z-score normalization
    # - Validation checks
    
    pass

def get_cached_embedding(text: str, model: str) -> Optional[List[float]]:
    """
    Get embedding from cache.
    
    TODO: Implement embedding cache
    TODO: Add cache expiration
    TODO: Add cache size management
    """
    # TODO: Your caching implementation
    # - Redis or in-memory cache
    # - Cache key generation
    # - Expiration handling
    # - Size limits
    
    pass

def cache_embedding(text: str, model: str, embedding: List[float]):
    """
    Cache embedding for future use.
    
    TODO: Implement cache storage
    TODO: Add cache metadata
    TODO: Add cache cleanup
    """
    # TODO: Your cache storage implementation
    # - Store embedding with metadata
    # - Add timestamp and usage count
    # - Implement LRU eviction
    # - Add cache statistics
    
    pass
```

## Step 3: Implement Advanced Search Features

Here are some advanced search features to implement:

```python
def search_with_reranking(query: str, initial_results: List[SearchResult]) -> List[SearchResult]:
    """
    Rerank search results using advanced techniques.
    
    TODO: Implement learning-to-rank
    TODO: Add query-document matching
    TODO: Add user behavior signals
    TODO: Add content quality signals
    """
    # TODO: Your reranking implementation
    # - Learning-to-rank algorithms
    # - Query-document similarity
    # - User click-through rates
    # - Content freshness and quality
    
    pass

def search_with_expansion(query: str, expansion_terms: List[str]) -> List[SearchResult]:
    """
    Search with query expansion.
    
    TODO: Implement query expansion
    TODO: Add synonym detection
    TODO: Add related term discovery
    TODO: Add expansion scoring
    """
    # TODO: Your query expansion implementation
    # - Synonym expansion
    # - Related term discovery
    # - Expansion term scoring
    # - Query reformulation
    
    pass

def search_with_facets(query: str, facets: Dict[str, List[str]]) -> Dict[str, List[SearchResult]]:
    """
    Search with faceted results.
    
    TODO: Implement faceted search
    TODO: Add facet counting
    TODO: Add facet filtering
    TODO: Add facet navigation
    """
    # TODO: Your faceted search implementation
    # - Facet extraction
    # - Facet counting
    # - Facet filtering
    # - Facet navigation UI
    
    pass

def search_with_autocomplete(query: str, limit: int = 5) -> List[str]:
    """
    Provide search autocomplete suggestions.
    
    TODO: Implement autocomplete
    TODO: Add query suggestion
    TODO: Add popular queries
    TODO: Add personalization
    """
    # TODO: Your autocomplete implementation
    # - Query prefix matching
    # - Popular query suggestions
    # - Personal query history
    # - Typo correction
    
    pass
```

## Step 4: Implement Performance Optimization

Here are some performance optimizations to implement:

```python
def optimize_search_performance(query: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize search performance based on query characteristics.
    
    TODO: Implement query analysis
    TODO: Add performance tuning
    TODO: Add caching strategies
    TODO: Add load balancing
    """
    # TODO: Your performance optimization implementation
    # - Query complexity analysis
    # - Dynamic timeout adjustment
    # - Cache strategy selection
    # - Resource allocation
    
    pass

def batch_search(queries: List[str], options: Dict[str, Any] = None) -> List[List[SearchResult]]:
    """
    Perform batch search for multiple queries.
    
    TODO: Implement batch processing
    TODO: Add parallel processing
    TODO: Add result aggregation
    TODO: Add error handling
    """
    # TODO: Your batch search implementation
    # - Parallel query processing
    # - Batch embedding creation
    # - Result aggregation
    # - Error handling and recovery
    
    pass

def search_with_caching(query: str, options: Dict[str, Any] = None) -> List[SearchResult]:
    """
    Search with intelligent caching.
    
    TODO: Implement search result caching
    TODO: Add cache invalidation
    TODO: Add cache warming
    TODO: Add cache analytics
    """
    # TODO: Your caching implementation
    # - Search result caching
    # - Cache key generation
    # - Cache invalidation strategies
    # - Cache performance monitoring
    
    pass
```

## Step 5: Implement Advanced Analytics

Here are some advanced analytics features to implement:

```python
def track_advanced_analytics(query: str, results: List[SearchResult], search_time: float, user_context: Dict[str, Any] = None):
    """
    Track advanced search analytics.
    
    TODO: Implement comprehensive analytics
    TODO: Add user behavior tracking
    TODO: Add search quality metrics
    TODO: Add performance monitoring
    """
    # TODO: Your advanced analytics implementation
    # - Query success metrics
    # - User engagement tracking
    # - Search quality assessment
    # - Performance monitoring
    
    pass

def analyze_search_patterns(analytics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze search patterns and trends.
    
    TODO: Implement pattern analysis
    TODO: Add trend detection
    TODO: Add anomaly detection
    TODO: Add insights generation
    """
    # TODO: Your pattern analysis implementation
    # - Query pattern analysis
    # - User behavior patterns
    # - Search trend detection
    # - Anomaly detection
    
    pass

def generate_search_insights(analytics_data: List[Dict[str, Any]]) -> List[str]:
    """
    Generate actionable search insights.
    
    TODO: Implement insight generation
    TODO: Add recommendation engine
    TODO: Add optimization suggestions
    TODO: Add user guidance
    """
    # TODO: Your insight generation implementation
    # - Search optimization suggestions
    # - Content gap identification
    # - User experience improvements
    # - Performance recommendations
    
    pass
```

## Step 6: Test Your Advanced Features

Create a comprehensive test:

```python
# test_search_engine_medium.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_engine import *

def test_advanced_features():
    """Test your advanced search engine features"""
    print("🌶️🌶️ Testing Advanced Search Engine...")
    
    # Test your query preprocessing
    # Test your hybrid search
    # Test your advanced ranking
    # Test your performance optimizations
    # Test your analytics
    # Add your own tests!
    
    print("🎉 Advanced features tested!")

if __name__ == "__main__":
    test_advanced_features()
```

## What You've Learned

✅ **Advanced Search**: Hybrid search combining vector and text
✅ **Performance**: Caching, batching, and optimization
✅ **Analytics**: Comprehensive search tracking and analysis
✅ **Ranking**: Advanced result ranking and reranking
✅ **User Experience**: Autocomplete, faceting, and personalization

## Next Steps

Once you've implemented the advanced features, you're ready for:
- **[Medium: RAG Pipeline](rag_pipeline.md)** - Enhanced RAG system
- **[Medium: Frontend Integration](frontend_integration.md)** - Advanced UI features

## Challenges to Try

1. **Performance**: How can you make search 10x faster?
2. **Quality**: What metrics help you measure search quality?
3. **Personalization**: How can you personalize search results?
4. **Analytics**: What insights can you extract from search data?

## Getting Help

- Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Ask questions in the discussion forum
- Look at the [Spicy version](../spicy/search_engine.md) for inspiration
- Experiment with different approaches!

Remember: There's no single "right" way to implement these features. Try different approaches and see what works best for your project! 🚀
