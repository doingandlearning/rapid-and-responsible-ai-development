# Lab 5: Document Processing & PDF Chunking for Edinburgh

## Learning Objectives
By the end of this lab, you will:
- ✅ Extract text from Edinburgh IT policy documents
- ✅ Implement and compare different chunking strategies
- ✅ Preserve document metadata for source attribution
- ✅ Assess chunk quality and optimize parameters
- ✅ Store document chunks in your vector database
- ✅ Verify chunks are stored correctly in vector database

## Time Estimate: 35 minutes

---

## Pre-Lab Setup

**Ensure your environment is ready:**
1. Services running: `cd environment && docker compose up -d`
2. Virtual environment activated: `source .venv/bin/activate`
3. Section 4 database ready: Run verification if needed
4. Create lab file: `lab5_document_processing.py`

**🆘 Need help?** Complete solutions are in `../solution/` folder!

---

## Lab Scenario

You're working with Edinburgh University's IT Services team to process their documentation for an AI-powered support system. You have three types of documents to process:

1. **IT Support Handbook** - Structured technical procedures
2. **Student WiFi Guide** - Step-by-step instructions with troubleshooting
3. **VPN Policy Document** - Formal policy with legal language

Your goal is to chunk these documents effectively so students and staff can get accurate, attributable answers to their IT questions.

---

## Part 1: Document Text Extraction (8 minutes)

### Step 1: Set Up Document Processing Infrastructure

First, let's create our document processing framework:

```python
import PyPDF2
import psycopg
import requests
import json
import time
import re
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Iterator, Dict, Any
from pathlib import Path

# Database configuration (from Section 4)
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# Ollama configuration (from Section 4)
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"

@dataclass
class DocumentChunk:
    """Represents a document chunk with full metadata."""
    id: str
    document_id: str
    document_title: str
    text: str
    embedding: Optional[List[float]] = None
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_index: int = 0
    word_count: int = 0
    character_count: int = 0
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.word_count == 0:
            self.word_count = len(self.text.split())
        if self.character_count == 0:
            self.character_count = len(self.text)

def extract_text_from_pdf(pdf_path: str) -> List[tuple]:
    """
    Extract text from PDF with page numbers.
    
    Returns:
        List of (page_number, text) tuples
    """
    print(f"📄 Extracting text from {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            pages = []
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():  # Only include non-empty pages
                    pages.append((page_num, text))
                    
            print(f"✅ Extracted text from {len(pages)} pages")
            return pages
            
    except Exception as e:
        print(f"❌ Failed to extract text from {pdf_path}: {e}")
        return []

# Test the extraction with our simulated Edinburgh documents
def create_sample_edinburgh_documents():
    """Create sample Edinburgh IT documents for testing."""
    
    # We'll simulate having these documents - in real life they'd be PDF files
    documents = {
        'it-support-handbook.pdf': {
            'title': 'Edinburgh IT Support Handbook 2024',
            'pages': [
                (1, """Edinburgh University IT Support Handbook
                
Chapter 1: Password Management
All university accounts require strong passwords that meet the following criteria:
- Minimum 8 characters in length
- Must contain uppercase and lowercase letters
- Must include at least one number and one special character
- Cannot reuse the last 5 passwords
- Must be changed every 90 days

Password reset procedures:
1. Visit https://password.ed.ac.uk
2. Enter your university username
3. Verify identity using registered mobile number
4. Create new password following criteria above
5. Confirm password change via email notification

For assistance, contact IT Service Desk on 0131 650 4500."""),
                
                (2, """Chapter 2: Network Access and WiFi
Edinburgh University provides wireless internet access through multiple networks:

EdUni Network (Primary):
- For registered university devices
- Automatic connection for managed devices
- High-speed access (up to 100Mbps)
- Available in all buildings and student accommodations

EdUni-Guest Network:
- For visitors and unregistered devices  
- 24-hour access with daily re-authentication
- Standard speed (up to 25Mbps)
- Available in public areas only

Connection troubleshooting steps:
1. Forget and re-add the network
2. Check device MAC address registration
3. Verify university account status
4. Contact accommodation office for residence issues""")
            ]
        },
        
        'student-wifi-guide.pdf': {
            'title': 'Student WiFi Connection Guide',
            'pages': [
                (1, """Student WiFi Setup Guide
University of Edinburgh

Quick Start:
Your student devices can connect to EdUni network after registration.

Step 1: Register Your Device
1. Connect to 'EdUni-Setup' network
2. Open web browser - registration page will appear automatically
3. Login with your university credentials (s[student-number]@ed.ac.uk)
4. Confirm your device details and MAC address
5. Accept terms and conditions
6. Disconnect from EdUni-Setup

Step 2: Connect to EdUni
1. Select 'EdUni' from available networks
2. Your device should connect automatically
3. If prompted, enter university credentials
4. Connection confirmed with welcome notification

Common Issues and Solutions:
- Can't see EdUni network: Check device WiFi is enabled, restart if necessary
- Connection fails: Verify credentials, check account is active
- Slow speeds: Check data usage limits, try different location
- Gaming consoles: Use ethernet cable or contact IT for MAC registration""")
            ]
        },
        
        'vpn-policy.pdf': {
            'title': 'Edinburgh University VPN Policy Document',
            'pages': [
                (1, """VPN Access Policy
University of Edinburgh
Document Version: 2024.1
Effective Date: January 1, 2024

1. Purpose and Scope
This policy defines the acceptable use of Virtual Private Network (VPN) services provided by the University of Edinburgh. All staff, students, and authorized users must comply with these requirements when accessing university resources remotely.

2. Authorized Use
VPN access is provided for legitimate university business including:
- Access to internal university systems and databases
- Secure connection to library resources from off-campus
- Remote access to research data and computational resources
- Administrative access to university services

3. Technical Requirements
- VPN client: FortiClient (official university-supported client)
- Two-factor authentication required for all connections
- Maximum 3 simultaneous connections per user account
- Connection logging is maintained for security audit purposes"""),
                
                (2, """4. User Responsibilities
Users of university VPN services must:
- Use VPN only for authorized university activities
- Maintain confidentiality of VPN credentials
- Report suspected security incidents immediately
- Comply with all university IT policies and procedures
- Accept that VPN usage may be monitored and logged

5. Prohibited Activities
The following activities are strictly forbidden:
- Sharing VPN credentials with unauthorized persons
- Using VPN for illegal activities or copyright infringement
- Circumventing university network security controls
- Excessive bandwidth usage affecting service performance
- Accessing prohibited or inappropriate content

6. Compliance and Enforcement
Violations of this policy may result in:
- Immediate suspension of VPN access
- Disciplinary action under university policies
- Legal action where appropriate
- Academic sanctions for students""")
            ]
        }
    }
    
    return documents

# Test text extraction
print("🧪 Testing document text extraction...")
sample_documents = create_sample_edinburgh_documents()

for doc_filename, doc_data in sample_documents.items():
    print(f"\n📖 Processing: {doc_data['title']}")
    print(f"   Pages: {len(doc_data['pages'])}")
    print(f"   Sample text: {doc_data['pages'][0][1][:100]}...")
```

---

## Part 2: Fixed-Size Chunking Implementation (10 minutes)

### Step 2: Implement Fixed-Size Chunking Strategy

