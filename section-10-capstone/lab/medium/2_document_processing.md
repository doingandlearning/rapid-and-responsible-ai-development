# 🌶️🌶️ Medium: Document Processing - Guided Experimentation

**"I like to experiment and add my own flavors"**

This guide gives you working examples with some gaps to fill in. You'll learn by doing while having guidance when you need it!

## Step 1: Core Document Processing

Here's the working structure with some improvements for you to implement:

```python
# services/document_processor.py
import json
import hashlib
import re
import os
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def process_document(file_path: str, content: str, project_type: str) -> List[Dict[str, Any]]:
    """
    Process a document into chunks with appropriate JSONB metadata.
    
    TODO: Add document validation
    TODO: Add error handling for different file types
    TODO: Add progress tracking for large documents
    """
    logger.info(f"Processing {project_type} document: {file_path}")
    
    # TODO: Add content validation
    if not content or len(content.strip()) == 0:
        logger.warning(f"Empty content in {file_path}")
        return []
    
    if project_type == "literature":
        return process_literature_document(file_path, content)
    elif project_type == "documentation":
        return process_documentation_document(file_path, content)
    elif project_type == "research":
        return process_research_document(file_path, content)
    elif project_type == "custom":
        return process_custom_document(file_path, content)
    else:
        return process_generic_document(file_path, content)

def process_literature_document(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Process literature with character and theme analysis.
    
    TODO: Add more sophisticated literary analysis
    TODO: Add support for different literary formats
    TODO: Add character relationship mapping
    """
    chunks = create_semantic_chunks(content)
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        # TODO: Enhance metadata extraction
        metadata = {
            "chunk_type": "literature",
            "word_count": len(chunk.split()),
            "sentence_count": len(re.findall(r'[.!?]+', chunk)),
            "has_dialogue": bool(re.search(r'"[^"]*"', chunk)),
            "has_character_names": extract_character_names(chunk),
            "literary_devices": extract_literary_devices(chunk),
            "themes": extract_themes(chunk),
            "reading_level": calculate_reading_level(chunk),
            # TODO: Add more literary analysis
            "emotional_tone": analyze_emotional_tone(chunk),
            "narrative_perspective": detect_narrative_perspective(chunk)
        }
        
        document_info = {
            "title": extract_title_from_filename(file_path),
            "file_path": file_path,
            "file_type": "literature",
            "language": "english",
            "author": extract_author_from_filename(file_path),
            "work_type": determine_work_type(file_path),
            "publication_year": extract_publication_year(file_path),
            # TODO: Add more document metadata
            "genre": detect_genre(chunk),
            "setting": extract_setting(chunk)
        }
        
        processing_info = {
            "chunk_index": i,
            "total_chunks": len(chunks),
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_method": "literature_parser",
            "project_type": "literature"
        }
        
        chunk_id = generate_chunk_id(file_path, i, "literature")
        
        processed_chunks.append({
            'chunk_id': chunk_id,
            'content': chunk,
            'metadata': metadata,
            'document_info': document_info,
            'processing_info': processing_info,
            'document_type': 'literature',
            'author': document_info['author']
        })
    
    logger.info(f"Processed {len(processed_chunks)} literature chunks")
    return processed_chunks
```

## Step 2: Implement Advanced Chunking

Here's the basic chunking with advanced features to implement:

```python
def create_semantic_chunks(content: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Create semantically meaningful chunks from content.
    
    TODO: Add support for different content structures
    TODO: Add intelligent sentence boundary detection
    TODO: Add paragraph-aware chunking
    TODO: Add table and list handling
    """
    # TODO: Detect content structure (paragraphs, sections, etc.)
    # TODO: Handle different content types (markdown, HTML, plain text)
    # TODO: Preserve formatting and structure
    
    # Basic implementation - enhance this!
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            
            # TODO: Implement smarter overlap strategy
            overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
            current_chunk = overlap_sentences + [sentence]
            current_length = sum(len(s.split()) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def create_advanced_chunks(content: str, options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Create chunks with advanced metadata and structure preservation.
    
    TODO: Implement paragraph-aware chunking
    TODO: Add section boundary detection
    TODO: Preserve formatting and links
    TODO: Add chunk quality scoring
    """
    if not options:
        options = {}
    
    # TODO: Your advanced chunking implementation
    # - Detect paragraphs, sections, headers
    # - Preserve markdown formatting
    # - Handle tables and lists
    # - Add chunk quality metrics
    
    pass
```

## Step 3: Implement Enhanced Metadata Extraction

Here are some advanced metadata extraction functions to implement:

```python
def analyze_emotional_tone(chunk: str) -> str:
    """
    Analyze the emotional tone of a text chunk.
    
    TODO: Implement sentiment analysis
    TODO: Add emotion detection
    TODO: Add mood classification
    """
    # TODO: Your emotional analysis implementation
    # - Use sentiment analysis libraries
    # - Detect emotions (joy, sadness, anger, etc.)
    # - Classify mood (positive, negative, neutral)
    
    pass

def detect_narrative_perspective(chunk: str) -> str:
    """
    Detect the narrative perspective of a text chunk.
    
    TODO: Implement perspective detection
    TODO: Add POV classification
    TODO: Handle different narrative styles
    """
    # TODO: Your perspective detection implementation
    # - First person (I, me, my)
    # - Second person (you, your)
    # - Third person (he, she, they)
    # - Omniscient vs limited
    
    pass

def detect_genre(chunk: str) -> str:
    """
    Detect the genre of a text chunk.
    
    TODO: Implement genre classification
    TODO: Add multiple genre support
    TODO: Handle genre mixing
    """
    # TODO: Your genre detection implementation
    # - Fiction vs non-fiction
    # - Literary genres (romance, mystery, sci-fi, etc.)
    # - Academic genres (research, review, etc.)
    
    pass

def extract_setting(chunk: str) -> Dict[str, str]:
    """
    Extract setting information from a text chunk.
    
    TODO: Implement setting extraction
    TODO: Add location and time detection
    TODO: Handle historical settings
    """
    # TODO: Your setting extraction implementation
    # - Time period detection
    # - Location extraction
    # - Historical context
    # - Cultural setting
    
    pass
```

## Step 4: Add Performance Optimizations

Here are some performance improvements to implement:

```python
def process_documents_batch(file_paths: List[str], project_type: str) -> List[Dict[str, Any]]:
    """
    Process multiple documents in batch for better performance.
    
    TODO: Implement parallel processing
    TODO: Add memory management
    TODO: Add progress tracking
    TODO: Add error handling for batch failures
    """
    # TODO: Your batch processing implementation
    # - Use multiprocessing or threading
    # - Implement memory-efficient processing
    # - Add progress bars
    # - Handle partial failures gracefully
    
    pass

def optimize_chunking_strategy(content: str, project_type: str) -> Dict[str, Any]:
    """
    Optimize chunking strategy based on content and project type.
    
    TODO: Implement adaptive chunking
    TODO: Add content analysis
    TODO: Add performance metrics
    """
    # TODO: Your optimization implementation
    # - Analyze content characteristics
    # - Choose optimal chunk size
    # - Adjust overlap based on content
    # - Measure chunk quality
    
    pass
```

## Step 5: Add Quality Assessment

Here are some quality assessment features to implement:

```python
def assess_chunk_quality(chunk: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess the quality of a document chunk.
    
    TODO: Implement quality metrics
    TODO: Add content completeness scoring
    TODO: Add semantic coherence analysis
    """
    # TODO: Your quality assessment implementation
    # - Content completeness
    # - Semantic coherence
    # - Information density
    # - Readability score
    
    pass

def validate_metadata(metadata: Dict[str, Any], project_type: str) -> bool:
    """
    Validate metadata completeness and accuracy.
    
    TODO: Implement metadata validation
    TODO: Add project-specific validation rules
    TODO: Add data quality checks
    """
    # TODO: Your validation implementation
    # - Check required fields
    # - Validate data types
    # - Check value ranges
    # - Project-specific rules
    
    pass
```

## Step 6: Test Your Advanced Features

Create a comprehensive test:

```python
# test_document_processing_medium.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_processor import *

def test_advanced_features():
    """Test your advanced document processing features"""
    print("🌶️🌶️ Testing Advanced Document Processing...")
    
    # Test your emotional tone analysis
    # Test your narrative perspective detection
    # Test your genre classification
    # Test your batch processing
    # Test your quality assessment
    # Add your own tests!
    
    print("🎉 Advanced features tested!")

if __name__ == "__main__":
    test_advanced_features()
```

## What You've Learned

✅ **Advanced Chunking**: Sophisticated document splitting strategies
✅ **Enhanced Metadata**: Rich metadata extraction and analysis
✅ **Performance**: Batch processing and optimization
✅ **Quality**: Content quality assessment and validation
✅ **Customization**: Project-specific processing enhancements

## Next Steps

Once you've implemented the advanced features, you're ready for:
- **[Medium: Search Engine](search_engine.md)** - Advanced search implementation
- **[Medium: RAG Pipeline](rag_pipeline.md)** - Enhanced RAG system

## Challenges to Try

1. **Performance**: How can you make document processing faster?
2. **Quality**: What metrics help you assess chunk quality?
3. **Customization**: How can you make processing more project-specific?
4. **Analysis**: What additional metadata would be useful for your project?

## Getting Help

- Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Ask questions in the discussion forum
- Look at the [Spicy version](../spicy/document_processing.md) for inspiration
- Experiment with different approaches!

Remember: There's no single "right" way to implement these features. Try different approaches and see what works best for your project! 🚀
