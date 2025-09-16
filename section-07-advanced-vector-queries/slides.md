# Section 7: Advanced Vector Queries

**Building Hybrid Search Systems with PostgreSQL + pgvector**

---

## Section Overview

**Time:** 90 minutes  
**Format:** 45 min presentation + 45 min hands-on lab

**Learning Goals:**
- Master hybrid queries combining vector similarity + relational filters
- Implement advanced search patterns for production use cases  
- Optimize complex queries for Edinburgh's diverse data requirements
- Build sophisticated filtering and ranking systems

---

## Why Advanced Vector Queries?

### Beyond Simple Similarity

**Simple vector search:**
```sql
SELECT * FROM documents 
ORDER BY embedding <=> query_vector 
LIMIT 5;
```

**Real-world requirements:**
- "Find similar documents from last 6 months"
- "Search within specific document types only"
- "Prioritize results by author or department"
- "Filter by metadata while maintaining relevance"

---

## The Power of Hybrid Search

### Combining Multiple Signals

**Vector similarity:** Semantic relevance  
**Relational filters:** Exact criteria  
**JSONB metadata:** Flexible attributes  
**Full-text search:** Keyword matching

**Result:** Precise, context-aware search that understands both meaning and constraints

---

## Edinburgh University Use Cases

### IT Support Scenarios

**Query:** *"Recent WiFi troubleshooting guides for student accommodation"*

**Requirements:**
- Semantic similarity to "WiFi troubleshooting"
- Document type = "guide" 
- Topic = "student accommodation"
- Published within last 12 months
- Priority by view count/rating

---

## Advanced Query Patterns

### 1. Vector + Metadata Filtering

```sql
SELECT 
  title,
  content,
  metadata->>'department' as dept,
  1 - (embedding <=> %s::vector) as similarity
FROM documents 
WHERE metadata->>'doc_type' = 'policy'
  AND metadata->>'status' = 'active'
ORDER BY embedding <=> %s::vector
LIMIT 10;
```

**Use case:** Find active policies similar to query

---

## Advanced Query Patterns

### 2. Time-Bounded Similarity

```sql
SELECT 
  title,
  content,
  created_at,
  1 - (embedding <=> %s::vector) as similarity
FROM documents 
WHERE created_at >= %s
  AND created_at <= %s
ORDER BY embedding <=> %s::vector
LIMIT 10;
```

**Use case:** Search within specific time windows

---

## Advanced Query Patterns

### 3. Multi-Criteria Ranking

```sql
SELECT 
  title,
  content,
  (1 - (embedding <=> %s::vector)) * 0.7 +  -- 70% semantic
  (metadata->>'priority')::float * 0.2 +     -- 20% priority
  LEAST(view_count / 1000.0, 1.0) * 0.1     -- 10% popularity
  as combined_score
FROM documents 
WHERE metadata->>'category' = %s
ORDER BY combined_score DESC
LIMIT 10;
```

**Use case:** Weighted scoring across multiple factors

---

## JSONB Advanced Patterns

### Flexible Metadata Queries

```sql
-- Array containment
WHERE metadata->'tags' @> '["urgent", "network"]'

-- Key existence
WHERE metadata ? 'department'

-- Nested object access
WHERE metadata->'author'->>'name' = 'IT Services'

-- Path queries
WHERE metadata @@ '$.priority > 5'
```

**Power:** Schema-free attributes with SQL performance

---

## Geographic and Numeric Ranges

### Campus-Specific Searches

```sql
SELECT 
  building_name,
  room_number,
  1 - (embedding <=> %s::vector) as similarity
FROM support_tickets 
WHERE metadata->>'campus' = 'King''s Buildings'
  AND (metadata->>'priority')::int >= 3
  AND created_at > NOW() - INTERVAL '30 days'
ORDER BY embedding <=> %s::vector
LIMIT 5;
```

**Use case:** Location and priority-aware support ticket search

---

## Performance Optimization Strategies

### Index Strategy for Hybrid Queries

