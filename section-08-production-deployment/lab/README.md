# Section 8 Lab: Evaluating and Monitoring RAG Systems

**Building Confidence in RAG Pipelines through Evals and Health Checks**

## Lab Overview

**Time:** 45 minutes
**Objective:** Learn how to evaluate RAG system quality, implement health checks, and apply basic database tuning for reliability at scale.
**Context:** Move beyond building a pipeline — learn how to measure its effectiveness, keep it healthy, and point towards production-ready workflows with tools like LangChain.

---

## Prerequisites

✅ Completed a working RAG pipeline (retrieval + generation)
✅ PostgreSQL with `pgvector` installed
✅ Sample documents loaded and indexed
✅ Python environment with requests/Flask/FastAPI

---

## Lab Exercises

### Exercise 1: Golden Queries (10 minutes)

Create a small set of **known queries** with expected answers.

```python
golden_set = [
    {"query": "What are the library opening hours?", "expected": "The library is open..."},
    {"query": "Where is the IT helpdesk?", "expected": "Located on the..."},
]

for item in golden_set:
    result = rag_pipeline(item["query"])
    print(f"Q: {item['query']}")
    print(f"A: {result}\nExpected: {item['expected']}\n")
```

➡️ Discuss: Where is the pipeline strong? Where does it break?

---

### Exercise 2: Lightweight Scoring (10 minutes)

Implement a very simple **pass/fail heuristic**:

```python
def simple_eval(result, expected):
    return "pass" if expected.lower().split()[0] in result.lower() else "fail"

for item in golden_set:
    result = rag_pipeline(item["query"])
    print(item["query"], simple_eval(result, item["expected"]))
```

➡️ Keeps evaluation low-tech but useful.

---

### Exercise 3: Health Checks (10 minutes)

Add a health endpoint for your pipeline.

```python
@app.get("/health")
def health():
    try:
        db_ok = run_sql("SELECT 1") is not None
        vec_ok = rag_pipeline("test") is not None
        return {"status": "healthy" if db_ok and vec_ok else "degraded"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

➡️ Catch failures early — embeddings mismatch, index not found, LLM down.

---

### Exercise 4: Database Tuning (10 minutes)

Check your vector queries:

```sql
EXPLAIN ANALYZE
SELECT *
FROM chunks
ORDER BY embedding <-> '{{vector}}'
LIMIT 5;
```

➡️ Compare index types (`ivfflat`, `hnsw`) and note differences in speed/recall.

---

### Exercise 5: Looking Ahead (5 minutes)

* SaaS evals: LangSmith, TruLens, Arize
* Monitoring: Prometheus/Grafana + custom health endpoints
* Prototyping: LangChain’s built-in evals and tracing

---

## Success Criteria

By the end of this lab, you can:

* Run golden queries against your pipeline
* Score responses with a simple heuristic
* Expose a basic health check
* Inspect pgvector query performance
* Know where to go next with dedicated tooling
