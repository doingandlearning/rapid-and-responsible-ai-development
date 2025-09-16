# Lab 3: RAG Architecture Deep Dive

## Learning Objectives

By the end of this lab, you will:

- ✅ Trace a complete query through all RAG system components
- ✅ Inspect and configure each architectural component
- ✅ Practice systematic troubleshooting with real issues
- ✅ Understand performance and quality trade-offs in Edinburgh context

## Time Estimate: 30 minutes

---

## Pre-Lab Setup

**Ensure your environment is ready:**

1. Services from previous labs running: `cd environment && docker compose up -d`
2. Virtual environment activated: `source .venv/bin/activate`
3. Create new lab file: `lab3_architecture.py`

---

## Part 1: Edinburgh Document Pipeline (8 minutes)

### Step 1: Create Edinburgh Knowledge Base

Let's build a realistic knowledge base with Edinburgh-specific content:

```python
import psycopg
import requests
import json
import time

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

def setup_edinburgh_knowledge_base():
    """Create a realistic Edinburgh IT knowledge base."""
    print("🏛️ SETTING UP EDINBURGH KNOWLEDGE BASE")
    print("=" * 50)

    # Edinburgh IT support documents (realistic examples)
    edinburgh_documents = [
        {
            "title": "Password Reset Procedure",
            "content": "To reset your Edinburgh University password: 1) Visit https://www.ed.ac.uk/is/password-reset 2) Enter your university username (not email) 3) Check your university email for reset link 4) Follow the link within 24 hours 5) Create new password meeting complexity requirements. Contact IT Service Desk on 0131 650 4500 if problems persist.",
            "category": "authentication",
            "last_updated": "2024-01-15"
        },
        {
            "title": "WiFi Connection Guide",
            "content": "Edinburgh University provides EdUni WiFi network for students and staff. To connect: 1) Select EdUni network 2) Use your university username and password 3) For personal devices, first connect to EdUni-Setup to register device 4) Eduroam also available for international visitors. Speed: up to 100Mbps. Coverage: All university buildings.",
            "category": "networking",
            "last_updated": "2024-02-01"
        },
        {
            "title": "Study Room Booking System",
            "content": "Book study rooms through MyEd student portal. Available rooms: George Square Library (Levels 2-7), Main Library (silent study areas), Informatics Library (group rooms). Booking window: 7 days in advance. Duration: Maximum 4 hours. Cancel unused bookings to help other students. Accessible rooms available on request.",
            "category": "facilities",
            "last_updated": "2024-01-20"
        },
        {
            "title": "Email Setup Instructions",
            "content": "Edinburgh student email access: Username format: s1234567@ed.ac.uk. Configure email clients: IMAP server: outlook.office365.com (port 993, SSL required). SMTP server: smtp.office365.com (port 587, TLS required). Use your university username and password. Enable 2FA for security. Quota: 50GB per account.",
            "category": "email",
            "last_updated": "2024-01-10"
        },
        {
            "title": "VPN Access for Remote Work",
            "content": "Edinburgh VPN provides secure access to university resources from off-campus. Download FortiClient VPN from IT Services website. Server: vpn.ed.ac.uk. Use your university credentials. Required for: library database access, internal systems, secure file transfer. Available 24/7. Contact IT if connection issues.",
            "category": "remote_access",
            "last_updated": "2024-02-05"
        },
        {
            "title": "Software Installation Support",
            "content": "Edinburgh students get free access to Microsoft Office 365, MATLAB, Adobe Creative Suite, and specialist academic software. Download from IT Services software portal using university login. Installation support: Self-service guides available, drop-in sessions every Tuesday 2-4pm at George Square IT desk, remote assistance available.",
            "category": "software",
            "last_updated": "2024-01-25"
        }
    ]

    # Create enhanced table with metadata
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Drop existing table if it exists
            cur.execute("DROP TABLE IF EXISTS edinburgh_knowledge;")

            # Create table with proper structure
            cur.execute("""
                CREATE TABLE edinburgh_knowledge (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(100),
                    last_updated DATE,
                    content_embedding vector(1024),
                    title_embedding vector(1024)
                );
            """)

            print(f"✅ Created table for {len(edinburgh_documents)} documents")

            # Generate embeddings and store documents
            for i, doc in enumerate(edinburgh_documents):
                print(f"🔄 Processing document {i+1}/{len(edinburgh_documents)}: {doc['title']}")

                # Generate embeddings for content and title
                content_embedding = get_embedding(doc['content'])
                title_embedding = get_embedding(doc['title'])

                if content_embedding and title_embedding:
                    cur.execute("""
                        INSERT INTO edinburgh_knowledge
                        (title, content, category, last_updated, content_embedding, title_embedding)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        doc['title'],
                        doc['content'],
                        doc['category'],
                        doc['last_updated'],
                        content_embedding,
                        title_embedding
                    ))
                    print(f"✅ Stored: {doc['title']}")
                else:
                    print(f"❌ Failed to generate embeddings for: {doc['title']}")

                # Small delay to be nice to Ollama
                time.sleep(0.5)

            conn.commit()

    print("\n🎉 Edinburgh knowledge base ready!")
    return len(edinburgh_documents)

def get_embedding(text):
    """Generate embedding using Ollama."""
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

# Set up the knowledge base
doc_count = setup_edinburgh_knowledge_base()
```

