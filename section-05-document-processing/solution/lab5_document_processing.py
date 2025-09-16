#!/usr/bin/env python3
"""
Section 5: Document Processing & PDF Chunking - Complete Solution
Edinburgh University IT Documents Processing Pipeline
"""

import PyPDF2
import psycopg
import requests
import json
import time
import re
import uuid
import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Iterator, Dict, Any
from pathlib import Path

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# Ollama configuration
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
                print(f"⚠️  Embedding failed: {e}")
            time.sleep(1)
    
    return None

def create_sample_edinburgh_documents():
    """Create sample Edinburgh IT documents for testing."""
    
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

def fixed_size_chunker(text: str, chunk_size: int = 300, overlap: int = 50) -> Iterator[str]:
    """Split text into fixed-size chunks with overlap."""
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if chunk_words:
            yield " ".join(chunk_words)

def content_aware_chunker(text: str, max_chunk_size: int = 500) -> List[str]:
    """Split text by paragraphs and sections, respecting size limits."""
    chunks = []
    
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph_words = len(paragraph.split())
        current_chunk_words = len(current_chunk.split()) if current_chunk else 0
        
        if current_chunk_words + paragraph_words > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        elif paragraph_words > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            chunks.extend(fixed_size_chunker(paragraph, max_chunk_size, max_chunk_size // 4))
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def smart_section_detector(text: str) -> Optional[str]:
    """Try to detect section titles in text."""
    lines = text.split('\n')
    
    for line in lines[:3]:
        line = line.strip()
        
        if re.match(r'^(Chapter|Section|Part)\s+\d+:', line, re.IGNORECASE):
            return line
        
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return line
            
        if line.isupper() and 5 <= len(line) <= 50:
            return line
    
    return None

def create_chunks_from_document(document_data: Dict[str, Any], 
                              chunk_strategy: str = "fixed",
                              chunk_size: int = 300,
                              overlap: int = 50) -> List[DocumentChunk]:
    """Create DocumentChunk objects from document data."""
    chunks = []
    chunk_index = 0
    document_id = document_data['title'].lower().replace(' ', '-')
    
    print(f"📝 Creating chunks using {chunk_strategy} strategy...")
    print(f"   Chunk size: {chunk_size} words, Overlap: {overlap} words")
    
    for page_num, page_text in document_data['pages']:
        cleaned_text = re.sub(r'\s+', ' ', page_text).strip()
        section_title = smart_section_detector(cleaned_text)
        
        if chunk_strategy == "fixed":
            page_chunks = list(fixed_size_chunker(cleaned_text, chunk_size, overlap))
        elif chunk_strategy == "content_aware":
            page_chunks = content_aware_chunker(cleaned_text, chunk_size)
        else:
            page_chunks = list(fixed_size_chunker(cleaned_text, chunk_size, overlap))
        
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
    
    print(f"✅ Created {len(chunks)} chunks")
    return chunks

def assess_chunk_quality(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """Comprehensive quality assessment of document chunks."""
    if not chunks:
        return {"error": "No chunks to assess"}
    
    word_counts = [c.word_count for c in chunks]
    
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text[-1] in '.!?':
            broken_sentences += 1
    
    very_short = sum(1 for wc in word_counts if wc < 20)
    very_long = sum(1 for wc in word_counts if wc > 800)
    
    chunk_texts = [c.text.lower().strip() for c in chunks]
    duplicates = len(chunk_texts) - len(set(chunk_texts))
    
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
    
    # Quality score calculation
    quality_score = 100
    quality_score -= (broken_sentences / len(chunks)) * 20
    quality_score -= (very_short / len(chunks)) * 15
    quality_score -= (very_long / len(chunks)) * 10
    quality_score -= (duplicates / len(chunks)) * 25
    quality_score = max(0, quality_score)
    
    quality_report['overall_quality_score'] = quality_score
    
    return quality_report

def setup_document_chunks_table():
    """Create enhanced table for document chunks."""
    
    print("🗄️  Setting up document chunks table...")
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS document_chunks CASCADE;")
                
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
                
                cur.execute("CREATE INDEX idx_doc_chunks_document_id ON document_chunks (document_id);")
                cur.execute("CREATE INDEX idx_doc_chunks_page ON document_chunks (page_number);")
                cur.execute("CREATE INDEX idx_doc_chunks_section ON document_chunks (section_title);")
                
                print("✅ Table and indexes created")
                conn.commit()
                
    except Exception as e:
        print(f"❌ Table setup failed: {e}")
        return False
    
    return True

def store_chunks_in_database(chunks: List[DocumentChunk], batch_size: int = 5) -> int:
    """Store document chunks with embeddings in database."""
    print(f"💾 Storing {len(chunks)} chunks in database...")
    
    stored_count = 0
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for i, chunk in enumerate(chunks):
                    print(f"🧠 Generating embedding for chunk {i+1}/{len(chunks)}...", end=" ")
                    
                    embedding = get_embedding(chunk.text)
                    if not embedding:
                        print("❌ Failed")
                        continue
                    
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
                    
                    if (i + 1) % batch_size == 0:
                        conn.commit()
                        print(f"💾 Committed batch {i+1-batch_size+1}-{i+1}")
                        time.sleep(0.5)
                
                conn.commit()
                print(f"✅ Stored {stored_count} chunks successfully")
                
    except Exception as e:
        print(f"❌ Database storage failed: {e}")
    
    return stored_count

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

def compare_chunking_strategies(document_data: Dict[str, Any]) -> tuple:
    """Compare different chunking strategies on the same document."""
    
    print(f"📊 CHUNKING STRATEGY COMPARISON")
    print(f"Document: {document_data['title']}")
    print("="*70)
    
    strategies = [
        ("Fixed-Size (200w, 40w overlap)", "fixed", 200, 40),
        ("Fixed-Size (300w, 50w overlap)", "fixed", 300, 50),
        ("Content-Aware (300w max)", "content_aware", 300, 0),
        ("Content-Aware (400w max)", "content_aware", 400, 0),
    ]
    
    results = []
    
    for strategy_name, strategy_type, chunk_size, overlap in strategies:
        print(f"\n🔧 Testing: {strategy_name}")
        chunks = create_chunks_from_document(
            document_data, 
            strategy_type, 
            chunk_size, 
            overlap
        )
        quality = assess_chunk_quality(chunks)
        
        results.append((strategy_name, chunks, quality))
        
        print(f"   Chunks created: {quality['total_chunks']}")
        print(f"   Avg words/chunk: {quality['word_count_stats']['mean']:.1f}")
        print(f"   Quality score: {quality['overall_quality_score']:.1f}/100")
        print(f"   Issues: {quality['quality_issues']['broken_sentences']} broken sentences, "
              f"{quality['quality_issues']['duplicate_chunks']} duplicates")
    
    best_strategy = max(results, key=lambda x: x[2]['overall_quality_score'])
    print(f"\n🏆 Best Strategy: {best_strategy[0]}")
    print(f"   Quality Score: {best_strategy[2]['overall_quality_score']:.1f}/100")
    
    return best_strategy

def main():
    """Main document processing workflow."""
    print("🚀 SECTION 5: DOCUMENT PROCESSING & PDF CHUNKING")
    print("="*80)
    print("Processing Edinburgh University IT Documents\n")
    
    # Create sample documents
    print("📚 Creating sample Edinburgh documents...")
    sample_documents = create_sample_edinburgh_documents()
    print(f"✅ Created {len(sample_documents)} sample documents")
    
    # Test chunking strategies
    print(f"\n📊 COMPREHENSIVE CHUNKING STRATEGY EVALUATION")
    print("="*80)
    
    # Test on VPN Policy (most structured document)
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
    
    # Database setup and storage
    print(f"\n💾 DATABASE STORAGE AND INTEGRATION")
    print("="*60)
    
    stored_count = 0  # Initialize variable
    
    if setup_document_chunks_table():
        # Store best chunks (first 8 for demonstration)
        demo_chunks = best_chunks[:8]
        stored_count = store_chunks_in_database(demo_chunks)
        
        if stored_count > 0:
            print(f"\n🎉 Successfully stored {stored_count} chunks in vector database!")
            
            # Verify storage
            try:
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
                
                # Verify chunk storage
                verify_chunk_storage()
                
            except Exception as e:
                print(f"⚠️  Database verification failed: {e}")
        else:
            print(f"\n⚠️  No chunks were stored in database")
    else:
        print(f"\n⚠️  Database setup failed - skipping storage phase")
        print(f"   Make sure PostgreSQL is running: cd environment && docker compose up -d")
    
    print(f"\n" + "="*80)
    print("✅ SECTION 5 COMPLETE!")
    print(f"Successfully processed Edinburgh IT documents with:")
    print(f"  • Multiple chunking strategies tested and evaluated")
    print(f"  • Quality assessment and optimization")
    print(f"  • Database storage with embeddings")
    print(f"  • Storage verification and validation")
    print(f"\n💡 Key findings:")
    print(f"  • Best strategy: {best_strategy_name}")
    print(f"  • Quality score: {best_quality['overall_quality_score']:.1f}/100")
    print(f"  • Chunks stored: {stored_count} with embeddings")
    print(f"\n🎯 Document chunks ready for Section 6: RAG Pipeline Integration!")

if __name__ == "__main__":
    main()