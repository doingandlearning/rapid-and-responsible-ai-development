#!/usr/bin/env python3
"""
Section 7 Complete Solution: Advanced Vector Queries
Edinburgh University IT Support System - Production-Ready Hybrid Search

This solution demonstrates advanced PostgreSQL + pgvector query patterns
combining semantic similarity with relational filtering and JSONB metadata.
"""

import psycopg
import requests
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structured search result with all metadata."""
    document_title: str
    section_title: Optional[str]
    text: str
    page_number: int
    metadata: Dict[str, Any]
    similarity: float
    combined_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

@dataclass  
class QueryConfig:
    """Configuration parameters for hybrid queries."""
    similarity_threshold: float = 0.4
    max_results: int = 10
    similarity_weight: float = 0.6
    priority_weight: float = 0.2
    popularity_weight: float = 0.1
    department_weight: float = 0.1
    timeout_seconds: int = 30

@dataclass
class QueryStats:
    """Query performance statistics."""
    query: str
    execution_time: float
    results_count: int
    embedding_time: float
    db_time: float
    filters_applied: Dict[str, Any]

class EdinburghHybridSearch:
    """
    Production-ready hybrid search system for Edinburgh University.
    
    Combines vector similarity with advanced filtering on:
    - JSONB metadata (department, campus, tags, priority)
    - Relational data (document titles, dates, page numbers)  
    - Custom scoring with configurable weights
    """
    
    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """Initialize with database and embedding service configuration."""
        
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5050,
            'dbname': 'pgvector',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        self.ollama_url = 'http://localhost:11434/api/embed'
        self.stats = []  # Query statistics for monitoring
        
        logger.info("Edinburgh Hybrid Search system initialized")
    
    @contextmanager
    def get_db_connection(self):
        """Database connection context manager with error handling."""
        conn = None
        try:
            conn = psycopg.connect(**self.db_config)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_embedding(self, text: str, max_retries: int = 3) -> List[float]:
        """
        Generate embedding using Ollama with retry logic.
        
        Args:
            text: Input text to embed
            max_retries: Maximum retry attempts
            
        Returns:
            List of embedding values
        """
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                response = requests.post(
                    self.ollama_url,
                    json={
                        'model': 'bge-m3',
                        'input': text
                    },
                    timeout=30
                )
                response.raise_for_status()
                
                embedding_time = time.time() - start_time
                logger.debug(f"Embedding generated in {embedding_time:.3f}s")
                
                return response.json()['embeddings'][0]
                
            except Exception as e:
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All embedding attempts failed for: {text[:50]}...")
                    raise
                time.sleep(0.5)  # Brief pause before retry
        
        return []
    
    def build_query_conditions(
        self, 
        filters: Dict[str, Any], 
        params: List[Any]
    ) -> Tuple[List[str], List[Any]]:
        """
        Build dynamic WHERE conditions and parameters from filters.
        
        Args:
            filters: Dictionary of filter criteria
            params: Existing parameter list to extend
            
        Returns:
            Tuple of (conditions list, updated params)
        """
        conditions = []
        
        # Base vector similarity threshold
        conditions.append("embedding <=> %s::vector < %s")
        params.extend([filters.get('_query_embedding'), filters.get('similarity_threshold', 0.4)])
        
        # Department filter
        if filters.get('department'):
            conditions.append("metadata->>'department' = %s")
            params.append(filters['department'])
        
        # Campus filter
        if filters.get('campus'):
            conditions.append("metadata->>'campus' = %s")
            params.append(filters['campus'])
        
        # Document type filter
        if filters.get('doc_type'):
            conditions.append("metadata->>'doc_type' = %s")
            params.append(filters['doc_type'])
        
        # Priority filter (minimum level)
        if filters.get('min_priority'):
            conditions.append("(metadata->>'priority')::int >= %s")
            params.append(filters['min_priority'])
        
        # Status filter (active/inactive)
        if filters.get('status'):
            conditions.append("metadata->>'status' = %s")
            params.append(filters['status'])
        
        # Tag containment (any of the tags)
        if filters.get('tags_any'):
            conditions.append("metadata->'tags' ?| %s")
            params.append(filters['tags_any'])
        
        # Tag containment (all of the tags)
        if filters.get('tags_all'):
            conditions.append("metadata->'tags' ?& %s")
            params.append(filters['tags_all'])
        
        # Date range filters
        if filters.get('since_date'):
            conditions.append("(metadata->>'last_reviewed')::timestamp >= %s")
            params.append(filters['since_date'])
        
        if filters.get('until_date'):
            conditions.append("(metadata->>'last_reviewed')::timestamp <= %s")
            params.append(filters['until_date'])
        
        # View count filter (minimum popularity)
        if filters.get('min_views'):
            conditions.append("(metadata->>'view_count')::int >= %s")
            params.append(filters['min_views'])
        
        # Clearance level filter (maximum access level)
        if filters.get('max_clearance'):
            conditions.append("(metadata->>'clearance_level')::int <= %s")
            params.append(filters['max_clearance'])
        
        # Document title contains
        if filters.get('title_contains'):
            conditions.append("document_title ILIKE %s")
            params.append(f"%{filters['title_contains']}%")
        
        return conditions, params
    
    def build_scoring_expression(
        self, 
        config: QueryConfig, 
        filters: Dict[str, Any], 
        params: List[Any]
    ) -> Tuple[str, List[Any]]:
        """
        Build dynamic scoring expression with configurable weights.
        
        Args:
            config: Query configuration with weights
            filters: Query filters
            params: Parameter list to extend
            
        Returns:
            Tuple of (scoring SQL expression, updated params)
        """
        score_components = []
        
        # Semantic similarity component (always included)
        score_components.append(f"(1 - (embedding <=> %s::vector)) * {config.similarity_weight}")
        params.append(filters.get('_query_embedding'))
        
        # Priority component
        score_components.append(f"LEAST((metadata->>'priority')::float / 5.0, 1.0) * {config.priority_weight}")
        
        # Popularity component (view count)
        score_components.append(f"LEAST((metadata->>'view_count')::float / 5000.0, 1.0) * {config.popularity_weight}")
        
        # Department match bonus
        if filters.get('user_department'):
            score_components.append(f"""
                CASE WHEN metadata->>'department' = %s 
                THEN {config.department_weight} 
                ELSE 0.0 END
            """)
            params.append(filters['user_department'])
        
        # Campus preference bonus  
        if filters.get('preferred_campus'):
            score_components.append(f"""
                CASE WHEN metadata->>'campus' = %s 
                THEN 0.05 
                ELSE 0.0 END
            """)
            params.append(filters['preferred_campus'])
        
        # Recency bonus for recently updated documents
        if filters.get('recency_bonus'):
            score_components.append(f"""
                CASE WHEN (metadata->>'last_reviewed')::timestamp > (NOW() - INTERVAL '90 days')
                THEN 0.05
                ELSE 0.0 END
            """)
        
        return f"({' + '.join(score_components)})", params
    
    def execute_hybrid_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        config: Optional[QueryConfig] = None
    ) -> List[SearchResult]:
        """
        Execute comprehensive hybrid search with all features.
        
        Args:
            query: Search query text
            filters: Optional filtering criteria
            config: Query configuration parameters
            
        Returns:
            List of SearchResult objects ordered by relevance
        """
        start_time = time.time()
        embedding_time = 0
        db_time = 0
        
        # Set defaults
        config = config or QueryConfig()
        filters = filters or {}
        filters['similarity_threshold'] = config.similarity_threshold
        
        logger.info(f"Executing hybrid search: '{query[:50]}...'")
        logger.info(f"Applied filters: {list(filters.keys())}")
        
        try:
            # Generate query embedding
            embed_start = time.time()
            query_embedding = self.get_embedding(query)
            embedding_time = time.time() - embed_start
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            filters['_query_embedding'] = query_embedding
            
            # Build dynamic query
            with self.get_db_connection() as conn:
                cur = conn.cursor()
                
                db_start = time.time()
                
                # Build WHERE conditions
                params = []
                where_conditions, params = self.build_query_conditions(filters, params)
                
                # Build scoring expression
                scoring_expr, params = self.build_scoring_expression(config, filters, params)
                
                # Final parameters for LIMIT
                params.append(config.max_results)
                
                # Execute the query
                query_sql = f"""
                    SELECT 
                        document_title,
                        section_title,
                        text,
                        page_number,
                        metadata,
                        1 - (embedding <=> %s::vector) as similarity,
                        {scoring_expr} as combined_score
                    FROM document_chunks 
                    WHERE {' AND '.join(where_conditions)}
                    ORDER BY combined_score DESC
                    LIMIT %s
                """
                
                # Add query embedding for similarity calculation
                params.insert(-1, query_embedding)  # Insert before LIMIT parameter
                
                cur.execute(query_sql, params)
                raw_results = cur.fetchall()
                
                db_time = time.time() - db_start
                
                # Convert to SearchResult objects
                results = []
                for row in raw_results:
                    (doc_title, section, text, page_num, metadata, 
                     similarity, combined_score) = row
                    
                    results.append(SearchResult(
                        document_title=doc_title,
                        section_title=section,
                        text=text,
                        page_number=page_num or 0,
                        metadata=json.loads(metadata) if metadata else {},
                        similarity=similarity,
                        combined_score=combined_score
                    ))
                
                cur.close()
        
        except Exception as e:
            logger.error(f"Hybrid search execution failed: {e}")
            return []
        
        # Record statistics
        execution_time = time.time() - start_time
        self.stats.append(QueryStats(
            query=query,
            execution_time=execution_time,
            results_count=len(results),
            embedding_time=embedding_time,
            db_time=db_time,
            filters_applied=filters
        ))
        
        logger.info(f"Search completed: {len(results)} results in {execution_time:.3f}s")
        return results
    
    def search_by_department(
        self,
        query: str,
        department: str,
        min_priority: Optional[int] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Convenience method for department-specific searches."""
        
        filters = {
            'department': department,
            'status': 'active'
        }
        
        if min_priority:
            filters['min_priority'] = min_priority
        
        config = QueryConfig(max_results=limit)
        
        return self.execute_hybrid_search(query, filters, config)
    
    def search_recent_documents(
        self,
        query: str,
        days_back: int = 90,
        include_department: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search for recently updated documents."""
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        filters = {
            'since_date': cutoff_date,
            'recency_bonus': True
        }
        
        if include_department:
            filters['department'] = include_department
        
        # Emphasize recency in scoring
        config = QueryConfig(
            max_results=limit,
            similarity_weight=0.5,
            priority_weight=0.3,
            popularity_weight=0.2
        )
        
        return self.execute_hybrid_search(query, filters, config)
    
    def search_by_campus(
        self,
        query: str,
        campus: str,
        user_department: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Campus-specific search with department bonus."""
        
        filters = {
            'campus': campus,
            'preferred_campus': campus
        }
        
        if user_department:
            filters['user_department'] = user_department
        
        config = QueryConfig(max_results=limit)
        
        return self.execute_hybrid_search(query, filters, config)
    
    def advanced_filtered_search(
        self,
        query: str,
        doc_types: List[str],
        required_tags: List[str],
        min_priority: int = 1,
        max_clearance: int = 4,
        limit: int = 15
    ) -> List[SearchResult]:
        """Complex multi-filter search."""
        
        filters = {
            'doc_type': doc_types[0] if len(doc_types) == 1 else None,  # Single type only for now
            'tags_all': required_tags,
            'min_priority': min_priority,
            'max_clearance': max_clearance,
            'status': 'active'
        }
        
        config = QueryConfig(max_results=limit)
        
        return self.execute_hybrid_search(query, filters, config)
    
    def get_query_performance_stats(self) -> Dict[str, Any]:
        """Get aggregated performance statistics."""
        
        if not self.stats:
            return {'message': 'No queries executed yet'}
        
        total_queries = len(self.stats)
        avg_time = sum(s.execution_time for s in self.stats) / total_queries
        avg_results = sum(s.results_count for s in self.stats) / total_queries
        avg_embedding_time = sum(s.embedding_time for s in self.stats) / total_queries
        avg_db_time = sum(s.db_time for s in self.stats) / total_queries
        
        return {
            'total_queries': total_queries,
            'avg_execution_time': round(avg_time, 3),
            'avg_results_count': round(avg_results, 1),
            'avg_embedding_time': round(avg_embedding_time, 3),
            'avg_db_time': round(avg_db_time, 3),
            'slowest_query_time': max(s.execution_time for s in self.stats),
            'fastest_query_time': min(s.execution_time for s in self.stats)
        }
    
    def explain_query_performance(self, query: str, filters: Optional[Dict[str, Any]] = None):
        """Analyze query execution plan for optimization."""
        
        try:
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return
            
            with self.get_db_connection() as conn:
                cur = conn.cursor()
                
                # Simple test query for EXPLAIN ANALYZE
                test_sql = """
                    EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
                    SELECT 
                        document_title,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM document_chunks 
                    WHERE embedding <=> %s::vector < 0.4
                    ORDER BY embedding <=> %s::vector
                    LIMIT 10
                """
                
                cur.execute(test_sql, [query_embedding, query_embedding, query_embedding])
                explain_result = cur.fetchone()[0]
                
                print(f"\n📊 QUERY PERFORMANCE ANALYSIS")
                print(f"Query: '{query}'")
                print("-" * 60)
                
                # Extract key metrics from JSON plan
                plan = explain_result[0]['Plan']
                total_cost = plan['Total Cost']
                actual_time = plan['Actual Total Time']
                rows_returned = plan['Actual Rows']
                
                print(f"Total Cost: {total_cost:.2f}")
                print(f"Execution Time: {actual_time:.2f} ms")
                print(f"Rows Returned: {rows_returned}")
                
                # Check for index usage
                if 'Index Scan' in plan['Node Type']:
                    print("✅ Using index scan")
                else:
                    print("⚠️ Not using index scan - consider adding indexes")
                
                cur.close()
        
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")

def setup_enhanced_database():
    """Setup database with enhanced metadata and indexes."""
    
    print("🔧 SETTING UP ENHANCED DATABASE")
    print("=" * 50)
    
    conn = psycopg.connect(
        host='localhost',
        port=5050,
        dbname='pgvector',
        user='postgres',
        password='postgres'
    )
    cur = conn.cursor()
    
    # Add enhanced metadata to existing chunks
    departments = ['IT Services', 'Student Services', 'Library', 'Estates', 'HR', 'Finance']
    campuses = ['Central Campus', "King's Buildings", 'Easter Bush', 'Western General']
    doc_types = ['policy', 'guide', 'procedure', 'faq', 'manual', 'form']
    
    print("Adding enhanced metadata...")
    
    # Get all chunks
    cur.execute("SELECT id, document_title FROM document_chunks ORDER BY id")
    chunks = cur.fetchall()
    
    import random
    
    for chunk_id, doc_title in chunks:
        metadata = {
            'department': random.choice(departments),
            'campus': random.choice(campuses),
            'doc_type': random.choice(doc_types),
            'priority': random.randint(1, 5),
            'status': 'active',
            'version': f"{random.randint(1, 5)}.{random.randint(0, 9)}",
            'created_by': f"user{random.randint(100, 999)}@ed.ac.uk",
            'last_reviewed': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            'view_count': random.randint(10, 5000),
            'tags': random.sample(['urgent', 'network', 'password', 'wifi', 'email', 'account', 'troubleshooting'], 
                                random.randint(1, 3)),
            'clearance_level': random.randint(1, 4),
            'academic_year': random.choice(['2023-24', '2024-25']),
            'category': 'general'
        }
        
        # Document-specific metadata
        title_lower = doc_title.lower()
        if 'password' in title_lower:
            metadata['category'] = 'authentication'
            metadata['tags'].append('security')
        elif 'wifi' in title_lower or 'network' in title_lower:
            metadata['category'] = 'networking'
            metadata['tags'].append('connectivity')
        elif 'email' in title_lower:
            metadata['category'] = 'communication'
            metadata['tags'].append('email')
        
        cur.execute("""
            UPDATE document_chunks 
            SET metadata = %s
            WHERE id = %s
        """, (json.dumps(metadata), chunk_id))
    
    conn.commit()
    
    # Create indexes
    print("Creating advanced indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS document_chunks_metadata_gin ON document_chunks USING gin (metadata)",
        "CREATE INDEX IF NOT EXISTS document_chunks_title_idx ON document_chunks (document_title)", 
        "CREATE INDEX IF NOT EXISTS document_chunks_page_idx ON document_chunks (page_number)"
    ]
    
    for idx_sql in indexes:
        try:
            cur.execute(idx_sql)
            print(f"  ✅ Created index")
        except Exception as e:
            print(f"  ⚠️ Index creation: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Database enhancement complete!")

def run_comprehensive_tests():
    """Run comprehensive test suite for all advanced query features."""
    
    print("🚀 COMPREHENSIVE ADVANCED QUERY TESTING")
    print("=" * 70)
    
    # Initialize search engine
    search = EdinburghHybridSearch()
    
    # Test 1: Basic hybrid search
    print("\n1️⃣ BASIC HYBRID SEARCH")
    print("-" * 40)
    
    results = search.execute_hybrid_search("password reset instructions")
    
    if results:
        print(f"✅ Found {len(results)} results")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.document_title}")
            print(f"     Similarity: {result.similarity:.3f} | Score: {result.combined_score:.3f}")
            print(f"     Dept: {result.metadata.get('department', 'N/A')} | Type: {result.metadata.get('doc_type', 'N/A')}")
    else:
        print("❌ No results found")
    
    # Test 2: Department-specific search
    print("\n\n2️⃣ DEPARTMENT-SPECIFIC SEARCH")
    print("-" * 40)
    
    it_results = search.search_by_department("network troubleshooting", "IT Services", min_priority=3)
    
    if it_results:
        print(f"✅ Found {len(it_results)} IT Services results")
        for i, result in enumerate(it_results[:2], 1):
            print(f"  {i}. {result.document_title}")
            print(f"     Priority: {result.metadata.get('priority')} | Score: {result.combined_score:.3f}")
    
    # Test 3: Recent documents search
    print("\n\n3️⃣ RECENT DOCUMENTS SEARCH")
    print("-" * 40)
    
    recent_results = search.search_recent_documents("email setup guide", days_back=120)
    
    if recent_results:
        print(f"✅ Found {len(recent_results)} recent results")
        for i, result in enumerate(recent_results[:2], 1):
            last_review = result.metadata.get('last_reviewed', 'Unknown')
            print(f"  {i}. {result.document_title}")
            print(f"     Last reviewed: {last_review[:10]} | Score: {result.combined_score:.3f}")
    
    # Test 4: Campus-specific search
    print("\n\n4️⃣ CAMPUS-SPECIFIC SEARCH")
    print("-" * 40)
    
    campus_results = search.search_by_campus(
        "IT support contact information", 
        "King's Buildings",
        user_department="IT Services"
    )
    
    if campus_results:
        print(f"✅ Found {len(campus_results)} King's Buildings results")
        for i, result in enumerate(campus_results[:2], 1):
            campus = result.metadata.get('campus', 'Unknown')
            print(f"  {i}. {result.document_title}")
            print(f"     Campus: {campus} | Score: {result.combined_score:.3f}")
    
    # Test 5: Advanced filtered search
    print("\n\n5️⃣ ADVANCED FILTERED SEARCH")
    print("-" * 40)
    
    filtered_results = search.advanced_filtered_search(
        "network connectivity issues",
        doc_types=['guide'],
        required_tags=['network'],
        min_priority=2
    )
    
    if filtered_results:
        print(f"✅ Found {len(filtered_results)} filtered results")
        for i, result in enumerate(filtered_results[:2], 1):
            tags = result.metadata.get('tags', [])
            print(f"  {i}. {result.document_title}")
            print(f"     Tags: {tags} | Priority: {result.metadata.get('priority')}")
    
    # Test 6: Complex multi-criteria search
    print("\n\n6️⃣ COMPLEX MULTI-CRITERIA SEARCH")
    print("-" * 40)
    
    complex_filters = {
        'department': 'IT Services',
        'doc_type': 'guide',
        'min_priority': 3,
        'tags_any': ['troubleshooting', 'network', 'wifi'],
        'user_department': 'IT Services',
        'preferred_campus': "King's Buildings",
        'recency_bonus': True
    }
    
    config = QueryConfig(
        similarity_weight=0.5,
        priority_weight=0.25,
        popularity_weight=0.15,
        department_weight=0.1,
        max_results=5
    )
    
    complex_results = search.execute_hybrid_search(
        "wifi connection problems in student accommodation", 
        filters=complex_filters,
        config=config
    )
    
    if complex_results:
        print(f"✅ Found {len(complex_results)} complex search results")
        for i, result in enumerate(complex_results, 1):
            print(f"  {i}. {result.document_title}")
            print(f"     Score: {result.combined_score:.3f} | Similarity: {result.similarity:.3f}")
            print(f"     Dept: {result.metadata.get('department')} | Campus: {result.metadata.get('campus')}")
            print(f"     Tags: {result.metadata.get('tags', [])}")
    
    # Performance statistics
    print("\n\n7️⃣ PERFORMANCE STATISTICS")
    print("-" * 40)
    
    stats = search.get_query_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Performance analysis
    print("\n\n8️⃣ QUERY PERFORMANCE ANALYSIS")
    print("-" * 40)
    
    search.explain_query_performance("password reset help")

