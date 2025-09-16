# Section 3: Architecture & Vocabulary
## Understanding How the Pieces Fit Together

---

## Quick Check-In

**From Section 2, what questions do you have about:**

<span class="fragment">🤔 **Vector similarity scores?**</span>

<span class="fragment">🤔 **The embedding black box?**</span>

<span class="fragment">🤔 **How this all connects together?**</span>

<span class="fragment">*30 seconds to think, then share one with your neighbor*</span>

---

## Today's Journey

<span class="fragment">🏗️ **System Architecture** - How components work together</span>

<span class="fragment">📖 **Vocabulary in Context** - Terms that matter for Edinburgh</span>

<span class="fragment">🔧 **Component Deep Dive** - Inside the black boxes</span>

<span class="fragment">🔍 **Troubleshooting** - When things go wrong</span>

---

# Part 1: The Big Picture
## RAG System Architecture

---

## Activity: Build the System

**Teams of 4 - 5 minutes**

<span class="fragment">**Your challenge:** A new Edinburgh student asks "How do I reset my password?"</span>

<span class="fragment">**Your task:** Using these component cards, arrange the flow from question to answer</span>

---

## Component Cards

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em; font-size: 0.8em;">
<div>

**User Interface**
*Student types question*

**Embedding Generator** 
*Ollama + BGE-M3*

**Vector Database**
*PostgreSQL + pgvector*

**Document Retrieval**
*Find similar content*

</div>
<div>

**LLM Completion**
*OpenAI API*

**Response Generator**
*Combine context + query*

**Knowledge Base**
*Edinburgh IT policies*

**Quality Filter**
*Check confidence scores*

</div>
</div>

---

## Let's Build It Together

**Step-by-step flow reconstruction**

<span class="fragment">*Teams share their arrangements - we'll build the correct flow*</span>

---

## The RAG Architecture

```mermaid
flowchart TD
    A[Student Question] --> B[Embedding Generator<br/>Ollama + BGE-M3]
    B --> C[Vector Search<br/>PostgreSQL + pgvector]
    C --> D[Document Retrieval<br/>Find similar content]
    D --> E[Context Assembly<br/>Combine relevant docs]
    E --> F[LLM Completion<br/>OpenAI API]
    F --> G[Response to Student]
```

---

## Data Flow: "How do I reset my password?"

<span class="fragment">**1. Question** → "How do I reset my password?"</span>

<span class="fragment">**2. Embedding** → [0.2, -0.1, 0.8, 0.3, ...]</span>

<span class="fragment">**3. Vector Search** → Find similar document chunks</span>

<span class="fragment">**4. Retrieval** → Edinburgh IT policy sections</span>

<span class="fragment">**5. Context** → Relevant policy + user question</span>

<span class="fragment">**6. Generation** → "To reset your Edinburgh password, visit..."</span>

---

## Why This Architecture?

<span class="fragment">**Modular** - Each component has one job</span>

<span class="fragment">**Scalable** - Add more documents without retraining</span>

<span class="fragment">**Accurate** - Grounded in real Edinburgh policies</span>

<span class="fragment">**Maintainable** - Update documents, not the AI</span>

---

# Part 2: Component Deep Dive
## Understanding Each Building Block

---

## Component 1: The User Interface

<span class="fragment">**What it does:** Accepts student questions</span>

<span class="fragment">**Edinburgh considerations:**</span>
- <span class="fragment">Single Sign-On integration?</span>
- <span class="fragment">Mobile-friendly for students?</span>
- <span class="fragment">Accessible for all users?</span>

---

## Component 2: Embedding Generator (Ollama)

<span class="fragment">**What it does:** Converts text to 1024-dimension vectors</span>

<span class="fragment">**Why Ollama for Edinburgh:**</span>
- <span class="fragment">**Privacy:** Runs locally, no data sent to third parties</span>
- <span class="fragment">**Cost:** No per-token charges</span>
- <span class="fragment">**Control:** University owns the process</span>

---

## Component 3: Vector Database (PostgreSQL + pgvector)

<span class="fragment">**What it does:** Stores and searches embeddings</span>

<span class="fragment">**Why PostgreSQL:**</span>
- <span class="fragment">**Familiar:** Edinburgh already uses PostgreSQL</span>
- <span class="fragment">**Integrated:** Vectors + relational data + JSON</span>
- <span class="fragment">**Reliable:** Battle-tested in production</span>

---

## Component 4: Knowledge Base

