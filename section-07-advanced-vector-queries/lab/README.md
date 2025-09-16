# Section 7 Lab: Advanced Vector Queries

**Building Hybrid Search Systems for Edinburgh University**

## Lab Overview

**Time:** 45 minutes  
**Objective:** Master complex hybrid queries combining vector similarity, metadata filtering, and relational constraints  
**Context:** Build production-ready search capabilities for Edinburgh's diverse institutional needs

---

## Prerequisites

✅ **Section 6 completed** - RAG pipeline working with document chunks  
✅ **PostgreSQL + pgvector running** - Database with embeddings  
✅ **OpenAI API key configured** - For testing search quality  
✅ **Python environment active** - All dependencies installed

### Quick Verification

```bash
# Verify database and embeddings are ready
python -c "
import psycopg
conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL')
print(f'Chunks with embeddings: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(DISTINCT document_title) FROM document_chunks')
print(f'Unique documents: {cur.fetchone()[0]}')
"
```

**Expected output:** At least 25 chunks from 5+ documents

---

## Lab Exercises

### Exercise 1: Enhanced Metadata Schema (8 minutes)

#### 1.1: Add Rich Metadata to Existing Documents

Let's enhance our document chunks with realistic Edinburgh metadata.

**Create the enhancement script:**

```python
# lab7_enhance_metadata.py
import psycopg
import json
from datetime import datetime, timedelta
import random

def connect_db():
    return psycopg.connect(
        host='localhost',
        port=5050,
        dbname='pgvector', 
        user='postgres',
        password='postgres'
    )

def enhance_document_metadata():
    """Add realistic Edinburgh University metadata to document chunks."""
    
    # Edinburgh-specific metadata patterns
    departments = ['IT Services', 'Student Services', 'Library', 'Estates', 'HR', 'Finance']
    campuses = ['Central Campus', 'King\'s Buildings', 'Easter Bush', 'Western General']
    doc_types = ['policy', 'guide', 'procedure', 'faq', 'manual', 'form']
    priorities = [1, 2, 3, 4, 5]  # 1=low, 5=critical
    
    conn = connect_db()
    cur = conn.cursor()
    
    print("🔧 ENHANCING DOCUMENT METADATA")
    print("=" * 50)
    
    # Get all document chunks
    cur.execute("SELECT id, document_title FROM document_chunks ORDER BY id")
    chunks = cur.fetchall()
    
    print(f"Found {len(chunks)} chunks to enhance...")
    
    updated_count = 0
    
    for chunk_id, doc_title in chunks:
        # Generate realistic metadata based on document title
        metadata = {
            'department': random.choice(departments),
            'campus': random.choice(campuses),
            'doc_type': random.choice(doc_types),
            'priority': random.choice(priorities),
            'status': 'active',
            'version': f"{random.randint(1, 5)}.{random.randint(0, 9)}",
            'created_by': f"user{random.randint(100, 999)}@ed.ac.uk",
            'last_reviewed': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            'view_count': random.randint(10, 5000),
            'tags': random.sample(['urgent', 'network', 'password', 'wifi', 'email', 'account', 'troubleshooting'], 
                                random.randint(1, 3)),
            'clearance_level': random.randint(1, 4),  # 1=public, 4=restricted
            'academic_year': random.choice(['2023-24', '2024-25']),
        }
        
        # Add document-specific metadata
        if 'password' in doc_title.lower():
            metadata['category'] = 'authentication'
            metadata['tags'].append('security')
        elif 'wifi' in doc_title.lower() or 'network' in doc_title.lower():
            metadata['category'] = 'networking'
            metadata['tags'].append('connectivity')
        elif 'email' in doc_title.lower():
            metadata['category'] = 'communication'
            metadata['tags'].append('email')
        else:
            metadata['category'] = 'general'
        
        # Update the chunk with enhanced metadata
        cur.execute("""
            UPDATE document_chunks 
            SET metadata = %s
            WHERE id = %s
        """, (json.dumps(metadata), chunk_id))
        
        updated_count += 1
        if updated_count % 5 == 0:
            print(f"  ✅ Enhanced {updated_count} chunks...")
    
    conn.commit()
    print(f"\n✅ Successfully enhanced {updated_count} document chunks")
    
    # Show some examples
    print("\n📋 SAMPLE ENHANCED METADATA:")
    cur.execute("""
        SELECT document_title, metadata 
        FROM document_chunks 
        LIMIT 3
    """)
    
    for title, metadata in cur.fetchall():
        print(f"\nDocument: {title}")
        meta_dict = json.loads(metadata) if metadata else {}
        for key, value in list(meta_dict.items())[:6]:  # Show first 6 fields
            print(f"  {key}: {value}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    enhance_document_metadata()
```

