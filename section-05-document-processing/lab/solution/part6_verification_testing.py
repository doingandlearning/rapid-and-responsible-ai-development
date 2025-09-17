"""
Part 6: Verification & Testing - Solution
=========================================

This solution shows how to verify the complete document processing
pipeline and run comprehensive tests.
"""

import psycopg
import requests
import time
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
class TestResult:
    """Represents the result of a test."""
    test_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None

def test_database_connection() -> TestResult:
    """
    Test database connection and basic functionality.
    
    Returns:
        TestResult object
    """
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Test basic connection
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                
                if result[0] == 1:
                    return TestResult(
                        test_name="Database Connection",
                        passed=True,
                        message="Successfully connected to database",
                        details={"connection": "active"}
                    )
                else:
                    return TestResult(
                        test_name="Database Connection",
                        passed=False,
                        message="Database connection failed",
                        details={"error": "Unexpected result"}
                    )
                    
    except Exception as e:
        return TestResult(
            test_name="Database Connection",
            passed=False,
            message=f"Database connection failed: {str(e)}",
            details={"error": str(e)}
        )

def test_table_structure() -> TestResult:
    """
    Test that the document_chunks table exists and has correct structure.
    
    Returns:
        TestResult object
    """
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'document_chunks'
                    );
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    return TestResult(
                        test_name="Table Structure",
                        passed=False,
                        message="document_chunks table does not exist",
                        details={"table_exists": False}
                    )
                
                # Check table columns
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'document_chunks'
                    ORDER BY ordinal_position;
                """)
                columns = cur.fetchall()
                
                expected_columns = [
                    'id', 'document_id', 'document_title', 'text', 'embedding',
                    'page_number', 'section_title', 'chunk_index', 'word_count',
                    'character_count', 'created_at'
                ]
                
                actual_columns = [col[0] for col in columns]
                missing_columns = set(expected_columns) - set(actual_columns)
                
                if missing_columns:
                    return TestResult(
                        test_name="Table Structure",
                        passed=False,
                        message=f"Missing columns: {missing_columns}",
                        details={"expected": expected_columns, "actual": actual_columns}
                    )
                
                return TestResult(
                    test_name="Table Structure",
                    passed=True,
                    message="Table structure is correct",
                    details={"columns": actual_columns}
                )
                
    except Exception as e:
        return TestResult(
            test_name="Table Structure",
            passed=False,
            message=f"Table structure check failed: {str(e)}",
            details={"error": str(e)}
        )

def test_embedding_generation() -> TestResult:
    """
    Test that embeddings can be generated successfully.
    
    Returns:
        TestResult object
    """
    try:
        test_text = "This is a test document for embedding generation."
        
        payload = {
            "model": EMBEDDING_MODEL,
            "input": test_text
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        embedding = result.get("embeddings", [])
        
        if not embedding:
            return TestResult(
                test_name="Embedding Generation",
                passed=False,
                message="No embeddings returned from Ollama",
                details={"response": result}
            )
        
        if len(embedding[0]) != 1024:
            return TestResult(
                test_name="Embedding Generation",
                passed=False,
                message=f"Wrong embedding dimension: {len(embedding[0])} (expected 1024)",
                details={"dimension": len(embedding[0])}
            )
        
        return TestResult(
            test_name="Embedding Generation",
            passed=True,
            message="Embeddings generated successfully",
            details={"dimension": len(embedding[0]), "model": EMBEDDING_MODEL}
        )
        
    except Exception as e:
        return TestResult(
            test_name="Embedding Generation",
            passed=False,
            message=f"Embedding generation failed: {str(e)}",
            details={"error": str(e)}
        )

def test_chunk_storage() -> TestResult:
    """
    Test that chunks are stored correctly in the database.
    
    Returns:
        TestResult object
    """
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Count total chunks
                cur.execute("SELECT COUNT(*) FROM document_chunks;")
                total_chunks = cur.fetchone()[0]
                
                if total_chunks == 0:
                    return TestResult(
                        test_name="Chunk Storage",
                        passed=False,
                        message="No chunks found in database",
                        details={"total_chunks": 0}
                    )
                
                # Count chunks with embeddings
                cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
                chunks_with_embeddings = cur.fetchone()[0]
                
                # Check embedding dimensions
                cur.execute("SELECT vector_dims(embedding) FROM document_chunks WHERE embedding IS NOT NULL LIMIT 1;")
                result = cur.fetchone()
                embedding_dims = result[0] if result else None
                
                # Check for required metadata
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN document_title IS NOT NULL THEN 1 END) as with_titles,
                        COUNT(CASE WHEN page_number IS NOT NULL THEN 1 END) as with_pages,
                        COUNT(CASE WHEN word_count > 0 THEN 1 END) as with_word_counts
                    FROM document_chunks;
                """)
                metadata_stats = cur.fetchone()
                
                return TestResult(
                    test_name="Chunk Storage",
                    passed=True,
                    message=f"Found {total_chunks} chunks with {chunks_with_embeddings} embeddings",
                    details={
                        "total_chunks": total_chunks,
                        "chunks_with_embeddings": chunks_with_embeddings,
                        "embedding_dimensions": embedding_dims,
                        "metadata_completeness": {
                            "titles": metadata_stats[1],
                            "pages": metadata_stats[2],
                            "word_counts": metadata_stats[3]
                        }
                    }
                )
                
    except Exception as e:
        return TestResult(
            test_name="Chunk Storage",
            passed=False,
            message=f"Chunk storage test failed: {str(e)}",
            details={"error": str(e)}
        )

