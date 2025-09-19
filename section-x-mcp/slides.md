# Model Context Protocol (MCP) — A Practical Intro for RAG

**Goal:** Give LLMs safe, portable access to your search and data tools.



---

## What is MCP?

- **Protocol** for LLM clients to call **external tools** you expose
- Client ↔ **stdio** ↔ Your MCP server ↔ **DB / APIs / FS**
- Tools are just **typed functions** (e.g. `search_chunks(query, limit)`)

```

User → LLM client → (MCP) → Your server → Vector DB / APIs

```

---

## Why MCP for RAG?

- **Portability:** One server; many clients
- **Separation of concerns:** Model prompts vs. data/IO boundary
- **Governance & audit:** Central choke point for permissions and logs
- **Speed:** Ship/modify tools without reworking prompts or apps

---

## Core Pieces

- **Client**: e.g. Claude Desktop
- **Server**: your Python process (FastMCP)
- **Tools**: typed functions the client can call
- **Resources / Prompts** *(optional)*: files and prompt snippets

---

## Where It Fits in a RAG Pipeline

- `search_chunks(query, limit)` → pgvector
- `similar_to_chunk(chunk_id)` → neighbours
- `get_doc(doc_id)` → object store
- `log_feedback(doc_ids, helpful)` → evals/QA

---

## Demo Flow (10–12 mins)

1. **Discover** tools (client shows `search_chunks`)
2. **Call** with a real query (“vector indexes in Postgres”, k=3)
3. **Use** results to answer, with citations
4. **Repeat** with a filter (e.g. `author=Shakespeare`) to show governance

---

## Deterministic Boundaries

- Tools do **I/O & policy**; model stays **stateless** about secrets
- Enforce **limits**, **filters**, **timeouts** in the tool
- Return **minimal JSON** the model can reliably use


---

## Types → Safer Calls

- Python **type hints** → JSON schema for the client
- Validated inputs reduce prompt fragility
- Clear docstrings = better tool selection


---

## Observability & Policy

- Log: request id, latency, result count, redactions
- Rate limit per tool or user
- Whitelist collections; redact PII in outputs


---

## Versioning & Portability

- Version tool names: `search_chunks.v2`
- Same server runs locally, CI, or jump boxes
- Client config just changes **command/path**, not code


---

## When MCP vs. Direct HTTP

**Use MCP when:**
- Multiple clients / assistants will call the same capability
- You need discovery, governance, or local-first workflows

**Use HTTP when:**
- A single app owns the flow and tight API coupling is fine


---

## Common Pitfalls → Fixes

- **Client can’t spawn Python** → use absolute interpreter path; `-u` for unbuffered stdio
- **Huge payloads** → paginate or truncate; return ids + snippets
- **JSON handling** → psycopg3 often returns Python objects; avoid double `json.loads`
- **Long calls** → add timeouts; fail fast with clear error text


---

## Stakeholder Frames

- **Engineering:** Stable interface for tools; ship changes faster
- **Security:** Central policy, least privilege, audit trail
- **Product:** Feature velocity; reusable across assistants and surfaces


---

## Checklist: Ship a Search Tool

- Clear **name** + docstring; validated **params**
- Parametrised SQL, **least-privilege** DB user
- Server-side **limit**, **filters**, **timeouts**
- Metrics: p50/p95 latency, hit-rate
- Latency budget: **< {{ PLACEHOLDER }} ms**
- Unit + simple load tests


---

## Quick Start (Claude Desktop + Python)

- Add to config:
  - **command**: absolute path to your venv python
  - **args**: `-u /abs/path/to/server.py`
- Restart client → call `search_chunks`


---

## Wrap-Up

- MCP = **standard plug** between LLMs and your data/tools
- Start with one tool: `search_chunks`
- Expand to **similarity**, **fetch**, **feedback/evals**

**Try now:**  
“Use `search_chunks` with query ‘hybrid search in Postgres’ limit 3.”

Note:
Close by running the tool live and asking the model to cite chunk ids in the answer.