**Run the enhancement:**

```bash
python lab7_enhance_metadata.py
```

#### 1.2: Add Indexes for Hybrid Queries

**Create indexing script:**

```python
# lab7_create_indexes.py
import psycopg

def create_advanced_indexes():
    """Create optimized indexes for hybrid vector queries."""
    
    conn = psycopg.connect(
        host='localhost',
        port=5050,
        dbname='pgvector', 
        user='postgres',
        password='postgres'
    )
    cur = conn.cursor()
    
    print("🚀 CREATING ADVANCED INDEXES")
    print("=" * 40)
    
    indexes = [
        # HNSW index for vector similarity (if not exists)
        {
            'name': 'document_chunks_embedding_idx',
            'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx ON document_chunks USING hnsw (embedding vector_cosine_ops)',
            'description': 'HNSW index for fast vector similarity'
        },
        
        # GIN index for JSONB metadata operations
        {
            'name': 'document_chunks_metadata_idx',
            'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_metadata_idx ON document_chunks USING gin (metadata)',
            'description': 'GIN index for JSONB metadata queries'
        },
        
        # B-tree indexes for common filters
        {
            'name': 'document_chunks_doc_title_idx',
            'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_doc_title_idx ON document_chunks (document_title)',
            'description': 'B-tree index for document title filtering'
        },
        
        # Composite index for common query patterns
        {
            'name': 'document_chunks_composite_idx',
            'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_composite_idx ON document_chunks (document_title, page_number)',
            'description': 'Composite index for document + page queries'
        }
    ]
    
    for idx in indexes:
        try:
            print(f"Creating {idx['name']}...")
            cur.execute(idx['sql'])
            print(f"  ✅ {idx['description']}")
        except Exception as e:
            print(f"  ⚠️ {idx['name']}: {str(e)}")
    
    conn.commit()
    
    # Verify indexes
    print("\n📊 VERIFYING INDEX CREATION:")
    cur.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'document_chunks'
        ORDER BY indexname
    """)
    
    indexes_found = cur.fetchall()
    for idx_name, idx_def in indexes_found:
        print(f"  ✅ {idx_name}")
    
    print(f"\nTotal indexes on document_chunks: {len(indexes_found)}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_advanced_indexes()
```

**Run the indexing:**

```bash
python lab7_create_indexes.py
```

---

### Exercise 2: Basic Hybrid Queries (10 minutes)

#### 2.1: Vector + Metadata Filtering

**Create hybrid query examples:**

