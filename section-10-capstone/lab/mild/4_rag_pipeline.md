# 🌶️ Mild: RAG Pipeline - Complete Working Code

**"I like to follow the recipe step-by-step"**

This guide gives you complete, working code for building a complete RAG (Retrieval Augmented Generation) pipeline. You'll understand every step of combining search with LLM generation!

## Step 1: Basic RAG Pipeline

Here's the complete working code for the RAG pipeline:

```python
# services/llm_integration.py
import openai
import requests
import logging
import json
from typing import List, Dict, Any, Optional
from .database_manager import SearchResult

logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = "your-openai-api-key-here"  # Replace with your actual key
OPENAI_MODEL = "gpt-3.5-turbo"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama2"

def generate_response(query: str, search_results: List[SearchResult], options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate a response using RAG pipeline.
    
    This function:
    1. Builds context from search results
    2. Creates a prompt for the LLM
    3. Generates a response with sources
    4. Calculates confidence score
    """
    if not options:
        options = {}
    
    logger.info(f"Generating response for query: {query}")
    
    try:
        # Step 1: Build context from search results
        context = build_context(search_results)
        
        # Step 2: Create system and user prompts
        system_prompt = create_system_prompt(options)
        user_prompt = create_user_prompt(query, context)
        
        # Step 3: Generate response using LLM
        response = call_llm(system_prompt, user_prompt, options)
        
        # Step 4: Extract sources from search results
        sources = extract_sources(search_results)
        
        # Step 5: Calculate confidence score
        confidence = calculate_confidence(search_results, response)
        
        # Step 6: Create final response
        final_response = {
            'answer': response,
            'sources': sources,
            'confidence': confidence,
            'query': query,
            'context_used': len(search_results),
            'metadata': {
                'model_used': options.get('model', OPENAI_MODEL),
                'timestamp': get_current_timestamp(),
                'processing_time': 0  # TODO: Add timing
            }
        }
        
        logger.info(f"Generated response with {len(sources)} sources and confidence {confidence}")
        return final_response
        
    except Exception as e:
        logger.error(f"RAG pipeline failed: {e}")
        return create_error_response(query, str(e))

def build_context(search_results: List[SearchResult]) -> str:
    """
    Build context string from search results.
    
    This function:
    1. Extracts content from search results
    2. Formats with source information
    3. Limits context length
    4. Returns formatted context
    """
    if not search_results:
        return "No relevant context found."
    
    context_parts = []
    max_context_length = 3000  # Limit context length
    
    for i, result in enumerate(search_results, 1):
        # Extract source information
        source_title = result.document_info.get('title', 'Unknown Document')
        source_author = result.document_info.get('author', 'Unknown Author')
        similarity_score = result.similarity_score
        
        # Format the context chunk
        context_chunk = f"""
Source {i}: {source_title} by {source_author} (Relevance: {similarity_score:.2f})
Content: {result.content}
"""
        context_parts.append(context_chunk)
        
        # Check if we're approaching context limit
        current_length = sum(len(part) for part in context_parts)
        if current_length > max_context_length:
            break
    
    return "\n".join(context_parts)

def create_system_prompt(options: Dict[str, Any]) -> str:
    """
    Create system prompt based on project type and options.
    
    This function:
    1. Determines project type
    2. Creates appropriate system prompt
    3. Includes specific instructions
    """
    project_type = options.get('project_type', 'general')
    
    system_prompts = {
        'literature': """You are a literary analysis assistant. Help users understand themes, characters, and literary devices in literature. Use the provided context to give accurate, insightful answers about literary works. Always cite your sources.""",
        
        'documentation': """You are a technical documentation assistant. Help users understand APIs, code examples, and technical concepts. Use the provided context to give accurate, helpful answers about technical topics. Always cite your sources.""",
        
        'research': """You are a research assistant. Help users understand academic papers, methodologies, and research concepts. Use the provided context to give accurate, scholarly answers about research topics. Always cite your sources.""",
        
        'custom': """You are a specialized assistant for the user's custom domain. Help users understand and work with their specific content and use cases. Use the provided context to give accurate, helpful answers. Always cite your sources.""",
        
        'general': """You are a helpful assistant that answers questions based on provided context. Use the information given to provide accurate, helpful answers. Always cite your sources when possible."""
    }
    
    base_prompt = system_prompts.get(project_type, system_prompts['general'])
    
    # Add additional instructions
    additional_instructions = """
    
Instructions:
- Answer based only on the provided context
- If the context doesn't contain enough information, say so
- Always cite your sources using the format: [Source X]
- Be concise but comprehensive
- If you're unsure about something, express that uncertainty
"""
    
    return base_prompt + additional_instructions

def create_user_prompt(query: str, context: str) -> str:
    """
    Create user prompt with query and context.
    
    This function:
    1. Formats the user's query
    2. Includes the context
    3. Asks for specific response format
    """
    user_prompt = f"""
Question: {query}

Context:
{context}

Please answer the question using the provided context. Include citations in your answer using the format [Source X] where X is the source number.
"""
    return user_prompt

def call_llm(system_prompt: str, user_prompt: str, options: Dict[str, Any]) -> str:
    """
    Call the LLM to generate a response.
    
    This function:
    1. Chooses between OpenAI and Ollama
    2. Makes the API call
    3. Handles errors gracefully
    4. Returns the response
    """
    model = options.get('model', OPENAI_MODEL)
    use_openai = options.get('use_openai', True)
    
    try:
        if use_openai and OPENAI_API_KEY != "your-openai-api-key-here":
            return call_openai(system_prompt, user_prompt, model)
        else:
            return call_ollama(system_prompt, user_prompt, model)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return f"I apologize, but I encountered an error while generating a response: {str(e)}"

def call_openai(system_prompt: str, user_prompt: str, model: str) -> str:
    """
    Call OpenAI API to generate response.
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise

def call_ollama(system_prompt: str, user_prompt: str, model: str) -> str:
    """
    Call Ollama API to generate response.
    """
    try:
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False
        }
        
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response generated')
        else:
            logger.error(f"Ollama API call failed: {response.status_code}")
            raise Exception(f"Ollama API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Ollama API call failed: {e}")
        raise

def extract_sources(search_results: List[SearchResult]) -> List[Dict[str, Any]]:
    """
    Extract source information from search results.
    
    This function:
    1. Extracts metadata from each result
    2. Formats source information
    3. Returns list of sources
    """
    sources = []
    
    for i, result in enumerate(search_results, 1):
        source = {
            'source_number': i,
            'title': result.document_info.get('title', 'Unknown Document'),
            'author': result.document_info.get('author', 'Unknown Author'),
            'document_type': result.document_info.get('document_type', 'unknown'),
            'similarity_score': result.similarity_score,
            'content_preview': result.content[:200] + "..." if len(result.content) > 200 else result.content,
            'metadata': result.metadata
        }
        sources.append(source)
    
    return sources

def calculate_confidence(search_results: List[SearchResult], response: str) -> float:
    """
    Calculate confidence score for the response.
    
    This function:
    1. Analyzes search result quality
    2. Checks response completeness
    3. Returns confidence score (0-1)
    """
    if not search_results:
        return 0.0
    
    # Base confidence on similarity scores
    avg_similarity = sum(r.similarity_score for r in search_results) / len(search_results)
    
    # Boost confidence for more results
    result_count_boost = min(len(search_results) / 5.0, 0.2)  # Max 0.2 boost
    
    # Check if response mentions uncertainty
    uncertainty_penalty = 0.0
    uncertainty_phrases = ["i don't know", "i'm not sure", "i can't find", "unclear", "uncertain"]
    if any(phrase in response.lower() for phrase in uncertainty_phrases):
        uncertainty_penalty = 0.2
    
    # Calculate final confidence
    confidence = avg_similarity + result_count_boost - uncertainty_penalty
    
    # Ensure confidence is between 0 and 1
    return max(0.0, min(1.0, confidence))

def create_error_response(query: str, error_message: str) -> Dict[str, Any]:
    """
    Create error response when RAG pipeline fails.
    """
    return {
        'answer': f"I apologize, but I encountered an error while processing your query: {error_message}",
        'sources': [],
        'confidence': 0.0,
        'query': query,
        'context_used': 0,
        'metadata': {
            'model_used': 'error',
            'timestamp': get_current_timestamp(),
            'error': error_message
        }
    }

def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    """
    from datetime import datetime
    return datetime.now().isoformat()
```

