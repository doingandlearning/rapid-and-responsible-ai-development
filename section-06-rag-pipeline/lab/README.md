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

## Part 1: Set Up RAG Infrastructure 

### Task 1.1: Create Project Structure

**Your task:** Set up the basic project structure and imports.

1. **Create `lab6_rag_pipeline.py`** with the following imports:
   ```python
   import psycopg
   import requests
   import json
   import time
   import statistics
   import argparse
   import sys
   from typing import List, Dict, Any, Optional
   from dataclasses import dataclass
   from datetime import datetime
   from flask import Flask, request, jsonify, render_template_string
   ```

2. **Add configuration constants:**
   - Database configuration (same as Section 4)
   - Ollama embedding service URL and model
   - OpenAI API configuration
   - Default parameters for search and context assembly

3. **Create data classes:**
   - `SearchResult` class to represent search results
   - `RAGResponse` class to represent complete responses

**💡 Hint:** Look at the solution file for the exact structure, but implement it yourself!

---

## Part 2: Implement Similarity Search 

### Task 2.1: Create Embedding Function

**Your task:** Implement the `get_embedding()` function.

**Requirements:**
- Use Ollama BGE-M3 model for embeddings
- Include retry logic with exponential backoff
- Handle errors gracefully
- Return 1024-dimensional vectors
- Add proper logging for debugging

**Key considerations:**
- What happens if the embedding service is down?
- How many retries should you attempt?
- What's the timeout for the request?

### Task 2.2: Implement Search Function

**Your task:** Create the `search_similar_chunks()` function.

**Requirements:**
- Generate query embedding using your function from Task 2.1
- Query PostgreSQL using cosine similarity (`<=>` operator)
- Filter results by similarity threshold
- Return `SearchResult` objects
- Include proper error handling

**SQL Query structure:**
```sql
SELECT id, text, document_title, page_number, section_title,
       1 - (embedding <=> %s::vector) as similarity_score
FROM document_chunks
WHERE embedding IS NOT NULL
ORDER BY embedding <=> %s::vector
LIMIT %s;
```

**Test your implementation:**
- Try queries like "password reset", "WiFi connection", "VPN setup"
- Verify similarity scores are reasonable (0.0 to 1.0)
- Check that results are properly sorted by relevance
- **Note**: For this dataset, similarity scores typically range from 0.4-0.7, so use threshold 0.4

---

## Part 3: Context Assembly 

### Task 3.1: Implement Context Assembly

**Your task:** Create the `assemble_context()` function.

**Requirements:**
- Combine multiple search results into coherent context
- Add source attribution for each chunk
- Respect token limits (estimate 4 characters per token)
- Create source metadata for citations
- Handle empty search results gracefully

**Context format:**
```
[Source 1: Document Title, Page X - Section Title]
Chunk text content here...

[Source 2: Document Title, Page Y]
More chunk text...
```

### Task 3.2: Create Source Display Function

**Your task:** Implement `format_sources_for_display()`.

**Requirements:**
- Format sources for user-friendly display
- Include document name, page number, section
- Show similarity scores as percentages
- Handle missing metadata gracefully

**Test your implementation:**
- Use a complex query that should return multiple chunks
- Verify context doesn't exceed token limits
- Check that source attribution is clear and accurate

---

## Part 4: OpenAI Integration 

### Task 4.1: Implement LLM Response Generation

**Your task:** Create the `generate_llm_response()` function.

**Requirements:**
- Use direct HTTP API calls (not the OpenAI library)
- Include Edinburgh-specific system prompt
- Handle rate limiting and authentication errors
- Return structured response with metadata
- Include proper error handling for all failure modes

**System prompt should include:**
- Role as Edinburgh IT assistant
- Requirement to cite sources
- Professional tone guidelines
- Instructions for handling unknown information

### Task 4.2: Add Error Handling

**Your task:** Implement comprehensive error handling.

**Error types to handle:**
- Rate limiting (HTTP 429)
- Authentication errors (HTTP 401)
- Network timeouts
- Invalid API responses
- General exceptions