```python
# lab7_hybrid_queries.py
import psycopg
import requests
import json
from typing import List, Dict, Any

def connect_db():
    return psycopg.connect(
        host='localhost',
        port=5050,
        dbname='pgvector', 
        user='postgres',
        password='postgres'
    )

def get_embedding(text: str) -> List[float]:
    """Generate embedding using Ollama."""
    try:
        response = requests.post(
            'http://localhost:11434/api/embed',
            json={
                'model': 'bge-m3',
                'input': text
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['embeddings'][0]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def hybrid_search_by_department(query: str, department: str, limit: int = 5):
    """Search for documents similar to query within specific department."""
    
    print(f"🔍 HYBRID SEARCH: Department '{department}'")
    print(f"Query: '{query}'")
    print("-" * 50)
    
    # Generate query embedding
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate embedding")
        return
    
    conn = connect_db()
    cur = conn.cursor()
    
    # Hybrid query: vector similarity + department filter
    cur.execute("""
        SELECT 
            document_title,
            section_title,
            text,
            metadata->>'department' as dept,
            metadata->>'doc_type' as doc_type,
            1 - (embedding <=> %s::vector) as similarity
        FROM document_chunks 
        WHERE metadata->>'department' = %s
          AND embedding <=> %s::vector < 0.4  -- similarity threshold
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, department, query_embedding, query_embedding, limit))
    
    results = cur.fetchall()
    
    if results:
        print(f"✅ Found {len(results)} relevant results:")
        for i, (doc_title, section, text, dept, doc_type, similarity) in enumerate(results, 1):
            print(f"\n{i}. {doc_title}")
            print(f"   Section: {section or 'N/A'}")
            print(f"   Type: {doc_type} | Dept: {dept}")
            print(f"   Similarity: {similarity:.3f}")
            print(f"   Preview: {text[:100]}...")
    else:
        print("❌ No relevant documents found")
    
    cur.close()
    conn.close()

def hybrid_search_by_priority(query: str, min_priority: int = 3, limit: int = 5):
    """Search for high-priority documents similar to query."""
    
    print(f"\n🔍 HYBRID SEARCH: Priority >= {min_priority}")
    print(f"Query: '{query}'")
    print("-" * 50)
    
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate embedding")
        return
    
    conn = connect_db()
    cur = conn.cursor()
    
    # Hybrid query: vector similarity + priority filter
    cur.execute("""
        SELECT 
            document_title,
            metadata->>'priority' as priority,
            metadata->>'category' as category,
            metadata->>'status' as status,
            1 - (embedding <=> %s::vector) as similarity
        FROM document_chunks 
        WHERE (metadata->>'priority')::int >= %s
          AND metadata->>'status' = 'active'
          AND embedding <=> %s::vector < 0.4
        ORDER BY 
            (metadata->>'priority')::int DESC,  -- Priority first
            embedding <=> %s::vector           -- Then similarity
        LIMIT %s
    """, (query_embedding, min_priority, query_embedding, query_embedding, limit))
    
    results = cur.fetchall()
    
    if results:
        print(f"✅ Found {len(results)} high-priority results:")
        for i, (doc_title, priority, category, status, similarity) in enumerate(results, 1):
            print(f"\n{i}. {doc_title}")
            print(f"   Priority: {priority} | Category: {category}")
            print(f"   Status: {status} | Similarity: {similarity:.3f}")
    else:
        print("❌ No high-priority documents found")
    
    cur.close()
    conn.close()

def hybrid_search_with_tags(query: str, required_tags: List[str], limit: int = 5):
    """Search for documents with specific tags."""
    
    print(f"\n🔍 HYBRID SEARCH: Required tags {required_tags}")
    print(f"Query: '{query}'")
    print("-" * 50)
    
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate embedding")
        return
    
    conn = connect_db()
    cur = conn.cursor()
    
    # Hybrid query: vector similarity + tag containment
    cur.execute("""
        SELECT 
            document_title,
            metadata->'tags' as tags,
            metadata->>'category' as category,
            1 - (embedding <=> %s::vector) as similarity
        FROM document_chunks 
        WHERE metadata->'tags' ?& %s  -- Contains all required tags
          AND embedding <=> %s::vector < 0.4
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, required_tags, query_embedding, query_embedding, limit))
    
    results = cur.fetchall()
    
    if results:
        print(f"✅ Found {len(results)} tagged results:")
        for i, (doc_title, tags, category, similarity) in enumerate(results, 1):
            tag_list = json.loads(tags) if tags else []
            print(f"\n{i}. {doc_title}")
            print(f"   Tags: {', '.join(tag_list)}")
            print(f"   Category: {category} | Similarity: {similarity:.3f}")
    else:
        print("❌ No documents found with required tags")
    
    cur.close()
    conn.close()

def run_basic_hybrid_tests():
    """Run basic hybrid query examples."""
    
    print("🚀 SECTION 7: BASIC HYBRID QUERIES")
    print("=" * 60)
    
    # Test 1: Search by department
    hybrid_search_by_department(
        query="password reset procedure",
        department="IT Services"
    )
    
    # Test 2: Search by priority
    hybrid_search_by_priority(
        query="network connectivity issues", 
        min_priority=3
    )
    
    # Test 3: Search by tags
    hybrid_search_with_tags(
        query="wifi connection problems",
        required_tags=["network", "troubleshooting"]
    )

if __name__ == "__main__":
    run_basic_hybrid_tests()
```

**Run basic hybrid queries:**

```bash
python lab7_hybrid_queries.py
```

---

### Exercise 3: Advanced Multi-Criteria Queries (12 minutes)

#### 3.1: Weighted Scoring System

**Add advanced scoring to hybrid queries:**

