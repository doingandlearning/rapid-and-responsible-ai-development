# Capstone Lab: Edinburgh University Student Support Chatbot

**Duration**: 6 hours (360 minutes)  
**Teams**: Work in pairs or groups of 3  
**Objective**: Build a complete, production-ready AI-powered student support system

## Overview

You will build an intelligent chatbot that helps Edinburgh University students find answers to their questions about courses, policies, procedures, and campus life. This capstone integrates everything you've learned throughout the course.

### What You'll Build

1. **Knowledge Base Ingestion System** - Process and store university documents
2. **RAG-Powered Backend** - FastAPI service with vector search and LLM integration
3. **Student-Friendly Frontend** - React web interface for easy interaction
4. **Analytics Dashboard** - Monitor usage and performance
5. **Ethical Compliance Layer** - Privacy protection and bias monitoring

## Project Structure

```
edinburgh-student-chatbot/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── vector_search.py
│   │   ├── rag_pipeline.py
│   │   └── ethics_monitor.py
│   ├── models/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── data/
│   ├── raw_documents/
│   ├── processed/
│   └── evaluation/
├── deployment/
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── monitoring/
├── docs/
├── tests/
└── README.md
```

---

## Phase 1: Foundation & Data Ingestion (90 minutes)

### Step 1.1: Environment Setup (15 minutes)

1. **Clone the starter repository:**
   ```bash
   git clone [STARTER_REPO_URL] edinburgh-student-chatbot
   cd edinburgh-student-chatbot
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up -d postgres ollama
   ```

3. **Install Python dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Verify services are running:**
   ```bash
   docker ps
   curl http://localhost:11434/api/tags  # Should show BGE-M3 model
   ```

### Step 1.2: Document Corpus Preparation (20 minutes)

Your knowledge base includes authentic Edinburgh University content:

- **Academic Handbooks** (30 documents) - Degree requirements, module guides
- **Student Services** (25 documents) - Support, counseling, accessibility
- **Campus Information** (20 documents) - Facilities, accommodation, dining
- **Policies & Procedures** (15 documents) - Academic integrity, appeals
- **Course Catalogs** (40 documents) - Module descriptions, timetables

**Task**: Examine and categorize the document corpus

```python
# backend/services/document_analyzer.py
import os
from pathlib import Path
from collections import Counter

def analyze_document_corpus(data_dir: str):
    """Analyze the provided document corpus for processing strategy"""
    
    documents = []
    file_types = Counter()
    sizes = []
    
    for file_path in Path(data_dir).rglob("*"):
        if file_path.is_file():
            size = file_path.stat().st_size
            ext = file_path.suffix.lower()
            
            documents.append({
                'path': str(file_path),
                'name': file_path.name,
                'size': size,
                'type': ext,
                'category': _categorize_document(file_path.name)
            })
            
            file_types[ext] += 1
            sizes.append(size)
    
    return {
        'total_documents': len(documents),
        'file_types': dict(file_types),
        'avg_size': sum(sizes) / len(sizes) if sizes else 0,
        'categories': Counter(doc['category'] for doc in documents),
        'documents': documents
    }

def _categorize_document(filename: str) -> str:
    """Categorize document based on filename patterns"""
    filename_lower = filename.lower()
    
    if any(term in filename_lower for term in ['handbook', 'degree', 'academic']):
        return 'academic_handbook'
    elif any(term in filename_lower for term in ['support', 'counseling', 'wellbeing']):
        return 'student_services'
    elif any(term in filename_lower for term in ['campus', 'facilities', 'accommodation']):
        return 'campus_information'
    elif any(term in filename_lower for term in ['policy', 'procedure', 'regulation']):
        return 'policies_procedures'
    elif any(term in filename_lower for term in ['course', 'module', 'catalog']):
        return 'course_catalog'
    else:
        return 'general'

if __name__ == "__main__":
    analysis = analyze_document_corpus("../data/raw_documents/")
    print("📊 Document Corpus Analysis")
    print(f"Total documents: {analysis['total_documents']}")
    print(f"File types: {analysis['file_types']}")
    print(f"Categories: {dict(analysis['categories'])}")
```

**Run the analysis and document your findings:**

```bash
cd backend/services
python document_analyzer.py
```

### Step 1.3: Advanced Document Processing (30 minutes)

Building on Section 5 techniques, implement sophisticated document processing:

```python
# backend/services/document_processor.py
import PyPDF2
import fitz  # PyMuPDF for better text extraction
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import re
import hashlib

@dataclass
class DocumentChunk:
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    document_id: str
    chunk_index: int
    char_count: int
    overlap_with_previous: str = ""

class EdinburghDocumentProcessor:
    """Advanced document processing for university content"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.processed_documents = {}
    
    def process_document(self, file_path: str, document_category: str) -> List[DocumentChunk]:
        """Process a single document into semantic chunks"""
        
        # Extract text with metadata preservation
        text_content = self._extract_text_with_structure(file_path)
        
        # Generate document metadata
        doc_metadata = self._extract_document_metadata(file_path, document_category)
        
        # Create document ID
        doc_id = self._generate_document_id(file_path, text_content[:100])
        
        # Semantic chunking with context preservation
        chunks = self._create_semantic_chunks(text_content, doc_metadata, doc_id)
        
        self.processed_documents[doc_id] = {
            'file_path': file_path,
            'category': document_category,
            'chunk_count': len(chunks),
            'processed_at': datetime.now()
        }
        
        return chunks
    
    def _extract_text_with_structure(self, file_path: str) -> str:
        """Extract text while preserving document structure"""
        
        if file_path.endswith('.pdf'):
            return self._extract_pdf_with_structure(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    def _extract_pdf_with_structure(self, pdf_path: str) -> str:
        """Extract PDF text with enhanced structure preservation"""
        
        doc = fitz.open(pdf_path)
        full_text = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Extract text with formatting
            text = page.get_text()
            
            # Clean and structure the text
            structured_text = self._clean_and_structure_text(text, page_num + 1)
            full_text.append(structured_text)
        
        doc.close()
        return "\n\n".join(full_text)
    
    def _clean_and_structure_text(self, text: str, page_num: int) -> str:
        """Clean extracted text and preserve important structure"""
        
        # Remove excessive whitespace but preserve paragraph breaks
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Add page marker
        text = f"[Page {page_num}]\n{text}"
        
        # Identify and mark sections/headers (simple heuristic)
        lines = text.split('\n')
        structured_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                structured_lines.append('')
                continue
                
            # Detect potential headers (all caps, short lines, etc.)
            if (len(line) < 100 and 
                (line.isupper() or 
                 re.match(r'^\d+\.?\s+[A-Z]', line) or
                 re.match(r'^[A-Z][^a-z]*$', line))):
                structured_lines.append(f"\n## {line}\n")
            else:
                structured_lines.append(line)
        
        return '\n'.join(structured_lines)
    
    def _extract_document_metadata(self, file_path: str, category: str) -> Dict[str, Any]:
        """Extract comprehensive document metadata"""
        
        file_stats = Path(file_path).stat()
        
        metadata = {
            'source_file': Path(file_path).name,
            'category': category,
            'file_size': file_stats.st_size,
            'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'processed_at': datetime.now().isoformat(),
        }
        
        # Category-specific metadata
        if category == 'academic_handbook':
            metadata.update({
                'authority': 'high',
                'student_facing': True,
                'update_frequency': 'annually'
            })
        elif category == 'student_services':
            metadata.update({
                'authority': 'high',
                'student_facing': True,
                'contact_info_likely': True
            })
        elif category == 'policies_procedures':
            metadata.update({
                'authority': 'very_high',
                'legal_document': True,
                'compliance_relevant': True
            })
        elif category == 'course_catalog':
            metadata.update({
                'authority': 'high',
                'academic_year_specific': True,
                'frequently_updated': True
            })
        
        return metadata
    
    def _create_semantic_chunks(self, text: str, doc_metadata: Dict, doc_id: str) -> List[DocumentChunk]:
        """Create semantically meaningful chunks with context preservation"""
        
        # Split into sentences for semantic boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_sentences = []
        chunk_index = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) > self.chunk_size and current_chunk:
                # Create chunk with current content
                chunk = self._finalize_chunk(
                    current_chunk, 
                    doc_metadata, 
                    doc_id, 
                    chunk_index,
                    chunks[-1].content[-self.chunk_overlap:] if chunks else ""
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = current_sentences[-2:] if len(current_sentences) >= 2 else current_sentences
                current_chunk = " ".join(overlap_sentences + [sentence])
                current_sentences = overlap_sentences + [sentence]
                chunk_index += 1
            else:
                current_chunk = potential_chunk
                current_sentences.append(sentence)
        
        # Handle remaining content
        if current_chunk.strip():
            chunk = self._finalize_chunk(
                current_chunk, 
                doc_metadata, 
                doc_id, 
                chunk_index,
                chunks[-1].content[-self.chunk_overlap:] if chunks else ""
            )
            chunks.append(chunk)
        
        return chunks
    
    def _finalize_chunk(self, content: str, doc_metadata: Dict, doc_id: str, 
                       index: int, overlap: str) -> DocumentChunk:
        """Create final DocumentChunk with all metadata"""
        
        chunk_id = f"{doc_id}_chunk_{index:03d}"
        
        # Enhanced chunk metadata
        chunk_metadata = doc_metadata.copy()
        chunk_metadata.update({
            'chunk_index': index,
            'chunk_id': chunk_id,
            'char_count': len(content),
            'word_count': len(content.split()),
            'has_contact_info': bool(re.search(r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b', content)),
            'has_dates': bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content)),
            'has_numbers': bool(re.search(r'\b\d+\b', content))
        })
        
        return DocumentChunk(
            content=content.strip(),
            metadata=chunk_metadata,
            chunk_id=chunk_id,
            document_id=doc_id,
            chunk_index=index,
            char_count=len(content),
            overlap_with_previous=overlap
        )
    
    def _generate_document_id(self, file_path: str, content_sample: str) -> str:
        """Generate stable document ID based on path and content"""
        combined = f"{file_path}_{content_sample}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]

# Example usage and testing
if __name__ == "__main__":
    processor = EdinburghDocumentProcessor(chunk_size=800, chunk_overlap=150)
    
    # Test with a sample document
    sample_doc = "../data/raw_documents/student-handbook-2024.pdf"
    chunks = processor.process_document(sample_doc, "academic_handbook")
    
    print(f"📄 Processed {len(chunks)} chunks from {sample_doc}")
    print(f"First chunk preview: {chunks[0].content[:200]}...")
    print(f"Chunk metadata: {chunks[0].metadata}")
```