```sql
-- HNSW for vector similarity
CREATE INDEX ON documents 
USING hnsw (embedding vector_cosine_ops);

-- B-tree for exact matches
CREATE INDEX ON documents (created_at);

-- GIN for JSONB operations
CREATE INDEX ON documents 
USING gin (metadata jsonb_path_ops);
```

**Goal:** Each query component uses optimal index type

---

## Query Execution Plans

### Understanding PostgreSQL Decisions

```sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT title, content,
       1 - (embedding <=> %s::vector) as similarity
FROM documents 
WHERE metadata->>'department' = 'IT'
  AND created_at > '2024-01-01'
ORDER BY embedding <=> %s::vector
LIMIT 10;
```

**Key metrics:** Index usage, scan types, execution time

---

## Advanced Filtering Techniques

### Complex Boolean Logic

```sql
SELECT title, content FROM documents 
WHERE (
  metadata->'tags' @> '["urgent"]' OR
  (metadata->>'priority')::int > 8
) AND (
  metadata->>'department' = 'IT' OR
  metadata->>'department' = 'Student Services'
) AND embedding <=> %s::vector < 0.3
ORDER BY embedding <=> %s::vector;
```

**Pattern:** Nested conditions with vector threshold

---

## Distance Thresholds and Quality Control

### Setting Similarity Boundaries

```sql
-- High confidence only
WHERE 1 - (embedding <=> %s::vector) > 0.8

-- Exclude poor matches  
WHERE embedding <=> %s::vector < 0.4

-- Dynamic thresholds
WHERE embedding <=> %s::vector < 
      CASE 
        WHEN metadata->>'category' = 'critical' THEN 0.2
        WHEN metadata->>'category' = 'standard' THEN 0.3
        ELSE 0.4
      END
```

**Goal:** Maintain result quality across different content types

---

## Aggregation with Vectors

### Department-Level Analytics

```sql
SELECT 
  metadata->>'department' as dept,
  COUNT(*) as doc_count,
  AVG(1 - (embedding <=> %s::vector)) as avg_similarity,
  MAX(1 - (embedding <=> %s::vector)) as best_match
FROM documents 
WHERE embedding <=> %s::vector < 0.5
GROUP BY metadata->>'department'
ORDER BY avg_similarity DESC;
```

**Use case:** Understanding content distribution by relevance

---

## Window Functions with Vectors

### Ranked Results Within Groups

```sql
SELECT 
  title,
  metadata->>'department' as dept,
  1 - (embedding <=> %s::vector) as similarity,
  ROW_NUMBER() OVER (
    PARTITION BY metadata->>'department' 
    ORDER BY embedding <=> %s::vector
  ) as dept_rank
FROM documents 
WHERE embedding <=> %s::vector < 0.4
ORDER BY similarity DESC;
```

**Pattern:** Top N results per category

---

## Common Table Expressions (CTEs)

### Multi-Stage Query Processing

```sql
WITH relevant_docs AS (
  SELECT id, title, embedding, metadata
  FROM documents 
  WHERE embedding <=> %s::vector < 0.3
), scored_docs AS (
  SELECT *, 
    (1 - (embedding <=> %s::vector)) * 0.8 +
    (metadata->>'importance')::float * 0.2 as final_score
  FROM relevant_docs
)
SELECT * FROM scored_docs 
ORDER BY final_score DESC 
LIMIT 10;
```

**Advantage:** Complex logic broken into readable stages

---

## Edinburgh-Specific Patterns

### Multi-Campus Search

```sql
SELECT 
  title, content,
  metadata->>'campus' as campus,
  metadata->>'building' as building,
  1 - (embedding <=> %s::vector) as similarity
FROM support_docs 
WHERE metadata->>'campus' = ANY(%s::text[])  -- ['KB', 'CM', 'EH']
  AND metadata->>'doc_type' = 'procedure'
  AND embedding <=> %s::vector < 0.35
ORDER BY 
  CASE metadata->>'campus'
    WHEN 'KB' THEN 1    -- King's Buildings priority
    WHEN 'CM' THEN 2    -- Central campus
    ELSE 3
  END,
  embedding <=> %s::vector;
```

---

## Academic Year Filtering

### Time-Aware Educational Content

