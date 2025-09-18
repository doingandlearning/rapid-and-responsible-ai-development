#!/usr/bin/env python3
"""
Section 6: RAG Pipeline Integration - Complete Solution
Edinburgh University AI-Powered IT Support System
"""

import psycopg
import requests
import json
import time
import statistics
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

# Database configuration
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
OPENAI_API_KEY = "your-api-key-here"  # Replace with actual key
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

@dataclass
class SearchResult:
    """Represents a search result chunk."""
    text: str
    document_title: str
    page_number: Optional[int]
    section_title: Optional[str]
    similarity_score: float
    chunk_id: str

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
    """Search for document chunks similar to the user query."""
    print(f"🔍 Searching for chunks similar to: '{query}'")
    
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate query embedding")
        return []
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
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

def assemble_context(search_results: List[SearchResult], 
                    max_tokens: int = 2000) -> tuple[str, List[Dict[str, Any]]]:
    """Assemble search results into coherent context for LLM input."""
    if not search_results:
        return "", []
    
    context_parts = []
    sources = []
    total_tokens = 0
    
    print(f"🧩 Assembling context from {len(search_results)} chunks...")
    
    for i, result in enumerate(search_results):
        source_info = {
            'id': i + 1,
            'document': result.document_title,
            'page': result.page_number,
            'section': result.section_title,
            'similarity': result.similarity_score
        }
        
        chunk_text = f"""
[Source {i+1}: {result.document_title}"""
        
        if result.page_number:
            chunk_text += f", Page {result.page_number}"
        if result.section_title:
            chunk_text += f" - {result.section_title}"
            
        chunk_text += f"]\n{result.text}\n"
        
        chunk_tokens = len(chunk_text) // 4
        
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