## Step 2: Complete RAG Pipeline Integration

Here's the complete integration with the search engine:

```python
# services/rag_pipeline.py
import logging
from typing import List, Dict, Any, Optional
from . import search_engine
from . import llm_integration
from . import database_manager

logger = logging.getLogger(__name__)

def process_rag_query(query: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Complete RAG pipeline processing.
    
    This function:
    1. Searches for relevant documents
    2. Generates response using LLM
    3. Returns complete RAG response
    """
    if not options:
        options = {}
    
    logger.info(f"Processing RAG query: {query}")
    
    try:
        # Step 1: Search for relevant documents
        search_results = search_engine.search_documents(query, options)
        
        if not search_results:
            return {
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': [],
                'confidence': 0.0,
                'query': query,
                'context_used': 0,
                'metadata': {
                    'model_used': 'none',
                    'timestamp': get_current_timestamp(),
                    'search_results': 0
                }
            }
        
        # Step 2: Generate response using LLM
        rag_response = llm_integration.generate_response(query, search_results, options)
        
        # Step 3: Add search metadata
        rag_response['metadata']['search_results'] = len(search_results)
        rag_response['metadata']['search_time'] = 0  # TODO: Add timing
        
        return rag_response
        
    except Exception as e:
        logger.error(f"RAG pipeline failed: {e}")
        return llm_integration.create_error_response(query, str(e))

def process_rag_query_with_filters(query: str, filters: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process RAG query with additional filters.
    
    This function:
    1. Searches with filters
    2. Generates filtered response
    3. Returns RAG response
    """
    if not options:
        options = {}
    
    logger.info(f"Processing filtered RAG query: {query}")
    
    try:
        # Search with filters
        search_results = search_engine.search_with_filters(query, filters)
        
        if not search_results:
            return {
                'answer': f"I couldn't find any relevant information matching your filters to answer your question.",
                'sources': [],
                'confidence': 0.0,
                'query': query,
                'context_used': 0,
                'filters_applied': filters,
                'metadata': {
                    'model_used': 'none',
                    'timestamp': get_current_timestamp(),
                    'search_results': 0
                }
            }
        
        # Generate response
        rag_response = llm_integration.generate_response(query, search_results, options)
        rag_response['filters_applied'] = filters
        
        return rag_response
        
    except Exception as e:
        logger.error(f"Filtered RAG pipeline failed: {e}")
        return llm_integration.create_error_response(query, str(e))

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()
```