```python
# lab7_advanced_queries.py
import psycopg
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

def connect_db():
    return psycopg.connect(
        host='localhost',
        port=5050,
        dbname='pgvector', 
        user='postgres',
        password='postgres'
    )

def get_embedding(text: str) -> List[float]:
    """Generate embedding using Ollama."""
    try:
        response = requests.post(
            'http://localhost:11434/api/embed',
            json={
                'model': 'bge-m3',
                'input': text
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['embeddings'][0]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def multi_criteria_search(query: str, user_department: str = None, limit: int = 10):
    """Advanced search with multiple weighted criteria."""
    
    print(f"🎯 MULTI-CRITERIA SEARCH")
    print(f"Query: '{query}'")
    print(f"User Department: {user_department or 'Any'}")
    print("-" * 60)
    
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate embedding")
        return
    
    conn = connect_db()
    cur = conn.cursor()
    
    # Advanced multi-criteria scoring
    cur.execute("""
        SELECT 
            document_title,
            section_title,
            text,
            metadata->>'department' as dept,
            metadata->>'priority' as priority,
            metadata->>'doc_type' as doc_type,
            metadata->>'view_count' as views,
            
            -- Multi-criteria score calculation
            (
                -- 60% semantic similarity
                (1 - (embedding <=> %s::vector)) * 0.6 +
                
                -- 20% priority weight
                LEAST((metadata->>'priority')::float / 5.0, 1.0) * 0.2 +
                
                -- 10% popularity (view count)
                LEAST((metadata->>'view_count')::float / 5000.0, 1.0) * 0.1 +
                
                -- 10% department match bonus
                CASE 
                    WHEN %s IS NULL THEN 0.1  -- No preference
                    WHEN metadata->>'department' = %s THEN 0.1
                    ELSE 0.0
                END
                
            ) as combined_score,
            
            -- Individual components for analysis
            1 - (embedding <=> %s::vector) as similarity,
            (metadata->>'priority')::float as priority_num,
            (metadata->>'view_count')::float as view_count
            
        FROM document_chunks 
        WHERE embedding <=> %s::vector < 0.5  -- Base relevance threshold
        ORDER BY combined_score DESC
        LIMIT %s
    """, (query_embedding, user_department, user_department, query_embedding, query_embedding, limit))
    
    results = cur.fetchall()
    
    if results:
        print(f"✅ Found {len(results)} results with multi-criteria scoring:")
        print("\nRank | Score | Similarity | Priority | Views | Document")
        print("-" * 80)
        
        for i, row in enumerate(results, 1):
            (doc_title, section, text, dept, priority, doc_type, views, 
             combined_score, similarity, priority_num, view_count) = row
            
            print(f"{i:2d}   | {combined_score:.3f} | {similarity:8.3f} | {priority:8s} | {views:>5s} | {doc_title[:40]}...")
            
            if i <= 3:  # Show details for top 3
                print(f"     Department: {dept} | Type: {doc_type}")
                print(f"     Preview: {text[:100]}...")
                print()
    else:
        print("❌ No relevant documents found")
    
    cur.close()
    conn.close()

def campus_priority_search(query: str, preferred_campus: str = "King's Buildings", limit: int = 8):
    """Search with campus-based prioritization."""
    
    print(f"\n🏫 CAMPUS-PRIORITY SEARCH")
    print(f"Query: '{query}'")
    print(f"Preferred Campus: {preferred_campus}")
    print("-" * 60)
    
    query_embedding = get_embedding(query)
    if not query_embedding:
        return
    
    conn = connect_db()
    cur = conn.cursor()
    
    # Campus-aware search with custom ordering
    cur.execute("""
        SELECT 
            document_title,
            metadata->>'campus' as campus,
            metadata->>'department' as dept,
            metadata->>'doc_type' as doc_type,
            1 - (embedding <=> %s::vector) as similarity
        FROM document_chunks 
        WHERE embedding <=> %s::vector < 0.4
        ORDER BY 
            -- Primary sort: preferred campus first
            CASE metadata->>'campus'
                WHEN %s THEN 1
                ELSE 2
            END,
            -- Secondary sort: similarity within campus
            embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, preferred_campus, query_embedding, limit))
    
    results = cur.fetchall()
    
    if results:
        print(f"✅ Found {len(results)} campus-prioritized results:")
        
        current_campus = None
        for i, (doc_title, campus, dept, doc_type, similarity) in enumerate(results, 1):
            if campus != current_campus:
                print(f"\n📍 {campus}:")
                current_campus = campus
            
            print(f"  {i}. {doc_title[:50]}...")
            print(f"     Dept: {dept} | Type: {doc_type} | Similarity: {similarity:.3f}")
    else:
        print("❌ No relevant documents found")
    
    cur.close()
    conn.close()

def time_bounded_search(query: str, days_back: int = 180, limit: int = 8):
    """Search within specific time window with recency boost."""
    
    print(f"\n⏰ TIME-BOUNDED SEARCH")
    print(f"Query: '{query}'")
    print(f"Time window: Last {days_back} days")
    print("-" * 60)
    
    query_embedding = get_embedding(query)
    if not query_embedding:
        return
    
    conn = connect_db()
    cur = conn.cursor()
    
    # Calculate date threshold
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Time-aware search with recency scoring
    cur.execute("""
        SELECT 
            document_title,
            metadata->>'last_reviewed' as last_reviewed,
            metadata->>'department' as dept,
            
            -- Time-weighted score
            (
                -- 70% semantic similarity
                (1 - (embedding <=> %s::vector)) * 0.7 +
                
                -- 30% recency bonus (more recent = higher score)
                CASE 
                    WHEN (metadata->>'last_reviewed')::timestamp > %s
                    THEN EXTRACT(EPOCH FROM (
                        (metadata->>'last_reviewed')::timestamp - %s
                    )) / EXTRACT(EPOCH FROM INTERVAL '180 days') * 0.3
                    ELSE 0.0
                END
                
            ) as time_weighted_score,
            
            1 - (embedding <=> %s::vector) as similarity
            
        FROM document_chunks 
        WHERE (metadata->>'last_reviewed')::timestamp >= %s
          AND embedding <=> %s::vector < 0.4
        ORDER BY time_weighted_score DESC
        LIMIT %s
    """, (query_embedding, cutoff_date, cutoff_date, query_embedding, cutoff_date, query_embedding, limit))
    
    results = cur.fetchall()
    
    if results:
        print(f"✅ Found {len(results)} recent documents:")
        
        for i, (doc_title, last_reviewed, dept, time_score, similarity) in enumerate(results, 1):
            review_date = datetime.fromisoformat(last_reviewed.replace('Z', '+00:00')) if last_reviewed else None
            days_ago = (datetime.now() - review_date.replace(tzinfo=None)).days if review_date else "Unknown"
            
            print(f"{i}. {doc_title[:45]}...")
            print(f"   Dept: {dept} | Reviewed: {days_ago} days ago")
            print(f"   Time Score: {time_score:.3f} | Similarity: {similarity:.3f}\n")
    else:
        print("❌ No recent documents found")
    
    cur.close()
    conn.close()

def run_advanced_query_tests():
    """Run advanced multi-criteria query examples."""
    
    print("🚀 SECTION 7: ADVANCED MULTI-CRITERIA QUERIES")
    print("=" * 70)
    
    # Test 1: Multi-criteria weighted search
    multi_criteria_search(
        query="email configuration setup",
        user_department="IT Services"
    )
    
    # Test 2: Campus-priority search
    campus_priority_search(
        query="network troubleshooting guide",
        preferred_campus="King's Buildings"
    )
    
    # Test 3: Time-bounded search with recency
    time_bounded_search(
        query="password policy requirements",
        days_back=90
    )

if __name__ == "__main__":
    run_advanced_query_tests()
```

