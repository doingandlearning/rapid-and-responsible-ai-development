# Section 7 Solution Files

## Complete Advanced Vector Queries Implementation
This directory contains the complete, working solution for Section 7: Advanced Vector Queries.

## Files Included

### `lab7_complete_system.py`
**Production-ready hybrid search system** with all lab requirements:
- Multi-criteria hybrid queries combining vector similarity + metadata filtering
- Advanced JSONB query patterns with proper indexing
- Configurable scoring with multiple weighted components
- Production-grade error handling and performance monitoring
- Edinburgh University-specific use cases and scenarios
- Comprehensive query performance analysis tools

## Running the Solution

### Prerequisites
Ensure your environment is ready:
```bash
# Start services (from repository root)
cd environment && docker compose up -d

# Activate Python environment
source .venv/bin/activate

# Verify Section 6 data is available
python -c "import psycopg; conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL'); print(f'Available chunks: {cur.fetchone()[0]}')"

# Ensure Ollama embedding service is running
curl http://localhost:11434/api/tags
```

### Execute Complete Solution
```bash
cd final_materials/section-07-advanced-vector-queries/solution
python lab7_complete_system.py
```

## Expected Output

### 1. Database Enhancement Phase
```
🔧 SETTING UP ENHANCED DATABASE
==================================================
Adding enhanced metadata...
Creating advanced indexes...
  ✅ Created index
  ✅ Created index
  ✅ Created index
✅ Database enhancement complete!
```

### 2. Comprehensive Testing Phase
```
🚀 COMPREHENSIVE ADVANCED QUERY TESTING
======================================================================

1️⃣ BASIC HYBRID SEARCH
----------------------------------------
✅ Found 8 results
  1. Edinburgh IT Support Handbook
     Similarity: 0.867 | Score: 0.724
     Dept: IT Services | Type: guide

2️⃣ DEPARTMENT-SPECIFIC SEARCH
----------------------------------------
✅ Found 5 IT Services results
  1. Network Troubleshooting Guide
     Priority: 4 | Score: 0.756
  2. WiFi Configuration Manual
     Priority: 3 | Score: 0.689

3️⃣ RECENT DOCUMENTS SEARCH
----------------------------------------
✅ Found 6 recent results
  1. Email Setup Guide
     Last reviewed: 2024-08-15 | Score: 0.823
  2. Password Policy Update
     Last reviewed: 2024-07-22 | Score: 0.767

4️⃣ CAMPUS-SPECIFIC SEARCH
----------------------------------------
✅ Found 7 King's Buildings results
  1. King's Buildings IT Contact Directory
     Campus: King's Buildings | Score: 0.845
  2. Local Network Services Guide
     Campus: King's Buildings | Score: 0.778

5️⃣ ADVANCED FILTERED SEARCH
----------------------------------------
✅ Found 4 filtered results
  1. Network Connectivity Troubleshooting
     Tags: ['network', 'troubleshooting'] | Priority: 4
  2. WiFi Connection Guide
     Tags: ['network', 'wifi'] | Priority: 3

6️⃣ COMPLEX MULTI-CRITERIA SEARCH
----------------------------------------
✅ Found 3 complex search results
  1. Student Accommodation Network Guide
     Score: 0.891 | Similarity: 0.823
     Dept: IT Services | Campus: King's Buildings
     Tags: ['wifi', 'network', 'troubleshooting']
  2. Residence WiFi Setup Procedures
     Score: 0.834 | Similarity: 0.776
     Dept: Student Services | Campus: Central Campus
     Tags: ['wifi', 'student']

7️⃣ PERFORMANCE STATISTICS
----------------------------------------
  total_queries: 6
  avg_execution_time: 0.347
  avg_results_count: 5.5
  avg_embedding_time: 0.145
  avg_db_time: 0.089
  slowest_query_time: 0.456
  fastest_query_time: 0.234

8️⃣ QUERY PERFORMANCE ANALYSIS
----------------------------------------
📊 QUERY PERFORMANCE ANALYSIS
Query: 'password reset help'
------------------------------------------------------------
Total Cost: 125.43
Execution Time: 23.45 ms
Rows Returned: 10
✅ Using index scan
```

