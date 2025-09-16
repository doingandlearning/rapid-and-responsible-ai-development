# Section 5 Solution Files

## Complete Implementation
This directory contains the complete, working solution for Section 5: Document Processing & PDF Chunking.

## Files Included

### `lab5_document_processing.py`
**Complete solution script** implementing all lab requirements:
- Edinburgh document simulation and processing
- Fixed-size and content-aware chunking strategies
- Quality assessment and strategy comparison
- Database integration with embeddings
- Storage verification and validation

## Running the Solution

### Prerequisites
Ensure your environment is ready:
```bash
# Start services
cd environment && docker compose up -d

# Activate Python environment
source .venv/bin/activate

# Verify Section 4 database is working
python final_materials/section-04-postgres-pgvector/solution/step1_verification.py
```

### Execute Complete Solution
```bash
cd final_materials/section-05-document-processing/solution
python lab5_document_processing.py
```

## Expected Output

### 1. Document Processing Phase
```
🚀 SECTION 5: DOCUMENT PROCESSING & PDF CHUNKING
================================================================================
Processing Edinburgh University IT Documents

📚 Creating sample Edinburgh documents...
✅ Created 3 sample documents
```

### 2. Strategy Comparison Phase
```
📊 COMPREHENSIVE CHUNKING STRATEGY EVALUATION
================================================================================
Document: Edinburgh University VPN Policy Document
======================================================================

🔧 Testing: Fixed-Size (200w, 40w overlap)
📝 Creating chunks using fixed strategy...
   Chunk size: 200 words, Overlap: 40 words
✅ Created 8 chunks
   Chunks created: 8
   Avg words/chunk: 167.5
   Quality score: 85.2/100
   Issues: 1 broken sentences, 0 duplicates

🔧 Testing: Content-Aware (400w max)
📝 Creating chunks using content_aware strategy...
   Chunk size: 400 words, Overlap: 0 words
✅ Created 4 chunks
   Chunks created: 4
   Avg words/chunk: 289.3
   Quality score: 91.7/100
   Issues: 0 broken sentences, 0 duplicates

🏆 Best Strategy: Content-Aware (400w max)
   Quality Score: 91.7/100
```

### 3. Database Integration Phase
```
💾 DATABASE STORAGE AND INTEGRATION
============================================================
🗄️  Setting up document chunks table...
✅ Table and indexes created

💾 Storing 8 chunks in database...
🧠 Generating embedding for chunk 1/8... ✅
🧠 Generating embedding for chunk 2/8... ✅
💾 Committed batch 1-5
🧠 Generating embedding for chunk 8/8... ✅
✅ Stored 8 chunks successfully

🎉 Successfully stored 8 chunks in vector database!

📊 Database Contents:
   'Edinburgh University VPN Policy Document': 8 chunks, 289.3 avg words, 8 with embeddings
```

### 4. Storage Verification Phase
```
✅ VERIFYING CHUNK STORAGE
==================================================
📊 Total chunks stored: 8
🧠 Chunks with embeddings: 8/8

📄 Document breakdown:
   • Edinburgh University VPN Policy Document
     Chunks: 8, Avg words: 289.3, Embeddings: 8

📖 Sample chunks:
   1. Page 1, Section: VPN Access Policy (285 words)
      'VPN Access Policy University of Edinburgh Document Version: 2024.1 Effective Date: January 1, 2024 1. Purpose and Scope...'

🔢 Embedding dimensions: 1024 (should be 1024 for BGE-M3)
   ✅ Embeddings are correct size
```

### 5. Success Summary
```
================================================================================
✅ SECTION 5 COMPLETE!
Successfully processed Edinburgh IT documents with:
  • Multiple chunking strategies tested and evaluated
  • Quality assessment and optimization
  • Database storage with embeddings
  • Storage verification and validation

💡 Key findings:
  • Best strategy: Content-Aware (400w max)
  • Quality score: 91.7/100
  • Chunks stored: 8 with embeddings

🎯 Document chunks ready for Section 6: RAG Pipeline Integration!
```

