# Section 6: RAG Pipeline Integration

---

## Learning Objectives

By the end of this section, you will:

- ✅ Understand the complete RAG (Retrieval Augmented Generation) architecture
- ✅ Implement similarity search to retrieve relevant document chunks
- ✅ Assemble context from multiple chunks for LLM input
- ✅ Integrate with OpenAI API for text generation
- ✅ Build source attribution and citation systems
- ✅ Create a complete Edinburgh Q&A system
- ✅ Handle edge cases and optimize performance

---

## What is RAG?

### 🧠 Retrieval Augmented Generation

**The Problem:**

- LLMs have **knowledge cutoffs** (training data ends at specific date)
- LLMs can **hallucinate** facts not in their training
- LLMs lack **institutional knowledge** (Edinburgh-specific information)

**The Solution:**

```
User Query → Retrieve Relevant Info → Augment LLM Context → Generate Response
```

**RAG = External Knowledge + LLM Generation**

---

## Edinburgh's RAG Challenge

### 🏫 University-Specific Knowledge

**What LLMs Don't Know:**

- Current Edinburgh IT policies (updated weekly)
- Specific phone numbers and procedures
- Building locations and room numbers
- Current academic calendar dates
- Staff directory and contact information

---

**What RAG Provides:**

- **Real-time accuracy** with current documents
- **Source attribution** ("According to the IT Handbook...")
- **Institutional context** (Edinburgh-specific language)
- **Verifiable information** (users can check sources)

---

## RAG Architecture Overview

### 🏗️ Complete System Components

```
┌─────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                         │
├─────────────────────────────────────────────────────────┤
│ 1. USER QUERY                                          │
│    "How do I reset my password?"                        │
│                          ↓                              │
│ 2. QUERY EMBEDDING                                      │
│    [0.1, 0.8, -0.3, ...] (1024 dimensions)            │
│                          ↓                              │
│ 3. SIMILARITY SEARCH                                    │
│    PostgreSQL + pgvector cosine similarity             │
│                          ↓                              │
│ 4. CONTEXT ASSEMBLY                                     │
│    "Password reset via MyEd portal..."                 │
│                          ↓                              │
│ 5. LLM GENERATION                                       │
│    OpenAI API + assembled context                      │
│                          ↓                              │
│ 6. RESPONSE WITH CITATIONS                              │
│    "To reset your password... (Source: IT Handbook)"   │
└─────────────────────────────────────────────────────────┘
```

---

## Step 1: Similarity Search Implementation

### 🔍 Finding Relevant Chunks

```python
def search_similar_chunks(query: str, limit: int = 5) -> List[Dict]:
    """
    Search for chunks similar to user query.

    Args:
        query: User's question
        limit: Number of chunks to return

    Returns:
        List of relevant chunks with similarity scores
    """
    # Generate embedding for user query
    query_embedding = get_embedding(query)

    # Search PostgreSQL for similar vectors
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    text,
                    document_title,
                    page_number,
                    section_title,
                    1 - (embedding <=> %s) as similarity
                FROM document_chunks
                WHERE embedding IS NOT NULL
                ORDER BY similarity 
                LIMIT %s;
            """, (json.dumps(query_embedding), limit))

            results = cur.fetchall()

    return [
        {
            'text': text,
            'document': document_title,
            'page': page_number,
            'section': section_title,
            'similarity': similarity_score
        }
        for text, document_title, page_number, section_title, similarity_score in results
    ]
```

---

## Step 2: Context Assembly

### 🧩 Building LLM Context

**Challenge:** Combine multiple chunks into coherent context

**Strategy:**

1. **Filter by relevance threshold** (similarity > 0.7)
2. **Rank by similarity score**
3. **Combine with source attribution**
4. **Stay within LLM token limits**

---

```python
def assemble_context(chunks: List[Dict], max_tokens: int = 2000) -> str:
    """
    Assemble chunks into coherent context for LLM.

    Args:
        chunks: List of relevant chunks
        max_tokens: Maximum tokens for context

    Returns:
        Formatted context string with citations
    """
    context_parts = []
    total_tokens = 0

    for i, chunk in enumerate(chunks):
        # Skip low-relevance chunks
        if chunk['similarity'] < 0.7:
            continue

        # Format chunk with citation
        chunk_text = f"""
Source {i+1}: {chunk['document']} (Page {chunk['page']})
{chunk['section'] or 'General Information'}

{chunk['text']}
"""

        # Estimate tokens (rough: 4 chars per token)
        chunk_tokens = len(chunk_text) // 4

        if total_tokens + chunk_tokens > max_tokens:
            break

        context_parts.append(chunk_text)
        total_tokens += chunk_tokens

    return "\n".join(context_parts)
```

