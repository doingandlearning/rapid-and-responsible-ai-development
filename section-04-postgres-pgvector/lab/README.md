# Lab 4: PostgreSQL + pgvector Setup and Optimization

## Learning Objectives
By the end of this lab, you will:
- ✅ Set up a production-ready vector database with PostgreSQL + pgvector
- ✅ Create optimized table schemas for Edinburgh's knowledge base
- ✅ Load real document embeddings efficiently
- ✅ Test and optimize vector search performance
- ✅ Understand scaling considerations for institutional use

## Time Estimate: 35 minutes

---

## Pre-Lab Setup

**Ensure your environment is ready:**
1. Services running: `cd environment && docker compose up -d`
2. Virtual environment activated: `source .venv/bin/activate`
3. Create lab file: `lab4_postgres_vectors.py`

**🆘 Need help?** Complete solutions are in `../solution/` folder!

---

## Part 1: PostgreSQL + pgvector Verification (5 minutes)

### Step 1: Verify Extensions and Capabilities

Let's ensure our PostgreSQL setup is vector-ready:

```python
import psycopg
import requests
import json
import time
import random

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

def verify_pgvector_setup():
    """Verify PostgreSQL + pgvector is ready for Edinburgh."""
    print("🔍 VERIFYING POSTGRESQL + PGVECTOR SETUP")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check PostgreSQL version
                cur.execute("SELECT version();")
                pg_version = cur.fetchone()[0]
                print(f"✅ PostgreSQL: {pg_version.split(',')[0]}")
                
                # Check pgvector extension
                cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                vector_ext = cur.fetchone()
                if vector_ext:
                    print(f"✅ pgvector extension: Installed")
                else:
                    print("❌ pgvector extension: Not found!")
                    return False
                
                # Test vector operations
                cur.execute("SELECT '[1,2,3]'::vector <=> '[1,2,4]'::vector as distance;")
                distance = cur.fetchone()[0]
                print(f"✅ Vector operations: Working (test distance: {distance:.3f})")
                
                # Check available vector operators
                cur.execute("""
                    SELECT oprname, oprleft::regtype, oprright::regtype
                    FROM pg_operator 
                    WHERE oprname IN ('<->', '<#>', '<=>')
                    ORDER BY oprname;
                """)
                operators = cur.fetchall()
                print(f"✅ Vector operators: {len(operators)} available")
                for op in operators:
                    print(f"   {op[0]}: {op[1]} {op[0]} {op[2]}")
                
    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        return False
    
    print("\n🎉 PostgreSQL + pgvector is ready for Edinburgh!")
    return True

# Verify setup first
if not verify_pgvector_setup():
    print("⚠️ Fix setup issues before continuing. Check solution/ folder if needed.")
    exit(1)
```

**Run this verification:**
```bash
python lab4_postgres_vectors.py
```

---

## Part 2: Edinburgh Knowledge Base Schema (8 minutes)

### Step 2: Design Production-Ready Table Schema

Create a schema optimized for Edinburgh's knowledge base:

```python
def create_edinburgh_schema():
    """Create optimized schema for Edinburgh knowledge base."""
    print("\n📊 CREATING EDINBURGH KNOWLEDGE BASE SCHEMA")
    print("=" * 50)
    
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Drop existing table if needed
            cur.execute("DROP TABLE IF EXISTS edinburgh_docs CASCADE;")
            
            # Create optimized table schema
            cur.execute("""
                CREATE TABLE edinburgh_docs (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    subcategory VARCHAR(100),
                    last_updated DATE DEFAULT CURRENT_DATE,
                    source_url VARCHAR(1000),
                    content_hash VARCHAR(64), -- for deduplication
                    word_count INTEGER,
                    
                    -- Vector embeddings
                    title_embedding vector(1024),
                    content_embedding vector(1024),
                    
                    -- Search optimization
                    content_tsvector tsvector, -- for hybrid text+vector search
                    
                    -- Metadata for quality control
                    embedding_model VARCHAR(50) DEFAULT 'bge-m3',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("✅ Table 'edinburgh_docs' created with optimized schema")
            
            # Create indexes for performance
            print("📊 Creating performance indexes...")
            
            # Text search indexes
            cur.execute("CREATE INDEX idx_edinburgh_title ON edinburgh_docs (title);")
            cur.execute("CREATE INDEX idx_edinburgh_category ON edinburgh_docs (category, subcategory);")
            cur.execute("CREATE INDEX idx_edinburgh_updated ON edinburgh_docs (last_updated);")
            cur.execute("CREATE INDEX idx_edinburgh_tsvector ON edinburgh_docs USING gin(content_tsvector);")
            
            print("✅ Text search indexes created")
            
            # We'll create vector indexes after loading data
            print("⏳ Vector indexes will be created after data loading")
            
            # Create trigger for automatic tsvector updates
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_tsvector() RETURNS trigger AS $$
                BEGIN
                    NEW.content_tsvector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, ''));
                    NEW.updated_at := CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            cur.execute("""
                CREATE TRIGGER tsvector_update_trigger
                BEFORE INSERT OR UPDATE ON edinburgh_docs
                FOR EACH ROW EXECUTE FUNCTION update_tsvector();
            """)
            
            print("✅ Automatic text search vector updates configured")
            
            conn.commit()
    
    print("\n🎉 Edinburgh schema ready for production!")

# Create the schema
create_edinburgh_schema()
```

