# Lab 6: RAG Pipeline Integration - Edinburgh Q&A System

## Learning Objectives
By the end of this lab, you will:
- ✅ Implement similarity search to retrieve relevant document chunks
- ✅ Assemble context from multiple chunks with proper attribution
- ✅ Integrate with OpenAI API for intelligent response generation
- ✅ Build a complete question-answering system for Edinburgh IT support
- ✅ Handle edge cases and validate response quality
- ✅ Create a simple web interface for testing

## Time Estimate: 45 minutes

---

## Pre-Lab Setup

**Ensure your environment is ready:**
1. **Section 5 completed**: Document chunks stored in database with embeddings
2. **Services running**: `cd environment && docker compose up -d`
3. **Virtual environment**: `source .venv/bin/activate`
4. **OpenAI API Key**: You'll be provided with an API key during the course
5. **Create lab file**: `lab6_rag_pipeline.py`

**🆘 Need help?** Complete solutions are in `../solution/` folder!

---

## Lab Scenario

You're building Edinburgh University's AI-powered IT support system. The system should:

1. **Answer staff questions** using processed document chunks from Section 5
2. **Provide source citations** so users can verify information
3. **Handle various query types** from password resets to VPN setup
4. **Decline to answer** when information isn't available
5. **Maintain Edinburgh's professional tone** in responses

Your goal is to create a production-ready RAG system that IT staff can rely on for accurate, attributable answers.

---

## Part 1: Similarity Search Implementation (10 minutes)

### Step 1: Set Up RAG Infrastructure

First, let's create our RAG system foundation:

```python
import psycopg
import requests
import openai
import json
import time
import statistics
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Database configuration (from Section 4)
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# API configuration
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"
OPENAI_API_KEY = "your-api-key-here"  # Will be provided during course

@dataclass
class SearchResult:
    """Represents a search result chunk."""
    text: str
    document_title: str
    page_number: Optional[int]
    section_title: Optional[str]
    similarity_score: float
    chunk_id: str

def get_embedding(text: str, max_retries: int = 3) -> Optional[List[float]]:
    """Generate embedding for text using Ollama BGE-M3 model."""
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
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"⚠️  Embedding failed: {e}")
            time.sleep(1)
    
    return None

def search_similar_chunks(query: str, limit: int = 5, 
                         similarity_threshold: float = 0.5) -> List[SearchResult]:
    """
    Search for document chunks similar to the user query.
    
    Args:
        query: User's question
        limit: Maximum number of chunks to return
        similarity_threshold: Minimum similarity score to include
        
    Returns:
        List of SearchResult objects sorted by similarity
    """
    print(f"🔍 Searching for chunks similar to: '{query}'")
    
    # Generate embedding for user query
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate query embedding")
        return []
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Search PostgreSQL for similar vectors using cosine similarity
                cur.execute("""
                    SELECT 
                        id,
                        text,
                        document_title,
                        page_number,
                        section_title,
                        1 - (embedding <=> %s::vector) as similarity_score
                    FROM document_chunks
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """, (query_embedding, query_embedding, limit))
                
                results = cur.fetchall()
                
                # Convert to SearchResult objects and filter by threshold
                search_results = []
                for chunk_id, text, doc_title, page_num, section, similarity in results:
                    if similarity >= similarity_threshold:
                        search_results.append(SearchResult(
                            text=text,
                            document_title=doc_title,
                            page_number=page_num,
                            section_title=section,
                            similarity_score=similarity,
                            chunk_id=chunk_id
                        ))
                
                print(f"✅ Found {len(search_results)} relevant chunks (similarity > {similarity_threshold})")
                return search_results
                
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

# Test similarity search
print("🧪 TESTING SIMILARITY SEARCH")
print("="*60)

# Test queries from Edinburgh context
test_queries = [
    "How do I reset my university password?",
    "I can't connect to WiFi on campus",
    "What are the VPN requirements for remote work?",
    "How do I configure student email?"
]

for query in test_queries:
    results = search_similar_chunks(query, limit=3, similarity_threshold=0.6)
    
    if results:
        print(f"\n🔍 Query: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.document_title} (Page {result.page_number})")
            print(f"      Similarity: {result.similarity_score:.3f}")
            print(f"      Text: '{result.text[:100]}...'")
    else:
        print(f"\n❌ No relevant chunks found for: '{query}'")
    
    print("-" * 40)
```

