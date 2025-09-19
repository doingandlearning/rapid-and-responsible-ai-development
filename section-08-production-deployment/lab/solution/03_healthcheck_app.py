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
    """Comprehensive health check for the RAG system"""
    start_time = time.time()
    
    # Individual component checks
    db_ok = check_database_health()
    embedding_ok = check_embedding_health()
    pipeline_ok = check_rag_pipeline_health()
    
    # Calculate overall status
    all_healthy = db_ok and embedding_ok and pipeline_ok
    status = "healthy" if all_healthy else "degraded"
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Prepare response
    health_data = {
        "status": status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "latency_ms": response_time_ms,
        "checks": {
            "database": {
                "status": "healthy" if db_ok else "unhealthy",
                "description": "PostgreSQL connection and data availability"
            },
            "embedding": {
                "status": "healthy" if embedding_ok else "unhealthy", 
                "description": "Ollama embedding service"
            },
            "pipeline": {
                "status": "healthy" if pipeline_ok else "unhealthy",
                "description": "Complete RAG pipeline functionality"
            }
        }
    }
    
    # Add detailed diagnostics if any component is unhealthy
    if not all_healthy:
        health_data["diagnostics"] = []
        
        if not db_ok:
            health_data["diagnostics"].append("Database connection failed or no embeddings found")
        
        if not embedding_ok:
            health_data["diagnostics"].append("Embedding service unavailable or returning invalid results")
            
        if not pipeline_ok:
            health_data["diagnostics"].append("RAG pipeline failed to process test query")
    
    return jsonify(health_data)

@app.route("/health/detailed")
def detailed_health():
    """Detailed health check with more information"""
    start_time = time.time()
    
    try:
        # Test database with more details
        from common import get_conn
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
            chunk_count = cur.fetchone()[0]
            db_ok = chunk_count > 0
    except Exception as e:
        db_ok = False
        db_error = str(e)
        chunk_count = 0
    else:
        db_error = None
    
    # Test embedding with details
    try:
        from common import embed_text
        embedding = embed_text("healthcheck test")
        embedding_ok = isinstance(embedding, list) and len(embedding) == 1024
        embedding_dims = len(embedding) if embedding else 0
    except Exception as e:
        embedding_ok = False
        embedding_error = str(e)
        embedding_dims = 0
    else:
        embedding_error = None
    
    # Test pipeline with details
    try:
        rag = get_rag_pipeline()
        response = rag("What are the library opening hours?")
        pipeline_ok = hasattr(response, 'success') and response.success
        if hasattr(response, 'confidence_level'):
            confidence = response.confidence_level
        else:
            confidence = "unknown"
    except Exception as e:
        pipeline_ok = False
        pipeline_error = str(e)
        confidence = "error"
    else:
        pipeline_error = None
    
    response_time_ms = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "status": "healthy" if all([db_ok, embedding_ok, pipeline_ok]) else "degraded",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "latency_ms": response_time_ms,
        "database": {
            "status": "healthy" if db_ok else "unhealthy",
            "chunks_available": chunk_count,
            "error": db_error
        },
        "embedding": {
            "status": "healthy" if embedding_ok else "unhealthy",
            "dimensions": embedding_dims,
            "error": embedding_error
        },
        "pipeline": {
            "status": "healthy" if pipeline_ok else "unhealthy",
            "confidence": confidence,
            "error": pipeline_error
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
    """

if __name__ == "__main__":
    print("🏥 Starting RAG Health Check Service...")
    print("   Basic health: http://localhost:8010/health")
    print("   Detailed health: http://localhost:8010/health/detailed")
    print("   Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=8010, debug=True)