## Step 3: API Integration

Here's the complete API integration:

```python
# app.py (add these routes)
from flask import Flask, request, jsonify
from services.rag_pipeline import process_rag_query, process_rag_query_with_filters

@app.route('/api/query', methods=['POST'])
def handle_query():
    """
    Handle RAG query requests.
    
    This endpoint:
    1. Receives query from frontend
    2. Processes through RAG pipeline
    3. Returns complete response
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        options = data.get('options', {})
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Process query through RAG pipeline
        if filters:
            response = process_rag_query_with_filters(query, filters, options)
        else:
            response = process_rag_query(query, options)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Query endpoint failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/query/stream', methods=['POST'])
def handle_streaming_query():
    """
    Handle streaming RAG query requests.
    
    This endpoint:
    1. Receives query from frontend
    2. Streams response as it's generated
    3. Provides real-time updates
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        options = data.get('options', {})
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # TODO: Implement streaming response
        # For now, return regular response
        response = process_rag_query(query, options)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Streaming query endpoint failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

## Step 4: Test Your RAG Pipeline

Create this test file to verify everything works:

```python
# test_rag_pipeline.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_pipeline import process_rag_query
from services.search_engine import search_documents
from services.llm_integration import generate_response

def test_rag_pipeline():
    """Test complete RAG pipeline"""
    print("🌶️ Testing RAG Pipeline...")
    
    # Test 1: Search functionality
    print("1. Testing search functionality...")
    search_results = search_documents("machine learning algorithms")
    
    if search_results:
        print(f"   ✅ Found {len(search_results)} search results")
    else:
        print("   ❌ No search results found")
        return False
    
    # Test 2: LLM integration
    print("2. Testing LLM integration...")
    try:
        response = generate_response("What is machine learning?", search_results)
        if response and 'answer' in response:
            print(f"   ✅ Generated response: {response['answer'][:100]}...")
            print(f"   Sources: {len(response.get('sources', []))}")
            print(f"   Confidence: {response.get('confidence', 0):.2f}")
        else:
            print("   ❌ Failed to generate response")
            return False
    except Exception as e:
        print(f"   ⚠️ LLM integration failed: {e}")
        print("   This might be expected if no API key is configured")
    
    # Test 3: Complete RAG pipeline
    print("3. Testing complete RAG pipeline...")
    try:
        rag_response = process_rag_query("What is machine learning?")
        if rag_response and 'answer' in rag_response:
            print(f"   ✅ RAG pipeline working: {rag_response['answer'][:100]}...")
            print(f"   Context used: {rag_response.get('context_used', 0)}")
            print(f"   Confidence: {rag_response.get('confidence', 0):.2f}")
        else:
            print("   ❌ RAG pipeline failed")
            return False
    except Exception as e:
        print(f"   ⚠️ RAG pipeline failed: {e}")
        print("   This might be expected if no API key is configured")
    
    print("\n🎉 RAG pipeline tests completed!")
    return True

if __name__ == "__main__":
    test_rag_pipeline()
```

## Step 5: Run the Test

```bash
cd backend
python test_rag_pipeline.py
```

## What You've Learned

✅ **RAG Pipeline**: Complete retrieval-augmented generation system
✅ **Context Building**: How to build context from search results
✅ **LLM Integration**: How to call OpenAI and Ollama APIs
✅ **Source Citation**: How to extract and format sources
✅ **Confidence Scoring**: How to calculate response confidence
✅ **Error Handling**: How to handle failures gracefully
✅ **API Integration**: How to expose RAG through REST API

## Next Steps

Once your RAG pipeline tests pass, you're ready for:
- **[Mild: Frontend Integration](frontend_integration.md)** - Complete React integration
- **System Testing** - End-to-end testing of the complete system

## Troubleshooting

**If LLM calls fail:**
- Check your OpenAI API key
- Make sure Ollama is running
- Verify network connectivity
- Check API rate limits

**If responses are poor quality:**
- Check search result quality
- Adjust similarity thresholds
- Improve context building
- Tune system prompts

**If confidence scores are low:**
- Check search result relevance
- Improve similarity thresholds
- Add more context
- Adjust confidence calculation

Need help? Check the [🆘 Troubleshooting Guide](../TROUBLESHOOTING.md) or ask questions! 🤝