---

## Step 3: LLM Integration

### 🤖 OpenAI API Integration

**Requirements:**

- OpenAI API key (provided during course)
- Chat completions endpoint
- System prompts for Edinburgh context
- Response formatting with citations

---

```python
import openai
from typing import Dict, Any

def generate_response(query: str, context: str, api_key: str) -> Dict[str, Any]:
    """
    Generate response using OpenAI API with Edinburgh context.

    Args:
        query: User's question
        context: Assembled context from chunks
        api_key: OpenAI API key

    Returns:
        Generated response with metadata
    """
    client = openai.Client(api_key=api_key)

    system_prompt = """You are an AI assistant for Edinburgh University technical staff.

Your role:
- Answer questions using the provided context from official university documents
- Always cite your sources using the format: (Source: Document Name, Page X)
- If information isn't in the context, say "I don't have that information"
- Use Edinburgh University terminology and be professional
- Focus on practical, actionable guidance

Remember: Staff rely on accurate information for their work."""

    user_prompt = f"""Context from Edinburgh University documents:
{context}

Question: {query}

Please provide a helpful answer based on the context above."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for factual responses
            max_tokens=500
        )

        return {
            'answer': response.choices[0].message.content,
            'tokens_used': response.usage.total_tokens,
            'cost_estimate': response.usage.total_tokens * 0.000002  # Rough cost
        }

    except Exception as e:
        return {
            'answer': f"Sorry, I encountered an error: {str(e)}",
            'tokens_used': 0,
            'cost_estimate': 0
        }
```

---

## Complete RAG Pipeline

### 🚀 Putting It All Together

```python
def answer_question(query: str, api_key: str) -> Dict[str, Any]:
    """
    Complete RAG pipeline: query → search → context → generate → respond

    Args:
        query: User's question
        api_key: OpenAI API key

    Returns:
        Complete response with answer, sources, and metadata
    """
    # Step 1: Search for relevant chunks
    similar_chunks = search_similar_chunks(query, limit=5)

    if not similar_chunks:
        return {
            'answer': "I couldn't find relevant information for your question.",
            'sources': [],
            'similarity_scores': [],
            'tokens_used': 0
        }

    # Step 2: Assemble context
    context = assemble_context(similar_chunks)

    # Step 3: Generate response
    response = generate_response(query, context, api_key)

    # Step 4: Compile complete result
    return {
        'answer': response['answer'],
        'sources': [
            {
                'document': chunk['document'],
                'page': chunk['page'],
                'section': chunk['section'],
                'similarity': chunk['similarity']
            }
            for chunk in similar_chunks[:3]  # Top 3 sources
        ],
        'similarity_scores': [chunk['similarity'] for chunk in similar_chunks],
        'tokens_used': response['tokens_used'],
        'cost_estimate': response['cost_estimate']
    }
```

---

## Edinburgh Use Cases

### 💼 Real-World Scenarios

**IT Help Desk Automation:**

```python
# User query
query = "I can't connect to WiFi in the library"

# RAG response
response = answer_question(query, api_key)
print(response['answer'])
# "To connect to WiFi in the library, first ensure you're connecting to
#  the EdUni network... (Source: Student WiFi Guide, Page 1)"
```

---

**Policy Clarification:**

```python
# Staff query
query = "What's the VPN policy for remote work?"

# RAG response
response = answer_question(query, api_key)
print(response['answer'])
# "The VPN policy allows staff to access university resources remotely
#  with FortiClient... (Source: VPN Policy Document, Page 1)"
```

---

**Procedure Lookup:**

```python
# Administrator query
query = "How do I register a new student device?"

# RAG response gets step-by-step procedures with citations
```

---

## Source Attribution & Citations

### 📚 Building Trust Through Transparency

**Why Citations Matter:**

- **Verifiability**: Users can check source documents
- **Trust**: Clear attribution builds confidence
- **Compliance**: Required for institutional use
- **Debugging**: Helps identify outdated information

---

**Citation Formats:**

```python
def format_citations(sources: List[Dict]) -> str:
    """Format sources for user display."""
    citations = []

    for i, source in enumerate(sources, 1):
        citation = f"{i}. {source['document']}"

        if source['page']:
            citation += f", Page {source['page']}"

        if source['section']:
            citation += f" ({source['section']})"

        citation += f" (Relevance: {source['similarity']:.2f})"
        citations.append(citation)

    return "\n".join(citations)

# Example output:
# 1. IT Support Handbook, Page 15 (Password Management) (Relevance: 0.89)
# 2. Student Guide 2024, Page 3 (Account Setup) (Relevance: 0.82)
```

---

## Quality Control & Validation

### ✅ Ensuring Reliable Responses