def test_vector_similarity_search() -> TestResult:
    """
    Test vector similarity search functionality.
    
    Returns:
        TestResult object
    """
    try:
        # Generate test query embedding
        test_query = "university VPN access"
        payload = {
            "model": EMBEDDING_MODEL,
            "input": test_query
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        query_embedding = result.get("embeddings", [])
        
        if not query_embedding:
            return TestResult(
                test_name="Vector Similarity Search",
                passed=False,
                message="Failed to generate query embedding",
                details={"error": "No embeddings returned"}
            )
        
        # Test similarity search
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Format embedding as PostgreSQL vector string
                embedding_str = '[' + ','.join(map(str, query_embedding[0])) + ']'
                
                cur.execute("""
                    SELECT 
                        document_title,
                        text,
                        embedding <=> %s::vector as distance
                    FROM document_chunks
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT 3
                """, (embedding_str, embedding_str))
                
                results = cur.fetchall()
                
                if not results:
                    return TestResult(
                        test_name="Vector Similarity Search",
                        passed=False,
                        message="No search results returned",
                        details={"query": test_query}
                    )
                
                # Check result quality
                similarities = [1 - row[2] for row in results]
                avg_similarity = sum(similarities) / len(similarities)
                
                return TestResult(
                    test_name="Vector Similarity Search",
                    passed=True,
                    message=f"Found {len(results)} results with avg similarity {avg_similarity:.3f}",
                    details={
                        "query": test_query,
                        "results_count": len(results),
                        "avg_similarity": avg_similarity,
                        "similarities": similarities
                    }
                )
                
    except Exception as e:
        return TestResult(
            test_name="Vector Similarity Search",
            passed=False,
            message=f"Vector similarity search failed: {str(e)}",
            details={"error": str(e)}
        )

def test_metadata_preservation() -> TestResult:
    """
    Test that document metadata is preserved correctly.
    
    Returns:
        TestResult object
    """
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check metadata completeness
                cur.execute("""
                    SELECT 
                        document_title,
                        COUNT(*) as chunk_count,
                        COUNT(CASE WHEN page_number IS NOT NULL THEN 1 END) as with_pages,
                        COUNT(CASE WHEN section_title IS NOT NULL THEN 1 END) as with_sections,
                        COUNT(CASE WHEN word_count > 0 THEN 1 END) as with_word_counts,
                        AVG(word_count) as avg_word_count
                    FROM document_chunks
                    GROUP BY document_title
                    ORDER BY document_title;
                """)
                
                results = cur.fetchall()
                
                if not results:
                    return TestResult(
                        test_name="Metadata Preservation",
                        passed=False,
                        message="No chunks found for metadata analysis",
                        details={}
                    )
                
                # Analyze metadata quality
                total_chunks = sum(row[1] for row in results)
                chunks_with_pages = sum(row[2] for row in results)
                chunks_with_sections = sum(row[3] for row in results)
                chunks_with_word_counts = sum(row[4] for row in results)
                
                page_coverage = (chunks_with_pages / total_chunks) * 100
                section_coverage = (chunks_with_sections / total_chunks) * 100
                word_count_coverage = (chunks_with_word_counts / total_chunks) * 100
                
                # Calculate overall metadata quality score
                quality_score = (page_coverage + section_coverage + word_count_coverage) / 3
                
                return TestResult(
                    test_name="Metadata Preservation",
                    passed=quality_score >= 80,  # 80% threshold
                    message=f"Metadata quality score: {quality_score:.1f}%",
                    details={
                        "total_chunks": total_chunks,
                        "page_coverage": page_coverage,
                        "section_coverage": section_coverage,
                        "word_count_coverage": word_count_coverage,
                        "quality_score": quality_score,
                        "documents": results
                    }
                )
                
    except Exception as e:
        return TestResult(
            test_name="Metadata Preservation",
            passed=False,
            message=f"Metadata preservation test failed: {str(e)}",
            details={"error": str(e)}
        )

def run_comprehensive_tests() -> List[TestResult]:
    """
    Run all tests and return results.
    
    Returns:
        List of TestResult objects
    """
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_table_structure,
        test_embedding_generation,
        test_chunk_storage,
        test_vector_similarity_search,
        test_metadata_preservation
    ]
    
    results = []
    
    for test_func in tests:
        print(f"\n🔍 Running: {test_func.__name__}")
        result = test_func()
        results.append(result)
        
        if result.passed:
            print(f"   ✅ {result.message}")
        else:
            print(f"   ❌ {result.message}")
    
    return results