**Each error should:**
- Return a user-friendly message
- Include appropriate fallback behavior
- Log the error for debugging
- Maintain system stability

---

## Part 5: Complete RAG Pipeline 

### Task 5.1: Implement Main Pipeline Function

**Your task:** Create the `answer_question()` function that orchestrates the entire RAG pipeline.

**Pipeline steps:**
1. Search for relevant chunks
2. Assemble context from results
3. Determine confidence level
4. Generate LLM response
5. Return complete RAG response

### Task 5.2: Add Confidence Scoring

**Your task:** Implement `determine_confidence_level()`.

**Confidence levels:**
- **High**: Best similarity ≥ 0.70 AND ≥ 2 chunks
- **Medium**: Best similarity ≥ 0.55 AND ≥ 1 chunk
- **Low**: Best similarity ≥ 0.45
- **Insufficient**: Best similarity < 0.45
- **No data**: No chunks found

### Task 5.3: Handle Edge Cases

**Your task:** Ensure your pipeline handles these scenarios:

- No relevant chunks found
- API failures
- Empty or invalid queries
- Very long responses
- Low confidence results

**Test with these queries:**
- "How do I reset my password?" (should work)
- "What's the weather today?" (should decline gracefully)
- "Tell me about quantum computing" (should decline gracefully)

---

## Part 6: System Validation 

### Task 6.1: Implement Validation Function

**Your task:** Create `validate_rag_system()` to test system health.

**Validation checks:**
- Database connectivity and chunk count
- Embedding service availability
- Search performance benchmarks
- Response time targets

**Benchmarks:**
- Search time: < 1.0 seconds
- Minimum chunks: ≥ 10
- Embedding dimensions: 1024

### Task 6.2: Add Performance Monitoring

**Your task:** Include performance metrics in your responses.

**Metrics to track:**
- Response time
- Tokens used
- Chunks found
- Confidence level
- Success/failure status

---

## Part 7: Web Interface (Optional - 5 minutes)

### Task 7.1: Create Basic Web Interface

**Your task:** Implement a simple Flask web interface for testing.

**Requirements:**
- Clean, professional UI for Edinburgh staff
- Real-time chat interface
- Source citation display
- Error handling
- Loading indicators

### Task 7.2: Add Command Line Interface

**Your task:** Create a main function with command-line options.

**Options to include:**
- `--web`: Start web interface
- `--port`: Specify port number
- `--debug`: Enable debug mode
- `--no-debug`: Disable debug mode

---

## Testing Your Implementation

### Test Cases

**Run these test queries to validate your system:**

1. **Password reset**: "How do I reset my university password?"
2. **WiFi issues**: "I can't connect to WiFi on campus"
3. **VPN setup**: "What are the VPN requirements for remote work?"
4. **Email configuration**: "How do I configure student email on my phone?"
5. **Invalid query**: "What's the weather like today?"

### Expected Behavior

- **Valid queries**: Should return helpful answers with source citations
- **Invalid queries**: Should gracefully decline with contact information
- **All responses**: Should include confidence levels and response times
- **Error cases**: Should handle failures gracefully

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
    response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    print("✅ API key is valid")
except:
    print("❌ API key issue - check configuration")
```

**Poor search relevance:**
```python
# Lower similarity threshold for testing
results = search_similar_chunks(query, similarity_threshold=0.4)
```

**No search results (most common issue):**

```python
# Check what similarity scores you're actually getting
results = search_similar_chunks(query, limit=10, similarity_threshold=0.0)
for result in results:
    print(f"Similarity: {result.similarity_score:.3f} - {result.document_title}")

# Then adjust threshold based on actual scores
# For this dataset, 0.4 works well, but 0.6 is too high
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

## Next Steps

After completing this lab:

1. **Test extensively** with various Edinburgh-specific queries
2. **Tune parameters** (similarity thresholds, chunk limits, token limits)
3. **Collect feedback** from potential users (IT staff, students)
4. **Prepare for Section 7** advanced querying capabilities

Your RAG system is now the foundation for sophisticated AI-powered support at Edinburgh! 🎉