**Run this to create your Edinburgh knowledge base:**

```bash
python lab3_architecture.py
```

---

## Part 2: Complete Query Tracing (10 minutes)

### Step 2: Trace Query Through All Components

Now let's trace a realistic student query through every component:

```python
def trace_complete_query(user_query):
    """Trace a query through all RAG system components."""
    print(f"\n🔍 TRACING QUERY: '{user_query}'")
    print("=" * 60)

    # Component 1: User Input Processing
    print("\n📝 COMPONENT 1: USER INPUT PROCESSING")
    print(f"   Input: '{user_query}'")
    print(f"   Length: {len(user_query)} characters")
    print(f"   Word count: {len(user_query.split())} words")

    # Component 2: Embedding Generation
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

    # Component 3: Vector Database Search
    print("\n🗄️ COMPONENT 3: VECTOR DATABASE SEARCH")
    start_time = time.time()
    search_results = search_knowledge_base(query_embedding, top_k=3)
    search_time = time.time() - start_time

    print(f"   ✅ Vector search completed in {search_time:.2f} seconds")
    print(f"   Results found: {len(search_results)}")

    # Component 4: Document Retrieval Analysis
    print("\n📋 COMPONENT 4: DOCUMENT RETRIEVAL ANALYSIS")
    relevant_docs = []
    for i, (doc_id, title, content, similarity) in enumerate(search_results):
        print(f"   Result {i+1}: '{title}' (similarity: {similarity:.3f})")
        if similarity > 0.7:  # Threshold for relevance
            relevant_docs.append({
                'title': title,
                'content': content,
                'similarity': similarity
            })
            print(f"      ✅ Above threshold - RELEVANT")
        else:
            print(f"      ⚠️  Below threshold - QUESTIONABLE")

    if not relevant_docs:
        print("   ❌ No documents met relevance threshold!")
        return

    # Component 5: Context Assembly
    print("\n📦 COMPONENT 5: CONTEXT ASSEMBLY")
    context = assemble_context_for_llm(relevant_docs, user_query)
    print(f"   ✅ Context assembled - {len(context)} characters")
    print(f"   Documents included: {len(relevant_docs)}")

    # Component 6: LLM Completion (Simulated)
    print("\n🤖 COMPONENT 6: LLM COMPLETION")
    print("   📤 Would send to OpenAI API:")
    print(f"   Context length: {len(context)} characters")
    print(f"   Estimated tokens: ~{len(context.split()) * 1.3:.0f}")
    print("   Temperature: 0.2 (low for factual responses)")
    print("   Model: GPT-4")

    # Component 7: Quality Assessment
    print("\n✅ COMPONENT 7: QUALITY ASSESSMENT")
    quality_score = assess_response_quality(relevant_docs, user_query)
    print(f"   Quality score: {quality_score:.2f}/1.0")
    if quality_score > 0.8:
        print("   ✅ HIGH CONFIDENCE - Approved for user")
    elif quality_score > 0.6:
        print("   ⚠️  MEDIUM CONFIDENCE - Review recommended")
    else:
        print("   ❌ LOW CONFIDENCE - Human review required")

    # Performance Summary
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

def search_knowledge_base(query_embedding, top_k=5):
    """Search Edinburgh knowledge base for similar content."""
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Search using both content and title embeddings
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
    """Assemble context for LLM from retrieved documents."""
    context = f"User Query: {user_query}\n\nRelevant Edinburgh University Information:\n\n"

    for i, doc in enumerate(docs, 1):
        context += f"Document {i}: {doc['title']}\n"
        context += f"Content: {doc['content']}\n"
        context += f"Relevance Score: {doc['similarity']:.3f}\n\n"

    context += "Please provide a helpful, accurate response based on the above Edinburgh University information."
    return context

def assess_response_quality(docs, user_query):
    """Assess potential response quality based on retrieved documents."""
    if not docs:
        return 0.0

    # Simple quality scoring based on document relevance and coverage
    avg_similarity = sum(doc['similarity'] for doc in docs) / len(docs)
    doc_coverage = min(1.0, len(docs) / 2)  # Optimal around 2-3 docs

    return avg_similarity * doc_coverage

# Test with realistic Edinburgh student queries
test_queries = [
    "How do I reset my university password?",
    "I can't connect to the WiFi",
    "How can I book a study room?",
    "My email isn't working properly",
    "I need help accessing library databases from home"
]

print("🎓 TESTING EDINBURGH RAG SYSTEM")
print("=" * 50)

for query in test_queries:
    result = trace_complete_query(query)
    if result:
        print("\n" + "="*60)
    time.sleep(1)  # Brief pause between queries
```

---

## Part 3: Component Performance Analysis (7 minutes)

### Step 3: Analyze System Performance and Bottlenecks