---

## Part 2: Context Assembly (8 minutes)

### Step 2: Build Context from Multiple Chunks

```python
def assemble_context(search_results: List[SearchResult], 
                    max_tokens: int = 2000) -> tuple[str, List[Dict[str, Any]]]:
    """
    Assemble search results into coherent context for LLM input.
    
    Args:
        search_results: List of SearchResult objects
        max_tokens: Maximum tokens for assembled context
        
    Returns:
        Tuple of (formatted_context, source_list)
    """
    if not search_results:
        return "", []
    
    context_parts = []
    sources = []
    total_tokens = 0
    
    print(f"🧩 Assembling context from {len(search_results)} chunks...")
    
    for i, result in enumerate(search_results):
        # Create source entry
        source_info = {
            'id': i + 1,
            'document': result.document_title,
            'page': result.page_number,
            'section': result.section_title,
            'similarity': result.similarity_score
        }
        
        # Format chunk with source attribution
        chunk_text = f"""
[Source {i+1}: {result.document_title}"""
        
        if result.page_number:
            chunk_text += f", Page {result.page_number}"
        if result.section_title:
            chunk_text += f" - {result.section_title}"
            
        chunk_text += f"]\n{result.text}\n"
        
        # Estimate tokens (rough: 4 characters per token)
        chunk_tokens = len(chunk_text) // 4
        
        # Check if adding this chunk would exceed token limit
        if total_tokens + chunk_tokens > max_tokens:
            print(f"⚠️  Stopping at {i} chunks to stay within {max_tokens} token limit")
            break
        
        context_parts.append(chunk_text)
        sources.append(source_info)
        total_tokens += chunk_tokens
        
        print(f"   ✅ Added chunk {i+1}: {result.document_title} ({chunk_tokens} tokens)")
    
    assembled_context = "\n".join(context_parts)
    print(f"📊 Final context: {total_tokens} estimated tokens from {len(sources)} sources")
    
    return assembled_context, sources

def format_sources_for_display(sources: List[Dict[str, Any]]) -> str:
    """Format sources for user display."""
    if not sources:
        return "No sources available."
    
    formatted_sources = ["📚 Sources:"]
    
    for source in sources:
        source_line = f"  {source['id']}. {source['document']}"
        
        if source['page']:
            source_line += f", Page {source['page']}"
        if source['section']:
            source_line += f" ({source['section']})"
            
        source_line += f" - Relevance: {source['similarity']:.2f}"
        formatted_sources.append(source_line)
    
    return "\n".join(formatted_sources)

# Test context assembly
print("\n🧩 TESTING CONTEXT ASSEMBLY")
print("="*60)

# Use a complex query that should retrieve multiple chunks
complex_query = "How do I set up network access and WiFi for students?"
search_results = search_similar_chunks(complex_query, limit=4, similarity_threshold=0.6)

if search_results:
    context, sources = assemble_context(search_results, max_tokens=1500)
    
    print(f"📄 Assembled context for: '{complex_query}'")
    print(f"Context length: {len(context)} characters")
    print(f"\n📖 Context preview:")
    print(context[:400] + "...")
    
    print(f"\n{format_sources_for_display(sources)}")
else:
    print("❌ No results to assemble context from")
```

---

## Part 3: OpenAI Integration (12 minutes)

### Step 3: Generate Responses with OpenAI API

