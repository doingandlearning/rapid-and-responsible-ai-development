# Solution Reference: PostgreSQL + pgvector Lab

This folder contains complete, working solutions for all lab exercises. Each solution includes detailed explanations, error handling, and production-ready code.

## 📁 Solution Files

### Step 1: Database Verification (`step1_verification.py`)
**Purpose**: Verify PostgreSQL + pgvector setup is complete and functional

**What it does**:
- ✅ Tests database connection
- ✅ Verifies pgvector extension installation
- ✅ Tests all vector operators (`<->`, `<#>`, `<=>`)
- ✅ Confirms 1024-dimension vector support (BGE-M3 compatibility)
- ✅ Checks available index methods (HNSW, IVFFlat)
- ✅ Runs production readiness checks

**When to use**: If you have connection issues or want to verify your setup

**Run with**:
```bash
cd solution/
python step1_verification.py
```

---

### Step 2: Schema Creation (`step2_schema_creation.py`)
**Purpose**: Create optimized database schema for Edinburgh knowledge base

**What it creates**:
- ✅ Main `edinburgh_docs` table with proper constraints
- ✅ Performance indexes for text search
- ✅ Automatic triggers for metadata maintenance
- ✅ Helper functions for common queries
- ✅ Summary views for reporting
- ✅ Full audit trail capabilities

**Key features**:
- Vector columns for title and content embeddings
- Text search vectors for hybrid search
- Automatic word/character count calculation
- Content deduplication via hashing
- Proper data types and constraints

**Run with**:
```bash
cd solution/
python step2_schema_creation.py
```

---

### Step 3: Data Loading (`step3_data_loading.py`)
**Purpose**: Load realistic Edinburgh documents with embeddings

**What it loads**:
- ✅ 10 comprehensive Edinburgh IT/service documents
- ✅ Categories: IT Support, Library Services, Accommodation, Student Services
- ✅ Both title and content embeddings for each document
- ✅ Proper metadata (categories, URLs, dates)
- ✅ Retry logic for embedding generation
- ✅ Comprehensive error handling

**Features**:
- Automatic embedding generation via Ollama
- Progress tracking with detailed output  
- Verification of loaded data integrity
- Category and content statistics
- Sample query examples

**Run with**:
```bash
cd solution/
python step3_data_loading.py
```

---

### Step 4: Performance Testing (`step4_performance_optimization.py`)
**Purpose**: Create vector indexes and benchmark performance

**What it does**:
- ✅ Tests baseline performance without indexes
- ✅ Creates optimized HNSW vector indexes
- ✅ Measures performance improvements
- ✅ Provides scaling analysis
- ✅ Tests concurrent query scenarios
- ✅ Edinburgh SLA compliance checking

**Index configuration**:
- HNSW indexes for both title and content embeddings
- Optimized parameters (`m=16, ef_construction=64`)
- Automatic statistics updating
- Performance monitoring queries

**Run with**:
```bash
cd solution/
python step4_performance_optimization.py
```

---

## 🚀 Quick Start (Complete Lab Solution)

If you want to run through the entire lab quickly:

```bash
cd final_materials/section-04-postgres-pgvector/solution/

# 1. Verify setup
python step1_verification.py

# 2. Create schema
python step2_schema_creation.py

# 3. Load data with embeddings
python step3_data_loading.py

# 4. Optimize performance
python step4_performance_optimization.py
```

## 🔧 Configuration

All solutions use these default settings:

```python
# Database connection
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# Ollama embedding service
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"  # 1024 dimensions
```

## 📊 Expected Results

After running all solutions, you should have:

- **Database**: `edinburgh_docs` table with 10 documents
- **Embeddings**: 20 total embeddings (title + content for each doc)
- **Indexes**: HNSW vector indexes for fast similarity search
- **Performance**: <1 second search times for most queries
- **Categories**: IT Support, Library Services, Accommodation, Student Services

## 🛠️ Troubleshooting Solutions

### Connection Issues
```bash
# Check if containers are running
docker ps

# Restart if needed
cd ../../environment && docker compose restart
```

### Embedding Generation Fails
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull model if missing
docker exec ollama-service ollama pull bge-m3
```

### Slow Performance
```bash
# Check if indexes were created
psql -h localhost -p 5050 -U postgres -d pgvector -c "\d+ edinburgh_docs"

# Look for HNSW indexes
```

## 📖 Understanding the Code

### Error Handling Patterns
All solutions include comprehensive error handling:

```python
try:
    # Database operation
    pass
except psycopg.OperationalError as e:
    # Connection-specific handling
    pass
except Exception as e:
    # General error handling with context
    pass
```

### Embedding Generation Pattern
Consistent retry logic across all solutions:

```python
def get_embedding(text, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Ollama API call
            return embedding
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    return None
```

### Performance Measurement Pattern
Timing and analysis in all performance-critical code:

```python
start_time = time.time()
# Operation
operation_time = time.time() - start_time
print(f"Operation completed in {operation_time:.3f}s")
```

## 🎯 Production Considerations

These solutions include production-ready features:

- **Comprehensive error handling** with specific error types
- **Retry logic** for unreliable network operations
- **Performance monitoring** with timing and statistics
- **Resource cleanup** with proper connection management
- **Data validation** before database insertion
- **Security considerations** with parameterized queries
- **Scalability planning** with resource usage analysis

## 📚 Learning From Solutions

Each solution file includes:

1. **Detailed docstrings** explaining what each function does
2. **Inline comments** for complex operations
3. **Error handling examples** for common failure modes
4. **Performance considerations** and optimization tips
5. **Production deployment guidance**

## 💡 Extending the Solutions

These solutions provide a foundation for:

- **Adding more document types** (PDFs, Word docs, etc.)
- **Implementing batch processing** for large document sets
- **Creating specialized indexes** for specific use cases
- **Adding monitoring and alerting** for production systems
- **Implementing hybrid search** combining text and vectors
- **Building REST APIs** on top of the database layer

## 🆘 Getting Additional Help

If solutions don't work in your environment:

1. **Check Prerequisites**: Docker containers running, Python dependencies installed
2. **Review Error Messages**: Solutions provide detailed error context
3. **Test Components**: Run verification script first to isolate issues
4. **Environment Variables**: Verify database connection parameters
5. **Resource Constraints**: Ensure adequate memory for embeddings and indexes

The solutions are designed to work in the standard course environment, but include guidance for adapting to different setups.