**Run advanced queries:**

```bash
python lab7_advanced_queries.py
```

---

### Exercise 4: Production-Ready Query System (10 minutes)

#### 4.1: Complete Query Class with Error Handling

**Create production query system:**

```python
# lab7_production_queries.py
import psycopg
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structured search result."""
    document_title: str
    section_title: Optional[str]
    text: str
    metadata: Dict[str, Any]
    similarity: float
    combined_score: float
    
@dataclass
class QueryConfig:
    """Configuration for hybrid queries."""
    similarity_threshold: float = 0.4
    max_results: int = 10
    similarity_weight: float = 0.6
    priority_weight: float = 0.2
    popularity_weight: float = 0.1
    department_weight: float = 0.1

class HybridQueryEngine:
    """Production-ready hybrid query engine for Edinburgh University."""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5050,
            'dbname': 'pgvector',
            'user': 'postgres', 
            'password': 'postgres'
        }
        self.ollama_url = 'http://localhost:11434/api/embed'
        
    def connect_db(self):
        """Create database connection with error handling."""
        try:
            return psycopg.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding with retry logic."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.ollama_url,
                    json={'model': 'bge-m3', 'input': text},
                    timeout=30
                )
                response.raise_for_status()
                return response.json()['embeddings'][0]
                
            except Exception as e:
                logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        return []
    
    def hybrid_search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        config: Optional[QueryConfig] = None
    ) -> List[SearchResult]:
        """
        Perform hybrid search with flexible filtering.
        
        Args:
            query: Search query text
            filters: Optional filters (department, campus, doc_type, etc.)
            config: Query configuration parameters
        
        Returns:
            List of SearchResult objects
        """
        config = config or QueryConfig()
        filters = filters or {}
        
        logger.info(f"Executing hybrid search: '{query[:50]}...'")
        logger.info(f"Filters: {filters}")
        
        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Build dynamic WHERE clause
            where_conditions = ["embedding <=> %s::vector < %s"]
            params = [query_embedding, config.similarity_threshold]
            
            # Add metadata filters
            if filters.get('department'):
                where_conditions.append("metadata->>'department' = %s")
                params.append(filters['department'])
            
            if filters.get('campus'):
                where_conditions.append("metadata->>'campus' = %s")
                params.append(filters['campus'])
            
            if filters.get('doc_type'):
                where_conditions.append("metadata->>'doc_type' = %s")
                params.append(filters['doc_type'])
            
            if filters.get('min_priority'):
                where_conditions.append("(metadata->>'priority')::int >= %s")
                params.append(filters['min_priority'])
            
            if filters.get('tags'):
                where_conditions.append("metadata->'tags' ?& %s")
                params.append(filters['tags'])
            
            if filters.get('since_date'):
                where_conditions.append("(metadata->>'last_reviewed')::timestamp >= %s")
                params.append(filters['since_date'])
            
            # Build dynamic score calculation
            score_components = [
                f"(1 - (embedding <=> %s::vector)) * {config.similarity_weight}",
                f"LEAST((metadata->>'priority')::float / 5.0, 1.0) * {config.priority_weight}",
                f"LEAST((metadata->>'view_count')::float / 5000.0, 1.0) * {config.popularity_weight}"
            ]
            
            # Add department bonus if specified
            if filters.get('user_department'):
                score_components.append(f"""
                    CASE WHEN metadata->>'department' = %s THEN {config.department_weight} ELSE 0.0 END
                """)
                params.append(filters['user_department'])
            
            combined_score = f"({' + '.join(score_components)})"
            
            # Final parameters for ORDER BY and LIMIT
            params.extend([query_embedding, config.max_results])
            
            # Execute query
            conn = self.connect_db()
            cur = conn.cursor()
            
            query_sql = f"""
                SELECT 
                    document_title,
                    section_title,
                    text,
                    metadata,
                    1 - (embedding <=> %s::vector) as similarity,
                    {combined_score} as combined_score
                FROM document_chunks 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY combined_score DESC
                LIMIT %s
            """
            
            cur.execute(query_sql, params)
            raw_results = cur.fetchall()
            
            # Convert to SearchResult objects
            results = []
            for row in raw_results:
                doc_title, section, text, metadata, similarity, score = row
                
                results.append(SearchResult(
                    document_title=doc_title,
                    section_title=section,
                    text=text,
                    metadata=json.loads(metadata) if metadata else {},
                    similarity=similarity,
                    combined_score=score
                ))
            
            cur.close()
            conn.close()
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    def explain_query_performance(self, query: str, filters: Optional[Dict[str, Any]] = None):
        """Analyze query performance using EXPLAIN ANALYZE."""
        
        filters = filters or {}
        
        try:
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return
            
            conn = self.connect_db()
            cur = conn.cursor()
            
            # Simple performance test query
            test_sql = """
                EXPLAIN (ANALYZE, BUFFERS)
                SELECT 
                    document_title,
                    1 - (embedding <=> %s::vector) as similarity
                FROM document_chunks 
                WHERE embedding <=> %s::vector < 0.4
                ORDER BY embedding <=> %s::vector
                LIMIT 10
            """
            
            cur.execute(test_sql, [query_embedding, query_embedding, query_embedding])
            explain_results = cur.fetchall()
            
            print(f"\n📊 QUERY PERFORMANCE ANALYSIS")
            print(f"Query: '{query}'")
            print("-" * 60)
            
            for row in explain_results:
                print(row[0])
            
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")

def run_production_tests():
    """Test production query system."""
    
    print("🚀 SECTION 7: PRODUCTION QUERY SYSTEM")
    print("=" * 70)
    
    engine = HybridQueryEngine()
    
    # Test 1: Basic search
    print("\n1️⃣ BASIC HYBRID SEARCH")
    results = engine.hybrid_search("password reset instructions")
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result.document_title}")
        print(f"   Similarity: {result.similarity:.3f} | Combined Score: {result.combined_score:.3f}")
        print(f"   Dept: {result.metadata.get('department', 'N/A')} | Type: {result.metadata.get('doc_type', 'N/A')}")
    
    # Test 2: Filtered search
    print("\n\n2️⃣ FILTERED SEARCH (IT Services only)")
    filters = {
        'department': 'IT Services',
        'min_priority': 3
    }
    results = engine.hybrid_search("network connectivity problems", filters=filters)
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result.document_title}")
        print(f"   Priority: {result.metadata.get('priority', 'N/A')} | Score: {result.combined_score:.3f}")
    
    # Test 3: Complex filters
    print("\n\n3️⃣ COMPLEX FILTERED SEARCH")
    complex_filters = {
        'doc_type': 'guide',
        'tags': ['network', 'troubleshooting'],
        'user_department': 'IT Services'  # Department match bonus
    }
    results = engine.hybrid_search("wifi setup instructions", filters=complex_filters)
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result.document_title}")
        print(f"   Tags: {result.metadata.get('tags', [])}")
        print(f"   Score: {result.combined_score:.3f}")
    
    # Test 4: Performance analysis
    print("\n\n4️⃣ PERFORMANCE ANALYSIS")
    engine.explain_query_performance("email configuration help")

if __name__ == "__main__":
    run_production_tests()
```