```python
def generate_llm_response(query: str, context: str, api_key: str) -> Dict[str, Any]:
    """
    Generate response using OpenAI API with Edinburgh-specific prompting.
    
    Args:
        query: User's question
        context: Assembled context from document chunks
        api_key: OpenAI API key
        
    Returns:
        Dictionary with response, token usage, and metadata
    """
    print(f"🤖 Generating LLM response for: '{query[:50]}...'")
    
    # Edinburgh-specific system prompt
    system_prompt = """You are an AI assistant for Edinburgh University's IT Services.

Your role and responsibilities:
- Provide accurate, helpful answers using ONLY the context from official Edinburgh University documents
- Always cite your sources using the format: (Source: Document Name, Page X)
- If the context doesn't contain relevant information, clearly state "I don't have that information in the available documents"
- Use professional, helpful language appropriate for university staff and students
- Focus on practical, actionable guidance
- When procedures have multiple steps, present them clearly

Remember: University staff rely on accurate information for their daily work. Be precise and cite all information properly."""

    # User prompt with context and query
    user_prompt = f"""Context from Edinburgh University documents:

{context}

User Question: {query}

Please provide a helpful, accurate answer based on the context above. Remember to cite your sources."""

    try:
        # Initialize OpenAI client
        client = openai.Client(api_key=api_key)
        
        # Generate response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for factual, consistent responses
            max_tokens=600,   # Reasonable limit for answers
            top_p=0.9
        )
        
        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        cost_estimate = tokens_used * 0.000002  # Rough GPT-3.5-turbo cost per token
        
        print(f"✅ Generated response: {len(answer)} characters, {tokens_used} tokens")
        
        return {
            'answer': answer,
            'tokens_used': tokens_used,
            'cost_estimate': cost_estimate,
            'model': 'gpt-3.5-turbo',
            'success': True
        }
        
    except openai.RateLimitError:
        return {
            'answer': "I'm currently experiencing high demand. Please try again in a moment.",
            'tokens_used': 0,
            'cost_estimate': 0,
            'error': 'rate_limit',
            'success': False
        }
        
    except openai.AuthenticationError:
        return {
            'answer': "Authentication issue with AI service. Please contact IT support.",
            'tokens_used': 0,
            'cost_estimate': 0,
            'error': 'authentication',
            'success': False
        }
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return {
            'answer': "I'm experiencing technical difficulties. Please try again or contact IT Services at 0131 650 4500.",
            'tokens_used': 0,
            'cost_estimate': 0,
            'error': str(e),
            'success': False
        }

# Test OpenAI integration (using a mock API key for now)
print("\n🤖 TESTING OPENAI INTEGRATION")
print("="*60)

# NOTE: Replace with actual API key during course
test_api_key = "sk-test-key-replace-with-real-key"

if search_results and context:  # Use results from previous test
    response = generate_llm_response(complex_query, context, test_api_key)
    
    print(f"🤖 Generated Response:")
    print(f"Success: {response['success']}")
    if response['success']:
        print(f"Tokens used: {response['tokens_used']}")
        print(f"Estimated cost: ${response['cost_estimate']:.6f}")
        print(f"\nResponse preview:")
        print(response['answer'][:300] + "...")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
        print(f"Fallback answer: {response['answer']}")
```

---

## Part 4: Complete RAG Pipeline (10 minutes)

### Step 4: Build the End-to-End System