```python
def fixed_size_chunker(text: str, chunk_size: int = 300, overlap: int = 50) -> Iterator[str]:
    """
    Split text into fixed-size chunks with overlap.
    
    Args:
        text: Input text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of words to overlap between chunks
        
    Yields:
        String chunks with specified overlap
    """
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if chunk_words:  # Only yield non-empty chunks
            yield " ".join(chunk_words)

def create_chunks_from_document(document_data: Dict[str, Any], 
                              chunk_strategy: str = "fixed",
                              chunk_size: int = 300,
                              overlap: int = 50) -> List[DocumentChunk]:
    """
    Create DocumentChunk objects from document data.
    
    Args:
        document_data: Dictionary with document info and pages
        chunk_strategy: "fixed", "content_aware", or "semantic"
        chunk_size: Size of chunks (words for fixed, max words for others)
        overlap: Overlap between chunks (words)
        
    Returns:
        List of DocumentChunk objects
    """
    chunks = []
    chunk_index = 0
    document_id = document_data['title'].lower().replace(' ', '-')
    
    print(f"📝 Creating chunks using {chunk_strategy} strategy...")
    print(f"   Chunk size: {chunk_size} words, Overlap: {overlap} words")
    
    for page_num, page_text in document_data['pages']:
        # Clean the text
        cleaned_text = re.sub(r'\s+', ' ', page_text).strip()
        
        # Create chunks from this page
        if chunk_strategy == "fixed":
            page_chunks = list(fixed_size_chunker(cleaned_text, chunk_size, overlap))
        else:
            # We'll implement other strategies in later steps
            page_chunks = list(fixed_size_chunker(cleaned_text, chunk_size, overlap))
        
        # Create DocumentChunk objects
        for chunk_text in page_chunks:
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                document_title=document_data['title'],
                text=chunk_text,
                page_number=page_num,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
            chunk_index += 1
    
    print(f"✅ Created {len(chunks)} chunks")
    return chunks

# Test fixed-size chunking
print("\n🔧 Testing Fixed-Size Chunking Strategy")
print("="*60)

# Process IT Support Handbook
handbook_chunks = create_chunks_from_document(
    sample_documents['it-support-handbook.pdf'],
    chunk_strategy="fixed",
    chunk_size=200,  # Smaller chunks for testing
    overlap=40
)

print(f"\n📊 Chunking Results:")
print(f"   Total chunks: {len(handbook_chunks)}")
print(f"   Average chunk size: {sum(c.word_count for c in handbook_chunks) / len(handbook_chunks):.1f} words")

# Show first few chunks
print(f"\n📖 Sample chunks:")
for i, chunk in enumerate(handbook_chunks[:3], 1):
    print(f"   Chunk {i} (Page {chunk.page_number}, {chunk.word_count} words):")
    print(f"   '{chunk.text[:100]}...'")
    print()
```

---

## Part 3: Content-Aware Chunking (10 minutes)

### Step 3: Implement Content-Aware Chunking

```python
def content_aware_chunker(text: str, max_chunk_size: int = 500) -> List[str]:
    """
    Split text by paragraphs and sections, respecting size limits.
    
    Args:
        text: Input text to chunk
        max_chunk_size: Maximum words per chunk
        
    Returns:
        List of text chunks respecting content boundaries
    """
    chunks = []
    
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph_words = len(paragraph.split())
        current_chunk_words = len(current_chunk.split()) if current_chunk else 0
        
        # If adding this paragraph would exceed the limit
        if current_chunk_words + paragraph_words > max_chunk_size and current_chunk:
            # Save current chunk and start new one
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        elif paragraph_words > max_chunk_size:
            # Paragraph itself is too large, use fixed-size chunking
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            # Split large paragraph
            chunks.extend(fixed_size_chunker(paragraph, max_chunk_size, max_chunk_size // 4))
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def smart_section_detector(text: str) -> Optional[str]:
    """
    Try to detect section titles in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Section title if found, None otherwise
    """
    lines = text.split('\n')
    
    for line in lines[:3]:  # Check first few lines
        line = line.strip()
        
        # Look for chapter/section patterns
        if re.match(r'^(Chapter|Section|Part)\s+\d+:', line, re.IGNORECASE):
            return line
        
        # Look for numbered sections
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return line
            
        # Look for all-caps titles (short ones)
        if line.isupper() and 5 <= len(line) <= 50:
            return line
    
    return None

# Enhanced chunk creation with content awareness
def create_content_aware_chunks(document_data: Dict[str, Any], 
                               max_chunk_size: int = 400) -> List[DocumentChunk]:
    """Create chunks using content-aware strategy."""
    
    chunks = []
    chunk_index = 0
    document_id = document_data['title'].lower().replace(' ', '-')
    
    print(f"🧠 Creating content-aware chunks (max {max_chunk_size} words)...")
    
    for page_num, page_text in document_data['pages']:
        # Clean the text
        cleaned_text = re.sub(r'\s+', ' ', page_text).strip()
        
        # Try to detect section title for this page
        section_title = smart_section_detector(cleaned_text)
        
        # Create content-aware chunks
        page_chunks = content_aware_chunker(cleaned_text, max_chunk_size)
        
        # Create DocumentChunk objects
        for chunk_text in page_chunks:
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                document_title=document_data['title'],
                text=chunk_text,
                page_number=page_num,
                section_title=section_title,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
            chunk_index += 1
    
    print(f"✅ Created {len(chunks)} content-aware chunks")
    return chunks

# Test content-aware chunking
print("\n🧠 Testing Content-Aware Chunking Strategy")
print("="*60)

# Process VPN Policy Document (has clear structure)
policy_chunks = create_content_aware_chunks(
    sample_documents['vpn-policy.pdf'],
    max_chunk_size=300
)

print(f"\n📊 Content-Aware Chunking Results:")
print(f"   Total chunks: {len(policy_chunks)}")
print(f"   Average chunk size: {sum(c.word_count for c in policy_chunks) / len(policy_chunks):.1f} words")

# Show chunks with sections
print(f"\n📖 Sample content-aware chunks:")
for i, chunk in enumerate(policy_chunks[:3], 1):
    section_info = f" - {chunk.section_title}" if chunk.section_title else ""
    print(f"   Chunk {i} (Page {chunk.page_number}{section_info}, {chunk.word_count} words):")
    print(f"   '{chunk.text[:120]}...'")
    print()
```

