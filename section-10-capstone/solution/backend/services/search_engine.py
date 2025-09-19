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
    
    This function:
    1. Creates an embedding for the search query
    2. Searches the database for similar chunks
    3. Returns ranked results with metadata
    """
    if not options:
        options = {}
    
    logger.info(f"Searching for: {query}")
    
    try:
        # Step 1: Create embedding for the query
        query_embedding = create_embedding(query)
        if not query_embedding:
            logger.error("Failed to create query embedding")
            return []
        
        # Step 2: Search database for similar chunks
        limit = options.get('limit', 10)
        
        search_results = database_manager.search_chunks(
            query_embedding=query_embedding,
            limit=limit,
        )
        
        # Step 3: Rank and filter results
        ranked_results = rank_results(search_results, query)
        
        logger.info(f"Found {len(ranked_results)} relevant documents")
        return ranked_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []

def create_embedding(text: str) -> List[float]:
    """
    Create a vector embedding for text using Ollama.
    
    This function:
    1. Sends text to Ollama embedding service
    2. Returns the vector embedding
    3. Handles errors gracefully
    """
    try:
        # Prepare the request
        payload = {
            "model": EMBEDDING_MODEL,
            "input": text
        }
        
        # Send request to Ollama
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get('embeddings')[0]

            
            if embedding and len(embedding) == 1024:
                logger.info(f"Created embedding with {len(embedding)} dimensions")
                return embedding
            else:
                logger.error(f"Invalid embedding format: {len(embedding) if embedding else 'None'} dimensions")
                return []
        else:
            logger.error(f"Ollama request failed: {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error creating embedding: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error creating embedding: {e}")
        return []

def rank_results(results: List[SearchResult], query: str) -> List[SearchResult]:
    """
    Rank search results by relevance.
    
    This function:
    1. Sorts results by similarity score
    2. Applies additional ranking factors
    3. Returns ordered results
    """
    if not results:
        return []
    
    # Sort by similarity score (highest first)
    ranked_results = sorted(results, key=lambda x: x.similarity_score, reverse=True)
    
    # TODO: Add more sophisticated ranking
    # - Boost results with query terms in title
    # - Boost results with higher metadata scores
    # - Apply project-specific ranking
    
    return ranked_results

def search_with_filters(query: str, filters: Dict[str, Any] = None) -> List[SearchResult]:
    """
    Search with additional filters.
    
    This function:
    1. Creates query embedding
    2. Applies metadata filters
    3. Returns filtered results
    """
    if not filters:
        filters = {}
    
    logger.info(f"Searching with filters: {filters}")
    
    try:
        # Create embedding
        query_embedding = create_embedding(query)
        if not query_embedding:
            return []
        
        # Search with filters
        # TODO: Implement JSONB filtering
        # For now, search all and filter in Python
        all_results = database_manager.search_chunks(
            query_embedding=query_embedding,
            limit=50,  # Get more results to filter
            similarity_threshold=0.1
        )
        
        # Apply filters
        filtered_results = apply_filters(all_results, filters)
        
        # Rank and limit results
        ranked_results = rank_results(filtered_results, query)
        
        return ranked_results[:10]  # Return top 10
        
    except Exception as e:
        logger.error(f"Filtered search failed: {e}")
        return []

def apply_filters(results: List[SearchResult], filters: Dict[str, Any]) -> List[SearchResult]:
    """
    Apply metadata filters to search results.
    
    This function:
    1. Filters by document type
    2. Filters by author
    3. Filters by custom metadata
    4. Returns filtered results
    """
    filtered_results = []
    
    for result in results:
        # Check document type filter
        if 'document_type' in filters:
            if result.document_info.get('document_type') != filters['document_type']:
                continue
        
        # Check author filter
        if 'author' in filters:
            if result.document_info.get('author') != filters['author']:
                continue
        
        # Check custom metadata filters
        if 'metadata_filters' in filters:
            metadata_filters = filters['metadata_filters']
            for key, value in metadata_filters.items():
                if result.metadata.get(key) != value:
                    continue
        
        # Check date range filter
        if 'date_range' in filters:
            date_range = filters['date_range']
            # TODO: Implement date filtering
            pass
        
        filtered_results.append(result)
    
    return filtered_results

def search_similar_documents(document_id: str, limit: int = 5) -> List[SearchResult]:
    """
    Find documents similar to a given document.
    
    This function:
    1. Gets the document's embedding
    2. Searches for similar documents
    3. Returns ranked similar documents
    """
    try:
        # Get document embedding from database
        # TODO: Implement get_document_embedding function
        document_embedding = get_document_embedding(document_id)
        if not document_embedding:
            logger.error(f"Could not find embedding for document {document_id}")
            return []
        
        # Search for similar documents
        similar_results = database_manager.search_chunks(
            query_embedding=document_embedding,
            limit=limit,
            similarity_threshold=0.3
        )
        
        # Filter out the original document
        filtered_results = [r for r in similar_results if r.chunk_id != document_id]
        
        return filtered_results
        
    except Exception as e:
        logger.error(f"Similar document search failed: {e}")
        return []

def get_document_embedding(document_id: str) -> List[float]:
    """
    Get the embedding for a specific document.
    
    This function:
    1. Queries the database for the document
    2. Returns its embedding vector
    """
    try:
        with database_manager.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT embedding FROM document_chunks WHERE chunk_id = %s",
                    (document_id,)
                )
                result = cur.fetchone()
                
                if result and result[0]:
                    return result[0]
                else:
                    return []
                    
    except Exception as e:
        logger.error(f"Failed to get document embedding: {e}")
        return []

def search_by_keywords(query: str, keywords: List[str]) -> List[SearchResult]:
    """
    Search using both vector similarity and keyword matching.
    
    This function:
    1. Performs vector search
    2. Performs keyword search
    3. Combines and ranks results
    """
    try:
        # Vector search
        vector_results = search_documents(query)
        
        # Keyword search
        keyword_results = search_by_keywords_only(keywords)
        
        # Combine results
        combined_results = combine_search_results(vector_results, keyword_results)
        
        # Rank combined results
        ranked_results = rank_combined_results(combined_results, query, keywords)
        
        return ranked_results
        
    except Exception as e:
        logger.error(f"Keyword search failed: {e}")
        return []

def search_by_keywords_only(keywords: List[str]) -> List[SearchResult]:
    """
    Search using only keyword matching.
    
    This function:
    1. Searches content for keywords
    2. Ranks by keyword frequency
    3. Returns keyword-based results
    """
    try:
        with database_manager.get_db_connection() as conn:
            with conn.cursor() as cur:
                # Build keyword search query
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.append(f"content ILIKE '%{keyword}%'")
                
                where_clause = " OR ".join(keyword_conditions)
                
                cur.execute(f"""
                    SELECT 
                        chunk_id,
                        content,
                        metadata,
                        document_info,
                        processing_info,
                        1.0 as similarity_score
                    FROM document_chunks
                    WHERE {where_clause}
                    ORDER BY 
                        CASE 
                            {' + '.join([f"CASE WHEN content ILIKE '%{kw}%' THEN 1 ELSE 0 END" for kw in keywords])}
                        END DESC
                    LIMIT 20
                """)
                
                results = []
                for row in cur.fetchall():
                    result = SearchResult(
                        chunk_id=row[0],
                        content=row[1],
                        metadata=row[2],
                        document_info=row[3],
                        processing_info=row[4],
                        similarity_score=row[5]
                    )
                    results.append(result)
                
                return results
                
    except Exception as e:
        logger.error(f"Keyword search failed: {e}")
        return []

def combine_search_results(vector_results: List[SearchResult], keyword_results: List[SearchResult]) -> List[SearchResult]:
    """
    Combine vector and keyword search results.
    
    This function:
    1. Merges results from both searches
    2. Deduplicates by chunk_id
    3. Combines similarity scores
    """
    # Create a dictionary to store combined results
    combined_dict = {}
    
    # Add vector results
    for result in vector_results:
        combined_dict[result.chunk_id] = result
    
    # Add keyword results with combined scoring
    for result in keyword_results:
        if result.chunk_id in combined_dict:
            # Combine scores (weighted average)
            existing_score = combined_dict[result.chunk_id].similarity_score
            combined_score = (existing_score + result.similarity_score) / 2
            combined_dict[result.chunk_id].similarity_score = combined_score
        else:
            combined_dict[result.chunk_id] = result
    
    return list(combined_dict.values())

def rank_combined_results(results: List[SearchResult], query: str, keywords: List[str]) -> List[SearchResult]:
    """
    Rank combined search results.
    
    This function:
    1. Applies multiple ranking factors
    2. Boosts results with query terms
    3. Returns optimally ranked results
    """
    for result in results:
        # Boost score for query terms in content
        query_terms = query.lower().split()
        content_lower = result.content.lower()
        
        query_boost = sum(1 for term in query_terms if term in content_lower)
        result.similarity_score += query_boost * 0.1
        
        # Boost score for keyword matches
        keyword_boost = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        result.similarity_score += keyword_boost * 0.05
    
    # Sort by combined score
    return sorted(results, key=lambda x: x.similarity_score, reverse=True)

def track_search_analytics(query: str, results: List[SearchResult], search_time: float):
    """
    Track search analytics for performance monitoring.
    
    This function:
    1. Records search metrics
    2. Tracks query performance
    3. Stores analytics data
    """
    try:
        analytics_data = {
            'query_text': query,
            'result_count': len(results),
            'search_time_ms': search_time * 1000,
            'avg_similarity': sum(r.similarity_score for r in results) / len(results) if results else 0,
            'top_similarity': results[0].similarity_score if results else 0,
            'query_metadata': {
                'word_count': len(query.split()),
                'has_question': '?' in query,
                'has_quotes': '"' in query,
                'query_type': classify_query_type(query)
            },
            'response_metadata': {
                'document_types': list(set(r.document_info.get('document_type', 'unknown') for r in results)),
                'authors': list(set(r.document_info.get('author', 'unknown') for r in results)),
                'date_range': get_date_range(results)
            }
        }
        
        # Store analytics in database
        store_search_analytics(analytics_data)
        
    except Exception as e:
        logger.error(f"Failed to track search analytics: {e}")

def store_search_analytics(analytics_data: Dict[str, Any]):
    """
    Store search analytics in the database.
    """
    try:
        with database_manager.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO query_analytics 
                    (query_text, query_metadata, response_metadata, user_session)
                    VALUES (%s, %s, %s, %s)
                """, (
                    analytics_data['query_text'],
                    json.dumps(analytics_data['query_metadata']),
                    json.dumps(analytics_data['response_metadata']),
                    json.dumps({'search_time_ms': analytics_data['search_time_ms']})
                ))
                conn.commit()
                
    except Exception as e:
        logger.error(f"Failed to store analytics: {e}")

def classify_query_type(query: str) -> str:
    """
    Classify the type of search query.
    """
    query_lower = query.lower()
    
    if query_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
        return 'question'
    elif query_lower.startswith(('find', 'search', 'look for')):
        return 'search'
    elif query_lower.startswith(('explain', 'describe', 'tell me about')):
        return 'explanation'
    else:
        return 'general'

def get_date_range(results: List[SearchResult]) -> Dict[str, str]:
    """
    Get date range from search results.
    """
    dates = []
    for result in results:
        created_at = result.processing_info.get('processing_timestamp')
        if created_at:
            dates.append(created_at)
    
    if dates:
        return {
            'earliest': min(dates),
            'latest': max(dates)
        }
    else:
        return {}


