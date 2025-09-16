# Section 5: Document Processing & PDF Chunking

---

## Learning Objectives

By the end of this section, you will:
- ✅ Understand why document chunking is essential for RAG systems
- ✅ Implement different chunking strategies (fixed-size, semantic, structure-aware)
- ✅ Extract and process text from various document formats
- ✅ Optimize chunk size and overlap for embedding quality
- ✅ Handle metadata preservation and document structure
- ✅ Build a production-ready document processing pipeline

---

## Why Document Chunking Matters

### The Challenge
Edinburgh's documents are typically **long and complex**:
- IT policy documents: 20-50 pages
- Student handbooks: 100+ pages
- Technical manuals: 200+ pages
- Research papers: 10-30 pages

---

## LLM Context Window Limitations

### The Technical Reality
- Most LLMs: **4,000-32,000 tokens** max
- Average university policy: **50,000+ tokens**
- **We can't fit entire documents** in a single query

---

## The Chunking Solution

### Before Chunking 📄
```
[Entire 100-page Student Handbook]
↓
❌ Too large for LLM context window
❌ Expensive to process
❌ Slow response times
❌ Poor relevance matching
```

---

## After Chunking 📄➡️📄📄📄

### The Transformation
```
[100-page handbook] → [200 focused chunks]
↓
✅ Fits in context window
✅ Cost-effective processing  
✅ Fast similarity search
✅ Precise relevance matching
```

---

## Real Edinburgh Use Case

### Student Query: *"How do I reset my password?"*

**Without chunking:**
- Search entire IT handbook (10,000+ words)
- LLM processes irrelevant sections
- Expensive, slow, unfocused response

---

## With Chunking: The Difference

### Student Query: *"How do I reset my password?"*

**With chunking:**
- Find relevant chunks: "Password Reset Procedures"
- LLM processes only 300-500 relevant words
- Fast, accurate, cost-effective response

---

## Chunking Strategies: Overview

### 🔧 Three Main Approaches

1. **Fixed-Size Chunking**
   - Split by word/character count
   - Simple and predictable
   - Good for consistent processing

---

## Strategy 2: Content-Aware Chunking

### How It Works
- Split by document structure
- Respects paragraphs, sections, headings
- Better semantic coherence

---

## Strategy 3: Semantic Chunking

### The Most Sophisticated Approach
- Split by topic/meaning changes
- Best quality results
- Higher complexity to implement

---

## Strategy 1: Fixed-Size Chunking

### ✅ Advantages
- **Simple to implement**
- **Predictable chunk sizes**
- **Consistent processing time**
- **Works with any document type**

---

## Fixed-Size Chunking: Disadvantages

### ❌ The Downsides
- **May split sentences mid-word**
- **Can break logical sections**
- **No awareness of document structure**

---

## Fixed-Size Chunking: Example

### 📊 Edinburgh IT Policy
```python
# 300-word chunks with 50-word overlap
chunk_1 = "Edinburgh University password policy requires..."
chunk_2 = "...policy requires all staff and students to..."
chunk_3 = "...students to use strong passwords with..."
```

---

## Strategy 2: Content-Aware Chunking

### ✅ Advantages
- **Respects document structure**
- **Preserves logical sections**
- **Better semantic coherence**
- **Maintains context boundaries**

---

## Content-Aware Chunking: Disadvantages

### ❌ The Downsides
- **Variable chunk sizes**
- **More complex implementation**
- **Document format dependent**

---

## Content-Aware Chunking: Example

### 📊 Edinburgh Student Handbook
```python
chunks = [
    "## Academic Calendar\nThe academic year at Edinburgh...",
    "## Registration Process\nAll students must register...", 
    "## Library Services\nThe university library provides..."
]
```

---

## Strategy 3: Semantic Chunking

### ✅ Advantages
- **Topic-aware boundaries**
- **Highest semantic coherence** 
- **Best search relevance**
- **Natural information grouping**

---

## Semantic Chunking: Disadvantages

### ❌ The Downsides
- **Complex implementation**
- **Requires NLP models**
- **Unpredictable chunk sizes**
- **Higher processing cost**

---

## Semantic Chunking: Example

