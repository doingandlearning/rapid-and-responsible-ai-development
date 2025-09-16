# Section 4: PostgreSQL + pgvector
## Building Your Vector Database Foundation

---

## Quick Check-In

**From Section 3, what questions do you have about:**

<span class="fragment">🤔 **RAG system architecture?**</span>

<span class="fragment">🤔 **Component troubleshooting?**</span>

<span class="fragment">🤔 **How PostgreSQL fits in?**</span>

<span class="fragment">*30 seconds to think, then share one with your neighbor*</span>

---

## Today's Journey

<span class="fragment">🗄️ **PostgreSQL Setup** - Vector-enabled database</span>

<span class="fragment">🔢 **Vector Operations** - Store, search, compare</span>

<span class="fragment">⚡ **Performance** - Indexes and optimization</span>

<span class="fragment">🏛️ **Edinburgh Scale** - Real-world considerations</span>

---

# Part 1: Why PostgreSQL?
## The Familiar Foundation

---

## Activity: Database Decision Matrix

**Teams of 4 - 3 minutes**

<span class="fragment">**Edinburgh IT Committee asks:** "Should we use PostgreSQL or a dedicated vector database?"</span>

<span class="fragment">**Your task:** Score each option (1-5) on these factors:</span>

---

## Decision Factors

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>

**PostgreSQL + pgvector:**
- Team expertise: ___/5
- Operational complexity: ___/5  
- Integration with existing systems: ___/5
- Performance for vectors: ___/5

</div>
<div>

**Dedicated Vector DB (Pinecone, Chroma):**
- Team expertise: ___/5
- Operational complexity: ___/5
- Integration with existing systems: ___/5  
- Performance for vectors: ___/5

</div>
</div>

---

## Team Recommendations

<span class="fragment">**Each team shares their top choice and reasoning**</span>

<span class="fragment">*Which factors mattered most for Edinburgh?*</span>

---

## Why PostgreSQL Wins for Edinburgh

<span class="fragment">**Familiarity** - Your team already knows it</span>

<span class="fragment">**Integration** - One database for vectors + relational data</span>

<span class="fragment">**Reliability** - Battle-tested in production</span>

<span class="fragment">**Cost** - No additional licensing or cloud costs</span>

<span class="fragment">**Control** - Data stays on Edinburgh servers</span>

---

## What is pgvector?

<span class="fragment">**PostgreSQL extension** for vector operations</span>

<span class="fragment">**Adds vector data type** - store embeddings natively</span>

<span class="fragment">**Similarity search** - fast nearest neighbor queries</span>

<span class="fragment">**Indexes** - HNSW for scale</span>

---

# Part 2: Hands-On Setup
## Let's Build It

---

## Activity: Vector Table Design

**Pairs - 5 minutes**

<span class="fragment">**Scenario:** Edinburgh student support knowledge base</span>

<span class="fragment">**Your task:** Design a table schema for storing:</span>
- <span class="fragment">Document text and metadata</span>
- <span class="fragment">1024-dimension embeddings</span>
- <span class="fragment">Categories and timestamps</span>
- <span class="fragment">Similarity search capability</span>

---

## Schema Design Challenge

<span class="fragment">**Draw or write your table structure:**</span>

<div style="font-size: 0.8em;">

```sql
CREATE TABLE your_table_name (
    -- Your columns here
);
```

</div>

<span class="fragment">**Consider:**</span>
- <span class="fragment">What data types?</span>
- <span class="fragment">What indexes?</span>
- <span class="fragment">What constraints?</span>

---

## Schema Sharing

<span class="fragment">**Teams share one design decision and reasoning**</span>

---

## The pgvector Vector Type

<span class="fragment">**vector(n)** - fixed dimensions</span>

```sql
embedding vector(1024)    -- BGE-M3 size
embedding vector(1536)    -- OpenAI text-ada-002  
embedding vector(384)     -- Sentence transformers
```

<span class="fragment">**Storage efficient** - optimized for similarity operations</span>

---

## Essential Vector Operations

<span class="fragment">**Distance operators:**</span>
- <span class="fragment">`<->` - L2 distance (Euclidean)</span>
- <span class="fragment">`<#>` - Inner product (dot product)</span>
- <span class="fragment">`<=>` - Cosine distance</span>

<span class="fragment">**Edinburgh choice:** Cosine distance for semantic similarity</span>

---

## Quick Demo: Vector Math

**Interactive calculation:**

<span class="fragment">Vector A: [1, 0, 0]</span>
<span class="fragment">Vector B: [0, 1, 0]</span>
<span class="fragment">Vector C: [1, 1, 0]</span>

<span class="fragment">**Which pairs are most similar?**</span>
<span class="fragment">*Show of hands - then we'll calculate*</span>

---