### 3. Real-World Scenarios Phase
```
🏴󠁧󠁢󠁳󠁣󠁴󠁿 EDINBURGH UNIVERSITY REAL-WORLD SCENARIOS
======================================================================

📱 SCENARIO: New Student Needs WiFi Help
Context: First-year student in accommodation, urgent connectivity issue
✅ Found 5 student-focused results:
  1. Student Accommodation WiFi Setup Guide
     Campus: Easter Bush | Tags: ['wifi', 'student', 'network']
     Relevance: 0.845 | Priority: 3
  2. EdUni Network Connection Instructions
     Campus: Central Campus | Tags: ['network', 'troubleshooting']
     Relevance: 0.789 | Priority: 2

🚨 SCENARIO: IT Staff Emergency Response
Context: Network outage at King's Buildings, need immediate procedures
✅ Found 3 emergency response documents:
  1. Network Outage Emergency Procedures
     Priority: 5 | Department: IT Services
     Combined Score: 0.934
  2. Critical System Recovery Guide
     Priority: 4 | Department: IT Services
     Combined Score: 0.887

📋 SCENARIO: Policy Compliance Check
Context: HR staff needs current data protection policies for audit
✅ Found 5 policy compliance documents:
  1. GDPR Compliance Policy 2024
     Version: 3.2 | Last Reviewed: 2024-06-15
     Relevance: 0.823
  2. Staff Data Protection Guidelines
     Version: 2.1 | Last Reviewed: 2024-05-08
     Relevance: 0.778
```

### 4. Success Summary
```
================================================================================
✅ SECTION 7 COMPLETE!
Advanced hybrid search system successfully implemented!
================================================================================

🎯 KEY ACHIEVEMENTS:
  • Multi-criteria hybrid queries with configurable weights
  • Advanced JSONB metadata filtering and indexing
  • Production-ready error handling and performance monitoring
  • Edinburgh-specific use cases and scenarios
  • Comprehensive query performance analysis

💡 SYSTEM CAPABILITIES:
  • Semantic similarity + relational filtering
  • Campus, department, and role-based search
  • Time-aware and priority-weighted results
  • Real-time performance statistics and optimization

🚀 Ready for Section 8: Production Deployment!
```

## Understanding the Implementation

### Key Components

#### 1. Advanced Hybrid Search Engine
```python
class EdinburghHybridSearch:
    def execute_hybrid_search(self, query: str, filters: Dict, config: QueryConfig):
        # 1. Generate query embedding
        # 2. Build dynamic WHERE conditions
        # 3. Construct weighted scoring expression
        # 4. Execute optimized SQL query
        # 5. Return structured results with performance stats
```

#### 2. Multi-Criteria Scoring System
```python
def build_scoring_expression(self, config: QueryConfig, filters: Dict):
    score_components = [
        # 60% semantic similarity
        f"(1 - (embedding <=> %s::vector)) * {config.similarity_weight}",
        
        # 20% priority weight  
        f"LEAST((metadata->>'priority')::float / 5.0, 1.0) * {config.priority_weight}",
        
        # 10% popularity (view count)
        f"LEAST((metadata->>'view_count')::float / 5000.0, 1.0) * {config.popularity_weight}",
        
        # 10% department match bonus
        f"CASE WHEN metadata->>'department' = %s THEN {config.department_weight} ELSE 0.0 END"
    ]
    
    return f"({' + '.join(score_components)})"
```

#### 3. Dynamic Query Building
```python
def build_query_conditions(self, filters: Dict, params: List):
    conditions = ["embedding <=> %s::vector < %s"]  # Base similarity threshold
    
    # Add metadata filters dynamically
    if filters.get('department'):
        conditions.append("metadata->>'department' = %s")
    
    if filters.get('tags_all'):
        conditions.append("metadata->'tags' ?& %s")  # Contains all tags
        
    if filters.get('since_date'):
        conditions.append("(metadata->>'last_reviewed')::timestamp >= %s")
    
    return conditions, params
```

