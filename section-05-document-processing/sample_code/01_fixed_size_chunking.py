"""
Sample Code: Fixed-Size Chunking
================================

This example demonstrates fixed-size chunking as described in the slides.
Shows the basic approach, advantages, and disadvantages.
"""

import re
from typing import List, Iterator
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class DocumentChunk:
    """Represents a chunk of a document with metadata."""
    id: str
    document_id: str
    document_title: str
    text: str
    page_number: int
    chunk_index: int
    word_count: int
    character_count: int
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

def fixed_size_chunker(text: str, chunk_size: int = 300, 
                      overlap: int = 50) -> Iterator[str]:
    """
    Split text into fixed-size chunks with overlap.
    
    This is the basic fixed-size chunking approach from the slides.
    
    Args:
        text: Input text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of words to overlap between chunks
        
    Yields:
        Text chunks as strings
    """
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        yield " ".join(chunk)

def create_fixed_chunks_with_metadata(text: str, 
                                    document_id: str,
                                    document_title: str,
                                    page_number: int = 1,
                                    chunk_size: int = 300,
                                    overlap: int = 50) -> List[DocumentChunk]:
    """
    Create DocumentChunk objects using fixed-size chunking.
    
    This demonstrates metadata preservation as shown in the slides.
    
    Args:
        text: Input text to chunk
        document_id: Unique identifier for the document
        document_title: Human-readable document title
        page_number: Page number this text came from
        chunk_size: Words per chunk
        overlap: Overlap between chunks
        
    Returns:
        List of DocumentChunk objects
    """
    chunks = []
    chunk_index = 0
    
    for chunk_text in fixed_size_chunker(text, chunk_size, overlap):
        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document_id,
            document_title=document_title,
            text=chunk_text,
            page_number=page_number,
            chunk_index=chunk_index,
            word_count=len(chunk_text.split()),
            character_count=len(chunk_text)
        )
        chunks.append(chunk)
        chunk_index += 1
    
    return chunks

def analyze_chunk_quality(chunks: List[DocumentChunk]) -> dict:
    """
    Analyze the quality of fixed-size chunks.
    
    This implements the quality assessment metrics from the slides.
    
    Args:
        chunks: List of DocumentChunk objects
        
    Returns:
        Dictionary with quality metrics
    """
    if not chunks:
        return {"error": "No chunks to analyze"}
    
    word_counts = [c.word_count for c in chunks]
    
    # Calculate statistics
    avg_words = sum(word_counts) / len(word_counts)
    min_words = min(word_counts)
    max_words = max(word_counts)
    
    # Count problematic chunks
    very_short = sum(1 for wc in word_counts if wc < 50)
    very_long = sum(1 for wc in word_counts if wc > 1000)
    
    # Check for broken sentences (chunks ending mid-sentence)
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            broken_sentences += 1
    
    # Calculate quality score (0-100)
    quality_score = 100
    quality_score -= (very_short / len(chunks)) * 30  # Penalty for very short chunks
    quality_score -= (very_long / len(chunks)) * 20   # Penalty for very long chunks
    quality_score -= (broken_sentences / len(chunks)) * 50  # Penalty for broken sentences
    
    return {
        "total_chunks": len(chunks),
        "avg_words_per_chunk": round(avg_words, 1),
        "min_words": min_words,
        "max_words": max_words,
        "very_short_chunks": very_short,
        "very_long_chunks": very_long,
        "broken_sentences": broken_sentences,
        "quality_score": max(0, round(quality_score, 1))
    }

def demonstrate_fixed_chunking():
    """
    Demonstrate fixed-size chunking with a sample Edinburgh IT policy.
    
    This shows the advantages and disadvantages mentioned in the slides.
    """
    print("🔧 FIXED-SIZE CHUNKING DEMONSTRATION")
    print("=" * 50)
    
    # Sample Edinburgh IT policy text
    sample_text = """
    University of Edinburgh IT Security Policy
    
    The University of Edinburgh is committed to maintaining the highest standards of information security. This policy outlines the requirements for all users of university IT systems and networks.
    
    Password Requirements:
    All passwords must be at least 12 characters long and contain a combination of uppercase letters, lowercase letters, numbers, and special characters. Passwords must be changed every 90 days and cannot be reused for the previous 12 password changes.
    
    Network Security:
    All devices connecting to the university network must have up-to-date antivirus software installed and enabled. Personal devices must be registered with IT Services before accessing the network. Unauthorized access to university systems is strictly prohibited.
    
    Data Protection:
    All university data must be handled in accordance with GDPR regulations. Personal data must be encrypted when stored or transmitted. Users must report any data breaches immediately to the Data Protection Officer.
    
    Incident Response:
    In case of a security incident, users must immediately disconnect from the network and contact IT Services. Do not attempt to resolve security issues independently. All incidents will be investigated and documented.
    
    Compliance:
    Failure to comply with this policy may result in disciplinary action, including suspension of IT access privileges. All users are required to acknowledge receipt and understanding of this policy annually.
    """
    
    # Create chunks using different sizes
    print("\n📊 Testing different chunk sizes:")
    
    for chunk_size in [200, 300, 500]:
        print(f"\n🔧 Chunk size: {chunk_size} words")
        chunks = create_fixed_chunks_with_metadata(
            sample_text,
            document_id="it-security-policy-2024",
            document_title="IT Security Policy 2024",
            page_number=1,
            chunk_size=chunk_size,
            overlap=50
        )
        
        quality = analyze_chunk_quality(chunks)
        
        print(f"   Chunks created: {quality['total_chunks']}")
        print(f"   Avg words/chunk: {quality['avg_words_per_chunk']}")
        print(f"   Quality score: {quality['quality_score']}/100")
        print(f"   Issues: {quality['very_short_chunks']} short, {quality['very_long_chunks']} long, {quality['broken_sentences']} broken sentences")
        
        # Show sample chunks
        print(f"   Sample chunks:")
        for i, chunk in enumerate(chunks[:2], 1):
            print(f"     {i}. ({chunk.word_count} words): {chunk.text[:80]}...")
    
    print(f"\n✅ ADVANTAGES of Fixed-Size Chunking:")
    print(f"   • Simple to implement")
    print(f"   • Predictable chunk sizes")
    print(f"   • Consistent processing time")
    print(f"   • Works with any document type")
    
    print(f"\n❌ DISADVANTAGES of Fixed-Size Chunking:")
    print(f"   • May split sentences mid-word")
    print(f"   • Can break logical sections")
    print(f"   • No awareness of document structure")

if __name__ == "__main__":
    demonstrate_fixed_chunking()
