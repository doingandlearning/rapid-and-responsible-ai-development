# Section 2: Gen-AI & LLM Foundations
## Understanding the Building Blocks

---

## Quick Check-In

**From Section 1, what questions do you have about those 1024 numbers?**

<span class="fragment">*30 seconds to think, then share one question with your neighbor*</span>

---

## Today's Journey

<span class="fragment">🎯 **Tokens** - How AI "sees" text</span>

<span class="fragment">🎯 **Embeddings** - How AI "understands" meaning</span>

<span class="fragment">🎯 **LLM Types** - Tools for different jobs</span>

<span class="fragment">🎯 **Common Problems** - What goes wrong and why</span>

---

## Activity: Vocabulary Check

**Individual sorting - 2 minutes**

<span class="fragment">Sort these terms into three columns:</span>
- <span class="fragment">**Never heard of**</span>
- <span class="fragment">**Heard of**</span>  
- <span class="fragment">**Could explain to someone**</span>

---

## Vocabulary Check Terms

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>

- Token
- Embedding
- Vector
- LLM
- RAG
- Prompt

</div>
<div>

- Context window
- Temperature
- Hallucination  
- Fine-tuning
- Transformer
- Attention

</div>
</div>

---

## Pair Share

**Find someone with different sorting**

<span class="fragment">*3 minutes: Explain one term you marked "Could explain"*</span>

<span class="fragment">*Ask about one term they know that you don't*</span>

---

# Part 1: Tokens
## How AI "Sees" Text

---

## What You Think Happens

```
"Hello world" → AI → Response
```

<span class="fragment">**But actually...**</span>

---

## What Actually Happens

```
"Hello world" → [15339, 1917] → AI → [18625, 11, 1917] → "Hi there"
```

<span class="fragment">**AI doesn't see letters - it sees numbers!**</span>

---

## Hands-On: Token Explorer

**Open this tool:** `https://platform.openai.com/tokenizer`

<span class="fragment">**Try typing:** "Edinburgh University technical support"</span>

<span class="fragment">*2 minutes - explore different phrases*</span>

---

## What Did You Notice?

**Turn to your neighbor:**

<span class="fragment">1. How many tokens was your university phrase?</span>

<span class="fragment">2. Were any splits surprising?</span>

<span class="fragment">3. Try "AI" vs "artificial intelligence" - what happens?</span>

---

## Token Patterns

<span class="fragment">**Common words** = 1 token</span>

<span class="fragment">**Rare words** = multiple tokens</span>

<span class="fragment">**Punctuation** = often separate tokens</span>

<span class="fragment">**Spaces** = part of tokens</span>

---

## Why Tokens Matter

<span class="fragment">**Cost** = Charged per token</span>

<span class="fragment">**Speed** = More tokens = slower</span>

<span class="fragment">**Limits** = Models have token maximums</span>

---

## Quick Practice

**Which costs more?**

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>

A) "Help me"

B) "Assist me"

</div>
<div>

C) "AI is great"

D) "Artificial intelligence is wonderful"

</div>
</div>

<span class="fragment">*Test your guesses in the tokenizer!*</span>

---

# Part 2: Embeddings
## How AI "Understands" Meaning

---

## Remember Section 1?

```
"Hello, vector world!" → [0.0123, -0.0456, 0.0789, ...]
```

<span class="fragment">**Those 1024 numbers are called an EMBEDDING**</span>

---

## What Is An Embedding?

<span class="fragment">**A mathematical representation of meaning**</span>

---

## Real-World Analogy

<span class="fragment">**How would you describe Edinburgh to someone?**</span>

<span class="fragment">*30 seconds - think of 3-5 characteristics*</span>

---

## Your Edinburgh Description

<span class="fragment">**Temperature:** Cold (-2)</span>
<span class="fragment">**Hills:** Very hilly (4)</span>
<span class="fragment">**History:** Very historic (5)</span>
<span class="fragment">**Size:** Medium (3)</span>

<span class="fragment">**Edinburgh = [-2, 4, 5, 3]**</span>

---

## That's An Embedding!

<span class="fragment">**Edinburgh:** [-2, 4, 5, 3]</span>
<span class="fragment">**Glasgow:** [-1, 2, 4, 4]</span>
<span class="fragment">**London:** [2, 1, 5, 5]</span>

<span class="fragment">**Which cities are most similar?**</span>

---

## Text Embeddings Work Similarly

<span class="fragment">**"Database"** = [0.2, -0.1, 0.8, ...]</span>
<span class="fragment">**"PostgreSQL"** = [0.3, -0.2, 0.7, ...]</span>
<span class="fragment">**"Cat"** = [-0.5, 0.9, 0.1, ...]</span>

<span class="fragment">**Which are most similar?**</span>

---

## Activity: Embedding Detective

**With your partner - 3 minutes:**