#### 4. Performance Monitoring
```python
@dataclass
class QueryStats:
    query: str
    execution_time: float
    results_count: int
    embedding_time: float
    db_time: float
    filters_applied: Dict[str, Any]

def get_query_performance_stats(self):
    # Aggregate performance metrics across all queries
    return {
        'total_queries': len(self.stats),
        'avg_execution_time': avg_time,
        'avg_results_count': avg_results,
        'slowest_query_time': max_time,
        'fastest_query_time': min_time
    }
```

#### 5. Edinburgh-Specific Query Methods
```python
def search_by_department(self, query: str, department: str, min_priority: int = None):
    # Convenience method for department-specific searches
    
def search_recent_documents(self, query: str, days_back: int = 90):
    # Time-bounded search with recency scoring
    
def search_by_campus(self, query: str, campus: str, user_department: str = None):
    # Campus-specific search with department bonus
    
def advanced_filtered_search(self, query: str, doc_types: List[str], required_tags: List[str]):
    # Complex multi-filter search for power users
```

## Customization Options

### Scoring Weight Configuration
Adjust system behavior by modifying scoring weights:
```python
# Emphasize semantic similarity for research queries
research_config = QueryConfig(
    similarity_weight=0.8,
    priority_weight=0.1,
    popularity_weight=0.05,
    department_weight=0.05
)

# Emphasize priority for emergency scenarios
emergency_config = QueryConfig(
    similarity_weight=0.4,
    priority_weight=0.4,
    department_weight=0.2
)
```

### Custom Filter Combinations
Create specialized searches for different user groups:
```python
# Student-focused searches
student_filters = {
    'tags_any': ['student', 'guide', 'help'],
    'max_clearance': 2,  # Public access only
    'doc_type': 'guide'
}

# Staff emergency searches  
emergency_filters = {
    'min_priority': 4,
    'department': 'IT Services',
    'tags_any': ['urgent', 'emergency'],
    'since_date': datetime.now() - timedelta(days=30)  # Recent only
}
```

### Edinburgh Campus Customization
Adapt for different Edinburgh locations:
```python
campus_preferences = {
    'KB': "King's Buildings",
    'CC': 'Central Campus', 
    'EB': 'Easter Bush',
    'WG': 'Western General'
}

def search_for_campus(query: str, campus_code: str):
    return search.search_by_campus(
        query, 
        campus_preferences[campus_code],
        user_department=user_dept
    )
```

## Advanced Features

### Query Performance Analysis
```python
# Analyze slow queries
search.explain_query_performance("complex search query")

# Monitor system performance over time
stats = search.get_query_performance_stats()
print(f"Average query time: {stats['avg_execution_time']}s")
```

### Dynamic Similarity Thresholds
```python
def adaptive_search(query: str, content_type: str):
    # Adjust thresholds based on content type
    thresholds = {
        'policy': 0.8,      # High precision for policies
        'guide': 0.6,       # Medium precision for guides  
        'faq': 0.4          # Lower precision for FAQs
    }
    
    config = QueryConfig(similarity_threshold=thresholds.get(content_type, 0.5))
    return search.execute_hybrid_search(query, config=config)
```

### Multi-Language Support Preparation
```python
# Framework for multi-language Edinburgh support
language_filters = {
    'en': {'tags_any': ['english']},
    'gd': {'tags_any': ['gaelic', 'gàidhlig']},  # Scottish Gaelic
    'zh': {'tags_any': ['chinese', 'international']}
}
```

## Troubleshooting

### Common Issues

**"No results with complex filters"**
```bash
# Check metadata distribution
python -c "
import psycopg
conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
cur = conn.cursor()
cur.execute('SELECT metadata->>\"department\", COUNT(*) FROM document_chunks GROUP BY metadata->>\"department\"')
for dept, count in cur.fetchall():
    print(f'{dept}: {count} chunks')
"
```

**"Slow hybrid query performance"**
```python
# Check index usage in queries
search = EdinburghHybridSearch()
search.explain_query_performance("test query")

# Look for "Index Scan" vs "Seq Scan" in output
# If seeing sequential scans, verify indexes exist:
# SELECT indexname FROM pg_indexes WHERE tablename = 'document_chunks';
```