### Step 3: Load Sample Edinburgh Documents

```python
def load_edinburgh_documents():
    """Load realistic Edinburgh documents with embeddings."""
    print("\n📚 LOADING EDINBURGH DOCUMENTS")
    print("=" * 50)
    
    # Expanded realistic Edinburgh document set
    edinburgh_docs = [
        {
            "title": "Password Reset Self-Service Guide",
            "content": "Edinburgh University provides self-service password reset through the MyEd portal. Access https://www.ed.ac.uk/is/password-reset using any web browser. Enter your university username (not email address). Check your university email for the reset link within 5 minutes. Links expire after 24 hours for security. New passwords must be at least 8 characters with uppercase, lowercase, numbers, and special characters. Contact IT Service Desk on 0131 650 4500 if self-service fails.",
            "category": "IT Support",
            "subcategory": "Authentication",
            "source_url": "https://www.ed.ac.uk/is/password-reset"
        },
        {
            "title": "EdUni WiFi Connection Instructions",
            "content": "Connect to Edinburgh University WiFi networks for internet access on campus. Primary network: EdUni (for registered devices). Guest network: EdUni-Guest (24-hour access). International visitors use Eduroam with home institution credentials. To register devices: 1) Connect to EdUni-Setup network 2) Open web browser 3) Login with university credentials 4) Register device MAC address. WiFi speed: up to 100Mbps. Coverage: All university buildings, student accommodations, and outdoor areas.",
            "category": "IT Support", 
            "subcategory": "Networking",
            "source_url": "https://www.ed.ac.uk/is/wifi"
        },
        {
            "title": "Library Study Room Booking System",
            "content": "Book individual and group study rooms through the MyEd student portal. Available locations: Main Library (floors 1-6), George Square Library (levels 2-7), Informatics Library (ground floor), Medical Library (basement level). Booking window: Up to 7 days in advance. Maximum duration: 4 hours per booking. Cancellation: At least 1 hour before start time. Accessibility: Accessible rooms available on request. Peak times (9am-5pm) have higher demand. Late cancellation fees apply for no-shows.",
            "category": "Library Services",
            "subcategory": "Facilities",
            "source_url": "https://www.ed.ac.uk/library/using-the-library/study-spaces"
        },
        {
            "title": "Student Email Setup and Troubleshooting", 
            "content": "Edinburgh student email accounts are hosted on Microsoft Office 365. Email format: s[student-number]@ed.ac.uk. IMAP settings: Server outlook.office365.com, Port 993, SSL required. SMTP settings: Server smtp.office365.com, Port 587, TLS required. Authentication: Use full email address and university password. Storage quota: 50GB per account. Mobile setup: Download Microsoft Outlook app, enter email address, authenticate with university credentials. Common issues: Check spam folder, verify password, ensure 2FA is configured.",
            "category": "IT Support",
            "subcategory": "Email", 
            "source_url": "https://www.ed.ac.uk/is/email"
        },
        {
            "title": "VPN Access for Remote Resources",
            "content": "Edinburgh VPN provides secure access to university resources from off-campus locations. Required for: Library database access, internal file shares, research data systems, administrative systems. VPN client: FortiClient (free download from IT Services). Connection details: Server vpn.ed.ac.uk, Port 443. Authentication: University username and password. Two-factor authentication required for staff accounts. Connection limit: 3 simultaneous sessions. Available 24/7 with maintenance windows announced in advance.",
            "category": "IT Support",
            "subcategory": "Remote Access",
            "source_url": "https://www.ed.ac.uk/is/vpn"
        },
        {
            "title": "Student Accommodation Wi-Fi Setup",
            "content": "Student accommodation provides high-speed internet access in all rooms. Network name: EdResNet. Connection is automatic in most accommodations. Manual setup: 1) Connect ethernet cable to wall port 2) Open web browser 3) Register device with university credentials. Wireless available in common areas using EdUni network. Speed: up to 1Gbps in newer buildings, 100Mbps in older buildings. Support: Contact accommodation office first, then IT Service Desk for technical issues.",
            "category": "Accommodation",
            "subcategory": "IT Services",
            "source_url": "https://www.ed.ac.uk/accommodation/current-residents/it-services"
        },
        {
            "title": "Academic Referencing and Citation Support",
            "content": "Edinburgh Library provides comprehensive referencing support for all academic work. Referencing styles: Harvard, APA, MLA, Chicago, Vancouver available. EndNote software free for students and staff through IT Services. Citation management: Download EndNote from software portal, attend library training sessions (weekly), use online tutorials. Plagiarism prevention: Use Turnitin similarity checker through Learn VLE. Support available: Drop-in sessions Monday-Friday 10am-4pm, online guides for all citation styles, email support library.skills@ed.ac.uk.",
            "category": "Library Services", 
            "subcategory": "Academic Support",
            "source_url": "https://www.ed.ac.uk/library/help/referencing"
        }
    ]
    
    def get_embedding(text):
        """Get embedding from Ollama with retry logic."""
        url = "http://localhost:11434/api/embed"
        payload = {"model": "bge-m3", "input": text}
        
        for attempt in range(3):  # Retry logic
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                return result.get("embeddings", [])[0]
            except Exception as e:
                if attempt == 2:  # Last attempt
                    print(f"❌ Embedding failed after 3 attempts: {e}")
                    return None
                time.sleep(1)  # Wait before retry
        
        return None
    
    # Load documents with embeddings
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            loaded_count = 0
            
            for i, doc in enumerate(edinburgh_docs, 1):
                print(f"🔄 Processing document {i}/{len(edinburgh_docs)}: {doc['title']}")
                
                # Generate embeddings
                title_embedding = get_embedding(doc['title'])
                content_embedding = get_embedding(doc['content'])
                
                if title_embedding and content_embedding:
                    # Calculate metadata
                    word_count = len(doc['content'].split())
                    content_hash = str(hash(doc['content']))  # Simple hash
                    
                    # Insert document
                    cur.execute("""
                        INSERT INTO edinburgh_docs 
                        (title, content, category, subcategory, source_url, 
                         word_count, content_hash, title_embedding, content_embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        doc['title'],
                        doc['content'],
                        doc['category'], 
                        doc['subcategory'],
                        doc['source_url'],
                        word_count,
                        content_hash,
                        title_embedding,
                        content_embedding
                    ))
                    
                    loaded_count += 1
                    print(f"✅ Loaded: {doc['title']}")
                else:
                    print(f"❌ Skipped: {doc['title']} (embedding failed)")
                
                # Brief delay to be nice to Ollama
                time.sleep(0.5)
            
            conn.commit()
            print(f"\n✅ Successfully loaded {loaded_count}/{len(edinburgh_docs)} documents")
    
    return loaded_count

# Load the documents
doc_count = load_edinburgh_documents()
```

