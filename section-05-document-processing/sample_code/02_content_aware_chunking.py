"""
Sample Code: Content-Aware Chunking
===================================

This example demonstrates content-aware chunking as described in the slides.
Shows how to respect document structure and preserve logical sections.
"""

import re
from typing import List, Optional
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
    section_title: Optional[str]
    chunk_index: int
    word_count: int
    character_count: int
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

def detect_section_title(text: str) -> Optional[str]:
    """
    Detect section titles in text using various patterns.
    
    This implements the section detection logic from the slides.
    
    Args:
        text: Text to analyze
        
    Returns:
        Section title if found, None otherwise
    """
    lines = text.split('\n')
    
    for line in lines[:5]:  # Check first few lines
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Look for numbered sections (1. Title, 2. Title, etc.)
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return line
        
        # Look for chapter/section patterns
        if re.match(r'^(Chapter|Section|Part)\s+\d+:', line, re.IGNORECASE):
            return line
        
        # Look for all-caps titles (short ones)
        if line.isupper() and 5 <= len(line) <= 50:
            return line
        
        # Look for titles that are short and start with capital
        if (len(line) <= 50 and 
            line[0].isupper() and 
            not line.endswith('.') and 
            not line.startswith(('The ', 'A ', 'An '))):
            return line
    
    return None

