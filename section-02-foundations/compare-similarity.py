# ask user for two words
word1 = input("What's your first word?")
word2 = input("What's your second word?")
# generate embeddings
import requests

def generate_embeddings(text):
  response = requests.post("http://localhost:11434/api/embed", json={
    "model": "bge-m3",
    "input": text
  })
  data = response.json()
  embedding = data["embeddings"][0]
  return embedding

embedding1 = generate_embeddings(word1)
embedding2 = generate_embeddings(word2)
# compare the embeddings
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
    
# print the result
print(cosine_similarity(embedding1, embedding2))