<span class="fragment">**What it contains:** Edinburgh-specific documents</span>

<span class="fragment">**Examples:**</span>
- <span class="fragment">IT support procedures</span>
- <span class="fragment">Student services policies</span>
- <span class="fragment">Academic regulations</span>
- <span class="fragment">Accommodation guidelines</span>

---

## Component 5: LLM Completion (OpenAI)

<span class="fragment">**What it does:** Generates human-like responses</span>

<span class="fragment">**Why external LLM:**</span>
- <span class="fragment">**Quality:** Better language generation</span>
- <span class="fragment">**Cost-effective:** Pay per use</span>
- <span class="fragment">**No training needed:** Works immediately</span>

---

## Activity: Component Health Check

**Pairs - 3 minutes each component**

<span class="fragment">**Your task:** For each component, identify:</span>
- <span class="fragment">**What could go wrong?**</span>
- <span class="fragment">**How would you know it's broken?**</span>
- <span class="fragment">**How would you fix it?**</span>

---

## Component Health Checks

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em; font-size: 0.7em;">
<div>

**Ollama Embedding**
- ❌ Service down
- ❌ Model not loaded
- ❌ Out of memory

**PostgreSQL + pgvector**
- ❌ Database connection issues
- ❌ Index corruption
- ❌ Disk space full

</div>
<div>

**Knowledge Base**
- ❌ Outdated documents
- ❌ Missing content
- ❌ Poor chunking

**OpenAI API**
- ❌ Rate limits hit
- ❌ API key expired
- ❌ Network timeouts

</div>
</div>

---

# Part 3: Vocabulary in Context
## Terms That Matter for Edinburgh Systems

---

## Vocabulary Learning Activity

**Individual - 2 minutes**

<span class="fragment">**Rate your understanding (1-5) of these terms in the context of Edinburgh AI systems:**</span>

---

## Technical Terms Assessment

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>

- **Embedding model** (1-5): ___
- **Vector index** (1-5): ___
- **Cosine similarity** (1-5): ___
- **Context window** (1-5): ___
- **Chunking strategy** (1-5): ___

</div>
<div>

- **RAG pipeline** (1-5): ___
- **Prompt engineering** (1-5): ___
- **Temperature** (1-5): ___
- **Retrieval threshold** (1-5): ___
- **Hallucination detection** (1-5): ___

</div>
</div>

---

## Vocabulary in Action: Embedding Model

<span class="fragment">**Definition:** The AI model that converts text to numerical vectors</span>

<span class="fragment">**Edinburgh context:** "Should we use BGE-M3 or OpenAI embeddings for our student support system?"</span>

<span class="fragment">**Decision factors:**</span>
- <span class="fragment">Privacy (local vs cloud)</span>
- <span class="fragment">Cost (free vs per-token)</span>
- <span class="fragment">Quality (accuracy for Edinburgh content)</span>

---

## Vocabulary in Action: Vector Index

<span class="fragment">**Definition:** Database structure for fast similarity search</span>

<span class="fragment">**Edinburgh context:** "Our vector search is taking 30 seconds per query"</span>

<span class="fragment">**Technical solution:**</span>
- <span class="fragment">**HNSW index** for approximate nearest neighbors</span>
- <span class="fragment">**Trade-off:** Speed vs accuracy</span>
- <span class="fragment">**Configuration:** Index parameters for Edinburgh scale</span>

---

## Vocabulary in Action: Context Window

<span class="fragment">**Definition:** Maximum text length an LLM can process at once</span>

<span class="fragment">**Edinburgh context:** "Can we include all relevant policy documents in one query?"</span>

<span class="fragment">**Practical implications:**</span>
- <span class="fragment">**GPT-4:** ~8,000 tokens context limit</span>
- <span class="fragment">**Strategy:** Retrieve most relevant chunks only</span>
- <span class="fragment">**Quality:** Better to be selective than truncate</span>

---

## Vocabulary in Action: Temperature

<span class="fragment">**Definition:** Controls randomness in LLM responses</span>

<span class="fragment">**Edinburgh context:** "Should our support bot give creative or consistent answers?"</span>

<span class="fragment">**Setting guidance:**</span>
- <span class="fragment">**Temperature 0.1:** Consistent, factual responses</span>
- <span class="fragment">**Temperature 0.7:** More creative, varied responses</span>
- <span class="fragment">**Edinburgh choice:** Low temperature for policy questions</span>

---