```python
def analyze_system_performance():
    """Analyze performance characteristics of each component."""
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

        # Test embedding generation
        start_time = time.time()
        embedding = get_embedding(query)
        embed_time = time.time() - start_time

        if not embedding:
            continue

        # Test vector search
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

    # Performance summary
    print(f"\n📊 PERFORMANCE SUMMARY")
    print(f"   Average embedding time: {sum(performance_data['embedding_times'])/len(performance_data['embedding_times']):.2f}s")
    print(f"   Average search time: {sum(performance_data['search_times'])/len(performance_data['search_times']):.2f}s")
    print(f"   Average total time: {sum(performance_data['total_times'])/len(performance_data['total_times']):.2f}s")
    print(f"   Average quality score: {sum(performance_data['quality_scores'])/len(performance_data['quality_scores']):.3f}")

    # Bottleneck analysis
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

# Run performance analysis
perf_data = analyze_system_performance()
```

---

## Part 4: Troubleshooting Practice (5 minutes)

### Step 4: Simulate and Fix Common Issues

```python
def simulate_common_problems():
    """Practice troubleshooting with simulated issues."""
    print("\n🔧 TROUBLESHOOTING SIMULATION")
    print("=" * 50)

    # Problem 1: No vector index (slow searches)
    print("\n❌ PROBLEM 1: Slow vector searches")
    print("Simulating: Database without vector indexes")

    # Check if we have indexes
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

    # Problem 2: Low similarity threshold
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

    # Problem 3: Context window overflow
    print("\n❌ PROBLEM 3: Context too large for LLM")
    long_query = "I need help with password reset, wifi connection, email setup, study room booking, and VPN access all at once"
    embedding = get_embedding(long_query)

    if embedding:
        results = search_knowledge_base(embedding, top_k=10)  # Retrieve many docs
        total_content_length = sum(len(r[2]) for r in results)

        print(f"   Query retrieves {len(results)} documents")
        print(f"   Total content length: {total_content_length} characters")
        print(f"   Estimated tokens: ~{total_content_length * 1.3 / 4:.0f}")  # Rough token estimate

        if total_content_length > 20000:  # Rough threshold
            print("   🔍 DIAGNOSIS: Context likely exceeds LLM window")
            print("   💡 SOLUTION: Limit to top 3 documents or implement smart truncation")
        else:
            print("   ✅ Context size looks manageable")

# Run troubleshooting simulation
simulate_common_problems()
```

**Run the complete analysis:**

```bash
python lab3_architecture.py
```

---

## Success Criteria ✅

**You've completed this lab when:**

- [ ] You understand how each query flows through all 7 RAG components
- [ ] You can identify performance bottlenecks in the system
- [ ] You've practiced systematic troubleshooting approaches
- [ ] You understand the trade-offs between speed, quality, and accuracy
- [ ] You can explain the system architecture to Edinburgh stakeholders

---

## Reflection & Next Steps (5 minutes)

### Discussion Questions

**With your partner, discuss:**

1. **Performance Trade-offs**: Which component would you optimize first for Edinburgh's scale? Why?

2. **Quality vs Speed**: How would you balance response time against answer accuracy for student support?

3. **Failure Modes**: Which component failure would be most disruptive to Edinburgh students? How would you prevent it?

4. **Edinburgh-Specific**: What additional components might Edinburgh need for their specific requirements (SSO, GDPR compliance, etc.)?

### Key Insights to Remember

- **Component Independence**: Each piece can be optimized separately
- **Performance Trade-offs**: Speed vs accuracy decisions at every level
- **Quality Monitoring**: Multiple points where quality can be assessed
- **Scalability Considerations**: What works for 100 users may not work for 10,000

### What's Coming Next

**In Section 4, we'll implement this architecture:**

- Set up PostgreSQL with pgvector
- Configure vector indexes for performance
- Build the complete pipeline from scratch
- Deploy it for real Edinburgh use cases

---

## Troubleshooting

### Common Issues

**Slow embedding generation:**

```bash
# Check Ollama container resources
docker stats ollama-service
# Consider: more CPU/RAM, model caching, or multiple replicas
```

**Vector search timeouts:**

```bash
# Check for vector indexes
\c pgvector
\d edinburgh_knowledge
# Create index if missing: CREATE INDEX ON table USING hnsw (embedding vector_cosine_ops);
```

**Connection errors:**

```bash
# Restart services if needed
cd environment && docker compose restart
```

**Memory issues:**

```bash
# Monitor Docker memory usage
docker system df
docker system prune  # Clean up if needed
```

---

## Advanced Extensions (If Time Permits)

### Performance Optimization

**Test different similarity thresholds:**

```python
for threshold in [0.5, 0.6, 0.7, 0.8]:
    # Test query quality vs result count
    pass
```

**Compare embedding strategies:**

```python
# Test content vs title embeddings
# Compare different chunking approaches
```

### Edinburgh Integration Planning

**Discuss these architectural questions:**

- How would this integrate with MyEd authentication?
- What monitoring would Edinburgh IT need?
- How would you handle multiple languages?
- What backup/disaster recovery is needed?

The hands-on experience with real components prepares you for tomorrow's implementation work!