### Step 1.4: Vector Database Setup & Optimization (25 minutes)

Implement an optimized vector storage system:

```python
# backend/services/vector_database.py
import asyncio
import asyncpg
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EdinburghVectorDatabase:
    """Optimized vector database for Edinburgh University chatbot"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.pool = None
        self.embedding_dimension = 1024  # BGE-M3 embedding size
    
    async def initialize(self):
        """Initialize database connection pool and schema"""
        
        self.pool = await asyncpg.create_pool(
            host=self.db_config['host'],
            port=self.db_config['port'],
            database=self.db_config['database'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            min_size=5,
            max_size=20
        )
        
        await self._create_schema()
        await self._create_indexes()
        logger.info("Vector database initialized successfully")
    
    async def _create_schema(self):
        """Create optimized database schema"""
        
        async with self.pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create main documents table with enhanced metadata
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS student_support_docs (
                    id SERIAL PRIMARY KEY,
                    chunk_id VARCHAR(50) UNIQUE NOT NULL,
                    document_id VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    content_hash VARCHAR(32) NOT NULL,
                    embedding vector(1024),
                    metadata JSONB NOT NULL,
                    
                    -- Extracted fields for faster filtering
                    category VARCHAR(50) NOT NULL,
                    authority VARCHAR(20) DEFAULT 'medium',
                    student_facing BOOLEAN DEFAULT true,
                    chunk_index INTEGER NOT NULL,
                    char_count INTEGER NOT NULL,
                    word_count INTEGER DEFAULT 0,
                    
                    -- Contact and date detection
                    has_contact_info BOOLEAN DEFAULT false,
                    has_dates BOOLEAN DEFAULT false,
                    has_procedures BOOLEAN DEFAULT false,
                    
                    -- Temporal tracking
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Search optimization
                    search_vector tsvector
                );
            """)
            
            # Create query analytics table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS query_analytics (
                    id SERIAL PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    query_hash VARCHAR(32) NOT NULL,
                    user_session VARCHAR(50),
                    response_time_ms INTEGER,
                    results_count INTEGER,
                    satisfaction_score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                );
            """)
            
            # Create feedback table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id SERIAL PRIMARY KEY,
                    query_id INTEGER REFERENCES query_analytics(id),
                    feedback_type VARCHAR(20) NOT NULL,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
    
    async def _create_indexes(self):
        """Create optimized indexes for fast querying"""
        
        async with self.pool.acquire() as conn:
            # HNSW index for vector similarity
            await conn.execute("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_docs_embedding_hnsw 
                ON student_support_docs 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            
            # IVFFlat index as fallback
            await conn.execute("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_docs_embedding_ivfflat 
                ON student_support_docs 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            # Metadata indexes for filtering
            await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_docs_category ON student_support_docs (category);")
            await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_docs_authority ON student_support_docs (authority);")
            await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_docs_document_id ON student_support_docs (document_id);")
            
            # Full-text search index
            await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_docs_search_vector ON student_support_docs USING gin(search_vector);")
            
            # Analytics indexes
            await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_query_hash ON query_analytics (query_hash);")
            await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_created_at ON query_analytics (created_at);")
    
    async def store_document_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """Store document chunks with their embeddings"""
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for chunk, embedding in zip(chunks, embeddings):
                    # Create full-text search vector
                    search_vector_query = "to_tsvector('english', $1)"
                    
                    await conn.execute("""
                        INSERT INTO student_support_docs (
                            chunk_id, document_id, content, content_hash, embedding, metadata,
                            category, authority, student_facing, chunk_index, char_count, word_count,
                            has_contact_info, has_dates, search_vector
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
                            to_tsvector('english', $3)
                        )
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            updated_at = CURRENT_TIMESTAMP
                    """, 
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.content,
                        self._hash_content(chunk.content),
                        embedding,
                        json.dumps(chunk.metadata),
                        chunk.metadata.get('category', 'general'),
                        chunk.metadata.get('authority', 'medium'),
                        chunk.metadata.get('student_facing', True),
                        chunk.chunk_index,
                        chunk.char_count,
                        chunk.metadata.get('word_count', 0),
                        chunk.metadata.get('has_contact_info', False),
                        chunk.metadata.get('has_dates', False)
                    )
        
        logger.info(f"Stored {len(chunks)} document chunks in vector database")
    
    async def hybrid_search(self, 
                           query_embedding: List[float], 
                           query_text: str,
                           limit: int = 10,
                           category_filter: Optional[str] = None,
                           authority_filter: Optional[str] = None,
                           hybrid_weight: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and full-text search
        
        Args:
            query_embedding: Vector representation of the query
            query_text: Original text query for full-text search
            limit: Maximum number of results
            category_filter: Optional category filter
            authority_filter: Optional authority level filter  
            hybrid_weight: Weight for vector similarity (0.0-1.0)
        """
        
        async with self.pool.acquire() as conn:
            # Build WHERE clause for filters
            where_conditions = ["TRUE"]
            params = [query_embedding, query_text, limit]
            param_index = 4
            
            if category_filter:
                where_conditions.append(f"category = ${param_index}")
                params.append(category_filter)
                param_index += 1
            
            if authority_filter:
                where_conditions.append(f"authority = ${param_index}")
                params.append(authority_filter)
                param_index += 1
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                WITH vector_scores AS (
                    SELECT 
                        *,
                        1 - (embedding <=> $1::vector) as vector_similarity,
                        ts_rank(search_vector, plainto_tsquery('english', $2)) as text_rank
                    FROM student_support_docs
                    WHERE {where_clause}
                ),
                hybrid_scores AS (
                    SELECT *,
                        ({hybrid_weight} * vector_similarity + 
                         {1 - hybrid_weight} * text_rank) as hybrid_score
                    FROM vector_scores
                    WHERE vector_similarity > 0.5 OR text_rank > 0.1
                )
                SELECT 
                    chunk_id,
                    document_id,
                    content,
                    metadata,
                    category,
                    authority,
                    chunk_index,
                    vector_similarity,
                    text_rank,
                    hybrid_score,
                    created_at
                FROM hybrid_scores
                ORDER BY hybrid_score DESC
                LIMIT $3;
            """
            
            results = await conn.fetch(query, *params)
            
            return [
                {
                    'chunk_id': row['chunk_id'],
                    'document_id': row['document_id'],
                    'content': row['content'],
                    'metadata': json.loads(row['metadata']),
                    'category': row['category'],
                    'authority': row['authority'],
                    'chunk_index': row['chunk_index'],
                    'vector_similarity': float(row['vector_similarity']),
                    'text_rank': float(row['text_rank']),
                    'hybrid_score': float(row['hybrid_score']),
                    'created_at': row['created_at']
                }
                for row in results
            ]
    
    async def log_query_analytics(self, 
                                 query_text: str, 
                                 response_time_ms: int,
                                 results_count: int,
                                 user_session: Optional[str] = None,
                                 metadata: Optional[Dict] = None) -> int:
        """Log query analytics for monitoring and improvement"""
        
        async with self.pool.acquire() as conn:
            query_id = await conn.fetchval("""
                INSERT INTO query_analytics (
                    query_text, query_hash, user_session, response_time_ms, 
                    results_count, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """,
                query_text,
                self._hash_content(query_text),
                user_session,
                response_time_ms,
                results_count,
                json.dumps(metadata or {})
            )
            
            return query_id
    
    async def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for the specified number of days"""
        
        async with self.pool.acquire() as conn:
            summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(results_count) as avg_results_count,
                    COUNT(DISTINCT user_session) as unique_sessions
                FROM query_analytics
                WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '%d days'
            """ % days)
            
            top_queries = await conn.fetch("""
                SELECT query_text, COUNT(*) as frequency
                FROM query_analytics
                WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '%d days'
                GROUP BY query_text
                ORDER BY frequency DESC
                LIMIT 10
            """ % days)
            
            return {
                'total_queries': summary['total_queries'],
                'avg_response_time_ms': float(summary['avg_response_time']) if summary['avg_response_time'] else 0,
                'avg_results_count': float(summary['avg_results_count']) if summary['avg_results_count'] else 0,
                'unique_sessions': summary['unique_sessions'],
                'top_queries': [
                    {'query': row['query_text'], 'frequency': row['frequency']}
                    for row in top_queries
                ]
            }
    
    def _hash_content(self, content: str) -> str:
        """Generate MD5 hash for content deduplication"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
```

