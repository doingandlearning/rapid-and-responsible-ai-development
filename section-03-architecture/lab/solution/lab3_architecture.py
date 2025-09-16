import psycopg
import requests
import json
import time

def get_embedding(text):
    url = "http://localhost:11434/api/embed"
    payload = {"model": "bge-m3", "input": text}
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("embeddings", [])[0]
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

def setup_edinburgh_knowledge_base():
    print("🏛️ SETTING UP EDINBURGH KNOWLEDGE BASE")
    print("=" * 50)
    edinburgh_documents = [
        # ...existing document list from the lab...
    ]
    # For brevity, see the README or original lab for full document list
    # ...existing code for table creation and embedding generation...
    return len(edinburgh_documents)

def search_knowledge_base(query_embedding, top_k=5):
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id, 
                    title, 
                    content,
                    GREATEST(
                        1 - (content_embedding <=> %s::vector),
                        1 - (title_embedding <=> %s::vector)
                    ) as max_similarity
                FROM edinburgh_knowledge
                ORDER BY max_similarity DESC
                LIMIT %s;
            """, (query_embedding, query_embedding, top_k))
            return cur.fetchall()

def assemble_context_for_llm(docs, user_query):
    context = f"User Query: {user_query}\n\nRelevant Edinburgh University Information:\n\n"
    for i, doc in enumerate(docs, 1):
        context += f"Document {i}: {doc['title']}\n"
        context += f"Content: {doc['content']}\n"
        context += f"Relevance Score: {doc['similarity']:.3f}\n\n"
    context += "Please provide a helpful, accurate response based on the above Edinburgh University information."
    return context

def assess_response_quality(docs, user_query):
    if not docs:
        return 0.0
    avg_similarity = sum(doc['similarity'] for doc in docs) / len(docs)
    doc_coverage = min(1.0, len(docs) / 2)
    return avg_similarity * doc_coverage

def trace_complete_query(user_query):
    print(f"\n🔍 TRACING QUERY: '{user_query}'")
    print("=" * 60)
    print("\n📝 COMPONENT 1: USER INPUT PROCESSING")
    print(f"   Input: '{user_query}'")
    print(f"   Length: {len(user_query)} characters")
    print(f"   Word count: {len(user_query.split())} words")
    print("\n🧠 COMPONENT 2: EMBEDDING GENERATION")
    print("   Converting query to vector representation...")
    start_time = time.time()
    query_embedding = get_embedding(user_query)
    embedding_time = time.time() - start_time
    if not query_embedding:
        print("   ❌ Embedding generation failed!")
        return
    print(f"   ✅ Generated embedding in {embedding_time:.2f} seconds")
    print(f"   Dimensions: {len(query_embedding)}")
    print(f"   Sample values: {query_embedding[:5]}")
    print("\n🗄️ COMPONENT 3: VECTOR DATABASE SEARCH")
    start_time = time.time()
    search_results = search_knowledge_base(query_embedding, top_k=3)
    search_time = time.time() - start_time
    print(f"   ✅ Vector search completed in {search_time:.2f} seconds")
    print(f"   Results found: {len(search_results)}")
    print("\n📋 COMPONENT 4: DOCUMENT RETRIEVAL ANALYSIS")
    relevant_docs = []
    for i, (doc_id, title, content, similarity) in enumerate(search_results):
        print(f"   Result {i+1}: '{title}' (similarity: {similarity:.3f})")
        if similarity > 0.7:
            relevant_docs.append({'title': title, 'content': content, 'similarity': similarity})
            print(f"      ✅ Above threshold - RELEVANT")
        else:
            print(f"      ⚠️  Below threshold - QUESTIONABLE")
    if not relevant_docs:
        print("   ❌ No documents met relevance threshold!")
        return
    print("\n📦 COMPONENT 5: CONTEXT ASSEMBLY")
    context = assemble_context_for_llm(relevant_docs, user_query)
    print(f"   ✅ Context assembled - {len(context)} characters")
    print(f"   Documents included: {len(relevant_docs)}")
    print("\n🤖 COMPONENT 6: LLM COMPLETION")
    print("   📤 Would send to OpenAI API:")
    print(f"   Context length: {len(context)} characters")
    print(f"   Estimated tokens: ~{len(context.split()) * 1.3:.0f}")
    print("   Temperature: 0.2 (low for factual responses)")
    print("   Model: GPT-4")
    print("\n✅ COMPONENT 7: QUALITY ASSESSMENT")
    quality_score = assess_response_quality(relevant_docs, user_query)
    print(f"   Quality score: {quality_score:.2f}/1.0")
    if quality_score > 0.8:
        print("   ✅ HIGH CONFIDENCE - Approved for user")
    elif quality_score > 0.6:
        print("   ⚠️  MEDIUM CONFIDENCE - Review recommended")
    else:
        print("   ❌ LOW CONFIDENCE - Human review required")
    total_time = embedding_time + search_time
    print(f"\n⏱️ PERFORMANCE SUMMARY")
    print(f"   Embedding generation: {embedding_time:.2f}s")
    print(f"   Vector search: {search_time:.2f}s")
    print(f"   Total processing time: {total_time:.2f}s")
    print(f"   Edinburgh SLA target: <5.0s")
    if total_time < 5.0:
        print("   ✅ Performance target met!")
    else:
        print("   ❌ Performance target missed - optimization needed")
    return {
        'relevant_docs': relevant_docs,
        'quality_score': quality_score,
        'performance': total_time,
        'context': context
    }

def analyze_system_performance():
    print("\n🔬 SYSTEM PERFORMANCE ANALYSIS")
    print("=" * 50)
    test_queries = [
        "password reset help",
        "wifi connection problems", 
        "study room booking",
        "email configuration support",
        "vpn access issues"
    ]
    performance_data = {
        'embedding_times': [],
        'search_times': [],
        'total_times': [],
        'quality_scores': []
    }
    for query in test_queries:
        print(f"\n⚡ Testing: '{query}'")
        start_time = time.time()
        embedding = get_embedding(query)
        embed_time = time.time() - start_time
        if not embedding:
            continue
        start_time = time.time()
        results = search_knowledge_base(embedding, top_k=3)
        search_time = time.time() - start_time
        total_time = embed_time + search_time
        quality = sum(1 - r[3] for r in results) / len(results) if results else 0
        performance_data['embedding_times'].append(embed_time)
        performance_data['search_times'].append(search_time)
        performance_data['total_times'].append(total_time)
        performance_data['quality_scores'].append(quality)
        print(f"   Embedding: {embed_time:.2f}s | Search: {search_time:.2f}s | Total: {total_time:.2f}s")
    print(f"\n📊 PERFORMANCE SUMMARY")
    print(f"   Average embedding time: {sum(performance_data['embedding_times'])/len(performance_data['embedding_times']):.2f}s")
    print(f"   Average search time: {sum(performance_data['search_times'])/len(performance_data['search_times']):.2f}s")
    print(f"   Average total time: {sum(performance_data['total_times'])/len(performance_data['total_times']):.2f}s")
    print(f"   Average quality score: {sum(performance_data['quality_scores'])/len(performance_data['quality_scores']):.3f}")
    avg_embed = sum(performance_data['embedding_times'])/len(performance_data['embedding_times'])
    avg_search = sum(performance_data['search_times'])/len(performance_data['search_times'])
    print(f"\n🔍 BOTTLENECK ANALYSIS")
    if avg_embed > avg_search:
        print(f"   PRIMARY BOTTLENECK: Embedding generation ({avg_embed:.2f}s)")
        print(f"   RECOMMENDATION: Scale up Ollama resources or add embedding cache")
    else:
        print(f"   PRIMARY BOTTLENECK: Vector search ({avg_search:.2f}s)")
        print(f"   RECOMMENDATION: Add vector indexes or optimize database")
    return performance_data

def simulate_common_problems():
    print("\n🔧 TROUBLESHOOTING SIMULATION")
    print("=" * 50)
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE tablename = 'edinburgh_knowledge' 
                AND indexname LIKE '%vector%';
            """)
            indexes = cur.fetchall()
            if not indexes:
                print("   🔍 DIAGNOSIS: No vector indexes found")
                print("   💡 SOLUTION: Create HNSW index for fast similarity search")
                print("   📝 COMMAND: CREATE INDEX ON edinburgh_knowledge USING hnsw (content_embedding vector_cosine_ops);")
            else:
                print("   ✅ Vector indexes already exist")
    print("\n❌ PROBLEM 2: 'I don't know' responses")
    test_query = "help with university login"
    embedding = get_embedding(test_query)
    if embedding:
        results = search_knowledge_base(embedding, top_k=3)
        max_similarity = max(r[3] for r in results) if results else 0
        print(f"   Query: '{test_query}'")
        print(f"   Best similarity: {max_similarity:.3f}")
        if max_similarity < 0.7:
            print("   🔍 DIAGNOSIS: Similarity threshold too high")
            print("   💡 SOLUTION: Lower threshold to 0.5 or add more synonyms")
        else:
            print("   ✅ Similarity scores look good")
    print("\n❌ PROBLEM 3: Context too large for LLM")
    long_query = "I need help with password reset, wifi connection, email setup, study room booking, and VPN access all at once"
    embedding = get_embedding(long_query)
    if embedding:
        results = search_knowledge_base(embedding, top_k=10)
        total_content_length = sum(len(r[2]) for r in results)
        print(f"   Query retrieves {len(results)} documents")
        print(f"   Total content length: {total_content_length} characters")
        print(f"   Estimated tokens: ~{total_content_length * 1.3 / 4:.0f}")
        if total_content_length > 20000:
            print("   🔍 DIAGNOSIS: Context likely exceeds LLM window")
            print("   💡 SOLUTION: Limit to top 3 documents or implement smart truncation")
        else:
            print("   ✅ Context size looks manageable")

# Example usage (see README for full workflow):
# doc_count = setup_edinburgh_knowledge_base()
# for query in test_queries:
#     result = trace_complete_query(query)
# perf_data = analyze_system_performance()
# simulate_common_problems()