---

## Part 4: Quality Assessment & Optimization (8 minutes)

### Step 4: Implement Chunk Quality Assessment

```python
import statistics
from collections import Counter

def assess_chunk_quality(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """
    Comprehensive quality assessment of document chunks.
    
    Args:
        chunks: List of DocumentChunk objects to assess
        
    Returns:
        Dictionary with quality metrics
    """
    if not chunks:
        return {"error": "No chunks to assess"}
    
    # Basic statistics
    word_counts = [c.word_count for c in chunks]
    char_counts = [c.character_count for c in chunks]
    
    # Check for broken sentences (chunks ending mid-sentence)
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text[-1] in '.!?':
            broken_sentences += 1
    
    # Check for very short chunks (likely poor splits)
    very_short = sum(1 for wc in word_counts if wc < 20)
    
    # Check for very long chunks (might need better splitting)
    very_long = sum(1 for wc in word_counts if wc > 800)
    
    # Duplicate detection (similar chunks)
    chunk_texts = [c.text.lower().strip() for c in chunks]
    duplicates = len(chunk_texts) - len(set(chunk_texts))
    
    # Section coverage (how many chunks have section titles)
    with_sections = sum(1 for c in chunks if c.section_title)
    
    quality_report = {
        'total_chunks': len(chunks),
        'word_count_stats': {
            'mean': statistics.mean(word_counts),
            'median': statistics.median(word_counts),
            'std_dev': statistics.stdev(word_counts) if len(word_counts) > 1 else 0,
            'min': min(word_counts),
            'max': max(word_counts)
        },
        'quality_issues': {
            'broken_sentences': broken_sentences,
            'very_short_chunks': very_short,
            'very_long_chunks': very_long,
            'duplicate_chunks': duplicates
        },
        'metadata_coverage': {
            'chunks_with_sections': with_sections,
            'section_coverage_pct': (with_sections / len(chunks)) * 100
        }
    }
    
    # Overall quality score (0-100)
    quality_score = 100
    quality_score -= (broken_sentences / len(chunks)) * 20  # Penalty for broken sentences
    quality_score -= (very_short / len(chunks)) * 15        # Penalty for very short chunks
    quality_score -= (very_long / len(chunks)) * 10         # Penalty for very long chunks
    quality_score -= (duplicates / len(chunks)) * 25        # Penalty for duplicates
    quality_score = max(0, quality_score)
    
    quality_report['overall_quality_score'] = quality_score
    
    return quality_report

def compare_chunking_strategies(document_data: Dict[str, Any]) -> None:
    """Compare different chunking strategies on the same document."""
    
    print(f"📊 CHUNKING STRATEGY COMPARISON")
    print(f"Document: {document_data['title']}")
    print("="*70)
    
    strategies = [
        ("Fixed-Size (200w, 40w overlap)", lambda d: create_chunks_from_document(d, "fixed", 200, 40)),
        ("Fixed-Size (300w, 50w overlap)", lambda d: create_chunks_from_document(d, "fixed", 300, 50)),
        ("Content-Aware (300w max)", lambda d: create_content_aware_chunks(d, 300)),
        ("Content-Aware (400w max)", lambda d: create_content_aware_chunks(d, 400)),
    ]
    
    results = []
    
    for strategy_name, strategy_func in strategies:
        print(f"\n🔧 Testing: {strategy_name}")
        chunks = strategy_func(document_data)
        quality = assess_chunk_quality(chunks)
        
        results.append((strategy_name, chunks, quality))
        
        print(f"   Chunks created: {quality['total_chunks']}")
        print(f"   Avg words/chunk: {quality['word_count_stats']['mean']:.1f}")
        print(f"   Quality score: {quality['overall_quality_score']:.1f}/100")
        print(f"   Issues: {quality['quality_issues']['broken_sentences']} broken sentences, "
              f"{quality['quality_issues']['duplicate_chunks']} duplicates")
    
    # Find best strategy
    best_strategy = max(results, key=lambda x: x[2]['overall_quality_score'])
    print(f"\n🏆 Best Strategy: {best_strategy[0]}")
    print(f"   Quality Score: {best_strategy[2]['overall_quality_score']:.1f}/100")
    
    return best_strategy

# Run comprehensive comparison
print("\n📊 COMPREHENSIVE CHUNKING STRATEGY EVALUATION")
print("="*80)

# Test on the most complex document (VPN Policy)
best_result = compare_chunking_strategies(sample_documents['vpn-policy.pdf'])
best_strategy_name, best_chunks, best_quality = best_result

print(f"\n📋 Detailed Quality Report for Best Strategy:")
print(f"Strategy: {best_strategy_name}")
print(f"Quality Score: {best_quality['overall_quality_score']:.1f}/100")
print(f"\nWord Count Distribution:")
print(f"  Mean: {best_quality['word_count_stats']['mean']:.1f}")
print(f"  Median: {best_quality['word_count_stats']['median']:.1f}")  
print(f"  Std Dev: {best_quality['word_count_stats']['std_dev']:.1f}")
print(f"  Range: {best_quality['word_count_stats']['min']} - {best_quality['word_count_stats']['max']}")

print(f"\nMetadata Coverage:")
print(f"  Sections identified: {best_quality['metadata_coverage']['chunks_with_sections']}")
print(f"  Section coverage: {best_quality['metadata_coverage']['section_coverage_pct']:.1f}%")
```