<span class="fragment">Given these Edinburgh-related embeddings, what might each represent?</span>

```
A: [0.9, 0.2, -0.1]  (high, low, negative)
B: [0.1, 0.9, 0.3]   (low, high, medium)  
C: [-0.2, 0.1, 0.8]  (negative, low, high)
```

<span class="fragment">**Hint:** Think student services, technical systems, research</span>

---

## The Embedding Mystery

<span class="fragment">**Plot twist:** Those numbers don't actually map to specific concepts!</span>

<span class="fragment">**We can't say:** "Position 1 = technical-ness, Position 2 = student-ness"</span>

<span class="fragment">**It's a black box** - we know similar concepts get similar numbers, but not what each number means</span>

---

## Why This Matters

<span class="fragment">**You can't debug by looking at individual numbers**</span>

<span class="fragment">**You can't manually adjust embeddings**</span>

<span class="fragment">**But you can compare whole embeddings for similarity**</span>

<span class="fragment">**Think:** GPS coordinates - each number is meaningless alone, but together they locate something</span>

---

# Part 3: Vector Similarity
## How Do We Compare 1024 Numbers?

---

## The Similarity Question

<span class="fragment">**We have:** "database" = [0.2, -0.1, 0.8, ...]</span>

<span class="fragment">**We have:** "PostgreSQL" = [0.3, -0.2, 0.7, ...]</span>

<span class="fragment">**Question:** How similar are these?</span>

---

## Similarity Intuition

<span class="fragment">**Imagine vectors as arrows in space**</span>

<span class="fragment">**Similar meanings** = arrows pointing in similar directions</span>

<span class="fragment">**Different meanings** = arrows pointing different ways</span>

---

## Measuring Similarity

<span class="fragment">**Cosine Similarity** - Most common approach</span>

<span class="fragment">**Range:** -1 to +1</span>
- <span class="fragment">**+1** = Identical meaning</span>
- <span class="fragment">**0** = Unrelated</span>
- <span class="fragment">**-1** = Opposite meaning</span>

---

## Real Similarity Examples

<span class="fragment">**"database" vs "PostgreSQL"** → 0.78 (highly similar)</span>

<span class="fragment">**"student" vs "pupil"** → 0.85 (very similar)</span>

<span class="fragment">**"email" vs "cat"** → 0.12 (unrelated)</span>

<span class="fragment">**"hot" vs "cold"** → -0.23 (somewhat opposite)</span>

---

## Edinburgh Similarity Predictions

**With your partner - 1 minute:**

<span class="fragment">Predict similarity scores (0-1) for these pairs:</span>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2em;">
<div>

- "help desk" vs "support"
- "student" vs "library" 
- "WiFi" vs "email"

</div>
<div>

- "course" vs "module"
- "accommodation" vs "housing"
- "password" vs "authentication"

</div>
</div>

---

## Why Similarity Scores Matter

<span class="fragment">**Search threshold:** Only show results above 0.7 similarity?</span>

<span class="fragment">**Quality control:** Flag low-confidence matches</span>

<span class="fragment">**User experience:** Order results by similarity</span>

---

# Part 4: LLM Jeopardy!
## Test Your Growing Knowledge

---

## LLM Jeopardy Rules

<span class="fragment">**Teams of 3-4 people**</span>

<span class="fragment">**Categories:** Tokens, Embeddings, Edinburgh AI, Common Sense</span>

<span class="fragment">**Points:** 100, 200, 300, 400, 500</span>

<span class="fragment">**5 minutes to play!**</span>

---

## Tokens - 100

**This is what AI models actually process instead of letters and words.**

<span class="fragment">*What are tokens?*</span>

---

## Tokens - 200

**This happens to rare or specialized words when they get tokenized.**

<span class="fragment">*What is they get split into multiple tokens?*</span>

---

## Tokens - 300

**This is why "AI" might cost less than "artificial intelligence" to process.**

<span class="fragment">*What is AI uses fewer tokens?*</span>

---

## Embeddings - 100

**This is how many dimensions the BGE-M3 model creates for each piece of text.**

<span class="fragment">*What is 1024?*</span>

---

## Embeddings - 200

**Similar text gets this type of embedding values.**

<span class="fragment">*What are similar/close values?*</span>

---

## Edinburgh AI - 100

**This type of university document would benefit most from semantic search.**

<span class="fragment">*What are policy documents/procedures/technical documentation?*</span>

---

## Edinburgh AI - 200

**This Edinburgh service area probably handles the most repetitive questions that AI could help with.**

<span class="fragment">*What is student support/IT help desk?*</span>

---

## Common Sense - 100

**This is what you call it when an AI confidently states incorrect information.**

<span class="fragment">*What is hallucination?*</span>

---

# Part 4: Embeddings vs Completions
## Two Different Jobs

---