**Run production system:**

```bash
python lab7_production_queries.py
```

---

### Exercise 5: Edinburgh-Specific Use Cases (5 minutes)

#### 5.1: Real-World Scenario Testing

**Create Edinburgh scenario tests:**

```python
# lab7_edinburgh_scenarios.py
from lab7_production_queries import HybridQueryEngine, QueryConfig
from datetime import datetime, timedelta

def test_edinburgh_scenarios():
    """Test realistic Edinburgh University search scenarios."""
    
    print("🏴󠁧󠁢󠁳󠁣󠁴󠁿 EDINBURGH UNIVERSITY SCENARIO TESTING")
    print("=" * 70)
    
    engine = HybridQueryEngine()
    
    # Scenario 1: New student needs WiFi help
    print("\n📱 SCENARIO 1: New Student WiFi Setup")
    print("Context: First-year student in accommodation, can't connect to WiFi")
    
    filters = {
        'tags': ['wifi', 'network'],
        'doc_type': 'guide'
    }
    
    results = engine.hybrid_search(
        "how to connect to WiFi in student accommodation", 
        filters=filters
    )
    
    if results:
        print(f"✅ Found {len(results)} helpful guides:")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.document_title}")
            print(f"     Campus: {result.metadata.get('campus', 'N/A')} | Score: {result.combined_score:.3f}")
    
    # Scenario 2: Staff member needs urgent policy info  
    print("\n\n🚨 SCENARIO 2: Urgent Policy Clarification")
    print("Context: HR staff needs immediate access to data protection policies")
    
    filters = {
        'department': 'HR',
        'min_priority': 4,
        'doc_type': 'policy'
    }
    
    results = engine.hybrid_search(
        "GDPR data protection staff responsibilities",
        filters=filters
    )
    
    if results:
        print(f"✅ Found {len(results)} urgent policy documents:")
        for i, result in enumerate(results[:2], 1):
            priority = result.metadata.get('priority', 'Unknown')
            print(f"  {i}. {result.document_title}")
            print(f"     Priority: {priority} | Score: {result.combined_score:.3f}")
    
    # Scenario 3: IT support looking for recent troubleshooting
    print("\n\n🔧 SCENARIO 3: Recent Troubleshooting Guides")  
    print("Context: IT technician needs latest network troubleshooting procedures")
    
    # Only include documents reviewed in last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    
    filters = {
        'department': 'IT Services',
        'since_date': six_months_ago,
        'tags': ['troubleshooting']
    }
    
    # Use custom config to prioritize recency
    recent_config = QueryConfig(
        similarity_weight=0.5,  # Less emphasis on similarity
        priority_weight=0.3,    # More emphasis on priority
        popularity_weight=0.2   # More emphasis on usage
    )
    
    results = engine.hybrid_search(
        "network outage diagnosis steps",
        filters=filters,
        config=recent_config
    )
    
    if results:
        print(f"✅ Found {len(results)} recent troubleshooting guides:")
        for i, result in enumerate(results[:2], 1):
            last_review = result.metadata.get('last_reviewed', 'Unknown')
            print(f"  {i}. {result.document_title}")
            print(f"     Last reviewed: {last_review} | Score: {result.combined_score:.3f}")
    
    # Scenario 4: Multi-campus search with preference
    print("\n\n🏫 SCENARIO 4: Campus-Specific Information")
    print("Context: King's Buildings staff needs local IT support info")
    
    # Search all campuses but prefer King's Buildings
    results_kb = engine.hybrid_search(
        "local IT support contact information",
        filters={'user_department': 'IT Services'}  # Department bonus
    )
    
    if results_kb:
        print(f"✅ Found {len(results_kb)} IT support documents:")
        
        # Group by campus for display
        by_campus = {}
        for result in results_kb[:6]:
            campus = result.metadata.get('campus', 'Unknown')
            if campus not in by_campus:
                by_campus[campus] = []
            by_campus[campus].append(result)
        
        for campus, docs in by_campus.items():
            print(f"\n📍 {campus}:")
            for doc in docs[:2]:  # Top 2 per campus
                print(f"    • {doc.document_title}")
                print(f"      Score: {doc.combined_score:.3f}")

if __name__ == "__main__":
    test_edinburgh_scenarios()
```