def split_by_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs, handling various paragraph markers.
    
    This respects document structure as mentioned in the slides.
    
    Args:
        text: Text to split
        
    Returns:
        List of paragraph strings
    """
    # Split by double newlines (standard paragraph break)
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Clean up paragraphs
    cleaned_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para and len(para.split()) > 3:  # Skip very short paragraphs
            cleaned_paragraphs.append(para)
    
    return cleaned_paragraphs

def content_aware_chunker(text: str, max_chunk_size: int = 500) -> List[str]:
    """
    Split text by content boundaries, respecting size limits.
    
    This implements the content-aware chunking algorithm from the slides.
    
    Args:
        text: Input text to chunk
        max_chunk_size: Maximum words per chunk
        
    Returns:
        List of text chunks respecting content boundaries
    """
    chunks = []
    
    # First, try to split by paragraphs
    paragraphs = split_by_paragraphs(text)
    
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
            # Paragraph itself is too large, need to split it
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # Split large paragraph using sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            temp_chunk = ""
            
            for sentence in sentences:
                sentence_words = len(sentence.split())
                temp_chunk_words = len(temp_chunk.split()) if temp_chunk else 0
                
                if temp_chunk_words + sentence_words > max_chunk_size and temp_chunk:
                    chunks.append(temp_chunk.strip())
                    temp_chunk = sentence
                else:
                    if temp_chunk:
                        temp_chunk += " " + sentence
                    else:
                        temp_chunk = sentence
            
            if temp_chunk:
                current_chunk = temp_chunk
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

def create_content_aware_chunks(text: str,
                               document_id: str,
                               document_title: str,
                               page_number: int = 1,
                               max_chunk_size: int = 500) -> List[DocumentChunk]:
    """
    Create DocumentChunk objects using content-aware chunking.
    
    This demonstrates the advantages mentioned in the slides.
    
    Args:
        text: Input text to chunk
        document_id: Unique identifier for the document
        document_title: Human-readable document title
        page_number: Page number this text came from
        max_chunk_size: Maximum words per chunk
        
    Returns:
        List of DocumentChunk objects
    """
    chunks = []
    chunk_index = 0
    
    # Clean the text but preserve line breaks for section detection
    cleaned_text = re.sub(r'[ \t]+', ' ', text)  # Only normalize spaces/tabs, not newlines
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text)  # Normalize multiple newlines to single
    cleaned_text = cleaned_text.strip()
    
    # Create content-aware chunks
    page_chunks = content_aware_chunker(cleaned_text, max_chunk_size)
    
    # Create DocumentChunk objects
    for chunk_text in page_chunks:
        # Detect section title for this specific chunk
        section_title = detect_section_title(chunk_text)
        
        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document_id,
            document_title=document_title,
            text=chunk_text,
            page_number=page_number,
            section_title=section_title,
            chunk_index=chunk_index,
            word_count=len(chunk_text.split()),
            character_count=len(chunk_text)
        )
        chunks.append(chunk)
        chunk_index += 1
    
    return chunks

def analyze_content_aware_quality(chunks: List[DocumentChunk]) -> dict:
    """
    Analyze the quality of content-aware chunks.
    
    This implements quality assessment specific to content-aware chunking.
    
    Args:
        chunks: List of DocumentChunk objects
        
    Returns:
        Dictionary with quality metrics
    """
    if not chunks:
        return {"error": "No chunks to analyze"}
    
    word_counts = [c.word_count for c in chunks]
    section_titles = [c.section_title for c in chunks if c.section_title]
    
    # Calculate statistics
    avg_words = sum(word_counts) / len(word_counts)
    min_words = min(word_counts)
    max_words = max(word_counts)
    
    # Count problematic chunks
    very_short = sum(1 for wc in word_counts if wc < 50)
    very_long = sum(1 for wc in word_counts if wc > 1000)
    
    # Check for broken sentences
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            broken_sentences += 1
    
    # Calculate quality score
    quality_score = 100
    quality_score -= (very_short / len(chunks)) * 20  # Less penalty for short chunks (content-aware)
    quality_score -= (very_long / len(chunks)) * 15   # Less penalty for long chunks (content-aware)
    quality_score -= (broken_sentences / len(chunks)) * 30  # Less penalty for broken sentences
    
    # Bonus for section detection
    section_detection_rate = len(section_titles) / len(chunks)
    quality_score += section_detection_rate * 20  # Bonus for good section detection
    
    return {
        "total_chunks": len(chunks),
        "avg_words_per_chunk": round(avg_words, 1),
        "min_words": min_words,
        "max_words": max_words,
        "very_short_chunks": very_short,
        "very_long_chunks": very_long,
        "broken_sentences": broken_sentences,
        "sections_detected": len(section_titles),
        "section_detection_rate": round(section_detection_rate * 100, 1),
        "quality_score": max(0, min(100, round(quality_score, 1)))
    }

def demonstrate_content_aware_chunking():
    """
    Demonstrate content-aware chunking with a sample Edinburgh student handbook.
    
    This shows the advantages mentioned in the slides.
    """
    print("🧠 CONTENT-AWARE CHUNKING DEMONSTRATION")
    print("=" * 50)
    
    # Sample Edinburgh student handbook text with clear structure
    sample_text = """
    Edinburgh Student Handbook 2024
    
    Welcome to the University of Edinburgh! This handbook contains essential information for all students.
    
    ## Academic Calendar
    
    The academic year runs from September to June, divided into two semesters. Semester 1 runs from September to December, with exams in January. Semester 2 runs from February to May, with exams in May and June.
    
    Important dates:
    - Freshers' Week: September 16-22, 2024
    - Semester 1 starts: September 23, 2024
    - Christmas break: December 16, 2024 - January 6, 2025
    - Semester 2 starts: January 27, 2025
    - Easter break: March 31 - April 14, 2025
    - Exams: May 5-23, 2025
    
    ## Registration Process
    
    All students must register online before the start of each semester. Registration includes:
    1. Confirming personal details
    2. Selecting courses (if applicable)
    3. Paying tuition fees
    4. Collecting student ID card
    
    Late registration incurs a £50 fee. Students who fail to register by the deadline may be withdrawn from their program.
    
    ## Library Services
    
    The university library provides access to millions of books, journals, and digital resources. Services include:
    - 24/7 access to main library
    - Study spaces and group rooms
    - Research support and training
    - Inter-library loan services
    - Digital resource access
    
    Library cards are required for all services. Lost cards can be replaced for £10.
    
    ## IT Services and Support
    
    The university provides comprehensive IT support for all students. Services include:
    - Email accounts (@ed.ac.uk)
    - WiFi access across campus
    - Software licenses and downloads
    - Computer labs and printing
    - Technical support helpdesk
    
    All students receive 1GB of free printing credit per semester. Additional credit can be purchased online.
    
    ## Accommodation
    
    The university offers various accommodation options:
    - University-managed halls of residence
    - Private accommodation partnerships
    - Homestay programs
    - Independent private rentals
    
    Applications for university accommodation open in January for the following academic year. Priority is given to first-year students and international students.
    """
    
    print("\n📊 Testing content-aware chunking:")
    
    # Create chunks using content-aware strategy
    chunks = create_content_aware_chunks(
        sample_text,
        document_id="student-handbook-2024",
        document_title="Student Handbook 2024",
        page_number=1,
        max_chunk_size=400
    )
    
    quality = analyze_content_aware_quality(chunks)
    
    print(f"   Chunks created: {quality['total_chunks']}")
    print(f"   Avg words/chunk: {quality['avg_words_per_chunk']}")
    print(f"   Quality score: {quality['quality_score']}/100")
    print(f"   Sections detected: {quality['sections_detected']} ({quality['section_detection_rate']}%)")
    print(f"   Issues: {quality['very_short_chunks']} short, {quality['very_long_chunks']} long, {quality['broken_sentences']} broken sentences")
    
    # Show sample chunks with their sections
    print(f"\n📖 Sample chunks with section detection:")
    for i, chunk in enumerate(chunks, 1):
        section_info = f" - {chunk.section_title}" if chunk.section_title else ""
        print(f"   {i}. ({chunk.word_count} words{section_info}): {chunk.text[:80]}...")
    
    print(f"\n✅ ADVANTAGES of Content-Aware Chunking:")
    print(f"   • Respects document structure")
    print(f"   • Preserves logical sections")
    print(f"   • Better semantic coherence")
    print(f"   • Maintains context boundaries")
    print(f"   • Detects section titles automatically")
    
    print(f"\n❌ DISADVANTAGES of Content-Aware Chunking:")
    print(f"   • Variable chunk sizes")
    print(f"   • More complex implementation")
    print(f"   • Document format dependent")

if __name__ == "__main__":
    demonstrate_content_aware_chunking()
