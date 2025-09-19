# 03_healthcheck_app.py
# Exercise 3: Healthcheck endpoint (Flask).
# Run: python 03_healthcheck_app.py

import time
from flask import Flask, jsonify
import sys
import os
sys.path.append(os.path.dirname(__file__))
from common import check_database_health, check_embedding_health, check_rag_pipeline_health, get_rag_pipeline

app = Flask(__name__)

@app.route("/health")
def health():
    """
    TODO: Implement comprehensive health check for the RAG system
    1. Check database health using check_database_health()
    2. Check embedding health using check_embedding_health()
    3. Check pipeline health using check_rag_pipeline_health()
    4. Calculate overall status (healthy/degraded)
    5. Return JSON response with status, timestamp, latency, and checks
    """
    start_time = time.time()
    
    # TODO: Check individual components
    # db_ok = check_database_health()
    # embedding_ok = check_embedding_health()
    # pipeline_ok = check_rag_pipeline_health()
    
    # TODO: Calculate overall status
    # all_healthy = db_ok and embedding_ok and pipeline_ok
    # status = "healthy" if all_healthy else "degraded"
    
    # TODO: Calculate response time
    # response_time_ms = int((time.time() - start_time) * 1000)
    
    # TODO: Prepare and return health data
    health_data = {
        "status": "TODO",  # Replace with actual status
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "latency_ms": 0,  # TODO: Calculate actual latency
        "checks": {
            "database": {
                "status": "TODO",  # TODO: Set based on db_ok
                "description": "PostgreSQL connection and data availability"
            },
            "embedding": {
                "status": "TODO",  # TODO: Set based on embedding_ok
                "description": "Ollama embedding service"
            },
            "pipeline": {
                "status": "TODO",  # TODO: Set based on pipeline_ok
                "description": "Complete RAG pipeline functionality"
            }
        }
    }
    
    # TODO: Add diagnostics if any component is unhealthy
    # if not all_healthy:
    #     health_data["diagnostics"] = []
    #     if not db_ok:
    #         health_data["diagnostics"].append("Database connection failed or no embeddings found")
    #     if not embedding_ok:
    #         health_data["diagnostics"].append("Embedding service unavailable or returning invalid results")
    #     if not pipeline_ok:
    #         health_data["diagnostics"].append("RAG pipeline failed to process test query")
    
    return jsonify(health_data)

@app.route("/health/detailed")
def detailed_health():
    """
    TODO: Implement detailed health check with more information
    1. Test database with chunk count details
    2. Test embedding with dimension details
    3. Test pipeline with confidence details
    4. Return comprehensive health information
    """
    start_time = time.time()
    
    # TODO: Test database with more details
    # try:
    #     from common import get_conn
    #     with get_conn() as conn, conn.cursor() as cur:
    #         cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
    #         chunk_count = cur.fetchone()[0]
    #         db_ok = chunk_count > 0
    # except Exception as e:
    #     db_ok = False
    #     db_error = str(e)
    #     chunk_count = 0
    # else:
    #     db_error = None
    
    # TODO: Test embedding with details
    # try:
    #     from common import embed_text
    #     embedding = embed_text("healthcheck test")
    #     embedding_ok = isinstance(embedding, list) and len(embedding) == 1024
    #     embedding_dims = len(embedding) if embedding else 0
    # except Exception as e:
    #     embedding_ok = False
    #     embedding_error = str(e)
    #     embedding_dims = 0
    # else:
    #     embedding_error = None
    
    # TODO: Test pipeline with details
    # try:
    #     rag = get_rag_pipeline()
    #     response = rag("What are the library opening hours?")
    #     pipeline_ok = hasattr(response, 'success') and response.success
    #     if hasattr(response, 'confidence_level'):
    #         confidence = response.confidence_level
    #     else:
    #         confidence = "unknown"
    # except Exception as e:
    #     pipeline_ok = False
    #     pipeline_error = str(e)
    #     confidence = "error"
    # else:
    #     pipeline_error = None
    
    response_time_ms = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "status": "TODO",  # TODO: Calculate based on all checks
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "latency_ms": response_time_ms,
        "database": {
            "status": "TODO",  # TODO: Set based on db_ok
            "chunks_available": 0,  # TODO: Set actual chunk count
            "error": None  # TODO: Set actual error if any
        },
        "embedding": {
            "status": "TODO",  # TODO: Set based on embedding_ok
            "dimensions": 0,  # TODO: Set actual dimensions
            "error": None  # TODO: Set actual error if any
        },
        "pipeline": {
            "status": "TODO",  # TODO: Set based on pipeline_ok
            "confidence": "unknown",  # TODO: Set actual confidence
            "error": None  # TODO: Set actual error if any
        }
    })

@app.route("/")
def index():
    """Simple status page"""
    return """
    <h1>RAG System Health Check</h1>
    <p>This service provides health monitoring for the RAG pipeline.</p>
    <ul>
        <li><a href="/health">Basic Health Check</a></li>
        <li><a href="/health/detailed">Detailed Health Check</a></li>
    </ul>
    <p><strong>Status:</strong> TODO - Implement health checks</p>
    """

if __name__ == "__main__":
    print("🏥 Starting RAG Health Check Service...")
    print("   Basic health: http://localhost:8010/health")
    print("   Detailed health: http://localhost:8010/health/detailed")
    print("   Press Ctrl+C to stop")
    print("   TODO: Implement the health check endpoints")
    app.run(host='0.0.0.0', port=8010, debug=True)