---

## Part 5: Database Integration & Storage (10 minutes)

### Step 5: Store Chunks in Vector Database

```python
def get_embedding(text: str, max_retries: int = 3) -> Optional[List[float]]:
    """Generate embedding for text using Ollama BGE-M3 model."""
    for attempt in range(max_retries):
        try:
            payload = {
                "model": EMBEDDING_MODEL,
                "input": text
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get("embeddings", [])
            
            if embedding and len(embedding[0]) == 1024:
                return embedding[0]
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"⚠️  Embedding failed for text: {text[:50]}... Error: {e}")
            time.sleep(1)
    
    return None

def setup_document_chunks_table():
    """Create enhanced table for document chunks."""
    
    print("🗄️  Setting up document chunks table...")
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Drop existing table if needed
                cur.execute("DROP TABLE IF EXISTS document_chunks CASCADE;")
                
                # Create enhanced table
                cur.execute("""
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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create indexes
                cur.execute("CREATE INDEX idx_doc_chunks_document_id ON document_chunks (document_id);")
                cur.execute("CREATE INDEX idx_doc_chunks_page ON document_chunks (page_number);")
                cur.execute("CREATE INDEX idx_doc_chunks_section ON document_chunks (section_title);")
                
                print("✅ Table and indexes created")
                conn.commit()
                
    except Exception as e:
        print(f"❌ Table setup failed: {e}")
        return False
    
    return True

def store_chunks_in_database(chunks: List[DocumentChunk], batch_size: int = 10) -> int:
    """
    Store document chunks with embeddings in database.
    
    Args:
        chunks: List of DocumentChunk objects
        batch_size: Number of chunks to process at once
        
    Returns:
        Number of chunks successfully stored
    """
    print(f"💾 Storing {len(chunks)} chunks in database...")
    
    stored_count = 0
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    print(f"🧠 Generating embedding for chunk {i+1}/{len(chunks)}...", end=" ")
                    
                    embedding = get_embedding(chunk.text)
                    if not embedding:
                        print("❌ Failed")
                        continue
                    
                    # Store in database
                    cur.execute("""
                        INSERT INTO document_chunks 
                        (id, document_id, document_title, text, embedding, 
                         page_number, section_title, chunk_index, word_count, character_count, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        chunk.id,
                        chunk.document_id,
                        chunk.document_title,
                        chunk.text,
                        embedding,
                        chunk.page_number,
                        chunk.section_title,
                        chunk.chunk_index,
                        chunk.word_count,
                        chunk.character_count,
                        chunk.created_at
                    ))
                    
                    stored_count += 1
                    print("✅")
                    
                    # Commit in batches
                    if (i + 1) % batch_size == 0:
                        conn.commit()
                        print(f"💾 Committed batch {i+1-batch_size+1}-{i+1}")
                        time.sleep(0.5)  # Be nice to Ollama
                
                # Final commit
                conn.commit()
                print(f"✅ Stored {stored_count} chunks successfully")
                
    except Exception as e:
        print(f"❌ Database storage failed: {e}")
    
    return stored_count

# Set up database and store our best chunks
print("\n💾 DATABASE STORAGE AND INTEGRATION")
print("="*60)

if setup_document_chunks_table():
    # Store our best chunks from the quality assessment
    stored_count = store_chunks_in_database(best_chunks[:5])  # Store first 5 for testing
    
    if stored_count > 0:
        print(f"\n🎉 Successfully stored {stored_count} chunks in vector database!")
        
        # Verify storage
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        document_title,
                        COUNT(*) as chunk_count,
                        AVG(word_count) as avg_words,
                        COUNT(embedding) as with_embeddings
                    FROM document_chunks 
                    GROUP BY document_title
                    ORDER BY document_title;
                """)
                
                results = cur.fetchall()
                print(f"\n📊 Database Contents:")
                for title, count, avg_words, embeddings in results:
                    print(f"   '{title}': {count} chunks, {avg_words:.1f} avg words, {embeddings} with embeddings")
```