**"Embedding generation timeouts"**
```bash
# Check Ollama service status
docker ps | grep ollama

# Restart if needed
cd environment && docker-compose restart ollama-service

# Test embedding service directly
curl -X POST http://localhost:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{"model": "bge-m3", "input": "test query"}'
```

**"Inconsistent scoring results"**
```python
# Verify metadata consistency
conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
cur = conn.cursor()

# Check for missing metadata fields
cur.execute("SELECT COUNT(*) FROM document_chunks WHERE metadata->>'priority' IS NULL")
print(f"Chunks missing priority: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM document_chunks WHERE metadata->>'view_count' IS NULL")  
print(f"Chunks missing view_count: {cur.fetchone()[0]}")
```

## Performance Optimization

### For High-Volume Usage
```python
# Implement connection pooling
from psycopg_pool import ConnectionPool

class OptimizedHybridSearch(EdinburghHybridSearch):
    def __init__(self):
        super().__init__()
        self.pool = ConnectionPool(
            f"postgresql://{self.db_config['user']}:{self.db_config['password']}@"
            f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['dbname']}",
            min_size=2,
            max_size=10
        )
```

### For Better Search Relevance
```python
# Implement query expansion
def expand_query(original_query: str) -> str:
    # Add Edinburgh-specific synonyms
    synonyms = {
        'wifi': 'wifi wireless network connectivity',
        'password': 'password authentication login credentials',
        'email': 'email outlook exchange mail'
    }
    
    expanded = original_query
    for term, expansion in synonyms.items():
        if term in original_query.lower():
            expanded += f" {expansion}"
    
    return expanded
```

### Index Maintenance
```sql
-- Monitor index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE tablename = 'document_chunks';

-- Rebuild indexes if needed (during low-usage periods)
REINDEX INDEX document_chunks_metadata_gin;
REINDEX INDEX document_chunks_embedding_idx;
```

## Production Deployment Notes

### Configuration Management
```python
# Use environment variables for production
import os

production_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'dbname': os.getenv('DB_NAME', 'pgvector'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}
```

### Monitoring Integration
```python
# Add metrics collection
import prometheus_client

query_duration = prometheus_client.Histogram('hybrid_search_duration_seconds')
query_results = prometheus_client.Counter('hybrid_search_results_total')

@query_duration.time()
def monitored_search(query: str, filters: Dict = None):
    results = search.execute_hybrid_search(query, filters)
    query_results.inc(len(results))
    return results
```

### Security Considerations
```python
# Implement query sanitization
def sanitize_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    # Validate and sanitize filter values
    safe_filters = {}
    
    # Department whitelist
    if 'department' in filters:
        allowed_depts = ['IT Services', 'Student Services', 'Library', 'HR']
        if filters['department'] in allowed_depts:
            safe_filters['department'] = filters['department']
    
    # Priority range validation
    if 'min_priority' in filters:
        priority = int(filters['min_priority'])
        if 1 <= priority <= 5:
            safe_filters['min_priority'] = priority
    
    return safe_filters
```

## Next Steps

After running this solution successfully:

1. **Test with various query patterns** to understand system behavior
2. **Analyze performance statistics** to identify optimization opportunities  
3. **Experiment with scoring weights** for different Edinburgh use cases
4. **Prepare for Section 8** production deployment and scaling considerations

The hybrid search system created by this solution provides Edinburgh University with production-ready, sophisticated search capabilities that combine the power of semantic understanding with precise institutional filtering requirements.

## Validation Checklist

Confirm your solution works correctly:

- [ ] Database enhanced with rich JSONB metadata and proper indexing
- [ ] Basic hybrid queries return relevant results with similarity + metadata filtering
- [ ] Multi-criteria scoring produces logical result rankings
- [ ] Campus, department, and time-based filtering works correctly
- [ ] Performance monitoring captures query statistics accurately
- [ ] Edinburgh scenarios demonstrate realistic institutional use cases
- [ ] Query performance analysis shows index usage and sub-second response times
- [ ] Error handling manages edge cases gracefully
- [ ] System scales to handle concurrent queries efficiently

**Success = Production-Ready Hybrid Search System for Edinburgh University! 🎉**