**Run to create schema and load data:**
```bash
python lab4_postgres_vectors.py
```

---

## Part 3: Vector Search Performance Testing (12 minutes)

### Step 4: Test Search Performance Without Indexes

```python
def test_search_performance(with_index=False):
    """Test vector search performance with and without indexes."""
    print(f"\n⚡ TESTING SEARCH PERFORMANCE {'WITH' if with_index else 'WITHOUT'} INDEXES")
    print("=" * 60)
    
    # Test queries representing common Edinburgh student questions
    test_queries = [
        "How do I reset my university password?",
        "I can't connect to WiFi on campus",
        "How can I book a study room in the library?",
        "My student email isn't working",
        "I need VPN access for off-campus research",
        "How do I set up internet in my accommodation?",
        "Where can I get help with academic citations?"
    ]
    
    performance_results = []
    
    def get_embedding(text):
        url = "http://localhost:11434/api/embed"
        payload = {"model": "bge-m3", "input": text}
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("embeddings", [])[0]
        except:
            return None
    
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            for query in test_queries:
                print(f"\n🔍 Testing: '{query}'")
                
                # Generate query embedding
                embedding_start = time.time()
                query_embedding = get_embedding(query)
                embedding_time = time.time() - embedding_start
                
                if not query_embedding:
                    print("❌ Embedding generation failed")
                    continue
                
                # Perform vector search
                search_start = time.time()
                cur.execute("""
                    SELECT 
                        title,
                        category,
                        subcategory,
                        1 - (content_embedding <=> %s::vector) as similarity,
                        word_count
                    FROM edinburgh_docs
                    ORDER BY content_embedding <=> %s::vector
                    LIMIT 3;
                """, (query_embedding, query_embedding))
                
                results = cur.fetchall()
                search_time = time.time() - search_start
                total_time = embedding_time + search_time
                
                print(f"   ⏱️  Embedding: {embedding_time:.3f}s | Search: {search_time:.3f}s | Total: {total_time:.3f}s")
                
                # Show top result
                if results:
                    top_result = results[0]
                    print(f"   🎯 Best match: '{top_result[0]}' (similarity: {top_result[3]:.3f})")
                    
                    if top_result[3] > 0.7:
                        print("   ✅ High relevance match")
                    elif top_result[3] > 0.5:
                        print("   ⚠️  Medium relevance match")
                    else:
                        print("   ❌ Low relevance match")
                
                performance_results.append({
                    'query': query,
                    'embedding_time': embedding_time,
                    'search_time': search_time,
                    'total_time': total_time,
                    'top_similarity': results[0][3] if results else 0
                })
                
                time.sleep(0.5)  # Brief pause between queries
    
    # Performance summary
    if performance_results:
        avg_embedding = sum(r['embedding_time'] for r in performance_results) / len(performance_results)
        avg_search = sum(r['search_time'] for r in performance_results) / len(performance_results)
        avg_total = sum(r['total_time'] for r in performance_results) / len(performance_results)
        avg_similarity = sum(r['top_similarity'] for r in performance_results) / len(performance_results)
        
        print(f"\n📊 PERFORMANCE SUMMARY {'WITH' if with_index else 'WITHOUT'} INDEXES")
        print(f"   Average embedding time: {avg_embedding:.3f}s")
        print(f"   Average search time: {avg_search:.3f}s")
        print(f"   Average total time: {avg_total:.3f}s")
        print(f"   Average similarity score: {avg_similarity:.3f}")
        print(f"   Edinburgh SLA target: <2.0s")
        
        if avg_total < 2.0:
            print("   ✅ Performance target MET")
        else:
            print("   ❌ Performance target MISSED")
            
        return performance_results
    
    return []

# Test performance without indexes first
print("📈 BASELINE PERFORMANCE TEST (No Vector Indexes)")
baseline_results = test_search_performance(with_index=False)
```