## Understanding the Implementation

### Key Components

#### 1. Document Processing Pipeline
```python
def main():
    # 1. Create realistic Edinburgh documents
    sample_documents = create_sample_edinburgh_documents()
    
    # 2. Test multiple chunking strategies
    best_result = compare_chunking_strategies(document_data)
    
    # 3. Store optimal chunks with embeddings
    stored_count = store_chunks_in_database(best_chunks)
    
    # 4. Verify similarity search works
    test_chunk_retrieval(query)
```

#### 2. Chunking Strategies Implemented
- **Fixed-Size:** Word-based chunking with configurable overlap
- **Content-Aware:** Paragraph-based chunking respecting document structure  
- **Section Detection:** Automatic identification of document sections

#### 3. Quality Assessment Framework
```python
quality_report = {
    'total_chunks': len(chunks),
    'word_count_stats': {...},           # Statistical analysis
    'quality_issues': {...},             # Problem identification
    'metadata_coverage': {...},          # Attribution completeness
    'overall_quality_score': score       # 0-100 composite score
}
```

#### 4. Database Integration
- **Enhanced schema** with metadata fields
- **Batch processing** for efficient storage
- **Vector embeddings** via Ollama BGE-M3
- **Storage verification** with comprehensive validation

## Customization Options

### Document Types
Modify `create_sample_edinburgh_documents()` to test with different document types:
```python
# Add your own Edinburgh documents
documents['your-document.pdf'] = {
    'title': 'Your Document Title',
    'pages': [
        (1, "Your document text here..."),
        (2, "More document content..."),
    ]
}
```

### Chunking Parameters
Adjust chunking strategies in `compare_chunking_strategies()`:
```python
strategies = [
    ("Your Strategy", "fixed", 250, 30),        # 250 words, 30 overlap
    ("Custom Content", "content_aware", 350, 0), # 350 max words
]
```

### Quality Thresholds
Modify quality scoring in `assess_chunk_quality()`:
```python
# Adjust penalty weights
quality_score -= (broken_sentences / len(chunks)) * 30  # Stricter
quality_score -= (very_short / len(chunks)) * 10        # More lenient
```

## Troubleshooting

### Common Issues

**Ollama Connection Errors:**
```bash
# Verify Ollama is running
docker ps | grep ollama

# Check BGE-M3 model is available  
docker exec ollama-service ollama list
```

**Database Connection Issues:**
```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Test connection
python -c "import psycopg; psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')"
```

**Slow Embedding Generation:**
```python
# Reduce batch size for testing
stored_count = store_chunks_in_database(demo_chunks[:3])  # Process only 3 chunks
```

### Performance Optimization

**For Large Document Sets:**
```python
# Implement parallel processing
from concurrent.futures import ThreadPoolExecutor

def parallel_embed_chunks(chunks, max_workers=3):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_embedding, chunk.text) for chunk in chunks]
        return [future.result() for future in futures]
```

**For Memory Efficiency:**
```python
# Process in smaller batches
def batch_process_documents(documents, batch_size=5):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        process_document_batch(batch)
        time.sleep(1)  # Rate limiting
```

## Next Steps

After running this solution successfully:

1. **Experiment** with different Edinburgh documents
2. **Tune** chunking parameters for your specific needs  
3. **Analyze** quality scores and optimize accordingly
4. **Prepare** for Section 6 RAG pipeline integration

The chunks and embeddings created by this solution will be used directly in Section 6 for building complete RAG question-answering systems.

## Validation Checklist

Confirm your solution works correctly:

- [ ] All 3 Edinburgh documents processed successfully
- [ ] Multiple chunking strategies compared with quality scores  
- [ ] Best strategy identified (typically Content-Aware with 85%+ quality)
- [ ] Document chunks stored in database with embeddings
- [ ] Storage verification confirms chunks and embeddings are correct
- [ ] Metadata preserved (page numbers, sections, word counts)
- [ ] No errors in embedding generation or database operations

**Success = Ready for Section 6! 🎉**