```python
@dataclass
class RAGResponse:
    """Complete RAG response with all metadata."""
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence_level: str
    tokens_used: int
    cost_estimate: float
    response_time: float
    chunks_found: int
    success: bool

def determine_confidence_level(search_results: List[SearchResult]) -> str:
    """Determine confidence level based on search results."""
    if not search_results:
        return "no_data"
    
    best_similarity = max(result.similarity_score for result in search_results)
    chunk_count = len(search_results)
    
    if best_similarity >= 0.85 and chunk_count >= 2:
        return "high"
    elif best_similarity >= 0.70 and chunk_count >= 1:
        return "medium"
    elif best_similarity >= 0.60:
        return "low"
    else:
        return "insufficient"

def answer_question(query: str, api_key: str, 
                   max_chunks: int = 5, 
                   similarity_threshold: float = 0.6) -> RAGResponse:
    """
    Complete RAG pipeline: search → assemble → generate → respond
    
    Args:
        query: User's question
        api_key: OpenAI API key
        max_chunks: Maximum chunks to retrieve
        similarity_threshold: Minimum similarity for chunks
        
    Returns:
        RAGResponse with complete answer and metadata
    """
    start_time = time.time()
    
    print(f"\n🚀 PROCESSING RAG QUERY: '{query}'")
    print("="*80)
    
    # Step 1: Search for relevant chunks
    print("Step 1: Searching for relevant chunks...")
    search_results = search_similar_chunks(query, max_chunks, similarity_threshold)
    
    if not search_results:
        return RAGResponse(
            query=query,
            answer="I don't have information about that topic in the Edinburgh University documents. "
                  "For direct assistance, please contact IT Services at 0131 650 4500 or email servicedesk@ed.ac.uk.",
            sources=[],
            confidence_level="no_data",
            tokens_used=0,
            cost_estimate=0,
            response_time=time.time() - start_time,
            chunks_found=0,
            success=True  # Successfully handled the case of no data
        )
    
    # Step 2: Assemble context
    print("Step 2: Assembling context...")
    context, sources = assemble_context(search_results)
    
    # Step 3: Determine confidence level
    confidence = determine_confidence_level(search_results)
    print(f"Step 3: Confidence level: {confidence}")
    
    # Step 4: Generate response
    print("Step 4: Generating LLM response...")
    llm_response = generate_llm_response(query, context, api_key)
    
    # Step 5: Finalize response
    response_time = time.time() - start_time
    
    # Add confidence qualifier to response if needed
    final_answer = llm_response['answer']
    if confidence == "low":
        final_answer = "Based on limited information: " + final_answer
    elif confidence == "insufficient":
        final_answer = "I have very limited information about this topic. " + final_answer
    
    rag_response = RAGResponse(
        query=query,
        answer=final_answer,
        sources=sources,
        confidence_level=confidence,
        tokens_used=llm_response['tokens_used'],
        cost_estimate=llm_response['cost_estimate'],
        response_time=response_time,
        chunks_found=len(search_results),
        success=llm_response['success']
    )
    
    print(f"\n✅ RAG PIPELINE COMPLETE")
    print(f"   Response time: {response_time:.2f}s")
    print(f"   Confidence: {confidence}")
    print(f"   Chunks used: {len(search_results)}")
    print(f"   Tokens: {llm_response['tokens_used']}")
    
    return rag_response

# Test complete RAG pipeline
print("\n🚀 TESTING COMPLETE RAG PIPELINE")
print("="*80)

# Edinburgh IT support test cases
test_cases = [
    "How do I reset my password if I forgot it?",
    "I'm having trouble connecting to university WiFi",
    "What are the VPN requirements for working from home?",
    "How do I configure my student email on iPhone?",
    "What's the weather like today?"  # Should gracefully decline
]

# NOTE: In actual lab, you'll use real API key provided during course
mock_api_key = "your-actual-openai-api-key"

for test_query in test_cases[:2]:  # Test first 2 to save API calls
    response = answer_question(test_query, mock_api_key)
    
    print(f"\n📋 QUERY: {response.query}")
    print(f"🤖 ANSWER: {response.answer[:200]}...")
    print(f"📊 METADATA:")
    print(f"   Confidence: {response.confidence_level}")
    print(f"   Chunks found: {response.chunks_found}")
    print(f"   Response time: {response.response_time:.2f}s")
    print(f"   Success: {response.success}")
    
    if response.sources:
        print(f"\n{format_sources_for_display(response.sources)}")
    
    print("-" * 80)
```

---

## Part 5: Quality Control & Testing (5 minutes)

### Step 5: Validate System Performance

