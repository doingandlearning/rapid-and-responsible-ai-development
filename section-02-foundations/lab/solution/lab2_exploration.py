import requests
import json
import math

def analyze_tokens_conceptually(text):
    """
    Estimate token count for a phrase.
    """
    print(f"\n🔍 Analyzing: '{text}'")
    print(f"📊 Length: {len(text)} characters")
    print(f"📊 Words: {len(text.split())} words")
    estimated_tokens = max(1, len(text.split()) * 1.3)  # Average 1.3 tokens per word
    print(f"📊 Estimated tokens: ~{estimated_tokens:.0f}")
    return estimated_tokens

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

def compare_phrases_for_efficiency(phrases_pairs):
    print("\n🔬 EFFICIENCY COMPARISON")
    print("=" * 40)
    for pair in phrases_pairs:
        short_phrase, long_phrase = pair
        short_tokens = analyze_tokens_conceptually(short_phrase)
        long_tokens = analyze_tokens_conceptually(long_phrase)
        print(f"\n📊 SHORT: '{short_phrase}' (~{short_tokens:.0f} tokens)")
        print(f"📊 LONG:  '{long_phrase}' (~{long_tokens:.0f} tokens)")
        print(f"💡 Efficiency gain: {long_tokens - short_tokens:.0f} tokens saved")

efficiency_pairs = [
    ("Help with email", "I need assistance with my email configuration"),
    ("Book room", "I would like to make a room booking reservation"),
    ("Reset password", "How can I reset my university login password?"),
    ("IT support", "Information Technology technical support department"),
    ("Student portal", "MyEdinburgh student information portal system"),
]

compare_phrases_for_efficiency(efficiency_pairs)

def get_embedding(text):
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
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))
    if magnitude1 * magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

university_concepts = [
    "database",
    "PostgreSQL",
    "SQL query",
    "help desk",
    "technical support",
    "customer service",
    "student accommodation",
    "university housing",
    "dormitory",
    "course registration",
    "class enrollment",
    "academic record",
    "weather forecast",
]

print("\n🧠 GENERATING EMBEDDINGS FOR EDINBURGH CONCEPTS")
print("=" * 55)

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

def analyze_similarities(concepts_dict):
    concept_names = list(concepts_dict.keys())
    print("\n🔬 SIMILARITY ANALYSIS")
    print("=" * 40)
    similarities = []
    for i, concept1 in enumerate(concept_names):
        for j, concept2 in enumerate(concept_names):
            if i < j:
                similarity = cosine_similarity(
                    concepts_dict[concept1], 
                    concepts_dict[concept2]
                )
                similarities.append((concept1, concept2, similarity))
                print(f"📊 '{concept1}' vs '{concept2}': {similarity:.3f}")
    similarities.sort(key=lambda x: x[2], reverse=True)
    print(f"\n🏆 MOST SIMILAR PAIR:")
    print(f"   '{similarities[0][0]}' and '{similarities[0][1]}' (similarity: {similarities[0][2]:.3f})")
    print(f"\n🔄 LEAST SIMILAR PAIR:")
    print(f"   '{similarities[-1][0]}' and '{similarities[-1][1]}' (similarity: {similarities[-1][2]:.3f})")
    return similarities

similarity_results = analyze_similarities(concept_embeddings)

def edinburgh_insights(similarity_results):
    print("\n🎓 EDINBURGH UNIVERSITY INSIGHTS")
    print("=" * 50)
    high_similarity = [s for s in similarity_results if s[2] > 0.8]
    medium_similarity = [s for s in similarity_results if 0.6 <= s[2] <= 0.8]
    low_similarity = [s for s in similarity_results if s[2] < 0.4]
    print(f"🔍 HIGH SIMILARITY PAIRS (>0.8): {len(high_similarity)}")
    for concept1, concept2, sim in high_similarity[:3]:
        print(f"   • '{concept1}' ↔ '{concept2}' ({sim:.3f})")
        print(f"     💡 Users searching for one might want the other")
    print(f"\n🔍 MEDIUM SIMILARITY PAIRS (0.6-0.8): {len(medium_similarity)}")
    for concept1, concept2, sim in medium_similarity[:3]:
        print(f"   • '{concept1}' ↔ '{concept2}' ({sim:.3f})")
        print(f"     💡 Might be relevant in broader searches")
    print(f"\n🔍 LOW SIMILARITY PAIRS (<0.4): {len(low_similarity)}")
    for concept1, concept2, sim in low_similarity[-3:]:
        print(f"   • '{concept1}' ↔ '{concept2}' ({sim:.3f})")
        print(f"     💡 Clearly different domains")

edinburgh_insights(similarity_results)