---

## Part 6: Database Verification (4 minutes)

### Step 6: Verify Chunks Are Stored Correctly

```python
def verify_chunk_storage() -> None:
    """Verify that chunks are stored correctly in the database."""
    print("\n✅ VERIFYING CHUNK STORAGE")
    print("="*50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Count total chunks
                cur.execute("SELECT COUNT(*) FROM document_chunks;")
                total_chunks = cur.fetchone()[0]
                print(f"📊 Total chunks stored: {total_chunks}")
                
                # Count chunks with embeddings
                cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;")
                chunks_with_embeddings = cur.fetchone()[0]
                print(f"🧠 Chunks with embeddings: {chunks_with_embeddings}/{total_chunks}")
                
                # Show document breakdown
                cur.execute("""
                    SELECT 
                        document_title,
                        COUNT(*) as chunk_count,
                        AVG(word_count) as avg_words,
                        COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings
                    FROM document_chunks 
                    GROUP BY document_title
                    ORDER BY document_title;
                """)
                
                results = cur.fetchall()
                print(f"\n📄 Document breakdown:")
                for title, count, avg_words, embeddings in results:
                    print(f"   • {title}")
                    print(f"     Chunks: {count}, Avg words: {avg_words:.1f}, Embeddings: {embeddings}")
                
                # Sample chunk verification
                cur.execute("""
                    SELECT text, word_count, page_number, section_title
                    FROM document_chunks 
                    ORDER BY created_at 
                    LIMIT 2;
                """)
                
                samples = cur.fetchall()
                print(f"\n📖 Sample chunks:")
                for i, (text, words, page, section) in enumerate(samples, 1):
                    section_info = f", Section: {section}" if section else ""
                    print(f"   {i}. Page {page}{section_info} ({words} words)")
                    print(f"      '{text[:120]}...'")
                
                # Check vector dimensions
                cur.execute("SELECT vector_dims(embedding) FROM document_chunks WHERE embedding IS NOT NULL LIMIT 1;")
                result = cur.fetchone()
                if result:
                    dims = result[0]
                    print(f"\n🔢 Embedding dimensions: {dims} (should be 1024 for BGE-M3)")
                    if dims == 1024:
                        print("   ✅ Embeddings are correct size")
                    else:
                        print("   ⚠️  Unexpected embedding size")
                
    except Exception as e:
        print(f"❌ Storage verification failed: {e}")

# Verify our chunk storage
verify_chunk_storage()

print(f"\n🎉 Document processing complete! Chunks are ready for similarity search in Section 6.")
```