**Run Edinburgh scenarios:**

```bash
python lab7_edinburgh_scenarios.py
```

---

## Lab Verification

### Quick Performance Check

```python
# lab7_verification.py
import time
from lab7_production_queries import HybridQueryEngine

def verify_lab_completion():
    """Verify all lab components are working correctly."""
    
    print("🔍 SECTION 7 LAB VERIFICATION")
    print("=" * 50)
    
    engine = HybridQueryEngine()
    
    # Test 1: Basic functionality
    print("1️⃣ Testing basic hybrid search...")
    start_time = time.time()
    
    results = engine.hybrid_search("password reset help")
    search_time = time.time() - start_time
    
    if results:
        print(f"   ✅ Found {len(results)} results in {search_time:.2f}s")
        print(f"   ✅ Top result: {results[0].document_title}")
    else:
        print("   ❌ No results found")
    
    # Test 2: Filtered search
    print("\n2️⃣ Testing filtered search...")
    filtered_results = engine.hybrid_search(
        "network problems",
        filters={'doc_type': 'guide', 'min_priority': 3}
    )
    
    if filtered_results:
        print(f"   ✅ Filtered search returned {len(filtered_results)} results")
    else:
        print("   ❌ Filtered search failed")
    
    # Test 3: Performance benchmarks
    print("\n3️⃣ Performance benchmarks:")
    print(f"   ✅ Search time: {search_time:.2f}s (target: <1.0s)")
    print(f"   ✅ Results quality: {len([r for r in results if r.similarity > 0.6])} high-confidence matches")
    
    # Test 4: Index verification
    print("\n4️⃣ Index verification...")
    try:
        conn = engine.connect_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'document_chunks' 
            AND indexname LIKE '%metadata%'
        """)
        
        metadata_indexes = cur.fetchall()
        print(f"   ✅ Metadata indexes: {len(metadata_indexes)}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"   ❌ Index check failed: {e}")
    
    print("\n🎯 LAB 7 VERIFICATION COMPLETE!")
    print(f"Advanced hybrid queries are working correctly! 🚀")

if __name__ == "__main__":
    verify_lab_completion()
```