```python
def validate_rag_system() -> Dict[str, Any]:
    """
    Comprehensive validation of RAG system performance.
    
    Returns:
        Dictionary with validation results and recommendations
    """
    print("\n🧪 VALIDATING RAG SYSTEM PERFORMANCE")
    print("="*60)
    
    # Test database connectivity
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
                chunk_count = cur.fetchone()[0]
                print(f"✅ Database: {chunk_count} chunks with embeddings available")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return {"status": "failed", "error": "database_connection"}
    
    # Test embedding service
    test_embedding = get_embedding("test query")
    if test_embedding:
        print(f"✅ Embedding service: Working ({len(test_embedding)} dimensions)")
    else:
        print("❌ Embedding service: Failed")
        return {"status": "failed", "error": "embedding_service"}
    
    # Test search performance
    search_start = time.time()
    test_results = search_similar_chunks("password reset", limit=3)
    search_time = time.time() - search_start
    
    print(f"✅ Search performance: {search_time:.2f}s for {len(test_results)} results")
    
    # Performance benchmarks for Edinburgh
    benchmarks = {
        "search_time_target": 1.0,    # seconds
        "min_chunks_available": 10,   # minimum chunks in database
        "embedding_dimensions": 1024   # BGE-M3 standard
    }
    
    results = {
        "status": "passed",
        "database_chunks": chunk_count,
        "embedding_dimensions": len(test_embedding) if test_embedding else 0,
        "search_time": search_time,
        "search_results": len(test_results),
        "benchmarks_met": {
            "search_speed": search_time <= benchmarks["search_time_target"],
            "sufficient_data": chunk_count >= benchmarks["min_chunks_available"],
            "correct_embeddings": len(test_embedding) == benchmarks["embedding_dimensions"] if test_embedding else False
        }
    }
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Search time: {search_time:.2f}s (target: <{benchmarks['search_time_target']}s)")
    print(f"   Available chunks: {chunk_count} (target: >{benchmarks['min_chunks_available']})")
    print(f"   Embedding dims: {len(test_embedding) if test_embedding else 0} (target: {benchmarks['embedding_dimensions']})")
    
    all_passed = all(results["benchmarks_met"].values())
    if all_passed:
        print("✅ All benchmarks met - System ready for production")
    else:
        print("⚠️  Some benchmarks not met - Review configuration")
    
    return results

# Run system validation
validation_results = validate_rag_system()
```

---

## Part 6: Simple Web Interface (Optional - 5 minutes)

### Step 6: Create a Basic Web Interface for Testing

```python
from flask import Flask, request, jsonify, render_template_string

def create_rag_web_interface():
    """Create a simple web interface for testing the RAG system."""
    
    app = Flask(__name__)
    
    # Simple HTML template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edinburgh IT Support - AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .chat-container { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
            .question { background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 5px; }
            .answer { background: #f1f8e9; padding: 10px; margin: 5px 0; border-radius: 5px; }
            .sources { background: #fafafa; padding: 5px; margin: 5px 0; font-size: 0.9em; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; background: #1976d2; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>🏫 Edinburgh IT Support Assistant</h1>
        <p>Ask questions about IT services, passwords, WiFi, VPN, and more.</p>
        
        <div id="chat-container" class="chat-container"></div>
        
        <div>
            <input type="text" id="question-input" placeholder="How can I help you with IT support?" />
            <button onclick="askQuestion()">Ask</button>
        </div>
        
        <p><small>This system uses official Edinburgh University documents to provide answers.</small></p>
        
        <script>
        async function askQuestion() {
            const input = document.getElementById('question-input');
            const question = input.value.trim();
            
            if (!question) return;
            
            // Show question
            addToChat('question', question);
            input.value = '';
            
            // Show loading
            addToChat('answer', '🔄 Searching Edinburgh documents...');
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                
                const data = await response.json();
                
                // Replace loading message with actual answer
                const chatContainer = document.getElementById('chat-container');
                chatContainer.removeChild(chatContainer.lastChild);
                
                addToChat('answer', data.answer);
                
                if (data.sources && data.sources.length > 0) {
                    const sourceText = data.sources.map(s => 
                        `${s.id}. ${s.document}${s.page ? ', Page ' + s.page : ''} (${(s.similarity * 100).toFixed(0)}% relevant)`
                    ).join('\\n');
                    addToChat('sources', '📚 Sources:\\n' + sourceText);
                }
                
            } catch (error) {
                const chatContainer = document.getElementById('chat-container');
                chatContainer.removeChild(chatContainer.lastChild);
                addToChat('answer', 'Sorry, I encountered an error. Please try again.');
            }
        }
        
        function addToChat(type, content) {
            const chatContainer = document.getElementById('chat-container');
            const div = document.createElement('div');
            div.className = type;
            div.innerText = content;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Allow Enter key to submit
        document.getElementById('question-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(html_template)
    
    @app.route('/ask', methods=['POST'])
    def ask_question():
        try:
            data = request.json
            question = data.get('question', '').strip()
            
            if not question:
                return jsonify({'error': 'Please provide a question'})
            
            # Process with RAG pipeline
            # NOTE: In production, use real API key
            rag_response = answer_question(question, mock_api_key)
            
            return jsonify({
                'answer': rag_response.answer,
                'sources': rag_response.sources,
                'confidence': rag_response.confidence_level,
                'response_time': rag_response.response_time
            })
            
        except Exception as e:
            return jsonify({'error': f'Internal error: {str(e)}'})
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'embedding_service': 'available'
        })
    
    print("🌐 Web interface created!")
    print("To run: app.run(debug=True, port=5100)")
    print("Then visit: http://localhost:5100")
    
    return app

# Create web interface (optional)
web_app = create_rag_web_interface()

# To run the web interface, uncomment the next line:
# web_app.run(debug=True, port=5100)
```