```sql
SELECT title, content, academic_year
FROM course_materials 
WHERE academic_year = %s  -- '2024-25'
  AND (
    metadata->'terms' @> %s OR  -- ["semester1"]
    metadata->>'availability' = 'year-round'
  )
  AND embedding <=> %s::vector < 0.3
ORDER BY embedding <=> %s::vector;
```

**Use case:** Current semester-relevant educational resources

---

## User Permission Integration

### Role-Based Vector Search

```sql
WITH user_permissions AS (
  SELECT department, role, clearance_level
  FROM staff_access 
  WHERE user_id = %s
)
SELECT d.title, d.content
FROM documents d, user_permissions up
WHERE d.metadata->>'department' = up.department
  AND (d.metadata->>'clearance_level')::int <= up.clearance_level
  AND d.embedding <=> %s::vector < 0.3
ORDER BY d.embedding <=> %s::vector;
```

**Security:** Vector search respects access controls

---

## Performance Monitoring

### Query Performance Metrics

```sql
-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE tablename = 'documents' 
  AND attname IN ('created_at', 'metadata');

-- Monitor vector operations
SELECT 
  calls, total_time, mean_time, query
FROM pg_stat_statements 
WHERE query LIKE '%<=>%'
ORDER BY total_time DESC;
```

**Goal:** Identify and optimize slow hybrid queries

---

## Error Handling Patterns

### Robust Query Design

```sql
-- Handle missing metadata gracefully
SELECT title, 
  COALESCE(metadata->>'priority', '0')::int as priority,
  COALESCE(1 - (embedding <=> %s::vector), 0) as similarity
FROM documents 
WHERE CASE 
  WHEN metadata IS NULL THEN false
  WHEN metadata->>'status' IS NULL THEN true
  ELSE metadata->>'status' = 'active'
END
ORDER BY embedding <=> %s::vector;
```

**Pattern:** Defensive programming for optional fields

---

## Advanced Use Case: Research Paper Search

### Academic Query Complexity

```sql
SELECT 
  p.title, p.abstract,
  p.metadata->>'subject_area' as subject,
  STRING_AGG(a.name, ', ') as authors,
  1 - (p.embedding <=> %s::vector) as relevance
FROM papers p
LEFT JOIN paper_authors pa ON p.id = pa.paper_id
LEFT JOIN authors a ON pa.author_id = a.id
WHERE p.publication_year BETWEEN %s AND %s
  AND p.metadata->'keywords' ?| %s::text[]  -- Any of these keywords
  AND p.metadata->>'peer_reviewed' = 'true'
GROUP BY p.id, p.title, p.abstract, p.metadata, p.embedding
HAVING 1 - (p.embedding <=> %s::vector) > 0.6
ORDER BY relevance DESC, p.citation_count DESC;
```

---

## Query Optimization Workshop

### Real-World Scenario Analysis

**Given:** Edinburgh's document database with:
- 50,000+ support documents
- 1,000+ staff procedures  
- 10,000+ student guides
- Rich JSONB metadata

**Challenge:** Design queries for complex institutional needs

---

## Scenario 1: Emergency Response

### Urgent Issue Resolution

**Need:** *"Find critical network outage procedures from the last 2 years, prioritizing King's Buildings campus"*

**Query requirements:**
- Vector similarity to "network outage procedures"
- Metadata: category = "emergency", campus = "KB"  
- Time window: 2022-2024
- Sort by: campus priority → recency → relevance

---

## Scenario 2: Policy Compliance

### Regulatory Requirement Search

**Need:** *"Locate all GDPR-related policies that mention 'student data' and were updated since the latest regulation change"*

**Query requirements:**
- Vector similarity to "GDPR student data policies"
- Full-text: contains "student data"
- Metadata: type = "policy", topic = "GDPR"
- Date filter: updated_at > regulation_date
- Include version tracking

---

## Scenario 3: Personalized Help

### Context-Aware Support

**Need:** *"Show troubleshooting guides relevant to this user's role, department, and recent support history"*

**Query requirements:**
- Vector similarity to user's current issue
- Filter by user's department and access level
- Exclude recently viewed documents  
- Boost results similar to previously successful solutions
- Consider user's technical expertise level