### Step 5: Create Vector Indexes and Optimize

```python
def create_vector_indexes():
    """Create optimized vector indexes for production use."""
    print("\n🚀 CREATING VECTOR INDEXES FOR PERFORMANCE")
    print("=" * 50)
    
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Create HNSW indexes for vector similarity search
            print("📊 Creating content embedding index (this may take a moment)...")
            
            cur.execute("""
                CREATE INDEX idx_content_embedding_hnsw 
                ON edinburgh_docs 
                USING hnsw (content_embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            print("✅ Content embedding HNSW index created")
            
            print("📊 Creating title embedding index...")
            cur.execute("""
                CREATE INDEX idx_title_embedding_hnsw
                ON edinburgh_docs
                USING hnsw (title_embedding vector_cosine_ops) 
                WITH (m = 16, ef_construction = 64);
            """)
            print("✅ Title embedding HNSW index created")
            
            # Analyze table for query optimization
            cur.execute("ANALYZE edinburgh_docs;")
            print("✅ Table statistics updated for query optimization")
            
            conn.commit()
    
    print("\n🎉 Vector indexes created! Performance should be much faster now.")

# Create the indexes
create_vector_indexes()

# Test performance with indexes
print("\n" + "="*60)
print("📈 OPTIMIZED PERFORMANCE TEST (With Vector Indexes)")
optimized_results = test_search_performance(with_index=True)
```

### Step 6: Performance Comparison Analysis