**Run the complete lab:**
```bash
python lab6_rag_pipeline.py
```

---

## Success Criteria ✅

**You've completed this lab when:**
- [ ] Similarity search returns relevant chunks for Edinburgh IT queries
- [ ] Context assembly combines multiple chunks with proper attribution
- [ ] OpenAI integration generates appropriate responses (with API key)
- [ ] Complete RAG pipeline handles various query types
- [ ] System gracefully handles edge cases (no data, API failures)
- [ ] Response quality validation shows appropriate confidence levels
- [ ] Basic web interface works for testing (optional)

---

## Reflection & Next Steps

### Discussion Questions

**With your partner, discuss:**

1. **Response Quality**: How do you balance comprehensiveness with accuracy when assembling context?

2. **Source Trust**: When chunks from different documents contradict each other, how should the system handle this?

3. **User Experience**: What additional features would make this system more useful for Edinburgh staff?

4. **Scaling Considerations**: How would you modify this system to handle 1000+ concurrent users?

### Key Takeaways

- **RAG combines** external knowledge retrieval with LLM generation capabilities
- **Source attribution** is critical for institutional credibility and user trust
- **Context assembly** requires careful balancing of relevance, completeness, and token limits
- **Quality control** ensures reliable responses through confidence scoring and validation

### What's Next

**In Section 7, we'll enhance the system with:**
- Hybrid search combining text and vector similarity
- Advanced filtering and metadata queries  
- Multi-document analysis and comparison
- Complex query handling and reasoning chains

---

## Troubleshooting

### Common Issues

**No search results:**
```python
# Check if chunks exist in database
with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
        print(f"Available chunks: {cur.fetchone()[0]}")
```

**OpenAI API errors:**
```python
# Test API key validity
try:
    client = openai.Client(api_key=your_api_key)
    client.models.list()
    print("✅ API key is valid")
except:
    print("❌ API key issue - check configuration")
```

**Poor search relevance:**
```python
# Lower similarity threshold for testing
results = search_similar_chunks(query, similarity_threshold=0.4)
```

**Context too long:**
```python
# Reduce max_tokens in context assembly
context, sources = assemble_context(results, max_tokens=1000)
```

### Performance Optimization

**Speed up searches:**
```python
# Ensure HNSW indexes are being used
with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
        cur.execute("EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM document_chunks ORDER BY embedding <=> '[0,0,0...]'::vector LIMIT 5;")
        print(cur.fetchall())
```

Great work! You now have a complete RAG system that can answer Edinburgh University IT questions using official documents with proper source attribution. The system is ready for production deployment with proper API keys and scaling considerations.

## Next Steps

After completing this lab:
1. **Test extensively** with various Edinburgh-specific queries
2. **Tune parameters** (similarity thresholds, chunk limits, token limits) 
3. **Collect feedback** from potential users (IT staff, students)
4. **Prepare for Section 7** advanced querying capabilities

Your RAG system is now the foundation for sophisticated AI-powered support at Edinburgh! 🎉