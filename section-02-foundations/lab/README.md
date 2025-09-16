# Lab 2: Token & Embedding Exploration

## Learning Objectives

By the end of this lab, you will:

- ✅ Understand how text becomes tokens and why it matters
- ✅ Generate and compare embeddings for Edinburgh University concepts
- ✅ See how semantic similarity works in practice
- ✅ Build intuition for when embeddings will be useful

## Time Estimate: 25 minutes

---

## Pre-Lab Setup

**Before starting:**

1. Environment from Lab 1 should still be running
2. If not: `cd environment && docker compose up -d`
3. Create a new file: `lab2_exploration.py`

---

## Part 1: Token Detective Work (8 minutes)

### Step 1: Edinburgh Token Analysis

Let's explore how different Edinburgh-related phrases get tokenized:

```python
import requests
import json

def analyze_tokens_conceptually(text):
    """
    We can't access the exact tokenizer programmatically,
    but we can estimate and learn patterns.
    """
    print(f"\n🔍 Analyzing: '{text}'")
    print(f"📊 Length: {len(text)} characters")
    print(f"📊 Words: {len(text.split())} words")

    # Rough estimation based on common patterns
    estimated_tokens = max(1, len(text.split()) * 1.3)  # Average 1.3 tokens per word
    print(f"📊 Estimated tokens: ~{estimated_tokens:.0f}")

    return estimated_tokens

# Test different Edinburgh phrases
edinburgh_phrases = [
    "Edinburgh University",
    "Edinburgh University technical support",
    "I need help with my MyEd account",
    "How do I reset my password?",
    "Student accommodation booking system",
    "IT",
    "Information Technology",
    "AI",
    "Artificial Intelligence",
    "PostgreSQL",
    "database",
]

print("🎯 TOKEN ANALYSIS FOR EDINBURGH PHRASES")
print("=" * 50)

total_estimated_tokens = 0
for phrase in edinburgh_phrases:
    tokens = analyze_tokens_conceptually(phrase)
    total_estimated_tokens += tokens

print(f"\n📊 Total estimated tokens for all phrases: {total_estimated_tokens:.0f}")
print(f"💰 Approximate cost if this was input to GPT-4: ~${total_estimated_tokens * 0.00003:.5f}")
```

**Run this and observe the patterns:**

```bash
python lab2_exploration.py
```

### Step 2: Token Pattern Discovery

Add this to your file to explore patterns:

```python
def compare_phrases_for_efficiency(phrases_pairs):
    """Compare similar phrases to see which might be more token-efficient."""
    print("\n🔬 EFFICIENCY COMPARISON")
    print("=" * 40)

    for pair in phrases_pairs:
        short_phrase, long_phrase = pair
        short_tokens = analyze_tokens_conceptually(short_phrase)
        long_tokens = analyze_tokens_conceptually(long_phrase)

        print(f"\n📊 SHORT: '{short_phrase}' (~{short_tokens:.0f} tokens)")
        print(f"📊 LONG:  '{long_phrase}' (~{long_tokens:.0f} tokens)")
        print(f"💡 Efficiency gain: {long_tokens - short_tokens:.0f} tokens saved")

# Compare Edinburgh-specific phrase pairs
efficiency_pairs = [
    ("Help with email", "I need assistance with my email configuration"),
    ("Book room", "I would like to make a room booking reservation"),
    ("Reset password", "How can I reset my university login password?"),
    ("IT support", "Information Technology technical support department"),
    ("Student portal", "MyEdinburgh student information portal system"),
]

compare_phrases_for_efficiency(efficiency_pairs)
```

### Reflection Questions (2 minutes)

**Discuss with your partner:**

1. Which Edinburgh phrases were surprisingly long in tokens?
2. How might this affect costs for a university AI system?
3. What patterns do you notice about token efficiency?

---

## Part 2: Edinburgh Embedding Generation (12 minutes)

### Step 3: Generate Embeddings for University Concepts

Now let's generate actual embeddings and compare them:

```python
def get_embedding(text):
    """Generate embedding using our Ollama service."""
    url = "http://localhost:11434/api/embed"
    payload = {
        "model": "bge-m3",
        "input": text
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        embedding = result.get("embeddings", [])[0]
        return embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None

def cosine_similarity(vec1, vec2):
    """Calculate similarity between two vectors."""
    import math

    # Dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    # Magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))

    # Cosine similarity
    if magnitude1 * magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

# Edinburgh University concepts to explore
university_concepts = [
    # Technical concepts
    "database",
    "PostgreSQL",
    "SQL query",

    # Support concepts
    "help desk",
    "technical support",
    "customer service",

    # Student services
    "student accommodation",
    "university housing",
    "dormitory",

    # Academic concepts
    "course registration",
    "class enrollment",
    "academic record",

    # Unrelated concept for comparison
    "weather forecast",
]

print("\n🧠 GENERATING EMBEDDINGS FOR EDINBURGH CONCEPTS")
print("=" * 55)

# Generate embeddings
concept_embeddings = {}
for concept in university_concepts:
    print(f"🔄 Generating embedding for: '{concept}'")
    embedding = get_embedding(concept)
    if embedding:
        concept_embeddings[concept] = embedding
        print(f"✅ Generated {len(embedding)} dimensions")
    else:
        print(f"❌ Failed to generate embedding")

print(f"\n📊 Successfully generated {len(concept_embeddings)} embeddings")
```

### Step 4: Similarity Analysis

Add this to explore how similar different concepts are:

```python
def analyze_similarities(concepts_dict):
    """Compare similarities between different concepts."""
    concept_names = list(concepts_dict.keys())

    print("\n🔬 SIMILARITY ANALYSIS")
    print("=" * 40)

    # Compare pairs and find most/least similar
    similarities = []

    for i, concept1 in enumerate(concept_names):
        for j, concept2 in enumerate(concept_names):
            if i < j:  # Avoid duplicates
                similarity = cosine_similarity(
                    concepts_dict[concept1],
                    concepts_dict[concept2]
                )
                similarities.append((concept1, concept2, similarity))
                print(f"📊 '{concept1}' vs '{concept2}': {similarity:.3f}")

    # Find most similar pair
    similarities.sort(key=lambda x: x[2], reverse=True)

    print(f"\n🏆 MOST SIMILAR PAIR:")
    print(f"   '{similarities[0][0]}' and '{similarities[0][1]}' (similarity: {similarities[0][2]:.3f})")

    print(f"\n🔄 LEAST SIMILAR PAIR:")
    print(f"   '{similarities[-1][0]}' and '{similarities[-1][1]}' (similarity: {similarities[-1][2]:.3f})")

    return similarities

# Analyze the similarities
similarity_results = analyze_similarities(concept_embeddings)
```

### Step 5: Edinburgh-Specific Insights

```python
def edinburgh_insights(similarity_results):
    """Draw insights specific to Edinburgh University use cases."""
    print("\n🎓 EDINBURGH UNIVERSITY INSIGHTS")
    print("=" * 50)

    # Group by similarity levels
    high_similarity = [s for s in similarity_results if s[2] > 0.8]
    medium_similarity = [s for s in similarity_results if 0.6 <= s[2] <= 0.8]
    low_similarity = [s for s in similarity_results if s[2] < 0.4]

    print(f"🔍 HIGH SIMILARITY PAIRS (>0.8): {len(high_similarity)}")
    for concept1, concept2, sim in high_similarity[:3]:  # Show top 3
        print(f"   • '{concept1}' ↔ '{concept2}' ({sim:.3f})")
        print(f"     💡 Users searching for one might want the other")

    print(f"\n🔍 MEDIUM SIMILARITY PAIRS (0.6-0.8): {len(medium_similarity)}")
    for concept1, concept2, sim in medium_similarity[:3]:  # Show top 3
        print(f"   • '{concept1}' ↔ '{concept2}' ({sim:.3f})")
        print(f"     💡 Might be relevant in broader searches")

    print(f"\n🔍 LOW SIMILARITY PAIRS (<0.4): {len(low_similarity)}")
    for concept1, concept2, sim in low_similarity[-3:]:  # Show bottom 3
        print(f"   • '{concept1}' ↔ '{concept2}' ({sim:.3f})")
        print(f"     💡 Clearly different domains")

edinburgh_insights(similarity_results)
```

**Run the complete program:**

```bash
python lab2_exploration.py
```

---

## Part 3: Practical Applications Discussion (5 minutes)

### Discussion Questions

**With your partner, discuss:**

1. **Surprising Similarities:** Which concept pairs were more similar than you expected? Why might that be useful for Edinburgh systems?

2. **Search Implications:** If a student searches for "technical support" but the document mentions "help desk," would traditional keyword search find it? Would semantic search?

3. **Real-World Application:** Based on what you've seen, what Edinburgh University content would benefit most from semantic search?

4. **Quality Assessment:** How would you tell if your embeddings are working well for Edinburgh's specific needs?

### Practical Scenarios

**Consider these Edinburgh scenarios:**

**Scenario A:** Student searches for "accommodation help" but relevant documents use terms like "housing support," "residence assistance," and "dormitory services."

**Scenario B:** Staff member searches for "database issues" but documentation uses "PostgreSQL problems," "SQL errors," and "data access troubles."

**Which approach would work better - traditional keyword search or semantic search? Why?**

---

## Success Criteria ✅

**You've completed this lab when:**

- [ ] You understand how text length affects token count and costs
- [ ] You've generated real embeddings for Edinburgh-specific concepts
- [ ] You've seen semantic similarity in action with university examples
- [ ] You can explain when semantic search would be better than keyword search
- [ ] You're curious about implementing this for real Edinburgh systems

---

## Reflection & Next Steps

### Key Insights to Remember

1. **Tokens:** Shorter phrases = lower costs, but meaning matters more than brevity
2. **Embeddings:** Similar concepts get similar numbers, even with different words
3. **Semantic Search:** Finds relevant content even when exact words don't match
4. **Real-World Impact:** This could significantly improve Edinburgh's knowledge systems

### What's Coming Next

**In Section 3, we'll learn:**

- How all these components fit together in a complete system
- The architecture patterns for RAG implementations
- How to design systems that serve Edinburgh users effectively

### Questions for Section 3

**Based on what you've learned, what questions do you have about:**

- How to organize embeddings for thousands of Edinburgh documents?
- How to ensure search results are accurate and relevant?
- How to measure if your semantic search is actually helping users?

---

## Troubleshooting

### Common Issues

**Embedding generation fails:**

```bash
# Check if Ollama is running
docker ps
# Restart if needed
cd environment && docker compose restart ollama
```

**Similarity calculations seem wrong:**

- Check that both embeddings have the same dimensions (1024)
- Verify no null values in the embedding arrays
- Cosine similarity should be between -1 and 1

**Python import errors:**

```bash
# Ensure virtual environment is activated
source .venv/bin/activate
```

### Getting Help

If you get stuck:

1. Check with your lab partner first
2. Compare results with neighboring teams
3. Raise your hand for instructor assistance
4. Remember: debugging is learning!
