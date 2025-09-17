"""
Part 2: Fixed-Size Chunking - Solution
=====================================

This solution shows how to implement fixed-size chunking with overlap
and proper metadata handling.
"""

import uuid
import re
from typing import List, Dict, Any, Iterator, Optional
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
    
    if len(words) <= chunk_size:
        yield " ".join(words)
        return
    
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
            # We'll implement other strategies in later parts
            page_chunks = list(fixed_size_chunker(cleaned_text, chunk_size, overlap))
        
        # Create DocumentChunk objects
        for chunk_text in page_chunks:
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                document_title=document_data['title'],
                text=chunk_text,
                page_number=page_num,
                chunk_index=chunk_index,
                word_count=len(chunk_text.split()),
                character_count=len(chunk_text)
            )
            chunks.append(chunk)
            chunk_index += 1
    
    print(f"✅ Created {len(chunks)} chunks")
    return chunks

def analyze_chunk_quality(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """
    Analyze the quality of created chunks.
    
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
    
    # Check for very short chunks (potential issues)
    very_short = sum(1 for wc in word_counts if wc < 20)
    
    # Check for very long chunks (might exceed limits)
    very_long = sum(1 for wc in word_counts if wc > 500)
    
    # Check for broken sentences (chunks ending mid-sentence)
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text[-1] in '.!?':
            broken_sentences += 1
    
    return {
        'total_chunks': len(chunks),
        'avg_words_per_chunk': round(avg_words, 1),
        'min_words': min_words,
        'max_words': max_words,
        'very_short_chunks': very_short,
        'very_long_chunks': very_long,
        'broken_sentences': broken_sentences,
        'quality_score': max(0, 100 - (very_short * 5) - (very_long * 3) - (broken_sentences * 10))
    }

def test_different_chunk_sizes(document_data: Dict[str, Any]) -> None:
    """
    Test different chunk sizes to find optimal parameters.
    
    Args:
        document_data: Document to test with
    """
    print(f"\n🔧 Testing Different Chunk Sizes")
    print(f"Document: {document_data['title']}")
    print("=" * 60)
    
    test_configs = [
        (200, 40, "Small chunks, moderate overlap"),
        (300, 50, "Medium chunks, good overlap"),
        (400, 60, "Large chunks, high overlap"),
        (250, 30, "Medium chunks, low overlap"),
    ]
    
    results = []
    
    for chunk_size, overlap, description in test_configs:
        print(f"\n📊 Testing: {description}")
        print(f"   Size: {chunk_size} words, Overlap: {overlap} words")
        
        # Create chunks
        chunks = create_chunks_from_document(
            document_data, 
            chunk_size=chunk_size, 
            overlap=overlap
        )
        
        # Analyze quality
        quality = analyze_chunk_quality(chunks)
        
        results.append({
            'config': (chunk_size, overlap),
            'description': description,
            'chunks': chunks,
            'quality': quality
        })
        
        print(f"   Chunks created: {quality['total_chunks']}")
        print(f"   Avg words/chunk: {quality['avg_words_per_chunk']}")
        print(f"   Quality score: {quality['quality_score']}/100")
        print(f"   Issues: {quality['very_short_chunks']} short, {quality['very_long_chunks']} long, {quality['broken_sentences']} broken sentences")
    
    # Find best configuration
    best_result = max(results, key=lambda x: x['quality']['quality_score'])
    print(f"\n🏆 Best Configuration: {best_result['description']}")
    print(f"   Quality Score: {best_result['quality']['quality_score']}/100")
    
    return best_result

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Fixed-Size Chunking")
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
        
        # Test different chunk sizes
        best_config = test_different_chunk_sizes(first_doc)
        
        # Show sample chunks from best configuration
        print(f"\n📖 Sample Chunks from Best Configuration:")
        for i, chunk in enumerate(best_config['chunks'][:3], 1):
            print(f"\n   Chunk {i} (Page {chunk.page_number}, {chunk.word_count} words):")
            print(f"   '{chunk.text[:100]}...'")
        
    except ImportError:
        print("⚠️  Part 1 text extraction not available. Using sample data...")
        # Fallback to sample data
        sample_document = {
            'title': 'Sample Document',
            'pages': [
                (1, "This is a sample document for testing chunking strategies. " * 50)
            ]
        }
        best_config = test_different_chunk_sizes(sample_document)
    
    print(f"\n🎉 Fixed-size chunking complete!")
    print(f"Next step: Implement content-aware chunking in Part 3")