### 📊 Edinburgh Research Paper
```python
# Semantic boundaries detected automatically
chunks = [
    "Introduction and background on campus networking...",
    "Methodology for WiFi performance analysis...",
    "Results showing connection speed improvements..."
]
```

---

## Implementation: Fixed-Size Chunking

### 🐍 Python Implementation
```python
import PyPDF2
from typing import List, Iterator

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text
```

---

## Fixed-Size Chunker Function

### 🐍 The Core Algorithm
```python
def fixed_size_chunker(text: str, chunk_size: int = 300, 
                      overlap: int = 50) -> Iterator[str]:
    """Split text into fixed-size chunks with overlap."""
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        yield " ".join(chunk)
```

---

## Implementation: Content-Aware Chunking

### 🐍 Python Implementation
```python
import re
from typing import List

def content_aware_chunker(text: str, 
                         max_chunk_size: int = 500) -> List[str]:
    """Split text by paragraphs, respecting size limits."""
    
    # Split by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
```

---

## Content-Aware Chunker Logic

### 🐍 The Algorithm
```python
    for paragraph in paragraphs:
        # If adding this paragraph exceeds limit, start new chunk
        if len(current_chunk.split()) + len(paragraph.split()) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                # Paragraph is too large, use fixed-size chunking
                chunks.extend(fixed_size_chunker(paragraph, max_chunk_size))
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
```

---

## Metadata Preservation

### 🏷️ Why Metadata Matters

When users get AI responses, they need:
- **Source attribution**: "According to the IT Handbook, page 23..."
- **Document context**: "From the 2024 Student Guide..."  
- **Page references**: "See page 15 for more details..."
- **Section identification**: "This is from the WiFi Setup section..."

---

## Essential Metadata Fields

### 📊 Metadata Structure
```python
chunk_metadata = {
    'document_id': 'student-handbook-2024',
    'document_title': 'Edinburgh Student Handbook 2024',
    'page_number': 23,
    'section': 'IT Services',
    'subsection': 'Password Reset',
    'chunk_index': 45,
    'word_count': 287,
    'created_at': '2024-09-01T10:30:00Z'
}
```

---

## Metadata Implementation

### 🐍 DocumentChunk Class
```python
from dataclasses import dataclass
from typing import List, Optional
import uuid
from datetime import datetime

@dataclass
class DocumentChunk:
    id: str
    document_id: str
    document_title: str
    text: str
    page_number: Optional[int]
    section: Optional[str] 
    chunk_index: int
    word_count: int
    character_count: int
    created_at: datetime
```

---

## Chunking with Metadata Function

### 🐍 The Implementation
```python
def chunk_with_metadata(pdf_path: str, 
                       document_id: str,
                       document_title: str,
                       chunk_size: int = 300) -> List[DocumentChunk]:
    """Extract and chunk PDF with full metadata."""
    
    reader = PyPDF2.PdfReader(pdf_path)
    chunks = []
    chunk_index = 0
```

---

## Metadata Processing Loop

### 🐍 Page-by-Page Processing
```python
    for page_num, page in enumerate(reader.pages, 1):
        page_text = page.extract_text()
        
        # Chunk this page's text
        for chunk_text in fixed_size_chunker(page_text, chunk_size):
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                document_title=document_title,
                text=chunk_text,
                page_number=page_num,
                section=None,  # Could be extracted from headings
                chunk_index=chunk_index,
                word_count=len(chunk_text.split()),
                character_count=len(chunk_text),
                created_at=datetime.now()
            )
            chunks.append(chunk)
            chunk_index += 1
    
    return chunks
```

---

## Chunk Size Optimization

### ⚖️ The Goldilocks Problem

**Too Small (< 100 words):**
- ❌ Lacks context
- ❌ Poor semantic meaning
- ❌ More chunks to process

---

## Chunk Size: Too Large

### ❌ The Problems
**Too Large (> 1000 words):**
- ❌ Mixed topics
- ❌ Poor search precision  
- ❌ Expensive embeddings

---

## Chunk Size: Just Right

### ✅ The Sweet Spot
**Just Right (200-500 words):**
- ✅ Good context preservation
- ✅ Clear semantic boundaries
- ✅ Optimal for embeddings