---

## Best Practices Summary

### Query Design Principles

✅ **Start simple, add complexity gradually**  
✅ **Use appropriate indexes for each filter**  
✅ **Set reasonable similarity thresholds**  
✅ **Handle edge cases and missing data**  
✅ **Monitor performance with EXPLAIN**  
✅ **Test with realistic data volumes**

❌ **Don't over-engineer initial queries**  
❌ **Don't ignore index maintenance**

---

## Common Anti-Patterns

### What to Avoid

**❌ Similarity without bounds:**
```sql
-- Too permissive - returns irrelevant results
ORDER BY embedding <=> %s::vector LIMIT 100;
```

**✅ Similarity with thresholds:**
```sql
-- Quality-controlled results
WHERE embedding <=> %s::vector < 0.4
ORDER BY embedding <=> %s::vector LIMIT 10;
```

---

## Common Anti-Patterns

### JSON Query Inefficiencies

**❌ Unindexed JSON operations:**
```sql
-- Slow for large tables
WHERE metadata->>'status' = 'active';
```

**✅ Proper indexing:**
```sql
-- Fast with GIN index
CREATE INDEX ON documents USING gin (metadata);
WHERE metadata->>'status' = 'active';
```

---

## Production Deployment Considerations

### Scaling Hybrid Queries

**Connection pooling:** Handle concurrent complex queries  
**Query caching:** Cache expensive hybrid results  
**Read replicas:** Distribute query load  
**Monitoring:** Track slow query patterns  
**Partitioning:** Split large tables by date/department

**Goal:** Maintain sub-second response times at scale

---

## Edinburgh Implementation Strategy

### Institutional Requirements

**Multi-campus support:** Geographic filtering and prioritization  
**Role-based access:** Department and clearance level integration  
**Academic calendar:** Time-aware content filtering  
**Audit logging:** Track all searches for compliance  
**Backup strategy:** Regular vector data backups

---

## Monitoring and Maintenance

### Query Health Metrics

```sql
-- Track query performance trends
SELECT 
  date_trunc('hour', query_start) as hour,
  COUNT(*) as query_count,
  AVG(total_time) as avg_time_ms,
  MAX(total_time) as max_time_ms
FROM query_log 
WHERE query_type = 'hybrid_vector'
  AND query_start > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

---

## Advanced Topics Preview

### Beyond Basic Hybrid Search

**Multi-vector queries:** Different embeddings for title vs content  
**Semantic clustering:** Group similar documents automatically  
**Anomaly detection:** Identify unusual patterns in embeddings  
**Cross-lingual search:** Query in English, find results in other languages  
**Temporal embeddings:** Track how document meaning changes over time

---

## Lab Preview

### What We'll Build Together

**45-minute hands-on lab:**
1. **Complex metadata schemas** for Edinburgh documents
2. **Multi-criteria hybrid queries** with realistic use cases  
3. **Performance optimization** using proper indexing
4. **Error handling** for production robustness
5. **Advanced filtering** with campus, role, and time constraints

**Outcome:** Production-ready hybrid search system

---

## Success Criteria

### After This Section

**You can confidently:**
- Design hybrid queries combining vectors + metadata + relational data
- Optimize complex queries for production performance  
- Handle edge cases and missing data gracefully
- Implement role-based and time-aware filtering
- Monitor and maintain query performance over time

**You have:** Working examples of Edinburgh's most complex search scenarios

---

## Ready for Advanced Querying?

### Key Concepts Mastered

🎯 **Hybrid search patterns**  
🎯 **JSONB metadata optimization**  
🎯 **Performance monitoring**  
🎯 **Edinburgh-specific requirements**  
🎯 **Production-ready error handling**

**Next:** 45 minutes of hands-on implementation!

---

## Questions & Discussion

**Before we start coding:**

- Which Edinburgh use cases resonate most with your work?
- What metadata patterns do you see in your current systems?  
- Any concerns about query complexity or performance?
- How would you adapt these patterns for your specific departments?

**Let's tackle advanced vector queries together! 🚀**