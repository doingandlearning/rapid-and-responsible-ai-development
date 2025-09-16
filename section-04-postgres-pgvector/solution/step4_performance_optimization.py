#!/usr/bin/env python3
"""
Step 4: Performance Optimization and Vector Search Testing
Complete solution for creating indexes and testing search performance.
"""

import psycopg
import requests
import time
import sys
from statistics import mean, stdev

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"

def get_embedding(text, max_retries=3):
    """Get embedding from Ollama with retry logic."""
    for attempt in range(max_retries):
        try:
            payload = {
                "model": EMBEDDING_MODEL,
                "input": text
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get("embeddings", [])
            
            if embedding and len(embedding[0]) == 1024:
                return embedding[0]
            else:
                continue
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                print(f"⚠️  Embedding failed: {e}")
    
    return None

def test_search_performance(with_indexes=False):
    """Test vector search performance with realistic Edinburgh queries."""
    print(f"\n⚡ TESTING SEARCH PERFORMANCE {'WITH' if with_indexes else 'WITHOUT'} VECTOR INDEXES")
    print("=" * 70)
    
    # Realistic Edinburgh student/staff queries
    test_queries = [
        "How do I reset my university password?",
        "I can't connect to WiFi on campus", 
        "How can I book a study room in the library?",
        "My student email isn't working properly",
        "I need VPN access for off-campus research",
        "How do I set up internet in my student accommodation?",
        "Where can I get help with academic citations?",
        "How do I access university software downloads?",
        "What's the IT Service Desk phone number?",
        "How do I use MyEd student portal?"
    ]
    
    performance_results = []
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check if we have data
                cur.execute("SELECT COUNT(*) FROM edinburgh_docs;")
                doc_count = cur.fetchone()[0]
                
                if doc_count == 0:
                    print("❌ No documents found! Run step3_data_loading.py first")
                    return []
                
                print(f"📊 Testing against {doc_count} documents")
                
                for i, query in enumerate(test_queries, 1):
                    print(f"\n🔍 Query {i}/{len(test_queries)}: '{query}'")
                    
                    # Generate query embedding
                    embedding_start = time.time()
                    query_embedding = get_embedding(query)
                    embedding_time = time.time() - embedding_start
                    
                    if not query_embedding:
                        print("   ❌ Embedding generation failed")
                        continue
                    
                    # Perform vector similarity search
                    search_start = time.time()
                    cur.execute("""
                        SELECT 
                            title,
                            category,
                            subcategory,
                            1 - (content_embedding <=> %s::vector) as similarity_score,
                            word_count,
                            source_url
                        FROM edinburgh_docs
                        ORDER BY content_embedding <=> %s::vector
                        LIMIT 5;
                    """, (query_embedding, query_embedding))
                    
                    results = cur.fetchall()
                    search_time = time.time() - search_start
                    total_time = embedding_time + search_time
                    
                    print(f"   ⏱️  Embedding: {embedding_time:.3f}s | Search: {search_time:.3f}s | Total: {total_time:.3f}s")
                    
                    # Show top results
                    if results:
                        print(f"   🎯 Top matches:")
                        for j, (title, category, subcategory, similarity, words, url) in enumerate(results[:3], 1):
                            relevance = "🟢 High" if similarity > 0.7 else "🟡 Medium" if similarity > 0.5 else "🔴 Low"
                            print(f"      {j}. '{title}' ({category}) - {relevance} ({similarity:.3f})")
                        
                        # Performance assessment
                        top_similarity = results[0][3]
                        if total_time <= 1.0:
                            perf_status = "✅ Excellent"
                        elif total_time <= 2.0:
                            perf_status = "✅ Good"
                        elif total_time <= 3.0:
                            perf_status = "⚠️  Acceptable"
                        else:
                            perf_status = "❌ Slow"
                        
                        print(f"   📈 Performance: {perf_status} | Best match: {top_similarity:.3f}")
                        
                        performance_results.append({
                            'query': query,
                            'embedding_time': embedding_time,
                            'search_time': search_time,
                            'total_time': total_time,
                            'top_similarity': top_similarity,
                            'results_count': len(results)
                        })
                    
                    # Brief pause between queries
                    time.sleep(0.3)
                
    except Exception as e:
        print(f"❌ Performance testing failed: {e}")
        return []
    
    # Performance summary
    if performance_results:
        print(f"\n📊 PERFORMANCE SUMMARY {'WITH' if with_indexes else 'WITHOUT'} INDEXES")
        print("=" * 50)
        
        avg_embedding = mean(r['embedding_time'] for r in performance_results)
        avg_search = mean(r['search_time'] for r in performance_results)
        avg_total = mean(r['total_time'] for r in performance_results)
        avg_similarity = mean(r['top_similarity'] for r in performance_results)
        
        max_search = max(r['search_time'] for r in performance_results)
        min_search = min(r['search_time'] for r in performance_results)
        
        print(f"   📈 Average times:")
        print(f"      Embedding generation: {avg_embedding:.3f}s")
        print(f"      Vector search: {avg_search:.3f}s (min: {min_search:.3f}s, max: {max_search:.3f}s)")
        print(f"      Total per query: {avg_total:.3f}s")
        
        print(f"   🎯 Search quality:")
        print(f"      Average similarity: {avg_similarity:.3f}")
        print(f"      Queries processed: {len(performance_results)}")
        
        # Edinburgh SLA compliance (target: <2.0s total time)
        sla_compliant = sum(1 for r in performance_results if r['total_time'] < 2.0)
        sla_percentage = (sla_compliant / len(performance_results)) * 100
        
        print(f"   🏫 Edinburgh SLA compliance:")
        print(f"      Target: <2.0s per query")
        print(f"      Compliant: {sla_compliant}/{len(performance_results)} ({sla_percentage:.1f}%)")
        
        if sla_percentage >= 95:
            print(f"      ✅ EXCELLENT - Exceeds Edinburgh requirements")
        elif sla_percentage >= 85:
            print(f"      ✅ GOOD - Meets Edinburgh requirements")
        elif sla_percentage >= 70:
            print(f"      ⚠️  ACCEPTABLE - Consider optimization")
        else:
            print(f"      ❌ POOR - Optimization required")
    
    return performance_results

def create_vector_indexes():
    """Create optimized HNSW vector indexes for production performance."""
    print("\n🚀 CREATING VECTOR INDEXES FOR PRODUCTION PERFORMANCE")
    print("=" * 60)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check if indexes already exist
                cur.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = 'edinburgh_docs' 
                    AND indexname LIKE '%hnsw%';
                """)
                existing_indexes = cur.fetchall()
                
                if existing_indexes:
                    print("⚠️  Vector indexes already exist:")
                    for (index_name,) in existing_indexes:
                        print(f"   • {index_name}")
                    
                    # Drop existing vector indexes for recreation
                    print("🗑️  Dropping existing vector indexes for recreation...")
                    for (index_name,) in existing_indexes:
                        cur.execute(f"DROP INDEX IF EXISTS {index_name};")
                        print(f"   ✅ Dropped {index_name}")
                
                print("\n📊 Creating optimized HNSW indexes...")
                
                # Content embedding index (primary search)
                print("   🔧 Creating content embedding index...")
                index_start = time.time()
                cur.execute("""
                    CREATE INDEX idx_content_embedding_hnsw 
                    ON edinburgh_docs 
                    USING hnsw (content_embedding vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64);
                """)
                content_index_time = time.time() - index_start
                print(f"   ✅ Content embedding index created ({content_index_time:.1f}s)")
                
                # Title embedding index (for title-based searches)
                print("   🔧 Creating title embedding index...")
                index_start = time.time()
                cur.execute("""
                    CREATE INDEX idx_title_embedding_hnsw
                    ON edinburgh_docs
                    USING hnsw (title_embedding vector_cosine_ops) 
                    WITH (m = 16, ef_construction = 64);
                """)
                title_index_time = time.time() - index_start
                print(f"   ✅ Title embedding index created ({title_index_time:.1f}s)")
                
                # Update table statistics for query planner
                print("   📊 Updating table statistics...")
                cur.execute("ANALYZE edinburgh_docs;")
                print("   ✅ Table statistics updated")
                
                # Show index details
                cur.execute("""
                    SELECT 
                        schemaname, 
                        tablename, 
                        indexname,
                        pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
                    FROM pg_indexes 
                    WHERE tablename = 'edinburgh_docs' 
                    AND indexname LIKE '%hnsw%'
                    ORDER BY indexname;
                """)
                index_info = cur.fetchall()
                
                print(f"\n📋 Created indexes:")
                total_index_time = content_index_time + title_index_time
                for schema, table, index_name, size in index_info:
                    print(f"   • {index_name}: {size}")
                
                print(f"\n✅ Vector indexes created successfully!")
                print(f"   Total creation time: {total_index_time:.1f}s")
                print(f"   Index parameters: m=16, ef_construction=64")
                print(f"   Distance function: Cosine similarity")
                
                conn.commit()
                
    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        return False
    
    return True

def analyze_index_performance():
    """Analyze how indexes are performing."""
    print("\n📈 ANALYZING INDEX PERFORMANCE")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Index usage statistics
                cur.execute("""
                    SELECT 
                        schemaname,
                        relname as tablename,
                        indexrelname as indexname,
                        idx_scan as scans,
                        idx_tup_read as tuples_read,
                        idx_tup_fetch as tuples_fetched
                    FROM pg_stat_user_indexes 
                    WHERE relname = 'edinburgh_docs'
                    AND indexrelname LIKE '%hnsw%'
                    ORDER BY idx_scan DESC;
                """)
                index_stats = cur.fetchall()
                
                print("📊 Index usage statistics:")
                if index_stats:
                    for schema, table, index_name, scans, reads, fetches in index_stats:
                        print(f"   {index_name}:")
                        print(f"      Scans: {scans}, Tuples read: {reads}, Tuples fetched: {fetches}")
                else:
                    print("   No usage statistics available yet (indexes just created)")
                
                # Table and index sizes
                cur.execute("""
                    SELECT 
                        pg_size_pretty(pg_relation_size('edinburgh_docs')) as table_size,
                        pg_size_pretty(pg_total_relation_size('edinburgh_docs') - pg_relation_size('edinburgh_docs')) as index_size,
                        pg_size_pretty(pg_total_relation_size('edinburgh_docs')) as total_size;
                """)
                sizes = cur.fetchone()
                table_size, index_size, total_size = sizes
                
                print(f"\n💾 Storage usage:")
                print(f"   Table size: {table_size}")
                print(f"   Index size: {index_size}")
                print(f"   Total size: {total_size}")
                
    except Exception as e:
        print(f"⚠️  Index analysis failed: {e}")

def compare_performance_results(baseline, optimized):
    """Compare performance before and after indexing."""
    if not baseline or not optimized:
        print("❌ Cannot compare - missing performance data")
        return
    
    print("\n📊 PERFORMANCE COMPARISON ANALYSIS")
    print("=" * 60)
    
    # Calculate improvements
    baseline_avg_search = mean(r['search_time'] for r in baseline)
    optimized_avg_search = mean(r['search_time'] for r in optimized)
    
    baseline_avg_total = mean(r['total_time'] for r in baseline)
    optimized_avg_total = mean(r['total_time'] for r in optimized)
    
    baseline_avg_similarity = mean(r['top_similarity'] for r in baseline)
    optimized_avg_similarity = mean(r['top_similarity'] for r in optimized)
    
    search_improvement = ((baseline_avg_search - optimized_avg_search) / baseline_avg_search) * 100
    total_improvement = ((baseline_avg_total - optimized_avg_total) / baseline_avg_total) * 100
    
    print(f"🏃 SEARCH PERFORMANCE:")
    print(f"   Before indexes: {baseline_avg_search:.3f}s average")
    print(f"   After indexes:  {optimized_avg_search:.3f}s average")
    print(f"   Improvement:    {search_improvement:.1f}% faster")
    
    print(f"\n🏁 TOTAL PERFORMANCE:")
    print(f"   Before indexes: {baseline_avg_total:.3f}s average") 
    print(f"   After indexes:  {optimized_avg_total:.3f}s average")
    print(f"   Improvement:    {total_improvement:.1f}% faster")
    
    print(f"\n🎯 SEARCH QUALITY:")
    print(f"   Before indexes: {baseline_avg_similarity:.3f} average similarity")
    print(f"   After indexes:  {optimized_avg_similarity:.3f} average similarity")
    
    # SLA compliance comparison
    baseline_sla = sum(1 for r in baseline if r['total_time'] < 2.0)
    optimized_sla = sum(1 for r in optimized if r['total_time'] < 2.0)
    
    baseline_sla_pct = (baseline_sla / len(baseline)) * 100
    optimized_sla_pct = (optimized_sla / len(optimized)) * 100
    
    print(f"\n🏫 EDINBURGH SLA COMPLIANCE (<2.0s):")
    print(f"   Before indexes: {baseline_sla}/{len(baseline)} queries ({baseline_sla_pct:.1f}%)")
    print(f"   After indexes:  {optimized_sla}/{len(optimized)} queries ({optimized_sla_pct:.1f}%)")
    
    if optimized_sla_pct == 100:
        print("   🎉 PERFECT - All queries now meet Edinburgh's performance target!")
    elif optimized_sla_pct >= 95:
        print("   ✅ EXCELLENT - Nearly all queries meet performance target")
    elif optimized_sla_pct > baseline_sla_pct:
        improvement = optimized_sla_pct - baseline_sla_pct
        print(f"   ✅ IMPROVED - {improvement:.1f}% more queries meet SLA target")
    else:
        print("   ⚠️  No SLA improvement - consider further optimization")

def demonstrate_search_types():
    """Demonstrate different types of vector searches."""
    print("\n🔍 DEMONSTRATING SEARCH CAPABILITIES")
    print("=" * 50)
    
    search_examples = [
        ("Password-related queries", "I forgot my password and need to reset it"),
        ("Network connectivity", "WiFi connection problems on campus"),
        ("Library services", "booking study rooms and spaces"),
        ("Email troubleshooting", "student email configuration issues"),
        ("Remote access", "VPN for accessing university resources from home")
    ]
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for search_type, query in search_examples:
                    print(f"\n🔍 {search_type}: '{query}'")
                    
                    query_embedding = get_embedding(query)
                    if not query_embedding:
                        print("   ❌ Embedding generation failed")
                        continue
                    
                    cur.execute("""
                        SELECT 
                            title,
                            category,
                            1 - (content_embedding <=> %s::vector) as similarity
                        FROM edinburgh_docs
                        ORDER BY content_embedding <=> %s::vector
                        LIMIT 2;
                    """, (query_embedding, query_embedding))
                    
                    results = cur.fetchall()
                    
                    for i, (title, category, similarity) in enumerate(results, 1):
                        relevance = "🎯" if similarity > 0.7 else "📋" if similarity > 0.5 else "📄"
                        print(f"   {i}. {relevance} '{title}' ({category}) - {similarity:.3f}")
    
    except Exception as e:
        print(f"⚠️  Search demonstration failed: {e}")

def main():
    """Main performance optimization workflow."""
    print("🚀 POSTGRESQL + PGVECTOR PERFORMANCE OPTIMIZATION")
    print("=" * 70)
    print("Testing vector search performance and creating production indexes.\n")
    
    # Test baseline performance (without indexes)
    print("📈 PHASE 1: BASELINE PERFORMANCE TEST (No Vector Indexes)")
    baseline_results = test_search_performance(with_indexes=False)
    
    if not baseline_results:
        print("❌ Baseline testing failed!")
        return 1
    
    # Create vector indexes
    print("\n" + "="*70)
    print("📈 PHASE 2: CREATING VECTOR INDEXES")
    if not create_vector_indexes():
        print("❌ Index creation failed!")
        return 1
    
    # Test optimized performance (with indexes)
    print("\n" + "="*70)
    print("📈 PHASE 3: OPTIMIZED PERFORMANCE TEST (With Vector Indexes)")
    optimized_results = test_search_performance(with_indexes=True)
    
    if not optimized_results:
        print("❌ Optimized testing failed!")
        return 1
    
    # Performance comparison
    print("\n" + "="*70)
    print("📈 PHASE 4: PERFORMANCE ANALYSIS")
    compare_performance_results(baseline_results, optimized_results)
    
    # Index analysis
    analyze_index_performance()
    
    # Search demonstrations
    demonstrate_search_types()
    
    print("\n" + "=" * 70)
    print("✅ PERFORMANCE OPTIMIZATION COMPLETE!")
    print("\n📊 Summary:")
    print(f"   • Tested {len(optimized_results)} different search queries")
    print(f"   • Created HNSW vector indexes for fast similarity search")
    print(f"   • Analyzed performance improvements and SLA compliance")
    print(f"   • Database is now optimized for Edinburgh's production needs")
    
    print("\n💡 Production recommendations:")
    print("   • Monitor query performance as document count grows")
    print("   • Consider index tuning for specialized workloads")
    print("   • Implement connection pooling for concurrent users")
    print("   • Set up monitoring for index usage and database performance")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)