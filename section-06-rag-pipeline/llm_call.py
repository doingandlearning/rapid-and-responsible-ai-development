import requests
import psycopg
import json
import sys

DB_CONFIG = {
  "dbname": "pgvector",
  "user": "postgres",
  "password": "postgres",
  "host": "localhost",
  "port": "5050"
}

request_count = 0

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "gpt-3.5-turbo"
LLM_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# generate embeddings
def get_embeddings(text):
  data = {
    "model": "bge-m3",
    "input": text
  }

  response = requests.post(OLLAMA_URL, 
                          json=data
  )
  response.raise_for_status()
  data = response.json()
  embedding = data.get("embeddings", [])
  if len(embedding) == 0:
    raise Exception("No embeddings.")
  return embedding[0]

def get_k_nearest_neighbors(user_embedding, k=3):
  with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
      cur.execute(
        """
        SELECT 
          text,
          id,
          document_title,
          page_number,
          section_title
          , 1 - (embedding <=> %s) AS similarity
        FROM document_chunks
        ORDER BY similarity DESC
        LIMIT %s
        """,
        (json.dumps(user_embedding), k)

      )
      results = cur.fetchall()
      search_results = []

      for text, id, document_title, page_number, section_title, similarity in results:
        if similarity >= 0.4:
          search_results.append(
            f"""
            Text: {text} 
            Source: {document_title} on page {page_number}  [section: {section_title}]
            Similarity score: {similarity}
            """
          )
      return search_results

def query_llm(user_query, relevant_documents):

  system_prompt = """
  You are an AI assistant for Edinburgh University's IT Services.
  Your role and responsibilities:
  - Provide accurate, helpful answers using ONLY the context from official Edinburgh University documents
- Always cite your sources using the format: (Source: Document Name, Page X, Section (if exists))
- There will be up to three chunks of relevant documents - reference all that you use for your response in the required format
- If the context doesn't contain relevant information, clearly state "I don't have that information in the available documents"
- Use professional, helpful language appropriate for university staff and students
- Focus on practical, actionable guidance
- When procedures have multiple steps, present them clearly
  """

  user_prompt = f"""
  Context from Edinburgh University documents:

  {relevant_documents}

  User question: {user_query}

  Please provide a helpful, accurate answer based on the context above. Remember to cite your sources.
  """
  try:
    response = requests.post(LLM_ENDPOINT,
    headers={
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    json={
      "model": MODEL,
      "messages": [
        {"role": "system", "content":  system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      "temperature": 0.2,
      "max_tokens": 600 
    })

    data = response.json()
    return {"answer": data["choices"][0]["message"]["content"]}
  except Exception as e:
    return {
      'answer': "Something went wrong"
    }
def verify_llm_response(llm_response, user_query):

  system_prompt = """
  You are a university auditor - return a score from 0-5 based on the following criteria.
  Only return that score - nothing else - no supporting text - that's it - i mean it!!

  - Professional tone
  - Actionable
  - Sources clearly attributed
  - Actually answers  the user query
  - Up to date information
  """


  user_prompt = f"""
  The LLM response:

  {llm_response}

  User question: {user_query}

  Please provide a helpful, accurate answer based on the context above. Remember to cite your sources.
  """
  try:
    response = requests.post(LLM_ENDPOINT,
    headers={
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    json={
      "model": MODEL,
      "messages": [
        {"role": "system", "content":  system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      "temperature": 1,
      "max_tokens": 600 
    })

    data = response.json()
    return {"answer": data["choices"][0]["message"]["content"]}
  except Exception as e:
    return {
      'answer': "Something went wrong"
    }

# Get our user input
user_query = input("What do you want? ")

# Generate embeddings
user_embedding = get_embeddings(user_query)

# Get relevant documents
relevant_documents = get_k_nearest_neighbors(user_embedding)

# Call to our LLM
if len(relevant_documents) == 0:
  print("I don't know how to help. Have you tried turning it on and off again?")
  sys.exit(1)

print(relevant_documents)
llm_response = query_llm(user_query, relevant_documents)

# Check it does have source
# Check that it 
score_response = verify_llm_response(llm_response, user_query)

with open("log.txt", "a") as file:
  file.write(f"{score_response} - other metadata blah")


print(llm_response["answer"])