```python
def compare_performance(baseline, optimized):
    """Compare performance before and after optimization."""
    print("\n📊 PERFORMANCE COMPARISON ANALYSIS")
    print("=" * 50)
    
    if not baseline or not optimized:
        print("❌ Missing performance data for comparison")
        return
    
    # Calculate improvements
    baseline_avg_search = sum(r['search_time'] for r in baseline) / len(baseline)
    optimized_avg_search = sum(r['search_time'] for r in optimized) / len(optimized)
    
    baseline_avg_total = sum(r['total_time'] for r in baseline) / len(baseline)
    optimized_avg_total = sum(r['total_time'] for r in optimized) / len(optimized)
    
    search_improvement = ((baseline_avg_search - optimized_avg_search) / baseline_avg_search) * 100
    total_improvement = ((baseline_avg_total - optimized_avg_total) / baseline_avg_total) * 100
    
    print(f"🏃 SEARCH TIME IMPROVEMENT:")
    print(f"   Before indexes: {baseline_avg_search:.3f}s")
    print(f"   After indexes:  {optimized_avg_search:.3f}s")
    print(f"   Improvement:    {search_improvement:.1f}% faster")
    
    print(f"\n🏁 TOTAL TIME IMPROVEMENT:")
    print(f"   Before indexes: {baseline_avg_total:.3f}s") 
    print(f"   After indexes:  {optimized_avg_total:.3f}s")
    print(f"   Improvement:    {total_improvement:.1f}% faster")
    
    # Edinburgh SLA analysis
    baseline_sla_pass = sum(1 for r in baseline if r['total_time'] < 2.0)
    optimized_sla_pass = sum(1 for r in optimized if r['total_time'] < 2.0)
    
    print(f"\n🎯 EDINBURGH SLA COMPLIANCE (<2.0s):")
    print(f"   Before indexes: {baseline_sla_pass}/{len(baseline)} queries ({baseline_sla_pass/len(baseline)*100:.1f}%)")
    print(f"   After indexes:  {optimized_sla_pass}/{len(optimized)} queries ({optimized_sla_pass/len(optimized)*100:.1f}%)")
    
    if optimized_sla_pass == len(optimized):
        print("   ✅ All queries now meet Edinburgh's performance requirements!")
    else:
        print("   ⚠️  Some queries still exceed SLA - consider further optimization")

# Compare the results
compare_performance(baseline_results, optimized_results)
```

**Run the complete performance testing:**
```bash
python lab4_postgres_vectors.py
```

---

## Part 4: Scaling Analysis for Edinburgh (10 minutes)

### Step 7: Database Size and Resource Analysis

```python
def analyze_database_scaling():
    """Analyze storage requirements and scaling characteristics."""
    print("\n📏 DATABASE SCALING ANALYSIS FOR EDINBURGH")
    print("=" * 50)
    
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Current database size analysis
            cur.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE tablename = 'edinburgh_docs'
                AND attname IN ('category', 'subcategory');
            """)
            stats = cur.fetchall()
            
            # Table size information
            cur.execute("""
                SELECT 
                    pg_size_pretty(pg_total_relation_size('edinburgh_docs')) as total_size,
                    pg_size_pretty(pg_relation_size('edinburgh_docs')) as table_size,
                    pg_size_pretty(pg_total_relation_size('edinburgh_docs') - pg_relation_size('edinburgh_docs')) as index_size;
            """)
            sizes = cur.fetchone()
            
            # Row count and vector info
            cur.execute("""
                SELECT 
                    COUNT(*) as total_docs,
                    AVG(word_count) as avg_word_count,
                    MAX(word_count) as max_word_count,
                    MIN(word_count) as min_word_count
                FROM edinburgh_docs;
            """)
            doc_stats = cur.fetchone()
            
            # Index usage analysis  
            cur.execute("""
                SELECT 
                    indexrelname,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE relname = 'edinburgh_docs'
                AND indexrelname LIKE '%hnsw%';
            """)
            index_usage = cur.fetchall()
    
    print(f"📊 CURRENT DATABASE STATE:")
    print(f"   Total documents: {doc_stats[0]:,}")
    print(f"   Average document length: {doc_stats[1]:.0f} words")
    print(f"   Table size: {sizes[1]}")
    print(f"   Index size: {sizes[2]}")  
    print(f"   Total size: {sizes[0]}")
    
    # Scaling projections for Edinburgh
    current_docs = doc_stats[0]
    scenarios = [
        ("Current (Test Data)", current_docs),
        ("Phase 1 (Core IT Docs)", 500),
        ("Phase 2 (All Student Services)", 2000), 
        ("Phase 3 (Academic Policies)", 5000),
        ("Full Edinburgh Scale", 50000)
    ]
    
    print(f"\n📈 SCALING PROJECTIONS:")
    print(f"{'Scenario':<25} {'Documents':>10} {'Est. Size':>12} {'RAM Needed':>12}")
    print("-" * 65)
    
    for scenario_name, doc_count in scenarios:
        # Rough scaling estimates
        estimated_size_mb = (doc_count / current_docs) * 50 if current_docs > 0 else 50  # Rough estimate
        ram_needed_mb = estimated_size_mb * 2  # Rule of thumb: 2x for indexes + working memory
        
        print(f"{scenario_name:<25} {doc_count:>10,} {estimated_size_mb:>9.0f} MB {ram_needed_mb:>9.0f} MB")
    
    print(f"\n💡 SCALING RECOMMENDATIONS:")
    print(f"   • Current test data is suitable for development")
    print(f"   • 2GB RAM minimum for Phase 2 (2,000 documents)")
    print(f"   • 8GB+ RAM recommended for Phase 3 (5,000 documents)")  
    print(f"   • 16GB+ RAM required for full Edinburgh scale (50,000 documents)")
    print(f"   • Consider read replicas for >100 concurrent users")
    print(f"   • Monitor query performance as document count grows")

# Run scaling analysis
analyze_database_scaling()
```