def demonstrate_edinburgh_scenarios():
    """Demonstrate realistic Edinburgh University usage scenarios."""
    
    print("\n🏴󠁧󠁢󠁳󠁣󠁴󠁿 EDINBURGH UNIVERSITY REAL-WORLD SCENARIOS")
    print("=" * 70)
    
    search = EdinburghHybridSearch()
    
    # Scenario 1: New student needs help
    print("\n📱 SCENARIO: New Student Needs WiFi Help")
    print("Context: First-year student in accommodation, urgent connectivity issue")
    
    student_filters = {
        'tags_any': ['wifi', 'network', 'student'],
        'doc_type': 'guide',
        'status': 'active',
        'min_priority': 2
    }
    
    student_config = QueryConfig(
        similarity_weight=0.7,  # Emphasize semantic match
        priority_weight=0.3,    # Less emphasis on priority
        max_results=5
    )
    
    student_results = search.execute_hybrid_search(
        "cannot connect to university WiFi in student residence",
        filters=student_filters,
        config=student_config
    )
    
    print(f"✅ Found {len(student_results)} student-focused results:")
    for i, result in enumerate(student_results[:3], 1):
        campus = result.metadata.get('campus', 'Any Campus')
        tags = result.metadata.get('tags', [])
        print(f"  {i}. {result.document_title}")
        print(f"     Campus: {campus} | Tags: {tags}")
        print(f"     Relevance: {result.similarity:.3f} | Priority: {result.metadata.get('priority')}")
    
    # Scenario 2: IT staff emergency response
    print("\n\n🚨 SCENARIO: IT Staff Emergency Response")
    print("Context: Network outage at King's Buildings, need immediate procedures")
    
    emergency_filters = {
        'department': 'IT Services',
        'campus': "King's Buildings",
        'min_priority': 4,
        'tags_any': ['urgent', 'network', 'outage'],
        'user_department': 'IT Services',
        'preferred_campus': "King's Buildings"
    }
    
    emergency_config = QueryConfig(
        similarity_weight=0.4,  # Less emphasis on semantic similarity
        priority_weight=0.4,    # High emphasis on priority
        department_weight=0.2,  # Strong department match bonus
        max_results=3
    )
    
    emergency_results = search.execute_hybrid_search(
        "network outage emergency response procedures",
        filters=emergency_filters,
        config=emergency_config
    )
    
    print(f"✅ Found {len(emergency_results)} emergency response documents:")
    for i, result in enumerate(emergency_results, 1):
        priority = result.metadata.get('priority', 'Unknown')
        dept = result.metadata.get('department', 'Unknown')
        print(f"  {i}. {result.document_title}")
        print(f"     Priority: {priority} | Department: {dept}")
        print(f"     Combined Score: {result.combined_score:.3f}")
    
    # Scenario 3: Policy compliance check
    print("\n\n📋 SCENARIO: Policy Compliance Check")  
    print("Context: HR staff needs current data protection policies for audit")
    
    policy_filters = {
        'doc_type': 'policy',
        'tags_any': ['data', 'protection', 'gdpr'],
        'status': 'active',
        'since_date': datetime.now() - timedelta(days=365),  # Within last year
        'user_department': 'HR'
    }
    
    policy_config = QueryConfig(
        similarity_weight=0.6,
        priority_weight=0.2,
        popularity_weight=0.1,
        department_weight=0.1,
        max_results=5
    )
    
    policy_results = search.execute_hybrid_search(
        "GDPR data protection compliance requirements staff",
        filters=policy_filters,
        config=policy_config
    )
    
    print(f"✅ Found {len(policy_results)} policy compliance documents:")
    for i, result in enumerate(policy_results[:3], 1):
        last_review = result.metadata.get('last_reviewed', 'Unknown')
        version = result.metadata.get('version', 'Unknown')
        print(f"  {i}. {result.document_title}")
        print(f"     Version: {version} | Last Reviewed: {last_review[:10]}")
        print(f"     Relevance: {result.similarity:.3f}")

