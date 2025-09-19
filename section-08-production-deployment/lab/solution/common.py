# 00_common.py
# Shared helpers for the lab - integrated with lab6_rag_pipeline.py patterns

import os
import sys
import json
import time
from typing import Any, Dict, Optional, Callable, List
import requests
import psycopg

# Add the parent directory to the path to import from lab6_rag_pipeline
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'section-06-rag-pipeline', 'solution'))

# Database configuration (matching lab6_rag_pipeline.py)
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# API configuration (matching lab6_rag_pipeline.py)
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# --- RAG pipeline entrypoint ---
def get_rag_pipeline() -> Callable[[str], Any]:
    """
    Import and use the RAG pipeline from lab6_rag_pipeline.py
    Returns the answer_question function with proper configuration
    """
    try:
        from lab6_rag_pipeline import answer_question
        def _rag_pipeline(query: str) -> Any:
            return answer_question(query, OPENAI_API_KEY)
        return _rag_pipeline
    except ImportError as e:
        print(f"Warning: Could not import lab6_rag_pipeline: {e}")
        print("Make sure you're running from the correct directory")
        raise

# --- Embedding helper ---
def embed_text(text: str) -> List[float]:
    """
    Generate embedding using the same method as lab6_rag_pipeline.py
    """
    try:
        from lab6_rag_pipeline import get_embedding
        embedding = get_embedding(text)
        if embedding is None:
            raise RuntimeError("Failed to generate embedding")
        return embedding
    except ImportError:
        # Fallback to direct API call
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
        else:
            raise RuntimeError("Invalid embedding response")

# --- DB helpers ---
def get_conn() -> psycopg.Connection:
    """Get database connection using the same config as lab6_rag_pipeline.py"""
    return psycopg.connect(**DB_CONFIG)

def select_one(sql: str) -> Any:
    """Execute a query and return the first value"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
        return row[0] if row else None

def run_sql(sql: str, params: tuple = None) -> List[tuple]:
    """Execute a query and return all results"""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

# --- Health check helpers ---
def check_database_health() -> bool:
    """Check if database is accessible and has data"""
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
            count = cur.fetchone()[0]
            return count > 0
    except Exception:
        return False

def check_embedding_health() -> bool:
    """Check if embedding service is working"""
    try:
        embedding = embed_text("test")
        return isinstance(embedding, list) and len(embedding) == 1024
    except Exception:
        return False

def check_rag_pipeline_health() -> bool:
    """Check if RAG pipeline is working"""
    try:
        rag = get_rag_pipeline()
        response = rag("test query")
        return hasattr(response, 'success') and response.success
    except Exception:
        return False