def generate_llm_response(query: str, context: str, api_key: str) -> Dict[str, Any]:
    """Generate response using OpenAI API with Edinburgh-specific prompting."""
    print(f"🤖 Generating LLM response for: '{query[:50]}...'")
    
    system_prompt = """You are an AI assistant for Edinburgh University's IT Services.

Your role and responsibilities:
- Provide accurate, helpful answers using ONLY the context from official Edinburgh University documents
- Always cite your sources using the format: (Source: Document Name, Page X)
- If the context doesn't contain relevant information, clearly state "I don't have that information in the available documents"
- Use professional, helpful language appropriate for university staff and students
- Focus on practical, actionable guidance
- When procedures have multiple steps, present them clearly

Remember: University staff rely on accurate information for their daily work. Be precise and cite all information properly."""

    user_prompt = f"""Context from Edinburgh University documents:

{context}

User Question: {query}

Please provide a helpful, accurate answer based on the context above. Remember to cite your sources."""

    try:
        # Prepare the request payload
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 600,
            "top_p": 0.9
        }
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Make the API request
        response = requests.post(
            OPENAI_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        
        # Extract the answer and usage information
        answer = response_data['choices'][0]['message']['content']
        usage = response_data.get('usage', {})
        tokens_used = usage.get('total_tokens', 0)
        cost_estimate = tokens_used * 0.000002  # Approximate cost for gpt-3.5-turbo
        
        print(f"✅ Generated response: {len(answer)} characters, {tokens_used} tokens")
        
        return {
            'answer': answer,
            'tokens_used': tokens_used,
            'cost_estimate': cost_estimate,
            'model': 'gpt-3.5-turbo',
            'success': True
        }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return {
                'answer': "I'm currently experiencing high demand. Please try again in a moment.",
                'tokens_used': 0,
                'cost_estimate': 0,
                'error': 'rate_limit',
                'success': False
            }
        elif e.response.status_code == 401:
            return {
                'answer': "Authentication issue with AI service. Please contact IT support.",
                'tokens_used': 0,
                'cost_estimate': 0,
                'error': 'authentication',
                'success': False
            }
        else:
            print(f"❌ OpenAI API HTTP error: {e}")
            return {
                'answer': f"I'm experiencing technical difficulties (HTTP {e.response.status_code}). Please try again or contact IT Services at 0131 650 4500.",
                'tokens_used': 0,
                'cost_estimate': 0,
                'error': f'http_error_{e.response.status_code}',
                'success': False
            }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAI API request error: {e}")
        return {
            'answer': "I'm experiencing network difficulties. Please try again or contact IT Services at 0131 650 4500.",
            'tokens_used': 0,
            'cost_estimate': 0,
            'error': 'network_error',
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
    """Complete RAG pipeline: search → assemble → generate → respond"""
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
            success=True
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

def validate_rag_system() -> Dict[str, Any]:
    """Comprehensive validation of RAG system performance."""
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
    
    benchmarks = {
        "search_time_target": 1.0,
        "min_chunks_available": 10,
        "embedding_dimensions": 1024
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

def create_rag_web_interface():
    """Create a simple web interface for testing the RAG system."""
    
    app = Flask(__name__)
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edinburgh IT Support - AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .header { background: #1976d2; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .chat-container { background: white; border: 1px solid #ccc; height: 500px; overflow-y: scroll; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .question { background: #e3f2fd; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 4px solid #1976d2; }
            .answer { background: #f1f8e9; padding: 12px; margin: 8px 0; border-radius: 5px; border-left: 4px solid #4caf50; }
            .sources { background: #fafafa; padding: 8px; margin: 5px 0; font-size: 0.9em; border-radius: 3px; border-left: 3px solid #ff9800; }
            .metadata { color: #666; font-size: 0.8em; margin-top: 5px; }
            .input-container { background: white; padding: 15px; border-radius: 5px; }
            input[type="text"] { width: 75%; padding: 12px; border: 1px solid #ddd; border-radius: 3px; }
            button { padding: 12px 25px; background: #1976d2; color: white; border: none; cursor: pointer; border-radius: 3px; margin-left: 10px; }
            button:hover { background: #1565c0; }
            .loading { color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏫 Edinburgh IT Support Assistant</h1>
            <p>Ask questions about IT services, passwords, WiFi, VPN, email configuration, and more.</p>
        </div>
        
        <div id="chat-container" class="chat-container">
            <div class="answer">
                <strong>Edinburgh IT Assistant:</strong> Hello! I'm here to help with IT support questions using official Edinburgh University documents. 
                What would you like to know about?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="question-input" placeholder="e.g., How do I reset my password?" />
            <button onclick="askQuestion()">Ask Question</button>
        </div>
        
        <p><small><strong>Note:</strong> This system uses official Edinburgh University documents to provide answers with source citations.</small></p>
        
        <script>
        async function askQuestion() {
            const input = document.getElementById('question-input');
            const question = input.value.trim();
            
            if (!question) return;
            
            // Show question
            addToChat('question', `<strong>You:</strong> ${question}`);
            input.value = '';
            
            // Show loading
            const loadingId = addToChat('answer', '<span class="loading">🔄 Searching Edinburgh University documents...</span>');
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                
                const data = await response.json();
                
                // Remove loading message
                document.getElementById(loadingId).remove();
                
                // Add actual answer
                let answerHtml = `<strong>Edinburgh IT Assistant:</strong> ${data.answer}`;
                
                if (data.confidence) {
                    const confidenceEmoji = data.confidence === 'high' ? '✅' : 
                                          data.confidence === 'medium' ? '⚠️' : 
                                          data.confidence === 'low' ? '❓' : '❌';
                    answerHtml += `<div class="metadata">${confidenceEmoji} Confidence: ${data.confidence}</div>`;
                }
                
                if (data.response_time) {
                    answerHtml += `<div class="metadata">⏱️ Response time: ${data.response_time.toFixed(2)}s</div>`;
                }
                
                addToChat('answer', answerHtml);
                
                // Add sources if available
                if (data.sources && data.sources.length > 0) {
                    const sourceHtml = '<strong>📚 Sources:</strong><br>' + 
                        data.sources.map(s => 
                            `${s.id}. ${s.document}${s.page ? ', Page ' + s.page : ''} 
                             ${s.section ? '(' + s.section + ')' : ''} 
                             - ${Math.round(s.similarity * 100)}% relevant`
                        ).join('<br>');
                    addToChat('sources', sourceHtml);
                }
                
            } catch (error) {
                // Remove loading message
                document.getElementById(loadingId).remove();
                addToChat('answer', '<strong>Edinburgh IT Assistant:</strong> Sorry, I encountered an error. Please try again or contact IT Services directly at 0131 650 4500.');
            }
        }
        
        function addToChat(type, content) {
            const chatContainer = document.getElementById('chat-container');
            const div = document.createElement('div');
            const id = 'msg-' + Date.now();
            div.id = id;
            div.className = type;
            div.innerHTML = content;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return id;
        }
        
        // Allow Enter key to submit
        document.getElementById('question-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
        
        // Focus on input
        document.getElementById('question-input').focus();
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(html_template)
    
    @app.route('/ask', methods=['POST'])
    def ask_question_endpoint():
        try:
            data = request.json
            question = data.get('question', '').strip()
            
            if not question:
                return jsonify({'error': 'Please provide a question'})
            
            # Process with RAG pipeline
            rag_response = answer_question(question, OPENAI_API_KEY)
            
            return jsonify({
                'answer': rag_response.answer,
                'sources': rag_response.sources,
                'confidence': rag_response.confidence_level,
                'response_time': rag_response.response_time,
                'chunks_found': rag_response.chunks_found,
                'tokens_used': rag_response.tokens_used
            })
            
        except Exception as e:
            return jsonify({'error': f'Internal error: {str(e)}'})
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    
    return app

def main():
    """Main RAG system demonstration and testing."""
    print("🚀 SECTION 6: RAG PIPELINE INTEGRATION")
    print("="*80)
    print("Edinburgh University AI-Powered IT Support System\n")
    
    # Step 1: System validation
    print("STEP 1: SYSTEM VALIDATION")
    print("-" * 40)
    validation_results = validate_rag_system()
    
    if validation_results["status"] != "passed":
        print("❌ System validation failed. Please check configuration.")
        return 1
    
    # Step 2: Similarity search testing
    print("\nSTEP 2: SIMILARITY SEARCH TESTING")
    print("-" * 40)
    
    test_queries = [
        "How do I reset my university password?",
        "I can't connect to WiFi on campus",
        "What are the VPN requirements for remote work?",
        "How do I configure student email on my phone?",
        "What's the process for two-factor authentication?"
    ]
    
    for query in test_queries[:3]:  # Test first 3 queries
        print(f"\n🔍 Testing query: '{query}'")
        results = search_similar_chunks(query, limit=3, similarity_threshold=0.6)
        
        if results:
            print(f"   ✅ Found {len(results)} relevant chunks:")
            for i, result in enumerate(results, 1):
                print(f"      {i}. {result.document_title} (Page {result.page_number}) - {result.similarity_score:.3f}")
        else:
            print("   ❌ No relevant chunks found")
    
    # Step 3: Context assembly testing
    print(f"\nSTEP 3: CONTEXT ASSEMBLY TESTING")
    print("-" * 40)
    
    complex_query = "How do I set up university email and WiFi access?"
    search_results = search_similar_chunks(complex_query, limit=4, similarity_threshold=0.6)
    
    if search_results:
        context, sources = assemble_context(search_results, max_tokens=1500)
        print(f"📄 Assembled context for: '{complex_query}'")
        print(f"   Context length: {len(context)} characters")
        print(f"   Sources included: {len(sources)}")
        print(f"\n{format_sources_for_display(sources)}")
    
    # Step 4: Complete RAG pipeline testing
    print(f"\nSTEP 4: COMPLETE RAG PIPELINE TESTING")
    print("-" * 40)
    
    # Test with and without API key
    if OPENAI_API_KEY and OPENAI_API_KEY != "your-api-key-here":
        print("🤖 Testing with OpenAI API...")
        
        for query in test_queries[:2]:  # Test 2 queries to avoid API costs
            print(f"\n📋 Query: '{query}'")
            response = answer_question(query, OPENAI_API_KEY)
            
            print(f"✅ Response generated:")
            print(f"   Confidence: {response.confidence_level}")
            print(f"   Chunks found: {response.chunks_found}")
            print(f"   Response time: {response.response_time:.2f}s")
            print(f"   Tokens used: {response.tokens_used}")
            print(f"   Success: {response.success}")
            
            if response.answer:
                print(f"\n🤖 Answer preview: {response.answer[:200]}...")
            
            if response.sources:
                print(f"\n{format_sources_for_display(response.sources)}")
            
            print("-" * 60)
    else:
        print("⚠️  OpenAI API key not configured - testing search and context only")
        
        for query in test_queries[:2]:
            print(f"\n📋 Query: '{query}'")
            mock_response = answer_question(query, "mock-key")
            print(f"   Chunks found: {mock_response.chunks_found}")
            print(f"   Confidence: {mock_response.confidence_level}")
            print(f"   Fallback answer: {mock_response.answer}")
    
    # Step 5: Web interface setup
    print(f"\nSTEP 5: WEB INTERFACE SETUP")
    print("-" * 40)
    
    web_app = create_rag_web_interface()
    print("🌐 Web interface created successfully!")
    print("To test the web interface:")
    print("   1. Run: python lab6_rag_pipeline.py")
    print("   2. In another terminal: python -c \"from lab6_rag_pipeline import create_rag_web_interface; create_rag_web_interface().run(debug=True, port=5100)\"")
    print("   3. Visit: http://localhost:5100")
    
    # Summary
    print(f"\n" + "="*80)
    print("✅ SECTION 6 COMPLETE!")
    print("Successfully built Edinburgh's AI-powered IT support system:")
    print("  • Similarity search with pgvector integration")
    print("  • Context assembly with proper source attribution")
    print("  • OpenAI integration for intelligent responses") 
    print("  • Quality validation and confidence scoring")
    print("  • Complete RAG pipeline with error handling")
    print("  • Web interface for user testing")
    
    print(f"\n💡 System capabilities:")
    print(f"  • Database chunks: {validation_results['database_chunks']}")
    print(f"  • Search performance: {validation_results['search_time']:.2f}s")
    print(f"  • Embedding dimensions: {validation_results['embedding_dimensions']}")
    
    print(f"\n🎯 Ready for Section 7: Advanced Vector Queries!")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)