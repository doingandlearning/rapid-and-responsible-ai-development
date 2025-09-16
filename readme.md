## Course at-a-Glance

| Item             | Details                                                                                                                                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Audience**     | 6–12 software engineers comfortable with Python & SQL                                                                                                                                                                    |
| **Duration**     | 3 days (≈ 60 % hands-on labs)                                                                                                                                                                                            |
| **Stack**        | • Local embeddings: **Ollama** Docker image<br>• Vector DB: **PostgreSQL 16 + pgvector**<br>• Completions: third-party REST API (key supplied at course start)<br>• Backend/UI: Python 3.13, FastAPI, minimal React demo |
| **Requirements** | Docker ≥ 24.x, docker-compose, Python 3.13, VS Code, Git                                                                                                                                                                 |
| **Outputs**      | Working repo, slide deck, ethics checklist, certificate                                                                                                                                                                  |

---

## Section & Learning-Objective Outline

| #      | Section                                       | Key learning objectives & labs                                                                                                                                        |
| ------ | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**  | Orientation & Outcomes                        | Map the journey (architecture → vector workflows → ethics). Deliverables & success criteria.                                                                          |
| **2**  | Gen-AI & LLM Foundations                      | Tokens, embeddings vs. completions, RAG, common failure modes.                                                                                                        |
| **3**  | Architecture & Vocabulary                     | Components: Ollama embeddings ↔ pgvector ↔ JSON/relational data ↔ remote Completion API.                                                                              |
| **4**  | Vector Database Complete Implementation       | *Lab:* Setup PostgreSQL+pgvector, create optimized schema, generate embeddings via Ollama, store documents with vectors, create HNSW indexes, test performance.      |
| **5**  | Document Processing & PDF Chunking            | *Lab:* Extract text from PDFs, implement chunking strategies (fixed-size, semantic, sliding window), handle metadata preservation, optimize chunk size for embeddings. |
| **6**  | RAG Pipeline Integration                      | k-NN/cosine search with HNSW, assemble context, `POST` to remote `/v1/chat/completions`. *Lab:* build a context-aware Q\&A micro-service that cites its sources.      |
| **7**  | Advanced Vector Queries                       | Blend JSONB, relational filters, and vector distance in one SQL statement. *Lab:* craft hybrid queries for complex use-cases.                                         |
| **8**  | Production Deployment                         | Scaling, monitoring, security, performance optimization. *Lab:* production-ready configuration and deployment strategies.                                              |
| **9**  | AI Ethics & Governance                        | UK-GDPR, UoE guidelines, model cards, PII masking, audit logging.                                                                                                     |
| **10** | Capstone Lab – Student Support Chatbot        | Deploy Ollama + pgvector + remote completion API, ingest course handbooks, expose REST chat endpoint & minimal React UI; measure relevance/latency; present findings. |
| **11** | Wrap-Up & Next Steps                          | Key takeaways, repo hand-off, future learning paths (fine-tuning, multimodal, eval frameworks).                                                                       |

---

### Why this approach?

* **PostgreSQL + pgvector** keeps the data model familiar to teams already working with MySQL/MSSQL while adding efficient similarity search.
* **Ollama for embeddings** means everything sensitive stays on-prem; only prompts (without source docs) leave the network for completion calls.
* **Docker-only install** minimises friction: each student spins up Postgres, Ollama, and the sample FastAPI app with `docker-compose up`.