---

## Chunk Overlap Strategy

### 🔄 Why Overlap Matters

**Without Overlap:**
```
Chunk 1: "...password must be changed"
Chunk 2: "regularly to maintain security..."
```
❌ **Lost context** at chunk boundaries

---

## With Overlap: Better Context

### ✅ Preserved Context
**With Overlap:**
```
Chunk 1: "...password must be changed regularly for security"
Chunk 2: "regularly for security and must contain special..."
```
✅ **Preserved context** across boundaries

---

## Overlap Recommendations

### 📊 Guidelines
- **Standard overlap**: 20-25% of chunk size
- **High-context documents**: 30-40% overlap
- **Simple documents**: 10-15% overlap

---

## Advanced Document Handling

### 📄 Document Type Challenges

**Scanned PDFs (OCR required):**
- Use `pytesseract` for text extraction
- Handle OCR errors and artifacts
- Consider image preprocessing

---

## Multi-Column Layouts

### 📄 Complex Document Structure
**Multi-column layouts:**
- Parse column structure first
- Maintain reading order
- Handle figure/table placement

---

## Tables and Structured Data

### 📊 Special Handling Required
**Tables and structured data:**
- Preserve table structure in chunks
- Consider separate table processing
- Maintain header-row relationships

---

## Production Pipeline Architecture

### 🏗️ End-to-End Document Processing

```python
class DocumentProcessor:
    def __init__(self, chunk_size=300, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedding_service = EmbeddingService()
        self.db = DatabaseConnection()
```

---

## Document Processing Steps

### 🏗️ The Complete Pipeline
```python
    def process_document(self, pdf_path: str, document_metadata: dict):
        # 1. Extract text
        text = self.extract_text(pdf_path)
        
        # 2. Clean and preprocess
        text = self.clean_text(text)
        
        # 3. Create chunks with metadata
        chunks = self.chunk_with_metadata(text, document_metadata)
```

---

## Embedding and Storage

### 🏗️ Final Processing Steps
```python
        # 4. Generate embeddings
        for chunk in chunks:
            chunk.embedding = self.embedding_service.embed(chunk.text)
        
        # 5. Store in database
        self.db.store_chunks(chunks)
        
        return len(chunks)
```

---

## Quality Assessment & Testing

### 🔍 Chunk Quality Metrics

**Coherence Score:**
- Semantic similarity within chunks
- Topic consistency measurement

**Boundary Quality:**
- Sentence splitting analysis  
- Context preservation check

**Size Distribution:**
- Chunk size variance
- Optimal range compliance

---

## Edinburgh Testing Strategy

### 🧪 Quality Assessment Function
```python
def assess_chunk_quality(chunks: List[DocumentChunk]):
    """Evaluate chunking quality for Edinburgh documents."""
    
    quality_report = {
        'total_chunks': len(chunks),
        'avg_word_count': statistics.mean(c.word_count for c in chunks),
        'size_variance': statistics.stdev(c.word_count for c in chunks),
        'broken_sentences': count_broken_sentences(chunks),
        'coherence_score': measure_semantic_coherence(chunks)
    }
    
    return quality_report
```

---

## Common Pitfalls & Solutions

### ⚠️ Pitfall 1: Poor OCR Quality
**Problem:** Scanned documents with text errors
**Solution:** 
- Use high-quality OCR tools
- Implement text cleaning pipelines
- Consider manual review for critical documents

---

## Pitfall 2: Identical Chunks

### ⚠️ Duplicate Content Problem
**Problem:** Repeated headers/footers creating duplicates
**Solution:**
- Implement deduplication logic
- Filter out common boilerplate text
- Use content hashing for detection

---

## Pitfall 3: Language and Formatting

### ⚠️ Character Encoding Issues
**Problem:** Mixed languages, special characters
**Solution:**
- Unicode normalization
- Language detection and handling
- Character encoding validation

---

## Performance Optimization

### ⚡ Speed Optimization Techniques

**1. Parallel Processing:**
```python
from multiprocessing import Pool
import concurrent.futures

def process_documents_parallel(pdf_paths: List[str]):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_document, path) 
                  for path in pdf_paths]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(f"Processed document: {result} chunks created")
```