## Activity: Vocabulary Translation

**Pairs - 4 minutes**

<span class="fragment">**Your task:** Translate these technical conversations into plain English for Edinburgh stakeholders</span>

---

## Translation Scenarios

<div style="font-size: 0.8em;">

**Scenario A:** "We need to tune our retrieval threshold because we're getting too many false positives with cosine similarity below 0.7"

**Scenario B:** "The embedding model is creating high-dimensional representations, but our vector index isn't optimized for this scale"

**Scenario C:** "We should implement prompt engineering to reduce hallucination when the context window exceeds our token limits"

</div>

<span class="fragment">**Goal:** Explain the problem and solution in terms Edinburgh IT managers would understand</span>

---

# Part 4: Troubleshooting Simulation
## When Things Go Wrong

---

## Edinburgh IT Emergency!

<span class="fragment">**Breaking:** The student support AI is giving weird responses</span>

<span class="fragment">**Your role:** Technical troubleshooting team</span>

<span class="fragment">**Your mission:** Diagnose and fix the problem</span>

---

## Problem Report: Case 1

<div style="background: #ffebee; padding: 1em; border-radius: 8px; font-size: 0.8em;">

**User complaint:** "I asked about booking a study room and got information about hotel reservations"

**System logs:**
- Embedding generation: ✅ Working
- Vector search: ✅ Returning results  
- LLM completion: ✅ Generating responses
- Response time: ✅ Normal

**Question:** What's wrong and how do you fix it?

</div>

---

## Troubleshooting Process

**Teams of 3 - 5 minutes**

<span class="fragment">**Step 1:** Identify which component is likely the problem</span>

<span class="fragment">**Step 2:** What specific issue within that component?</span>

<span class="fragment">**Step 3:** How would you test your hypothesis?</span>

<span class="fragment">**Step 4:** What's your fix?</span>

---

## Problem Report: Case 2

<div style="background: #ffebee; padding: 1em; border-radius: 8px; font-size: 0.8em;">

**User complaint:** "The AI says 'I don't have information about that' for common password reset questions"

**System logs:**
- Embedding generation: ✅ Working
- Vector search: ❌ No similar documents found (similarity < 0.3)
- Knowledge base: Contains password reset procedures
- LLM completion: Not reached

**Question:** What's wrong and how do you fix it?

</div>

---

## Problem Report: Case 3

<div style="background: #ffebee; padding: 1em; border-radius: 8px; font-size: 0.8em;">

**User complaint:** "Responses are taking 2 minutes and sometimes timeout"

**System logs:**
- Embedding generation: ⚠️ 5 seconds per query
- Vector search: ⚠️ 45 seconds per search
- Database: 50,000 documents, no vector index
- LLM completion: ⚠️ 30 seconds when reached

**Question:** What's wrong and how do you fix it?

</div>

---

## Teams Report Back

<span class="fragment">**Each team shares their diagnosis for one case**</span>

<span class="fragment">**Focus on:**</span>
- <span class="fragment">Which component is the root cause?</span>
- <span class="fragment">What specific fix would you implement?</span>
- <span class="fragment">How would you prevent this in the future?</span>

---

## Common Troubleshooting Patterns

<span class="fragment">**Wrong results:** Usually knowledge base or retrieval issues</span>

<span class="fragment">**"I don't know" responses:** Vector similarity threshold or missing content</span>

<span class="fragment">**Slow performance:** Missing indexes or oversized contexts</span>

<span class="fragment">**Service errors:** Component health monitoring needed</span>

---

# Part 5: Hands-On Lab Preview
## Architecture in Action

---

## Lab Objectives

<span class="fragment">**Build mental model** of complete system</span>

<span class="fragment">**Inspect real components** with Edinburgh data</span>

<span class="fragment">**Practice troubleshooting** with simulated issues</span>

---

## Lab Structure

<span class="fragment">**Part 1:** Edinburgh document ingestion pipeline</span>

<span class="fragment">**Part 2:** Component inspection and health checks</span>

<span class="fragment">**Part 3:** Trace a query through the entire system</span>

<span class="fragment">**Part 4:** Break something and fix it!</span>

---

## Ready to Get Technical?

<span class="fragment">**Questions about the architecture before we build it?**</span>

---

## Lab Time!

**Go to:** `final_materials/section-03-architecture/lab/`

<span class="fragment">**Time:** 30 minutes</span>

<span class="fragment">**Goal:** Deep understanding of RAG system architecture</span>