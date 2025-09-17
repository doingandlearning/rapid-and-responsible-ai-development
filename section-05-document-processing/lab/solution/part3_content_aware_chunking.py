"""
Part 3: Content-Aware Chunking - Solution
=========================================

This solution shows how to implement content-aware chunking that respects
document structure and natural boundaries.
"""

import re
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

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
    section_title: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        
        # Calculate counts if not provided
        if self.word_count == 0:
            self.word_count = len(self.text.split())
        if self.character_count == 0:
            self.character_count = len(self.text)

def detect_section_title(text: str) -> Optional[str]:
    """
    Detect section titles in text using various patterns.
    
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

def create_content_aware_chunks(document_data: Dict[str, Any],
                               max_chunk_size: int = 400) -> List[DocumentChunk]:
    """
    Create chunks using content-aware strategy.
    
    Args:
        document_data: Document data with pages
        max_chunk_size: Maximum words per chunk
        
    Returns:
        List of DocumentChunk objects
    """
    chunks = []
    chunk_index = 0
    document_id = document_data['title'].lower().replace(' ', '-')
    
    print(f"🧠 Creating content-aware chunks (max {max_chunk_size} words)...")
    
    for page_num, page_text in document_data['pages']:
        # Clean the text but preserve line breaks for section detection
        cleaned_text = re.sub(r'[ \t]+', ' ', page_text)  # Only normalize spaces/tabs, not newlines
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
                document_title=document_data['title'],
                text=chunk_text,
                page_number=page_num,
                section_title=section_title,
                chunk_index=chunk_index,
                word_count=len(chunk_text.split()),
                character_count=len(chunk_text)
            )
            chunks.append(chunk)
            chunk_index += 1
    
    print(f"✅ Created {len(chunks)} content-aware chunks")
    return chunks

def compare_chunking_strategies(document_data: Dict[str, Any]) -> None:
    """
    Compare fixed-size vs content-aware chunking strategies.
    
    Args:
        document_data: Document to test with
    """
    print(f"\n📊 CHUNKING STRATEGY COMPARISON")
    print(f"Document: {document_data['title']}")
    print("=" * 70)
    
    # Fixed-size chunking
    print(f"\n🔧 Testing Fixed-Size Chunking (300 words, 50 overlap)")
    from part2_fixed_chunking import create_chunks_from_document, analyze_chunk_quality
    
    fixed_chunks = create_chunks_from_document(
        document_data, 
        chunk_strategy="fixed", 
        chunk_size=300, 
        overlap=50
    )
    fixed_quality = analyze_chunk_quality(fixed_chunks)
    
    print(f"   Chunks created: {fixed_quality['total_chunks']}")
    print(f"   Avg words/chunk: {fixed_quality['avg_words_per_chunk']}")
    print(f"   Quality score: {fixed_quality['quality_score']}/100")
    
    # Content-aware chunking
    print(f"\n🧠 Testing Content-Aware Chunking (400 words max)")
    content_chunks = create_content_aware_chunks(document_data, max_chunk_size=400)
    content_quality = analyze_chunk_quality(content_chunks)
    
    print(f"   Chunks created: {content_quality['total_chunks']}")
    print(f"   Avg words/chunk: {content_quality['avg_words_per_chunk']}")
    print(f"   Quality score: {content_quality['quality_score']}/100")
    
    # Count chunks with section titles
    chunks_with_sections = sum(1 for c in content_chunks if c.section_title)
    print(f"   Chunks with section titles: {chunks_with_sections}/{len(content_chunks)}")
    
    # Determine best strategy
    if content_quality['quality_score'] > fixed_quality['quality_score']:
        print(f"\n🏆 Best Strategy: Content-Aware Chunking")
        print(f"   Quality Score: {content_quality['quality_score']}/100")
        return content_chunks, content_quality
    else:
        print(f"\n🏆 Best Strategy: Fixed-Size Chunking")
        print(f"   Quality Score: {fixed_quality['quality_score']}/100")
        return fixed_chunks, fixed_quality

def analyze_content_structure(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """
    Analyze the content structure of chunks.
    
    Args:
        chunks: List of DocumentChunk objects
        
    Returns:
        Dictionary with structure analysis
    """
    if not chunks:
        return {"error": "No chunks to analyze"}
    
    # Count chunks with section titles
    chunks_with_sections = sum(1 for c in chunks if c.section_title)
    
    # Analyze section title patterns
    section_titles = [c.section_title for c in chunks if c.section_title]
    unique_sections = len(set(section_titles))
    
    # Analyze chunk sizes
    word_counts = [c.word_count for c in chunks]
    avg_words = sum(word_counts) / len(word_counts)
    
    # Check for semantic coherence (chunks that start mid-sentence)
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text[0].isupper():
            broken_sentences += 1
    
    return {
        'total_chunks': len(chunks),
        'chunks_with_sections': chunks_with_sections,
        'section_coverage_pct': (chunks_with_sections / len(chunks)) * 100,
        'unique_sections': unique_sections,
        'avg_words_per_chunk': round(avg_words, 1),
        'broken_sentences': broken_sentences,
        'structure_quality_score': max(0, 100 - (broken_sentences * 15) + (chunks_with_sections * 2))
    }

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Content-Aware Chunking")
    print("=" * 50)
    
    # Import text extraction from Part 1
    try:
        from part1_text_extraction import process_all_input_files
        processed_documents = process_all_input_files("input")
        
        if not processed_documents:
            print("\n💡 To test this solution:")
            print("   1. Add some .txt, .pdf, or .html files to the 'input' folder")
            print("   2. Run this script again")
            exit(0)
        
        # Test with the first document
        first_doc = list(processed_documents.values())[0]
        print(f"\n📄 Testing with: {first_doc['title']}")
        
        # Compare chunking strategies
        best_chunks, best_quality = compare_chunking_strategies(first_doc)
        
    except ImportError:
        print("⚠️  Part 1 text extraction not available. Using sample data...")
        # Fallback to sample data
        sample_document = {
            'title': 'Sample Policy Document',
            'pages': [
                (1, """1. Introduction

This is a sample policy document with clear structure.

2. Requirements

All users must follow these guidelines:
- Use strong passwords
- Report security incidents
- Follow data handling procedures

3. Compliance

Violations may result in:
- Account suspension
- Disciplinary action
- Legal consequences""")
            ]
        }
        best_chunks, best_quality = compare_chunking_strategies(sample_document)
    
    # Analyze content structure
    structure_analysis = analyze_content_structure(best_chunks)
    
    print(f"\n📋 Content Structure Analysis:")
    print(f"   Total chunks: {structure_analysis['total_chunks']}")
    print(f"   Chunks with sections: {structure_analysis['chunks_with_sections']}")
    print(f"   Section coverage: {structure_analysis['section_coverage_pct']:.1f}%")
    print(f"   Unique sections: {structure_analysis['unique_sections']}")
    print(f"   Structure quality: {structure_analysis['structure_quality_score']}/100")
    
    # Show sample chunks
    print(f"\n📖 Sample Chunks:")
    for i, chunk in enumerate(best_chunks[:3], 1):
        section_info = f" - {chunk.section_title}" if chunk.section_title else ""
        print(f"\n   Chunk {i} (Page {chunk.page_number}{section_info}, {chunk.word_count} words):")
        print(f"   '{chunk.text[:120]}...'")
    
    print(f"\n🎉 Content-aware chunking complete!")
    print(f"Next step: Implement quality assessment in Part 4")