**Complete Step 1 by running the ingestion pipeline:**

```python
# backend/scripts/ingest_documents.py
import asyncio
import sys
from pathlib import Path
sys.path.append('..')

from services.document_processor import EdinburghDocumentProcessor
from services.vector_database import EdinburghVectorDatabase
from services.embedding_service import EmbeddingService

async def main():
    # Configuration
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'database': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    # Initialize services
    processor = EdinburghDocumentProcessor(chunk_size=800, chunk_overlap=150)
    vector_db = EdinburghVectorDatabase(db_config)
    embedding_service = EmbeddingService("http://localhost:11434")
    
    await vector_db.initialize()
    
    # Process all documents
    documents_dir = Path("../data/raw_documents")
    total_chunks = 0
    
    for category in ['academic_handbook', 'student_services', 'campus_information', 'policies_procedures', 'course_catalog']:
        category_dir = documents_dir / category
        if not category_dir.exists():
            continue
            
        for doc_path in category_dir.glob("*.pdf"):
            print(f"Processing {doc_path.name}...")
            
            # Process document
            chunks = processor.process_document(str(doc_path), category)
            
            # Generate embeddings
            contents = [chunk.content for chunk in chunks]
            embeddings = await embedding_service.get_embeddings_batch(contents)
            
            # Store in vector database
            await vector_db.store_document_chunks(chunks, embeddings)
            
            total_chunks += len(chunks)
            print(f"  Added {len(chunks)} chunks")
    
    print(f"\n✅ Ingestion complete! Total chunks: {total_chunks}")
    await vector_db.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Phase 2: Core Development (120 minutes)

### Step 2.1: RAG Pipeline Implementation (45 minutes)

Build an advanced RAG system that handles complex queries:

```python
# backend/services/rag_pipeline.py
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import openai
from datetime import datetime
import json
import re
from dataclasses import dataclass

