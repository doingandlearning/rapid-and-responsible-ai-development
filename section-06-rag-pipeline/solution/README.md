# Section 6 Solution Files

## Complete RAG Pipeline Implementation
This directory contains the complete, working solution for Section 6: RAG Pipeline Integration.

## Files Included

### `lab6_rag_pipeline.py`
**Complete RAG system implementation** with all lab requirements:
- Similarity search using document chunks from Section 5
- Context assembly with proper source attribution  
- OpenAI API integration for intelligent response generation
- Complete Q&A pipeline with error handling
- Quality validation and confidence scoring
- Web interface for interactive testing
- Performance monitoring and optimization

## Running the Solution

### Prerequisites
Ensure your environment is ready:
```bash
# Start services (from repository root)
cd environment && docker compose up -d

# Activate Python environment
source .venv/bin/activate

# Verify Section 5 chunks are available
python -c "import psycopg; conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL'); print(f'Available chunks: {cur.fetchone()[0]}')"

# Set OpenAI API key (provided during course)
export OPENAI_API_KEY="your-api-key-here"
```

### Execute Complete Solution
```bash
cd final_materials/section-06-rag-pipeline/solution
python lab6_rag_pipeline.py
```

### Optional: Run Web Interface
```bash
# In a separate terminal, after running the main solution
python -c "from lab6_rag_pipeline import create_rag_web_interface; create_rag_web_interface().run(debug=True, port=5100)"

# Then visit: http://localhost:5100
```

## Expected Output

### 1. System Validation Phase
```
🚀 SECTION 6: RAG PIPELINE INTEGRATION
================================================================================
Edinburgh University AI-Powered IT Support System

STEP 1: SYSTEM VALIDATION
----------------------------------------
🧪 VALIDATING RAG SYSTEM PERFORMANCE
============================================================
✅ Database: 25 chunks with embeddings available
✅ Embedding service: Working (1024 dimensions)
✅ Search performance: 0.15s for 3 results

📊 VALIDATION RESULTS:
   Search time: 0.15s (target: <1.0s)
   Available chunks: 25 (target: >10)
   Embedding dims: 1024 (target: 1024)
✅ All benchmarks met - System ready for production
```

### 2. Similarity Search Testing Phase
```
STEP 2: SIMILARITY SEARCH TESTING
----------------------------------------

🔍 Testing query: 'How do I reset my university password?'
🔍 Searching for chunks similar to: 'How do I reset my university password?'
✅ Found 3 relevant chunks (similarity > 0.6)
   ✅ Found 3 relevant chunks:
      1. Edinburgh IT Support Handbook (Page 1) - 0.891
      2. Student Account Guide (Page 3) - 0.823  
      3. Password Policy Document (Page 2) - 0.767

🔍 Testing query: 'I can't connect to WiFi on campus'
🔍 Searching for chunks similar to: 'I can't connect to WiFi on campus'
✅ Found 2 relevant chunks (similarity > 0.6)
   ✅ Found 2 relevant chunks:
      1. Student WiFi Guide (Page 1) - 0.885
      2. Network Troubleshooting Guide (Page 4) - 0.734
```

### 3. Context Assembly Testing Phase
```
STEP 3: CONTEXT ASSEMBLY TESTING
----------------------------------------
🔍 Testing query: 'How do I set up university email and WiFi access?'
🔍 Searching for chunks similar to: 'How do I set up university email and WiFi access?'
🧩 Assembling context from 4 chunks...
   ✅ Added chunk 1: Student WiFi Guide (285 tokens)
   ✅ Added chunk 2: Email Configuration Guide (312 tokens)
   ✅ Added chunk 3: IT Support Handbook (298 tokens)
   ✅ Added chunk 4: Account Setup Guide (267 tokens)
📊 Final context: 1162 estimated tokens from 4 sources

📄 Assembled context for: 'How do I set up university email and WiFi access?'
   Context length: 1847 characters
   Sources included: 4

📚 Sources:
  1. Student WiFi Guide, Page 1 - Relevance: 0.88
  2. Email Configuration Guide, Page 2 (Email Setup) - Relevance: 0.84
  3. IT Support Handbook, Page 15 (Network Access) - Relevance: 0.79
  4. Account Setup Guide, Page 1 - Relevance: 0.72
```