def generate_test_report(results: List[TestResult]) -> None:
    """
    Generate a comprehensive test report.
    
    Args:
        results: List of TestResult objects
    """
    print(f"\n📋 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    passed_tests = sum(1 for r in results if r.passed)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    print(f"\nTest Results:")
    for result in results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"   {status} {result.test_name}: {result.message}")
        
        if result.details and not result.passed:
            print(f"      Details: {result.details}")
    
    print(f"\nRecommendations:")
    if success_rate < 100:
        print("   - Fix failing tests before proceeding to production")
        print("   - Check database connection and table structure")
        print("   - Verify Ollama service is running and accessible")
        print("   - Ensure embeddings are generated with correct dimensions")
    else:
        print("   - All tests passed! Pipeline is ready for production")
        print("   - Consider adding performance benchmarks")
        print("   - Set up monitoring and alerting for production use")

def performance_benchmark() -> Dict[str, Any]:
    """
    Run performance benchmarks on the pipeline.
    
    Returns:
        Dictionary with performance metrics
    """
    print(f"\n⚡ PERFORMANCE BENCHMARK")
    print("=" * 40)
    
    try:
        # Test embedding generation speed
        start_time = time.time()
        test_text = "This is a performance test for embedding generation speed."
        
        payload = {"model": EMBEDDING_MODEL, "input": test_text}
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        embedding_time = time.time() - start_time
        
        # Test database query speed
        start_time = time.time()
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM document_chunks;")
                count = cur.fetchone()[0]
        query_time = time.time() - start_time
        
        # Test similarity search speed
        start_time = time.time()
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Format embedding as PostgreSQL vector string
                embedding_str = '[' + ','.join(map(str, response.json()["embeddings"][0])) + ']'
                
                cur.execute("""
                    SELECT document_title, embedding <=> %s::vector as distance
                    FROM document_chunks
                    WHERE embedding IS NOT NULL
                    ORDER BY distance
                    LIMIT 5
                """, (embedding_str,))
                results = cur.fetchall()
        search_time = time.time() - start_time
        
        return {
            "embedding_generation_time": embedding_time,
            "database_query_time": query_time,
            "similarity_search_time": search_time,
            "total_chunks": count,
            "search_results": len(results)
        }
        
    except Exception as e:
        return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Verification & Testing")
    print("=" * 50)
    
    # Run comprehensive tests
    test_results = run_comprehensive_tests()
    
    # Generate test report
    generate_test_report(test_results)
    
    # Run performance benchmark
    performance_metrics = performance_benchmark()
    if "error" not in performance_metrics:
        print(f"\n⚡ Performance Metrics:")
        print(f"   Embedding generation: {performance_metrics['embedding_generation_time']:.3f}s")
        print(f"   Database query: {performance_metrics['database_query_time']:.3f}s")
        print(f"   Similarity search: {performance_metrics['similarity_search_time']:.3f}s")
        print(f"   Total chunks: {performance_metrics['total_chunks']}")
    
    print(f"\n🎉 Verification and testing complete!")
    print(f"Pipeline is ready for RAG implementation in Section 6!")