**Relevance Thresholds:**

```python
SIMILARITY_THRESHOLDS = {
    'high_confidence': 0.85,    # Excellent match
    'medium_confidence': 0.70,  # Good match
    'low_confidence': 0.60,     # Questionable match
    'no_answer': 0.50          # Don't respond below this
}

def validate_response_quality(chunks: List[Dict]) -> str:
    """Determine response confidence level."""
    if not chunks:
        return 'no_data'

    best_similarity = max(chunk['similarity'] for chunk in chunks)

    if best_similarity >= SIMILARITY_THRESHOLDS['high_confidence']:
        return 'high_confidence'
    elif best_similarity >= SIMILARITY_THRESHOLDS['medium_confidence']:
        return 'medium_confidence'
    elif best_similarity >= SIMILARITY_THRESHOLDS['low_confidence']:
        return 'low_confidence'
    else:
        return 'insufficient_confidence'
```

**Response Qualification:**

```python
def qualify_response(answer: str, confidence: str) -> str:
    """Add confidence qualifiers to responses."""

    qualifiers = {
        'high_confidence': "",  # No qualifier needed
        'medium_confidence': "Based on the available information, ",
        'low_confidence': "I found limited information suggesting that ",
        'insufficient_confidence': "I don't have reliable information about this topic."
    }

    if confidence == 'insufficient_confidence':
        return qualifiers[confidence]
    else:
        return qualifiers[confidence] + answer
```

---

## Error Handling & Edge Cases

### 🛠️ Robust Production Implementation

**Common Issues:**

1. **No Relevant Chunks Found**

```python
def handle_no_results(query: str) -> Dict[str, Any]:
    return {
        'answer': f"I couldn't find specific information about '{query}' in the Edinburgh documents. "
                 f"You might want to contact IT Services directly at 0131 650 4500.",
        'sources': [],
        'confidence': 'no_data'
    }
```

---

2. **OpenAI API Failures**

```python
def handle_api_failure(error: Exception) -> Dict[str, Any]:
    fallback_msg = "I'm experiencing technical difficulties. Please try again or contact IT Services."

    return {
        'answer': fallback_msg,
        'sources': [],
        'error': str(error),
        'confidence': 'api_error'
    }
```

---

3. **Rate Limiting**

```python
import time
from functools import wraps

def rate_limit_retry(max_retries=3, delay=1):
    """Decorator for API rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except openai.RateLimitError:
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    raise
            return None
        return wrapper
    return decorator
```

---

## Performance Optimization

### ⚡ Making RAG Fast and Efficient

**Database Optimization:**

```python
# Pre-compute query embeddings for common questions
COMMON_QUERIES = [
    "How do I reset my password?",
    "WiFi connection problems",
    "VPN access setup",
    "Email configuration"
]

def precompute_common_embeddings():
    """Pre-compute embeddings for frequent queries."""
    cache = {}
    for query in COMMON_QUERIES:
        cache[query] = get_embedding(query)
    return cache

# Use indexes effectively
def optimized_similarity_search(query_embedding: List[float], limit: int = 5):
    """Optimized search using HNSW indexes."""
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Force index usage
            cur.execute("SET enable_seqscan = off;")

            cur.execute("""
                SELECT text, document_title, page_number, section_title,
                       1 - (embedding <=> %s::vector) as similarity_score
                FROM document_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_embedding, query_embedding, limit))

            return cur.fetchall()
```

---

**Response Caching:**

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_answer_question(query_hash: str, query: str, api_key: str):
    """Cache responses for identical queries."""
    return answer_question(query, api_key)

def answer_with_cache(query: str, api_key: str):
    """Answer question with caching."""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return cached_answer_question(query_hash, query, api_key)
```

---

## Testing & Validation

### 🧪 Ensuring System Quality

**Test Question Sets:**

```python
EDINBURGH_TEST_QUERIES = [
    # IT Support queries
    ("How do I reset my university password?", "password"),
    ("I can't connect to WiFi", "network"),
    ("VPN setup for remote access", "vpn"),

    # Student services queries
    ("How do I book a study room?", "library"),
    ("Student email configuration", "email"),
    ("Two-factor authentication setup", "security"),

    # Edge cases
    ("What's the weather like?", None),  # Should decline to answer
    ("Who is the vice-chancellor?", None),  # Not in our documents
    ("", None),  # Empty query
]

def test_rag_system():
    """Comprehensive RAG system testing."""
    results = []

    for query, expected_topic in EDINBURGH_TEST_QUERIES:
        response = answer_question(query, api_key)

        test_result = {
            'query': query,
            'expected_topic': expected_topic,
            'answer_length': len(response['answer']),
            'sources_found': len(response['sources']),
            'avg_similarity': statistics.mean(response['similarity_scores']) if response['similarity_scores'] else 0,
            'tokens_used': response['tokens_used'],
            'has_citations': '(Source:' in response['answer']
        }

        results.append(test_result)

    return results
