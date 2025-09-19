# Section 8: Evaluation, Healthchecks & Tuning

---

## Learning Goals

- Judge efficacy of LLM/RAG workflows with evals  
- Implement meaningful healthchecks  
- Tune pgvector queries for performance  
- Identify when to use LangChain vs. direct SQL/Python  

---

## Why Evaluation & Monitoring Matter

**Eval gap:** A system that *runs* ≠ a system that’s *useful*  

---

**Silent failures erode trust**  
- Wrong answers with confidence  
- Missing or stale documents  

---

**Ops reality:**  
- Monitoring queries  
- Validating embeddings  
- Checking data freshness  

---

## Types of Evaluation

**Intrinsic (model-centric):** Accuracy, perplexity, BLEU, ROUGE  

**Extrinsic (task-centric):** Does retrieval improve answers?  

**Human-in-the-loop:** Manual spot checks, red-teaming  

---

## SaaS Options for Evals

- **LangSmith** – trace, eval, dataset mgmt  
- **TruLens** – open-source evals (faithfulness, relevance)  
- **Arize Phoenix** – observability for RAG  
- **W&B Weave** – LLM logging + evals  

---

## DIY Evaluation Pipeline

```bash
python evals/run_eval.py \
  --queries eval_queries.json \
  --output results.json
````

* Define gold queries & expected answers
* Run retrieval + generation
* Score: relevance, factuality, citation correctness
* Log results for aggregation

---

## Healthchecks

**Beyond "is the API up?"**

* DB: vector dims match, index exists, latency < X ms
* Embedding service: model loaded, correct shape
* Cache: warm and returning results
* Pipeline: known Q → known A

---

```python
def rag_pipeline_healthcheck():
    q = "What are the library opening hours?"
    a = rag_pipeline(q)
    assert "hours" in a.lower()
```

---

## Database Tuning for pgvector

* **Indexing:** HNSW for ANN, GIN for JSONB filters
* **Hybrid queries:** similarity + metadata ranking
* **Parameters:** tune `work_mem`, parallel workers
* **Monitoring:** `pg_stat_statements` for slow `<=>` queries

---

## Example Ranked Query with JSONB

```sql
WITH scored AS (
  SELECT
    id,
    text,
    1 - (embedding <=> %s::vector) AS similarity,
    (meta_data->>'priority')::int AS priority
  FROM chunks
)
SELECT
  id, text, similarity, priority,
  (similarity * 0.8 + priority * 0.2) AS final_score
FROM scored
ORDER BY final_score DESC
LIMIT 10;
```

---

## Tools like LangChain

**When useful:**

* Fast prototyping
* Logging, tracing, evals (LangSmith)
* Multi-tool orchestration

**When not:**

* Simple RAG: direct SQL + Python cleaner
* Performance-critical loops

---

## Lab: Build an Eval & Healthcheck Suite

1. Write gold dataset (5 queries + expected answers)
2. Eval script: log relevance & citations
3. Healthcheck endpoint:

   * DB connectivity
   * Embedding service
   * Known Q → A check
4. Tune a JSONB + vector ranked query

---

# ✅ Takeaways

* Evaluate **retrieval + generation**, not just uptime
* Healthchecks catch **silent failures**
* pgvector tuning = performance at scale
* LangChain: good for prototyping, not always for prod
