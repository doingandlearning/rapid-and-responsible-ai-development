# Lab 1: Environment Verification & First Embedding

## Learning Objectives

By the end of this lab, you will:

- ✅ Verify your complete development environment is working
- ✅ Generate your first embedding using Ollama
- ✅ See what an embedding looks like (without needing to understand it yet!)
- ✅ Have questions ready for Section 2: "How does this actually work?"

## Time Estimate: 10 minutes

---

## Pre-Lab Check

**Before starting, ensure you have:**

1. Docker Desktop running
2. Virtual environment activated (`source .venv/bin/activate`)
3. All services started (`cd environment && docker compose up -d`)

**Quick verification:**

```bash
# Check services are running
docker ps

# Should see containers for:
# - pgvector-db (PostgreSQL)
# - ollama-service (Ollama)
```

---

## Part 1: Service Health Check (3 minutes)

### Step 1: Verify PostgreSQL Connection

Create a new file called `hello_vector.py`:

```python
import psycopg
import requests
import json

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

def test_database():
    """Test PostgreSQL connection and pgvector extension."""
    print("🔍 Testing database connection...")
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Test basic connection
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"✅ PostgreSQL connected: {version.split(',')[0]}")

                # Test pgvector extension
                cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                if cur.fetchone():
                    print("✅ pgvector extension is installed")
                else:
                    print("❌ pgvector extension not found")
                    return False
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# Test the database
if test_database():
    print("🎉 Database is ready!\n")
else:
    print("❌ Fix database issues before continuing")
    exit(1)
```

**Run it:**

```bash
python hello_vector.py
```

**Expected output:**

```
🔍 Testing database connection...
✅ PostgreSQL connected: PostgreSQL 17.x
✅ pgvector extension is installed
🎉 Database is ready!
```

---

## Part 2: Generate Your First Embedding (7 minutes)

### Step 2: Test Ollama Embedding Service

Add this to your `hello_vector.py` file:

```python
def test_ollama():
    """Test Ollama embedding service."""
    print("🧠 Testing Ollama embedding service...")
    try:
        url = "http://localhost:11434/api/embed"
        payload = {
            "model": "bge-m3",
            "input": "Hello, vector world!"
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        embedding = result.get("embeddings", [])

        if embedding and len(embedding[0]) > 0:
            print(f"✅ Embedding generated: {len(embedding[0])} dimensions")
            print(f"   First few values: {embedding[0][:5]}")
            print(f"   Last few values: {embedding[0][-5:]}")
            print(f"   This is how AI 'understands' your text!")
            return embedding[0]
        else:
            print("❌ No embedding returned")
            return None

    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return None

# Test Ollama
embedding = test_ollama()
if embedding:
    print("🎉 Ollama is working!\n")
    print("🤔 Questions for Section 2:")
    print("   - What do these 1024 numbers actually represent?")
    print("   - How can numbers capture the 'meaning' of text?")
    print("   - What makes one embedding similar to another?")
    print("   - How does this help us build better search?")
else:
    print("❌ Fix Ollama issues before continuing")
    exit(1)
```

**Run again:**

```bash
python hello_vector.py
```

**Expected output:**

```
✅ Embedding generated: 1024 dimensions
   First few values: [0.0123, -0.0456, 0.0789, -0.0321, 0.0654]
   Last few values: [0.0987, -0.0234, 0.0567, -0.0890, 0.0345]
   This is how AI 'understands' your text!
🎉 Ollama is working!

🤔 Questions for Section 2:
   - What do these 1024 numbers actually represent?
   - How can numbers capture the 'meaning' of text?
   - What makes one embedding similar to another?
   - How does this help us build better search?
```

---

## Reflection Questions (Building Curiosity for Section 2)

**Look at those 1024 numbers that represent "Hello, vector world!" Turn to your partner and discuss:**

1. **Curiosity**: What do you think those numbers actually represent? How could numbers capture the "meaning" of text?

2. **Patterns**: We saw the embedding has both positive and negative values. What might that mean?

3. **Scale**: This is just one sentence. How do you think this would work with a 50-page university policy document?

4. **Institutional Context**: What Edinburgh systems or documents would benefit from this kind of "meaning representation"?

5. **Questions for Section 2**: What do you want to understand about how embeddings actually work?

---

## Success Criteria ✅

**You've completed this lab when:**

- [ ] All services are verified working (PostgreSQL + Ollama)
- [ ] You've generated your first embedding
- [ ] You've seen what an embedding looks like (1024 dimensions of numbers)
- [ ] You have genuine curiosity about how this works
- [ ] You can relate this to potential Edinburgh University applications

---

## Troubleshooting

### **Docker Services Not Running**

```bash
cd environment
docker compose down
docker compose up -d
docker ps  # Verify both containers are running
```

### **Ollama Model Not Found**

```bash
docker exec ollama-service ollama list
# If bge-m3 not listed:
docker exec ollama-service ollama pull bge-m3
```

### **PostgreSQL Connection Issues**

- Verify port 5050 is not blocked
- Check if another PostgreSQL instance is running on port 5432
- Try restarting Docker Desktop

### **Python Import Errors**

```bash
# Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

---

## What's Next?

**In Section 2, we'll dive deeper into:**

- How embeddings actually work (the math behind the magic)
- Why 1024 dimensions? What do they represent?
- Different types of LLM operations (embeddings vs completions)
- How to compare embeddings for similarity

**Your environment is ready and you've seen your first embedding! Questions welcomed in Section 2! 🧠**