**Run the complete lab:**
```bash
python lab5_document_processing.py
```

---

## Success Criteria ✅

**You've completed this lab when:**
- [ ] Successfully extracted text from all three document types
- [ ] Implemented both fixed-size and content-aware chunking
- [ ] Quality assessment shows 80%+ quality score for best strategy
- [ ] Stored chunks with embeddings in database
- [ ] Database verification shows chunks stored with correct embeddings
- [ ] Metadata is preserved (page numbers, sections, etc.)

---

## Reflection & Next Steps

### Discussion Questions

**With your partner, discuss:**

1. **Strategy Trade-offs**: Which chunking strategy worked best for which document type? Why?

2. **Quality vs. Quantity**: How did chunk size affect both quality scores and search relevance?

3. **Metadata Value**: How important was preserving page numbers and section titles for user experience?

4. **Real-World Scaling**: How would you optimize this for processing 1,000 Edinburgh documents?

### Key Takeaways

- **Document structure matters** - formal policies need different handling than guides
- **Chunk size optimization** is crucial for both embedding quality and search precision
- **Metadata preservation** enables better user attribution and trust
- **Quality assessment** helps identify optimal parameters for different document types

### What's Next

**In Section 6, we'll use these chunks to:**
- Test similarity search and vector retrieval  
- Build complete RAG pipelines with LLM integration
- Create context-aware responses with source attribution
- Handle multi-document queries and complex user questions

---

## Troubleshooting

### Common Issues

**PyPDF2 extraction problems:**
```python
# Try alternative extraction if PyPDF2 fails
import pdfplumber

def alternative_pdf_extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text
```

**Poor chunk quality:**
```python
# Adjust parameters based on document type
document_type_configs = {
    'policy': {'chunk_size': 400, 'overlap': 80},    # Formal documents
    'guide': {'chunk_size': 250, 'overlap': 50},     # Step-by-step instructions  
    'handbook': {'chunk_size': 300, 'overlap': 60}   # Mixed content
}
```

**Slow embedding generation:**
```python
# Implement caching for repeated text
embedding_cache = {}

def cached_get_embedding(text):
    if text in embedding_cache:
        return embedding_cache[text]
    
    embedding = get_embedding(text)
    if embedding:
        embedding_cache[text] = embedding
    return embedding
```

Great work! You now have a sophisticated document processing pipeline that can handle real Edinburgh University documents and prepare them for effective AI-powered search and question-answering.