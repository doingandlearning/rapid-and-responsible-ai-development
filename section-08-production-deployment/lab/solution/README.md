# Section 8 Lab Solutions - Updated for lab6_rag_pipeline.py Integration

This directory contains updated solutions that integrate with the RAG pipeline from `section-06-rag-pipeline/solution/lab6_rag_pipeline.py`.

## Prerequisites

1. **Complete Section 6**: Make sure you have a working RAG pipeline from Section 6
2. **Database Setup**: PostgreSQL with pgvector running on port 5050
3. **Embedding Service**: Ollama with BGE-M3 model running on port 11434
4. **Python Dependencies**: Flask, psycopg, requests

## Updated Files

### `common.py` (formerly `00_common.py`)
- Integrates with `lab6_rag_pipeline.py` patterns
- Uses same database configuration and connection patterns
- Provides health check functions for all components

### `01_golden_queries.py`
- Tests RAG pipeline with predefined queries
- Handles RAGResponse objects with detailed metrics
- Shows confidence levels, response times, and sources

### `02_simple_scoring.py`
- Implements pass/fail scoring for RAG responses
- Works with both RAGResponse objects and string responses
- Provides detailed evaluation metrics and performance analysis

### `03_healthcheck_app.py`
- Flask-based health check service (replaces FastAPI)
- Comprehensive health monitoring for database, embeddings, and pipeline
- Two endpoints: `/health` (basic) and `/health/detailed` (comprehensive)

### `04_explain_query.py`
- Database query performance analysis using EXPLAIN ANALYZE
- Uses correct schema from `document_chunks` table
- Supports comparison of different distance operators

### `05_ranked_query.py`
- Advanced ranked queries with JSONB metadata
- Combines vector similarity with priority and relevance scoring
- Includes fallback to simple ranking if metadata is unavailable

## Usage

### Running Individual Exercises

```bash
# Exercise 1: Golden Queries
python 01_golden_queries.py

# Exercise 2: Simple Scoring
python 02_simple_scoring.py

# Exercise 3: Health Check Service
python 03_healthcheck_app.py
# Then visit http://localhost:8010/health

# Exercise 4: Query Performance Analysis
python 04_explain_query.py "How do I reset my password?"
python 04_explain_query.py --compare "WiFi setup"

# Exercise 5: Ranked Queries
python 05_ranked_query.py "password reset"
python 05_ranked_query.py "WiFi setup" --strategies
```

### Key Changes from Original

1. **Flask instead of FastAPI**: All web services now use Flask to match the lab6 pattern
2. **RAGResponse Integration**: Properly handles the RAGResponse objects from lab6_rag_pipeline.py
3. **Database Schema**: Uses `document_chunks` table instead of `chunks`
4. **Connection Patterns**: Matches the database configuration from lab6_rag_pipeline.py
5. **Error Handling**: Improved error handling and fallback mechanisms
6. **Health Checks**: More comprehensive health monitoring

### Integration Notes

- The solutions automatically import from `lab6_rag_pipeline.py` when available
- Fallback mechanisms are provided for when the RAG pipeline is not accessible
- All solutions use the same database configuration as the main RAG pipeline
- Health checks verify all components of the RAG system

### Troubleshooting

If you encounter import errors:
1. Make sure you're running from the solution directory
2. Ensure `lab6_rag_pipeline.py` is accessible (complete Section 6 first)
3. Check that all required services are running (PostgreSQL, Ollama)
4. Verify database contains the `document_chunks` table with embeddings

### Next Steps

After completing these exercises:
1. Review the performance metrics and identify bottlenecks
2. Consider implementing more sophisticated evaluation metrics
3. Set up monitoring dashboards using the health check endpoints
4. Experiment with different ranking strategies and similarity thresholds