### 4. Complete RAG Pipeline Testing Phase
```
STEP 4: COMPLETE RAG PIPELINE TESTING
----------------------------------------
🤖 Testing with OpenAI API...

📋 Query: 'How do I reset my university password?'

🚀 PROCESSING RAG QUERY: 'How do I reset my university password?'
================================================================================
Step 1: Searching for relevant chunks...
🔍 Searching for chunks similar to: 'How do I reset my university password?'
✅ Found 3 relevant chunks (similarity > 0.6)

Step 2: Assembling context...
🧩 Assembling context from 3 chunks...
   ✅ Added chunk 1: Edinburgh IT Support Handbook (289 tokens)
   ✅ Added chunk 2: Password Policy Document (234 tokens)  
   ✅ Added chunk 3: Student Account Guide (198 tokens)
📊 Final context: 721 estimated tokens from 3 sources

Step 3: Confidence level: high
Step 4: Generating LLM response...
🤖 Generating LLM response for: 'How do I reset my university password?'...
✅ Generated response: 432 characters, 87 tokens

✅ RAG PIPELINE COMPLETE
   Response time: 3.24s
   Confidence: high
   Chunks used: 3
   Tokens: 87

✅ Response generated:
   Confidence: high
   Chunks found: 3
   Response time: 3.24s
   Tokens used: 87
   Success: True

🤖 Answer preview: To reset your Edinburgh University password, follow these steps:

1. Visit https://password.ed.ac.uk using any web browser
2. Enter your university username (not your email address)
3. Verify identity using your registered mobile number...

📚 Sources:
  1. Edinburgh IT Support Handbook, Page 1 - Relevance: 0.89
  2. Password Policy Document, Page 2 (Password Management) - Relevance: 0.82
  3. Student Account Guide, Page 3 (Account Recovery) - Relevance: 0.77
```

### 5. Web Interface Setup Phase
```
STEP 5: WEB INTERFACE SETUP
----------------------------------------
🌐 Web interface created successfully!
To test the web interface:
   1. Run: python lab6_rag_pipeline.py
   2. In another terminal: python -c "from lab6_rag_pipeline import create_rag_web_interface; create_rag_web_interface().run(debug=True, port=5100)"
   3. Visit: http://localhost:5100
```

### 6. Success Summary
```
================================================================================
✅ SECTION 6 COMPLETE!
Successfully built Edinburgh's AI-powered IT support system:
  • Similarity search with pgvector integration
  • Context assembly with proper source attribution
  • OpenAI integration for intelligent responses
  • Quality validation and confidence scoring
  • Complete RAG pipeline with error handling
  • Web interface for user testing

💡 System capabilities:
  • Database chunks: 25
  • Search performance: 0.15s
  • Embedding dimensions: 1024

🎯 Ready for Section 7: Advanced Vector Queries!
```

## Understanding the Implementation

### Key Components

#### 1. Complete RAG Pipeline
```python
def answer_question(query: str, api_key: str) -> RAGResponse:
    # Step 1: Generate query embedding
    search_results = search_similar_chunks(query)
    
    # Step 2: Assemble context with citations
    context, sources = assemble_context(search_results)
    
    # Step 3: Generate LLM response
    response = generate_llm_response(query, context, api_key)
    
    # Step 4: Package complete response
    return RAGResponse(answer, sources, confidence, metadata)
```

#### 2. Similarity Search Implementation
```python
def search_similar_chunks(query: str, limit: int = 5) -> List[SearchResult]:
    query_embedding = get_embedding(query)
    
    # Use pgvector cosine similarity
    cur.execute("""
        SELECT text, document_title, page_number, section_title,
               1 - (embedding <=> %s::vector) as similarity_score
        FROM document_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (query_embedding, query_embedding, limit))
```

#### 3. Context Assembly with Attribution
```python
def assemble_context(search_results: List[SearchResult]) -> tuple:
    context_parts = []
    sources = []
    
    for i, result in enumerate(search_results):
        # Format with source attribution
        chunk_text = f"""
[Source {i+1}: {result.document_title}, Page {result.page_number}]
{result.text}
"""
        context_parts.append(chunk_text)
        sources.append(source_metadata)
    
    return "\n".join(context_parts), sources
```

#### 4. OpenAI Integration with Edinburgh Context
```python
def generate_llm_response(query: str, context: str, api_key: str):
    system_prompt = """You are an AI assistant for Edinburgh University's IT Services.
    
    - Answer using ONLY the provided context from official documents
    - Always cite sources: (Source: Document Name, Page X)
    - Use professional language appropriate for university staff
    - Focus on practical, actionable guidance"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ],
        temperature=0.1  # Low temperature for factual accuracy
    )
```