## Two Types of AI Tasks

<span class="fragment">**Embeddings:** Understanding meaning</span>

<span class="fragment">**Completions:** Generating text</span>

---

## Embeddings Job

<span class="fragment">**Input:** "Edinburgh University support"</span>

<span class="fragment">**Output:** [0.2, -0.1, 0.8, 0.3, ...]</span>

<span class="fragment">**Purpose:** Find similar content</span>

---

## Completions Job

<span class="fragment">**Input:** "How do I reset my Edinburgh password?"</span>

<span class="fragment">**Output:** "To reset your Edinburgh University password, visit..."</span>

<span class="fragment">**Purpose:** Generate helpful responses</span>

---

## Interactive Demo

**Let's try both with the same text:**

<span class="fragment">*"I need help with my email settings"*</span>

---

## Activity: Job Assignment

**Work in pairs - 2 minutes**

<span class="fragment">Which type of AI would you use for each task?</span>

<div style="font-size: 0.8em;">

- Find similar support tickets
- Write an email response  
- Search policy documents
- Generate a help article
- Categorize user requests
- Create FAQ answers

</div>

---

# Part 5: RAG Architecture
## Putting It All Together

---

## The Smart Librarian Returns

<span class="fragment">**Step 1:** Understand what you're asking (Embeddings)</span>

<span class="fragment">**Step 2:** Find relevant information (Vector Search)</span>

<span class="fragment">**Step 3:** Write a helpful answer (Completions)</span>

---

## RAG in Action

```
User: "How do I book a room?"
```

<span class="fragment">**1. Embedding:** [0.3, 0.7, -0.2, ...]</span>

<span class="fragment">**2. Search:** Find similar documents</span>

<span class="fragment">**3. Generate:** "Based on the room booking policy..."</span>

---

## Why RAG Works

<span class="fragment">**Accurate:** Uses your real documents</span>

<span class="fragment">**Current:** Information stays up-to-date</span>

<span class="fragment">**Trustworthy:** Can cite sources</span>

---

## Activity: RAG Design Challenge

**Groups of 3 - 5 minutes**

<span class="fragment">**Scenario:** Design a RAG system for Edinburgh student questions</span>

<span class="fragment">**Your task:**</span>
- <span class="fragment">What documents would you include?</span>
- <span class="fragment">What types of questions should it answer?</span>
- <span class="fragment">How would you measure success?</span>

---

# Part 6: Common Failure Modes
## What Goes Wrong?

---

## Failure Mode Detective

**Let's experience problems firsthand**

<span class="fragment">*Better to see problems than just read about them*</span>

---

## Problem 1: Hallucination

**AI Response:** <span class="fragment">"Edinburgh University was founded in 1492 by Christopher Columbus..."</span>

<span class="fragment">**What went wrong?**</span>

<span class="fragment">*30 seconds - discuss with neighbor*</span>

---

## Problem 2: Out of Context

**User:** "How do I reset my password?"

**AI:** <span class="fragment">"I don't have information about password resets in the documents provided."</span>

<span class="fragment">**What went wrong?**</span>

---

## Problem 3: Too Generic

**User:** "I'm having email problems."

**AI:** <span class="fragment">"Email problems can be frustrating. Have you tried turning it off and on again?"</span>

<span class="fragment">**What went wrong?**</span>

---

## Problem 4: Wrong Context

**User:** "How do I book a room?"

**AI:** <span class="fragment">"Based on the hotel booking policies I found..."</span>

<span class="fragment">**What went wrong?**</span>

---

## Activity: Problem Solving

**Groups of 4 - 3 minutes each problem**

<span class="fragment">**How would you fix each failure mode?**</span>

<span class="fragment">**Think about:**</span>
- <span class="fragment">Better documents?</span>
- <span class="fragment">Better search?</span>
- <span class="fragment">Better prompts?</span>

---

## Quick Debrief

**One insight per group:**

<span class="fragment">*What's the most important thing to get right?*</span>

---

# Part 7: Hands-On Lab Preview
## Time to Build

---

## Lab Objectives

<span class="fragment">**Explore tokens** with real text</span>

<span class="fragment">**Compare embeddings** for similar concepts</span>

<span class="fragment">**Build understanding** for tomorrow's implementation</span>

---

## Lab Structure

<span class="fragment">**Part 1:** Token exploration with Edinburgh examples</span>

<span class="fragment">**Part 2:** Generate embeddings for university terms</span>

<span class="fragment">**Part 3:** See how similar concepts cluster together</span>

---

## Ready for Hands-On?

<span class="fragment">**Questions before we dive in?**</span>

---

## Lab Time!

**Go to:** `final_materials/section-02-foundations/lab/`

<span class="fragment">**Time:** 25 minutes</span>

<span class="fragment">**Goal:** Deep understanding of tokens and embeddings</span>