```

---

## User Interface Integration

### 🖥️ Building the Complete Experience

**Simple Web Interface:**

```python
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    query = data.get('question', '')

    if not query.strip():
        return jsonify({'error': 'Please provide a question'})

    # Get RAG response
    response = answer_question(query, OPENAI_API_KEY)

    return jsonify({
        'answer': response['answer'],
        'sources': response['sources'],
        'confidence': validate_response_quality([
            {'similarity': s} for s in response['similarity_scores']
        ])
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'database': check_database_connection(),
        'ollama': check_ollama_connection(),
        'openai': check_openai_connection()
    })
```

---

**Chat Interface Template:**

```html
<!-- Simple chat interface -->
<div id="chat-container">
  <div id="messages"></div>
  <form id="question-form">
    <input
      type="text"
      id="question-input"
      placeholder="Ask about Edinburgh IT services..."
    />
    <button type="submit">Ask</button>
  </form>
</div>

<script>
  document
    .getElementById("question-form")
    .addEventListener("submit", async function (e) {
      e.preventDefault();

      const question = document.getElementById("question-input").value;
      const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      displayAnswer(data.answer, data.sources);
    });
</script>
```

---

## Production Deployment

### 🚀 Edinburgh-Ready Implementation

**Configuration Management:**

```python
import os
from dataclasses import dataclass

@dataclass
class RAGConfig:
    # Database
    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_port: str = os.getenv('DB_PORT', '5050')
    db_name: str = os.getenv('DB_NAME', 'pgvector')
    db_user: str = os.getenv('DB_USER', 'postgres')
    db_password: str = os.getenv('DB_PASSWORD', 'postgres')

    # APIs
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    ollama_url: str = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/embed')

    # RAG Parameters
    similarity_threshold: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
    max_chunks: int = int(os.getenv('MAX_CHUNKS', '5'))
    max_context_tokens: int = int(os.getenv('MAX_CONTEXT_TOKENS', '2000'))

    # Performance
    cache_size: int = int(os.getenv('CACHE_SIZE', '100'))
    rate_limit_rpm: int = int(os.getenv('RATE_LIMIT_RPM', '60'))
```

---

**Monitoring & Logging:**

```python
import logging
from datetime import datetime

def setup_rag_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_rag_interaction(query: str, response_time: float, sources_count: int):
    """Log RAG system usage for monitoring."""
    logging.info(f"RAG Query: '{query[:50]}...' | "
                f"Time: {response_time:.2f}s | "
                f"Sources: {sources_count}")
```

---

## Lab Preview

### 🧪 Hands-On RAG Implementation

**Lab Scenario:** Build Edinburgh IT Support Chatbot

**You'll implement:**

1. **Similarity search** using chunks from Section 5
2. **Context assembly** with source attribution
3. **OpenAI integration** for response generation
4. **Complete Q&A system** with web interface
5. **Quality validation** and error handling
6. **Performance testing** with realistic queries

---

**Success criteria:**

- Answer Edinburgh IT questions accurately
- Provide proper source citations
- Handle edge cases gracefully
- Meet response time targets (<3 seconds)

---

## Next Steps

### 🎯 What's Coming

**Section 7: Advanced Vector Queries**

- Hybrid search (text + vectors)
- Complex filtering and metadata queries
- Multi-document analysis

**Section 8: Production Deployment**

- Scaling and load balancing
- Security and authentication
- Monitoring and maintenance

---

### 💡 Key Takeaways

- **RAG combines** external knowledge with LLM generation
- **Source attribution** is crucial for institutional trust
- **Quality validation** ensures reliable responses
- **Performance optimization** makes systems production-ready

---

## Discussion Questions

### 🤔 With your partner, discuss:

1. **Trust vs. Automation:** How do you balance automated responses with the need for verifiable information in a university setting?

2. **Context Assembly:** What strategies would you use if multiple chunks contradict each other?

3. **User Experience:** How would you handle queries that span multiple documents or require complex reasoning?

4. **System Limits:** When should the RAG system decline to answer and direct users to human support?

---

## Summary

### ✅ Section 6 Completed

You now understand:

- **Complete RAG architecture** from query to response
- **Similarity search implementation** with PostgreSQL + pgvector
- **Context assembly** with proper source attribution
- **LLM integration** using OpenAI API
- **Quality control** and confidence validation
- **Production considerations** for Edinburgh deployment

**Ready for the lab?** Let's build a complete RAG system! 🚀