#### 5. Quality Control and Confidence Scoring
```python
def determine_confidence_level(search_results: List[SearchResult]) -> str:
    best_similarity = max(r.similarity_score for r in search_results)
    chunk_count = len(search_results)
    
    if best_similarity >= 0.85 and chunk_count >= 2:
        return "high"
    elif best_similarity >= 0.70:
        return "medium"
    elif best_similarity >= 0.60:
        return "low"
    else:
        return "insufficient"
```

## Customization Options

### RAG Configuration
Modify system behavior by adjusting parameters:
```python
# In answer_question function
response = answer_question(
    query, 
    api_key,
    max_chunks=7,              # More context sources
    similarity_threshold=0.65  # Lower threshold for broader results
)
```

### Edinburgh-Specific Prompting
Customize system prompts for different departments:
```python
system_prompts = {
    'it_support': "You are an IT support specialist...",
    'library': "You are a library services assistant...",  
    'admissions': "You are an admissions office assistant..."
}
```

### Response Formatting
Adjust output style for different user groups:
```python
def format_response(answer: str, audience: str) -> str:
    if audience == 'students':
        return f"Hi! {answer}\n\nNeed more help? Contact Student Services!"
    elif audience == 'staff':
        return f"{answer}\n\nFor additional support: IT Service Desk (0131 650 4500)"
```

## Troubleshooting

### Common Issues

**"No relevant chunks found"**
```bash
# Check if Section 5 data is available
python -c "
import psycopg
conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL')
print(f'Chunks with embeddings: {cur.fetchone()[0]}')
"
```

**"OpenAI Authentication Error"**
```bash
# Verify API key is set correctly
echo $OPENAI_API_KEY

# Test API key validity
python -c "
import openai
client = openai.Client(api_key='$OPENAI_API_KEY')
try:
    client.models.list()
    print('✅ API key is valid')
except:
    print('❌ API key is invalid')
"
```

**"Slow similarity search"**
```sql
-- Check if HNSW indexes are being used
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM document_chunks 
ORDER BY embedding <=> '[0,0,0...]'::vector 
LIMIT 5;
```

**"Poor response quality"**
```python
# Lower similarity threshold for testing
results = search_similar_chunks(query, similarity_threshold=0.4)

# Check embedding quality
query_embedding = get_embedding("test query")
print(f"Embedding dimensions: {len(query_embedding)}")
print(f"Sample values: {query_embedding[:5]}")
```

### Performance Optimization

**For High-Volume Usage:**
```python
# Implement response caching
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_answer_question(query_hash: str, query: str, api_key: str):
    return answer_question(query, api_key)
```

**For Better Search Results:**
```python
# Use multiple similarity thresholds
def multi_threshold_search(query: str):
    # Try high threshold first
    results = search_similar_chunks(query, similarity_threshold=0.8)
    if not results:
        # Fall back to lower threshold
        results = search_similar_chunks(query, similarity_threshold=0.6)
    return results
```

## Web Interface Features

### Interactive Testing
The web interface provides:
- **Real-time chat interface** for testing queries
- **Response time monitoring** for performance analysis
- **Source citation display** for verification
- **Confidence level indicators** for quality assessment
- **Professional Edinburgh University styling**

### API Endpoints
```python
# Question answering endpoint
POST /ask
{
  "question": "How do I reset my password?"
}

# Returns:
{
  "answer": "To reset your Edinburgh University password...",
  "sources": [{"document": "IT Handbook", "page": 15, ...}],
  "confidence": "high",
  "response_time": 2.34
}

# Health check endpoint  
GET /health
# Returns system status and component health
```

## Next Steps

After running this solution successfully:

1. **Test with various queries** to understand system capabilities
2. **Analyze response quality** using the built-in confidence scoring
3. **Experiment with parameters** (similarity thresholds, chunk limits)
4. **Prepare for Section 7** advanced querying capabilities

The RAG system created by this solution is production-ready and can serve as the foundation for Edinburgh University's AI-powered support systems.

## Validation Checklist

Confirm your solution works correctly:

- [ ] System validation passes all benchmarks
- [ ] Similarity search returns relevant chunks for Edinburgh queries  
- [ ] Context assembly combines multiple sources with proper attribution
- [ ] OpenAI integration generates appropriate responses (with valid API key)
- [ ] Complete RAG pipeline handles various query types effectively
- [ ] Error handling manages edge cases gracefully
- [ ] Web interface loads and responds to user input
- [ ] Source citations are complete and properly formatted
- [ ] Response quality meets professional standards

**Success = Complete RAG System Ready for Advanced Querying! 🎉**