# Part 3: Performance Matters
## Making It Fast

---

## The Index Question

<span class="fragment">**Without index:** Linear search through all vectors</span>

<span class="fragment">**With 50,000 documents:** ~30 seconds per query</span>

<span class="fragment">**Edinburgh SLA:** <2 seconds response time</span>

<span class="fragment">**Solution:** Vector indexes!</span>

---

## HNSW Index Deep Dive

<span class="fragment">**Hierarchical Navigable Small World**</span>

<span class="fragment">**How it works:**</span>
- <span class="fragment">Builds a graph of vector connections</span>
- <span class="fragment">Navigates quickly to similar regions</span>
- <span class="fragment">Trade-off: Speed vs perfect accuracy</span>

---

## Index Configuration

```sql
-- Create HNSW index
CREATE INDEX ON documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

<span class="fragment">**m**: connections per node (higher = better recall)</span>
<span class="fragment">**ef_construction**: search width (higher = better quality)</span>

---

## Activity: Performance Prediction

**Individual - 2 minutes**

<span class="fragment">**Scenario:** Edinburgh's system with 50,000 documents</span>

<span class="fragment">**Predict search times:**</span>

| Configuration | Your Prediction |
|---------------|----------------|
| No index | _____ seconds |
| HNSW m=16, ef=64 | _____ seconds |
| HNSW m=32, ef=128 | _____ seconds |

<span class="fragment">*We'll test your predictions in the lab!*</span>

---

# Part 4: Edinburgh Scale Planning
## Real-World Considerations

---

## Edinburgh's Numbers

<span class="fragment">**Students:** ~47,000</span>
<span class="fragment">**Staff:** ~12,000</span>
<span class="fragment">**Documents:** Thousands of policies, procedures, guides</span>
<span class="fragment">**Query volume:** Hundreds of searches per day</span>

---

## Scaling Considerations

<span class="fragment">**Storage:** ~4KB per 1024-dim vector</span>
<span class="fragment">**Memory:** Indexes load into RAM</span>
<span class="fragment">**CPU:** Vector operations are compute-intensive</span>
<span class="fragment">**Concurrent users:** Multiple searches simultaneously</span>

---

## Activity: Resource Planning

**Teams of 3 - 4 minutes**

<span class="fragment">**Edinburgh gives you £10,000 hardware budget**</span>

<span class="fragment">**Your task:** Spec a server for their vector database</span>
- <span class="fragment">50,000 documents (vectors + metadata)</span>
- <span class="fragment">200 concurrent users at peak</span>
- <span class="fragment">&lt;2 second response time requirement</span>

---

## Hardware Recommendations

<span class="fragment">**Teams present their server specs and reasoning**</span>

---

## Vector Database Sizing

<span class="fragment">**Storage calculation:**</span>
- <span class="fragment">50,000 vectors × 1024 dims × 4 bytes = ~200MB</span>
- <span class="fragment">Plus metadata, indexes, overhead = ~1GB total</span>

<span class="fragment">**Memory for performance:**</span>
- <span class="fragment">Load indexes into RAM for speed</span>
- <span class="fragment">16-32GB recommended for Edinburgh scale</span>

---

# Part 5: Hands-On Lab Preview
## Time to Build

---

## Lab Objectives

<span class="fragment">**Set up** vector-enabled PostgreSQL</span>

<span class="fragment">**Create** Edinburgh knowledge base schema</span>

<span class="fragment">**Load** real document vectors</span>

<span class="fragment">**Test** similarity search performance</span>

<span class="fragment">**Optimize** with indexes</span>

---

## Lab Structure

<span class="fragment">**Part 1:** PostgreSQL + pgvector setup verification</span>

<span class="fragment">**Part 2:** Create optimized table schema</span>

<span class="fragment">**Part 3:** Load Edinburgh documents with embeddings</span>

<span class="fragment">**Part 4:** Performance testing and optimization</span>

<span class="fragment">**Part 5:** Scaling analysis</span>

---

## Solution Reference

<span class="fragment">**NEW:** Complete step-by-step solutions provided</span>

<span class="fragment">**Located:** `solution/` folder</span>

<span class="fragment">**Includes:**</span>
- <span class="fragment">Working code for each step</span>
- <span class="fragment">Detailed explanations</span>
- <span class="fragment">Common troubleshooting tips</span>

---

## Ready to Build?

<span class="fragment">**Questions about PostgreSQL + pgvector before we start?**</span>

---

## Lab Time!

**Go to:** `final_materials/section-04-postgres-pgvector/lab/`

<span class="fragment">**Time:** 35 minutes</span>

<span class="fragment">**Goal:** Production-ready vector database for Edinburgh</span>

<span class="fragment">**Backup plan:** Full solutions in `solution/` folder</span>