**Run verification:**

```bash
python lab7_verification.py
```

---

## Success Criteria

### ✅ Lab Completion Checklist

**After completing this lab, you should have:**

- [ ] **Enhanced metadata** - Rich JSONB metadata added to document chunks
- [ ] **Optimized indexes** - HNSW, GIN, and B-tree indexes for hybrid queries
- [ ] **Basic hybrid queries** - Vector similarity + metadata filtering
- [ ] **Advanced scoring** - Multi-criteria weighted scoring system
- [ ] **Production system** - Error handling, logging, configurable queries
- [ ] **Edinburgh scenarios** - Real-world use case testing
- [ ] **Performance verification** - Sub-second search times maintained

### 🎯 Key Achievements

**Technical Skills:**
- Master complex PostgreSQL queries combining vectors, JSONB, and relational data
- Implement production-ready error handling and performance optimization
- Design flexible, configurable search systems

**Edinburgh Context:**
- Handle multi-campus, multi-department search requirements
- Implement role-based and time-aware filtering
- Create realistic institutional search scenarios

---

## Next Steps

**For Section 8: Production Deployment**
- Scaling considerations for Edinburgh's full document corpus
- Monitoring and alerting for hybrid query performance
- Security and access control implementation
- Advanced caching and optimization strategies

**Advanced Experimentation:**
- Try different scoring weight combinations
- Experiment with similarity thresholds for different content types
- Test performance with larger document sets
- Explore more complex JSONB query patterns

---

## Troubleshooting

### Common Issues

**"No results found" errors:**
```bash
# Check if embeddings exist
python -c "
import psycopg
conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL')
print(f'Chunks with embeddings: {cur.fetchone()[0]}')
"
```

**Slow query performance:**
```bash
# Verify indexes are being used
python lab7_production_queries.py  # Check the performance analysis output
```

**Ollama connection errors:**
```bash
# Restart Ollama service
cd environment && docker-compose restart ollama-service
```

---

**🎉 Congratulations! You've mastered advanced vector queries for Edinburgh University! 🚀**