---

## Success Criteria ✅

**You've completed this lab when:**
- [ ] PostgreSQL + pgvector is verified and working
- [ ] Edinburgh knowledge base schema is created and optimized
- [ ] Sample documents loaded with embeddings
- [ ] Vector search performance tested and optimized
- [ ] HNSW indexes created for fast similarity search
- [ ] Performance improvements measured and documented
- [ ] Scaling requirements understood for Edinburgh's needs

---

## Reflection & Next Steps

### Discussion Questions

**With your partner, discuss:**

1. **Performance Impact**: How much did the HNSW indexes improve search speed? Was the trade-off worth it?

2. **Edinburgh Scale**: Based on the scaling analysis, what hardware would you recommend for Edinburgh's full deployment?

3. **Index Configuration**: We used `m=16, ef_construction=64` for HNSW. When might you tune these parameters?

4. **Hybrid Approach**: Our schema supports both vector and text search. How could Edinburgh benefit from combining both approaches?

### Key Takeaways

- **PostgreSQL + pgvector**: Familiar database with vector superpowers
- **Index Importance**: Vector indexes are crucial for performance at scale
- **Trade-offs**: Index creation time vs query speed
- **Resource Planning**: Memory requirements grow with document count and index size

### What's Next

**In Section 5, we'll build on this foundation:**
- Generate and store embeddings for larger document sets
- Implement batch processing for efficiency
- Add document chunking strategies
- Connect to our embedding generation pipeline

---

## Troubleshooting

### Common Issues

**Vector index creation fails:**
```sql
-- Check if table has enough data
SELECT COUNT(*) FROM edinburgh_docs;
-- Need at least a few rows for HNSW index creation
```

**Slow performance even with indexes:**
```sql
-- Force index usage for testing
SET enable_seqscan = off;
-- Check if indexes are being used
EXPLAIN (ANALYZE, BUFFERS) SELECT ... FROM edinburgh_docs ORDER BY content_embedding <=> '[...]'::vector LIMIT 5;
```

**Memory issues:**
```bash
# Check PostgreSQL memory settings
docker exec pgvector-db psql -U postgres -d pgvector -c "SHOW shared_buffers;"
# May need to tune PostgreSQL memory configuration for large indexes
```

### Performance Optimization Tips

**For better search quality:**
- Increase `ef_construction` parameter (slower build, better quality)
- Use larger `m` parameter (more memory, better connectivity)

**For faster build times:**
- Decrease `ef_construction` parameter  
- Build indexes during low-usage periods
- Consider parallel index builds for very large datasets

**For memory optimization:**
- Monitor index size vs available RAM
- Consider partial indexes for frequently-accessed categories
- Use connection pooling to limit concurrent memory usage

Great work! You now have a production-ready vector database foundation for Edinburgh's AI systems. The solution files provide complete working examples if you need reference implementations.