@dataclass
class RAGResponse:
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    response_time_ms: int
    metadata: Dict[str, Any]

class EdinburghRAGPipeline:
    """Advanced RAG pipeline for Edinburgh University student support"""
    
    def __init__(self, 
                 vector_db: EdinburghVectorDatabase,
                 embedding_service: EmbeddingService,
                 openai_api_key: str,
                 model: str = "gpt-4"):
        self.vector_db = vector_db
        self.embedding_service = embedding_service
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        
        # Query classification patterns
        self.query_patterns = {
            'factual': [
                r'what is', r'what are', r'when is', r'when are', 
                r'where is', r'where are', r'how many', r'how much'
            ],
            'procedural': [
                r'how do i', r'how can i', r'what do i need', r'what steps',
                r'how to', r'what is the process'
            ],
            'comparative': [
                r'difference between', r'compare', r'versus', r'vs',
                r'better than', r'which is'
            ],
            'policy': [
                r'what happens if', r'what if i', r'policy on', r'rules about',
                r'allowed to', r'not allowed'
            ]
        }
    
    async def process_query(self, 
                          query: str, 
                          user_context: Optional[Dict[str, Any]] = None,
                          max_context_length: int = 4000) -> RAGResponse:
        """Process a student query and generate a comprehensive response"""
        
        start_time = datetime.now()
        
        # Step 1: Classify and enhance the query
        query_analysis = await self._analyze_query(query, user_context)
        enhanced_query = query_analysis['enhanced_query']
        
        # Step 2: Generate query embedding
        query_embedding = await self.embedding_service.get_embedding(enhanced_query)
        
        # Step 3: Retrieve relevant documents with hybrid search
        search_results = await self._retrieve_documents(
            query_embedding, 
            enhanced_query, 
            query_analysis,
            limit=15
        )
        
        # Step 4: Re-rank and filter results
        ranked_results = await self._rerank_results(search_results, query_analysis)
        
        # Step 5: Build optimized context
        context = await self._build_context(ranked_results, max_context_length)
        
        # Step 6: Generate response using LLM
        response_data = await self._generate_response(
            query, enhanced_query, context, query_analysis
        )
        
        # Step 7: Post-process and validate response
        final_response = await self._post_process_response(
            response_data, ranked_results, query_analysis
        )
        
        # Calculate timing
        end_time = datetime.now()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Build final response object
        return RAGResponse(
            answer=final_response['answer'],
            sources=final_response['sources'],
            confidence_score=final_response['confidence'],
            response_time_ms=response_time_ms,
            metadata={
                'query_type': query_analysis['type'],
                'enhanced_query': enhanced_query,
                'context_length': len(context),
                'sources_used': len(final_response['sources']),
                'model': self.model
            }
        )
    
    async def _analyze_query(self, query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze query to understand intent and enhance search"""
        
        query_lower = query.lower()
        
        # Classify query type
        query_type = 'general'
        for q_type, patterns in self.query_patterns.items():
            if any(re.search(pattern, query_lower) for pattern in patterns):
                query_type = q_type
                break
        
        # Extract key entities and concepts
        entities = self._extract_entities(query)
        
        # Determine search strategy
        search_strategy = {
            'category_filters': self._suggest_categories(query_lower, entities),
            'authority_preference': self._determine_authority_preference(query_type),
            'hybrid_weight': self._calculate_hybrid_weight(query_type)
        }
        
        # Enhance query for better search
        enhanced_query = self._enhance_query_for_search(query, entities, user_context)
        
        return {
            'original_query': query,
            'enhanced_query': enhanced_query,
            'type': query_type,
            'entities': entities,
            'search_strategy': search_strategy,
            'user_context': user_context or {}
        }
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract key entities from the query"""
        
        entities = {
            'courses': [],
            'departments': [],
            'locations': [],
            'services': [],
            'processes': []
        }
        
        # Course-related keywords
        course_keywords = [
            'course', 'module', 'class', 'lecture', 'tutorial', 'seminar',
            'degree', 'program', 'masters', 'phd', 'undergraduate', 'postgraduate'
        ]
        
        # Department keywords
        dept_keywords = [
            'computer science', 'engineering', 'medicine', 'law', 'business',
            'psychology', 'history', 'literature', 'physics', 'chemistry'
        ]
        
        # Location keywords
        location_keywords = [
            'library', 'campus', 'building', 'room', 'kings buildings', 
            'central area', 'accommodation', 'residence'
        ]
        
        # Service keywords
        service_keywords = [
            'counseling', 'support', 'disability', 'financial aid', 'career',
            'health', 'wellbeing', 'academic advisor'
        ]
        
        query_lower = query.lower()
        
        for keyword in course_keywords:
            if keyword in query_lower:
                entities['courses'].append(keyword)
        
        for keyword in dept_keywords:
            if keyword in query_lower:
                entities['departments'].append(keyword)
        
        for keyword in location_keywords:
            if keyword in query_lower:
                entities['locations'].append(keyword)
                
        for keyword in service_keywords:
            if keyword in query_lower:
                entities['services'].append(keyword)
        
        return entities
    
    def _suggest_categories(self, query_lower: str, entities: Dict) -> List[str]:
        """Suggest document categories to focus search on"""
        
        categories = []
        
        if (entities['courses'] or 'course' in query_lower or 'module' in query_lower):
            categories.extend(['course_catalog', 'academic_handbook'])
        
        if (entities['services'] or any(service in query_lower for service in 
            ['support', 'help', 'counseling', 'disability', 'financial'])):
            categories.append('student_services')
        
        if (entities['locations'] or any(location in query_lower for location in 
            ['campus', 'building', 'library', 'accommodation'])):
            categories.append('campus_information')
        
        if ('policy' in query_lower or 'rule' in query_lower or 'regulation' in query_lower):
            categories.append('policies_procedures')
        
        return categories if categories else ['academic_handbook', 'student_services']
    
    def _determine_authority_preference(self, query_type: str) -> str:
        """Determine preferred authority level based on query type"""
        
        if query_type in ['policy', 'procedural']:
            return 'high'  # Prefer authoritative sources for policies and procedures
        elif query_type == 'factual':
            return 'medium'  # Balance authority with comprehensiveness
        else:
            return 'any'  # No strong preference
    
    def _calculate_hybrid_weight(self, query_type: str) -> float:
        """Calculate hybrid search weight based on query type"""
        
        # Higher vector weight for semantic queries, higher text weight for exact matches
        weights = {
            'factual': 0.6,      # Slightly favor vector similarity
            'procedural': 0.7,   # Favor vector similarity for process understanding
            'comparative': 0.8,  # Strong vector similarity for comparisons
            'policy': 0.5,       # Balance semantic and exact text matching
            'general': 0.65      # Default balanced approach
        }
        
        return weights.get(query_type, 0.65)
    
    def _enhance_query_for_search(self, query: str, entities: Dict, user_context: Optional[Dict]) -> str:
        """Enhance query with context and synonyms for better search"""
        
        enhanced_parts = [query]
        
        # Add context from user if available
        if user_context:
            if user_context.get('student_type') == 'international':
                enhanced_parts.append("international student")
            if user_context.get('study_level'):
                enhanced_parts.append(user_context['study_level'])
        
        # Add relevant synonyms and expansions
        if entities['courses']:
            enhanced_parts.append("academic program curriculum")
        
        if entities['services']:
            enhanced_parts.append("student support university services")
            
        if entities['locations']:
            enhanced_parts.append("Edinburgh University campus facilities")
        
        return " ".join(enhanced_parts)
    
    async def _retrieve_documents(self, 
                                query_embedding: List[float],
                                enhanced_query: str,
                                query_analysis: Dict,
                                limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using optimized search strategy"""
        
        search_strategy = query_analysis['search_strategy']
        
        # Perform searches with different strategies and combine
        all_results = []
        
        # Primary search with category filtering
        if search_strategy['category_filters']:
            for category in search_strategy['category_filters']:
                category_results = await self.vector_db.hybrid_search(
                    query_embedding=query_embedding,
                    query_text=enhanced_query,
                    limit=max(3, limit // len(search_strategy['category_filters'])),
                    category_filter=category,
                    authority_filter=search_strategy['authority_preference'] if search_strategy['authority_preference'] != 'any' else None,
                    hybrid_weight=search_strategy['hybrid_weight']
                )
                all_results.extend(category_results)
        
        # Fallback broad search if not enough results
        if len(all_results) < limit // 2:
            broad_results = await self.vector_db.hybrid_search(
                query_embedding=query_embedding,
                query_text=enhanced_query,
                limit=limit,
                hybrid_weight=search_strategy['hybrid_weight']
            )
            all_results.extend(broad_results)
        
        # Deduplicate by chunk_id
        seen_chunks = set()
        unique_results = []
        for result in all_results:
            if result['chunk_id'] not in seen_chunks:
                seen_chunks.add(result['chunk_id'])
                unique_results.append(result)
        
        return unique_results[:limit]
    
    async def _rerank_results(self, results: List[Dict], query_analysis: Dict) -> List[Dict]:
        """Re-rank results based on query-specific criteria"""
        
        query_type = query_analysis['type']
        entities = query_analysis['entities']
        
        for result in results:
            base_score = result['hybrid_score']
            adjustments = 0
            
            # Authority boost for policy queries
            if query_type == 'policy' and result['authority'] in ['high', 'very_high']:
                adjustments += 0.1
            
            # Recency boost for procedural queries
            if query_type == 'procedural' and result.get('metadata', {}).get('frequently_updated'):
                adjustments += 0.05
            
            # Content-specific boosts
            content_lower = result['content'].lower()
            
            # Boost if content contains detected entities
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    if entity in content_lower:
                        adjustments += 0.02
            
            # Boost for contact information when query might need it
            if (any(word in query_analysis['original_query'].lower() for word in ['contact', 'email', 'phone', 'help']) 
                and result.get('has_contact_info')):
                adjustments += 0.1
            
            # Apply adjustments
            result['reranked_score'] = base_score + adjustments
        
        # Sort by reranked score
        return sorted(results, key=lambda x: x['reranked_score'], reverse=True)
    
    async def _build_context(self, results: List[Dict], max_length: int) -> str:
        """Build optimized context from search results"""
        
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results):
            # Format source information
            source_info = f"[Source {i+1}: {result['metadata'].get('source_file', 'Document')} - {result['category']}]"
            content_with_source = f"{source_info}\n{result['content']}\n"
            
            # Check if adding this content would exceed the limit
            if current_length + len(content_with_source) > max_length:
                # Try to add a truncated version
                remaining_space = max_length - current_length - len(source_info) - 20
                if remaining_space > 100:  # Only add if meaningful amount of content fits
                    truncated_content = result['content'][:remaining_space] + "..."
                    context_parts.append(f"{source_info}\n{truncated_content}\n")
                break
            
            context_parts.append(content_with_source)
            current_length += len(content_with_source)
        
        return "\n".join(context_parts)
    
    async def _generate_response(self, 
                               original_query: str,
                               enhanced_query: str, 
                               context: str, 
                               query_analysis: Dict) -> Dict[str, Any]:
        """Generate response using OpenAI API with specialized prompts"""
        
        query_type = query_analysis['type']
        
        # Customize system prompt based on query type
        system_prompts = {
            'factual': """You are a helpful Edinburgh University student support assistant. Provide accurate, factual answers based on the provided context. Always cite your sources using [Source X] notation. If the information isn't in the context, clearly state what you don't know.""",
            
            'procedural': """You are a Edinburgh University student support assistant specializing in procedures and processes. Provide clear, step-by-step guidance based on the provided context. Always cite sources and mention if students need to contact specific offices. If any steps are unclear from the context, acknowledge this.""",
            
            'policy': """You are a Edinburgh University student support assistant focusing on policies and regulations. Provide accurate policy information based on the provided context, always citing official sources. If the policy isn't fully covered in the context, direct students to official university resources.""",
            
            'comparative': """You are a Edinburgh University student support assistant helping with comparisons and choices. Analyze the provided context to highlight key differences and similarities. Present information objectively and cite all sources. If insufficient information is available for a complete comparison, clearly state this.""",
            
            'general': """You are a helpful Edinburgh University student support assistant. Provide comprehensive answers based on the provided context, always citing your sources. Be conversational but accurate, and clearly indicate if you cannot fully answer based on the available information."""
        }
        
        system_prompt = system_prompts.get(query_type, system_prompts['general'])
        
        user_prompt = f"""
Context from Edinburgh University documents:
{context}

Student question: {original_query}

Please provide a helpful, accurate response based on the context above. Remember to:
1. Cite sources using [Source X] notation
2. Be specific and actionable where possible
3. If you cannot fully answer from the context, be honest about limitations
4. Focus on what would be most helpful for an Edinburgh University student
"""

        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=1000
            )
            
            return {
                'raw_response': response.choices[0].message.content,
                'usage': response.usage._asdict() if response.usage else {},
                'model': response.model
            }
            
        except Exception as e:
            return {
                'raw_response': f"I apologize, but I'm having trouble generating a response right now. Please try asking your question again or contact student support directly. Error: {str(e)}",
                'usage': {},
                'model': self.model,
                'error': str(e)
            }
    
    async def _post_process_response(self, 
                                   response_data: Dict,
                                   search_results: List[Dict],
                                   query_analysis: Dict) -> Dict[str, Any]:
        """Post-process the response to add sources and calculate confidence"""
        
        answer = response_data['raw_response']
        
        # Extract source citations from the response
        cited_sources = re.findall(r'\[Source (\d+)\]', answer)
        cited_source_indices = [int(x) - 1 for x in cited_sources if int(x) <= len(search_results)]
        
        # Build detailed source information
        sources = []
        for idx in cited_source_indices:
            if idx < len(search_results):
                result = search_results[idx]
                sources.append({
                    'source_id': idx + 1,
                    'title': result['metadata'].get('source_file', 'University Document'),
                    'category': result['category'],
                    'authority': result['authority'],
                    'excerpt': result['content'][:200] + "...",
                    'similarity_score': result['hybrid_score'],
                    'chunk_id': result['chunk_id']
                })
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(
            response_data, search_results, cited_source_indices, query_analysis
        )
        
        # Add helpful fallback information if confidence is low
        if confidence < 0.6:
            answer += "\n\nIf you need more specific information, you might want to:\n"
            answer += "- Contact Student Services directly\n"
            answer += "- Check the official Edinburgh University website\n"
            answer += "- Visit your academic advisor"
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence
        }
    
    def _calculate_confidence_score(self, 
                                  response_data: Dict,
                                  search_results: List[Dict],
                                  cited_indices: List[int],
                                  query_analysis: Dict) -> float:
        """Calculate confidence score for the response"""
        
        base_confidence = 0.5
        
        # Boost confidence based on search result quality
        if search_results:
            avg_similarity = sum(r['hybrid_score'] for r in search_results[:3]) / min(3, len(search_results))
            base_confidence += min(avg_similarity * 0.3, 0.3)
        
        # Boost if sources were actually cited
        if cited_indices:
            citation_ratio = len(cited_indices) / len(search_results[:5])
            base_confidence += citation_ratio * 0.2
        
        # Boost based on authority of cited sources
        if cited_indices:
            authority_scores = {
                'very_high': 0.15,
                'high': 0.1,
                'medium': 0.05,
                'low': 0
            }
            for idx in cited_indices:
                if idx < len(search_results):
                    authority = search_results[idx]['authority']
                    base_confidence += authority_scores.get(authority, 0)
        
        # Reduce confidence if response contains uncertainty language
        uncertainty_phrases = ['not sure', 'unclear', 'might be', 'possibly', 'i don\'t know']
        answer_lower = response_data.get('raw_response', '').lower()
        uncertainty_count = sum(phrase in answer_lower for phrase in uncertainty_phrases)
        base_confidence -= uncertainty_count * 0.1
        
        return max(0.1, min(1.0, base_confidence))

# Usage example
async def test_rag_pipeline():
    # Initialize components (in real implementation, these would be dependency-injected)
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'database': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    vector_db = EdinburghVectorDatabase(db_config)
    await vector_db.initialize()
    
    embedding_service = EmbeddingService("http://localhost:11434")
    rag_pipeline = EdinburghRAGPipeline(
        vector_db=vector_db,
        embedding_service=embedding_service,
        openai_api_key="your-openai-api-key"
    )
    
    # Test query
    response = await rag_pipeline.process_query(
        "How do I change my course at Edinburgh University?",
        user_context={'student_type': 'undergraduate', 'year': 2}
    )
    
    print(f"Answer: {response.answer}")
    print(f"Confidence: {response.confidence_score}")
    print(f"Sources: {len(response.sources)}")
    
    await vector_db.close()

if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
```

Continue with Step 2.2 - FastAPI Backend (45 minutes) and Step 2.3 - React Frontend (30 minutes)...