if __name__ == "__main__":
    """
    Main execution flow for Section 7 complete solution.
    
    This demonstrates the full advanced vector query capabilities
    for Edinburgh University's hybrid search system.
    """
    
    print("🚀 SECTION 7: ADVANCED VECTOR QUERIES - COMPLETE SOLUTION")
    print("=" * 80)
    print("Edinburgh University IT Support System")
    print("Production-Ready Hybrid Search Implementation")
    print("=" * 80)
    
    try:
        # Step 1: Setup enhanced database
        print("\nSTEP 1: DATABASE ENHANCEMENT")
        setup_enhanced_database()
        
        # Step 2: Comprehensive testing  
        print("\n\nSTEP 2: COMPREHENSIVE TESTING")
        run_comprehensive_tests()
        
        # Step 3: Real-world scenarios
        print("\n\nSTEP 3: REAL-WORLD SCENARIOS") 
        demonstrate_edinburgh_scenarios()
        
        print("\n" + "=" * 80)
        print("✅ SECTION 7 COMPLETE!")
        print("Advanced hybrid search system successfully implemented!")
        print("=" * 80)
        print("\n🎯 KEY ACHIEVEMENTS:")
        print("  • Multi-criteria hybrid queries with configurable weights")
        print("  • Advanced JSONB metadata filtering and indexing")
        print("  • Production-ready error handling and performance monitoring")
        print("  • Edinburgh-specific use cases and scenarios")
        print("  • Comprehensive query performance analysis")
        print("\n💡 SYSTEM CAPABILITIES:")
        print("  • Semantic similarity + relational filtering")
        print("  • Campus, department, and role-based search")
        print("  • Time-aware and priority-weighted results")
        print("  • Real-time performance statistics and optimization")
        print("\n🚀 Ready for Section 8: Production Deployment!")
        
    except Exception as e:
        logger.error(f"Solution execution failed: {e}")
        print(f"\n❌ Error: {e}")
        print("Please check your database connection and try again.")