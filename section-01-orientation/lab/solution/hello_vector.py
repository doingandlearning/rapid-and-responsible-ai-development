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