---

## Batch Database Operations

### ⚡ Database Performance
**2. Batch Database Operations:**
```python
def batch_insert_chunks(chunks: List[DocumentChunk], batch_size=100):
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        cursor.executemany(INSERT_CHUNK_SQL, [c.to_tuple() for c in batch])
        connection.commit()
```

---

## Edinburgh-Specific Considerations

### 🏫 University Document Types

**Student Handbooks:**
- Structured sections (academic, housing, IT)
- Annual updates with version control
- Multiple formats (PDF, web, mobile)

---

## IT Documentation

### 🏫 Technical Content
**IT Documentation:**
- Technical procedures and policies
- Step-by-step guides
- Troubleshooting flowcharts

---

## Research Papers

### 🏫 Academic Content
**Research Papers:**
- Academic formatting (abstracts, citations)
- Mathematical formulas and symbols
- Complex figure/table relationships

---

## Policy Documents

### 🏫 Legal Content
**Policy Documents:**
- Legal language and definitions
- Hierarchical numbering systems
- Cross-references and appendices

---

## Integration with Previous Sections

### 🔄 Connection to Section 4 (Vector Database)

The chunks we create here will be:
- **Stored** in our PostgreSQL + pgvector database
- **Embedded** using our Ollama BGE-M3 setup
- **Indexed** with HNSW for fast similarity search
- **Queried** in our RAG pipeline (Section 6)

---

## Updated Database Schema

### 📊 Enhanced Schema for Document Chunks
```sql
-- Enhanced schema for document chunks
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id TEXT NOT NULL,
    document_title TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding vector(1024),
    page_number INTEGER,
    section_title TEXT,
    chunk_index INTEGER,
    word_count INTEGER,
    character_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Vector search index
    INDEX USING hnsw (embedding vector_cosine_ops)
);
```

---

## Lab Preview

### 🧪 Hands-On Exercise: Edinburgh IT Documentation

**Scenario:** Process university IT support documents

**You'll implement:**
1. **PDF text extraction** from IT policy documents
2. **Content-aware chunking** preserving section structure
3. **Metadata preservation** with page numbers and sections
4. **Quality assessment** of chunking results
5. **Database integration** with your Section 4 setup

---

## Lab Success Criteria

### 🧪 What You'll Achieve
**Success criteria:**
- Process 3 different IT documents
- Create 50+ high-quality chunks
- Preserve document structure and references
- Enable accurate similarity search

---

## Next Steps

### 🎯 What's Coming

**Section 6: RAG Pipeline Integration**
- Use these chunks in similarity search
- Combine retrieval with LLM generation
- Build complete question-answering system

---

## Section 7: Advanced Vector Queries

### 🎯 Advanced Features
**Section 7: Advanced Vector Queries**
- Hybrid search (keywords + vectors)
- Complex filtering and ranking
- Multi-document queries

---

## Key Takeaways

### 💡 What You've Learned
- **Document chunking is crucial** for effective RAG systems
- **Choose chunking strategy** based on document type and use case  
- **Metadata preservation** enables better user experiences
- **Quality assessment** ensures reliable system performance

---

## Discussion Questions

### 🤔 With your partner, discuss:

1. **Strategy Selection:** Which chunking strategy would work best for Edinburgh's student handbook? Why?

2. **Metadata Importance:** What metadata fields would be most valuable for Edinburgh staff using the AI system?

---

## More Discussion Questions

### 🤔 Continue the conversation:

3. **Quality vs. Performance:** How would you balance chunk quality with processing speed for 10,000 documents?

4. **Error Handling:** What could go wrong when processing scanned university policy documents, and how would you handle it?

---

## Summary

### ✅ Section 5 Completed

You now understand:
- **Why chunking is essential** for RAG systems
- **Three main chunking strategies** and when to use each
- **Implementation techniques** for robust document processing
- **Metadata preservation** for better user experience  
- **Quality assessment** and optimization approaches
- **Integration patterns** with vector databases

---

## Ready for the Lab?

### 🚀 Let's Process Real Documents!

**Ready for the lab?** Let's process some real Edinburgh documents! 🚀