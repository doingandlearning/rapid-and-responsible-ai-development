# Section 8 Lab Starter Files

**Building Confidence in RAG Pipelines through Evals and Health Checks**

This directory contains starter files with TODO comments to guide you through implementing evaluation and monitoring for your RAG system.

## Prerequisites

✅ Completed Section 6: RAG Pipeline Integration  
✅ PostgreSQL with `pgvector` installed and running on port 5050  
✅ Ollama with BGE-M3 model running on port 11434  
✅ Python environment with Flask, psycopg, requests  

## Lab Structure

### Exercise 1: Golden Queries (`01_golden_queries.py`)
**Time:** 10 minutes  
**Goal:** Create a test suite of known queries with expected answers

**TODO Tasks:**
1. Define your golden set of test queries with expected answer hints
2. Implement the evaluation loop that calls your RAG pipeline
3. Handle both RAGResponse objects and string responses
4. Add error handling for failed queries
5. Display results with proper formatting

**Key Learning:** How to systematically test your RAG system with known good examples

---

### Exercise 2: Simple Scoring (`02_simple_scoring.py`)
**Time:** 10 minutes  
**Goal:** Implement pass/fail evaluation with detailed metrics

**TODO Tasks:**
1. Implement `simple_eval()` function for keyword-based scoring
2. Create `detailed_eval()` function for comprehensive metrics
3. Build the main evaluation loop with scoring
4. Calculate and display summary statistics
5. Add performance analysis and recommendations

**Key Learning:** How to measure RAG system performance with simple heuristics

---

### Exercise 3: Health Checks (`03_healthcheck_app.py`)
**Time:** 10 minutes  
**Goal:** Create Flask-based health monitoring service

**TODO Tasks:**
1. Implement `/health` endpoint with basic component checks
2. Create `/health/detailed` endpoint with comprehensive diagnostics
3. Add proper error handling and status reporting
4. Test database, embedding, and pipeline health
5. Return structured JSON responses

**Key Learning:** How to monitor RAG system health in production

---

### Exercise 4: Query Performance (`04_explain_query.py`)
**Time:** 10 minutes  
**Goal:** Analyze database query performance with EXPLAIN ANALYZE

**TODO Tasks:**
1. Implement vector query performance analysis
2. Create comparison function for different distance operators
3. Parse and display query execution plans
4. Add performance recommendations
5. Handle different database schemas and indexes

**Key Learning:** How to optimize vector database queries for performance

---

### Exercise 5: Ranked Queries (`05_ranked_query.py`)
**Time:** 10 minutes  
**Goal:** Implement advanced ranking with JSONB metadata

**TODO Tasks:**
1. Create ranked query combining vector similarity with metadata
2. Implement weighted scoring formula
3. Add fallback to simple ranking if metadata unavailable
4. Create strategy comparison demonstration
5. Handle JSONB metadata fields (priority, relevance, timestamps)

**Key Learning:** How to create sophisticated ranking systems for better results

---

## Getting Started

1. **Start with Exercise 1**: Begin with `01_golden_queries.py`
2. **Follow the TODOs**: Each file has detailed TODO comments guiding you
3. **Test incrementally**: Run each exercise as you complete it
4. **Check the solutions**: Compare with `../solution/` when stuck
5. **Iterate and improve**: Refine your implementations based on results

## Running the Exercises

```bash
# Exercise 1: Golden Queries
python 01_golden_queries.py

# Exercise 2: Simple Scoring  
python 02_simple_scoring.py

# Exercise 3: Health Check Service
python 03_healthcheck_app.py
# Then visit http://localhost:8010/health

# Exercise 4: Query Performance
python 04_explain_query.py "How do I reset my password?"
python 04_explain_query.py --compare "WiFi setup"

# Exercise 5: Ranked Queries
python 05_ranked_query.py "password reset"
python 05_ranked_query.py "WiFi setup" --strategies
```

## Success Criteria

By the end of this lab, you should be able to:

- ✅ Run golden queries against your RAG pipeline
- ✅ Score responses with simple heuristics and detailed metrics
- ✅ Expose health check endpoints for monitoring
- ✅ Analyze and optimize vector query performance
- ✅ Implement advanced ranking with metadata
- ✅ Understand where to go next with dedicated tooling

## Tips for Success

1. **Read the TODOs carefully**: They provide step-by-step guidance
2. **Test frequently**: Run your code after each major change
3. **Use the common module**: It provides helper functions for database and API access
4. **Handle errors gracefully**: RAG systems can fail in many ways
5. **Think about production**: Consider how these tools would work in a real system

## Troubleshooting

**Import Errors:**
- Make sure you're running from the starter directory
- Check that `common.py` is in the same directory
- Verify that Section 6 RAG pipeline is accessible

**Database Errors:**
- Ensure PostgreSQL is running on port 5050
- Check that `document_chunks` table exists with embeddings
- Verify pgvector extension is installed

**API Errors:**
- Confirm Ollama is running on port 11434
- Check that BGE-M3 model is available
- Verify network connectivity

## Next Steps

After completing these exercises:
1. Review the solution files to see different approaches
2. Experiment with different evaluation metrics
3. Set up monitoring dashboards using the health endpoints
4. Consider implementing more sophisticated evaluation frameworks
5. Explore production monitoring tools like Prometheus and Grafana

---

**Happy coding! 🚀**
