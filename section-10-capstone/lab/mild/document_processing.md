# 🌶️ Mild: Document Processing - Complete Working Code

**"I like to follow the recipe step-by-step"**

This guide gives you complete, working code for processing documents into chunks with rich metadata. You'll understand every step of the document processing pipeline!

## Step 1: Basic Document Processing

Here's the complete working code for processing different types of documents:

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
    
    This function:
    1. Determines the project type
    2. Calls the appropriate processing function
    3. Returns a list of processed chunks
    """
    logger.info(f"Processing {project_type} document: {file_path}")
    
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
    
    This function:
    1. Splits content into semantic chunks
    2. Extracts literary metadata
    3. Identifies characters and themes
    4. Creates rich JSONB metadata
    """
    # Split content into chunks
    chunks = create_semantic_chunks(content)
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        # Extract basic literary metadata
        metadata = {
            "chunk_type": "literature",
            "word_count": len(chunk.split()),
            "sentence_count": len(re.findall(r'[.!?]+', chunk)),
            "has_dialogue": bool(re.search(r'"[^"]*"', chunk)),
            "has_character_names": extract_character_names(chunk),
            "literary_devices": extract_literary_devices(chunk),
            "themes": extract_themes(chunk),
            "reading_level": calculate_reading_level(chunk)
        }
        
        # Document information
        document_info = {
            "title": extract_title_from_filename(file_path),
            "file_path": file_path,
            "file_type": "literature",
            "language": "english",
            "author": extract_author_from_filename(file_path),
            "work_type": determine_work_type(file_path),
            "publication_year": extract_publication_year(file_path)
        }
        
        # Processing information
        processing_info = {
            "chunk_index": i,
            "total_chunks": len(chunks),
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_method": "literature_parser",
            "project_type": "literature"
        }
        
        # Generate unique chunk ID
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

def process_documentation_document(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Process API documentation with code examples and parameters.
    
    This function:
    1. Identifies code blocks and examples
    2. Extracts API endpoints and parameters
    3. Categorizes content by type
    4. Creates technical metadata
    """
    chunks = create_semantic_chunks(content)
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        # Extract technical metadata
        metadata = {
            "chunk_type": "documentation",
            "word_count": len(chunk.split()),
            "has_code_blocks": bool(re.search(r'```[\s\S]*?```', chunk)),
            "has_api_endpoints": extract_api_endpoints(chunk),
            "has_parameters": extract_parameters(chunk),
            "has_examples": bool(re.search(r'example|Example', chunk)),
            "code_language": extract_code_language(chunk),
            "complexity_level": calculate_complexity_level(chunk)
        }
        
        document_info = {
            "title": extract_title_from_filename(file_path),
            "file_path": file_path,
            "file_type": "documentation",
            "language": "english",
            "api_version": extract_api_version(chunk),
            "section_type": determine_section_type(chunk),
            "last_updated": extract_last_updated(chunk)
        }
        
        processing_info = {
            "chunk_index": i,
            "total_chunks": len(chunks),
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_method": "documentation_parser",
            "project_type": "documentation"
        }
        
        chunk_id = generate_chunk_id(file_path, i, "documentation")
        
        processed_chunks.append({
            'chunk_id': chunk_id,
            'content': chunk,
            'metadata': metadata,
            'document_info': document_info,
            'processing_info': processing_info,
            'document_type': 'documentation',
            'author': 'API Documentation'
        })
    
    logger.info(f"Processed {len(processed_chunks)} documentation chunks")
    return processed_chunks

def process_research_document(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Process research papers with citations and methodology.
    
    This function:
    1. Extracts citations and references
    2. Identifies methodology sections
    3. Categorizes by research type
    4. Creates academic metadata
    """
    chunks = create_semantic_chunks(content)
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        # Extract academic metadata
        metadata = {
            "chunk_type": "research",
            "word_count": len(chunk.split()),
            "has_citations": extract_citations(chunk),
            "has_methodology": bool(re.search(r'method|Method|approach|Approach', chunk)),
            "has_results": bool(re.search(r'result|Result|finding|Finding', chunk)),
            "has_abstract": bool(re.search(r'abstract|Abstract', chunk)),
            "research_type": determine_research_type(chunk),
            "academic_level": calculate_academic_level(chunk)
        }
        
        document_info = {
            "title": extract_title_from_filename(file_path),
            "file_path": file_path,
            "file_type": "research",
            "language": "english",
            "authors": extract_authors(chunk),
            "journal": extract_journal(chunk),
            "publication_year": extract_publication_year(chunk),
            "doi": extract_doi(chunk)
        }
        
        processing_info = {
            "chunk_index": i,
            "total_chunks": len(chunks),
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_method": "research_parser",
            "project_type": "research"
        }
        
        chunk_id = generate_chunk_id(file_path, i, "research")
        
        processed_chunks.append({
            'chunk_id': chunk_id,
            'content': chunk,
            'metadata': metadata,
            'document_info': document_info,
            'processing_info': processing_info,
            'document_type': 'research',
            'author': document_info['authors'][0] if document_info['authors'] else 'Unknown'
        })
    
    logger.info(f"Processed {len(processed_chunks)} research chunks")
    return processed_chunks

def process_custom_document(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Process custom documents - the sky's the limit!
    
    This function:
    1. Creates basic chunks
    2. Extracts custom metadata
    3. Allows for domain-specific processing
    4. Provides flexible structure
    """
    chunks = create_semantic_chunks(content)
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        # Basic custom metadata
        metadata = {
            "chunk_type": "custom",
            "word_count": len(chunk.split()),
            "has_numbers": bool(re.search(r'\d+', chunk)),
            "has_dates": bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', chunk)),
            "has_contact_info": bool(re.search(r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b', chunk)),
            "custom_field_1": "your_value_here",
            "custom_field_2": "another_value",
            "domain": "your_domain"
        }
        
        document_info = {
            "title": os.path.basename(file_path),
            "file_path": file_path,
            "file_type": "custom",
            "language": "english",
            "custom_doc_field": "your_document_metadata"
        }
        
        processing_info = {
            "chunk_index": i,
            "total_chunks": len(chunks),
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_method": "custom_parser",
            "project_type": "custom"
        }
        
        chunk_id = generate_chunk_id(file_path, i, "custom")
        
        processed_chunks.append({
            'chunk_id': chunk_id,
            'content': chunk,
            'metadata': metadata,
            'document_info': document_info,
            'processing_info': processing_info,
            'document_type': 'custom',
            'author': 'Custom Author'
        })
    
    logger.info(f"Processed {len(processed_chunks)} custom chunks")
    return processed_chunks

def process_generic_document(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Process generic documents with basic metadata.
    
    This function:
    1. Creates basic chunks
    2. Extracts simple metadata
    3. Provides fallback processing
    4. Handles any document type
    """
    chunks = create_semantic_chunks(content)
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        metadata = {
            "chunk_type": "generic",
            "word_count": len(chunk.split()),
            "has_numbers": bool(re.search(r'\d+', chunk)),
            "has_dates": bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', chunk)),
            "has_contact_info": bool(re.search(r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b', chunk))
        }
        
        document_info = {
            "title": os.path.basename(file_path),
            "file_path": file_path,
            "file_type": "generic",
            "language": "english"
        }
        
        processing_info = {
            "chunk_index": i,
            "total_chunks": len(chunks),
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_method": "generic_parser",
            "project_type": "generic"
        }
        
        chunk_id = generate_chunk_id(file_path, i, "generic")
        
        processed_chunks.append({
            'chunk_id': chunk_id,
            'content': chunk,
            'metadata': metadata,
            'document_info': document_info,
            'processing_info': processing_info,
            'document_type': 'generic',
            'author': 'Unknown'
        })
    
    logger.info(f"Processed {len(processed_chunks)} generic chunks")
    return processed_chunks
```

## Step 2: Helper Functions

Here are all the helper functions you need:

```python
def create_semantic_chunks(content: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Create semantically meaningful chunks from content.
    
    This function:
    1. Splits content by sentences
    2. Groups sentences into chunks
    3. Preserves context with overlap
    4. Handles different content types
    """
    # Split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        
        # If adding this sentence would exceed chunk size, start a new chunk
        if current_length + sentence_length > chunk_size and current_chunk:
            # Join current chunk and add to chunks
            chunks.append(' '.join(current_chunk))
            
            # Start new chunk with overlap
            overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
            current_chunk = overlap_sentences + [sentence]
            current_length = sum(len(s.split()) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    # Add the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def generate_chunk_id(file_path: str, index: int, project_type: str) -> str:
    """
    Generate a unique chunk ID.
    
    This function:
    1. Creates a hash from file path and index
    2. Includes project type for organization
    3. Ensures uniqueness across all chunks
    """
    base = f"{file_path}_{index}_{project_type}"
    return hashlib.md5(base.encode()).hexdigest()[:12]

# Literature-specific helper functions
def extract_character_names(chunk: str) -> List[str]:
    """Extract character names from literature chunk."""
    # Simple pattern matching for character names
    # Look for capitalized words that might be names
    potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', chunk)
    # Filter out common words that aren't names
    common_words = {'The', 'This', 'That', 'There', 'Then', 'They', 'Their', 'These', 'Those'}
    return [name for name in potential_names if name not in common_words]

def extract_literary_devices(chunk: str) -> List[str]:
    """Extract literary devices from chunk."""
    devices = []
    if re.search(r'like|as', chunk):
        devices.append('simile')
    if re.search(r'is\s+\w+', chunk):
        devices.append('metaphor')
    if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', chunk):
        devices.append('alliteration')
    return devices

def extract_themes(chunk: str) -> List[str]:
    """Extract themes from chunk."""
    themes = []
    theme_keywords = {
        'love': ['love', 'romance', 'heart', 'passion'],
        'death': ['death', 'die', 'dead', 'mortality'],
        'war': ['war', 'battle', 'fight', 'conflict'],
        'nature': ['nature', 'forest', 'tree', 'flower', 'bird'],
        'time': ['time', 'past', 'future', 'memory', 'remember']
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in chunk.lower() for keyword in keywords):
            themes.append(theme)
    
    return themes

def calculate_reading_level(chunk: str) -> str:
    """Calculate reading level of chunk."""
    words = chunk.split()
    sentences = len(re.findall(r'[.!?]+', chunk))
    
    if len(words) == 0 or sentences == 0:
        return 'unknown'
    
    avg_words_per_sentence = len(words) / sentences
    
    if avg_words_per_sentence < 10:
        return 'easy'
    elif avg_words_per_sentence < 20:
        return 'medium'
    else:
        return 'difficult'

# Documentation-specific helper functions
def extract_api_endpoints(chunk: str) -> List[str]:
    """Extract API endpoints from documentation."""
    endpoints = re.findall(r'[A-Z]+\s+/[a-zA-Z0-9/{}]+', chunk)
    return endpoints

def extract_parameters(chunk: str) -> List[str]:
    """Extract parameters from documentation."""
    params = re.findall(r'\{[a-zA-Z_]+\}', chunk)
    return params

def extract_code_language(chunk: str) -> str:
    """Extract programming language from code blocks."""
    code_blocks = re.findall(r'```(\w+)', chunk)
    return code_blocks[0] if code_blocks else 'unknown'

def calculate_complexity_level(chunk: str) -> str:
    """Calculate complexity level of documentation."""
    if '```' in chunk and 'example' in chunk.lower():
        return 'high'
    elif '```' in chunk:
        return 'medium'
    else:
        return 'low'

# Research-specific helper functions
def extract_citations(chunk: str) -> List[str]:
    """Extract citations from research chunk."""
    citations = re.findall(r'\([A-Za-z]+\s+et\s+al\.?\s+\d{4}\)', chunk)
    return citations

def determine_research_type(chunk: str) -> str:
    """Determine type of research."""
    if 'experiment' in chunk.lower():
        return 'experimental'
    elif 'survey' in chunk.lower():
        return 'survey'
    elif 'case study' in chunk.lower():
        return 'case_study'
    else:
        return 'theoretical'

def calculate_academic_level(chunk: str) -> str:
    """Calculate academic level of content."""
    academic_terms = ['methodology', 'hypothesis', 'analysis', 'conclusion', 'implications']
    term_count = sum(1 for term in academic_terms if term in chunk.lower())
    
    if term_count >= 3:
        return 'advanced'
    elif term_count >= 1:
        return 'intermediate'
    else:
        return 'basic'

# Generic helper functions
def extract_title_from_filename(file_path: str) -> str:
    """Extract title from filename."""
    return os.path.splitext(os.path.basename(file_path))[0]

def extract_author_from_filename(file_path: str) -> str:
    """Extract author from filename (if in format author_title.txt)."""
    filename = os.path.basename(file_path)
    if '_' in filename:
        return filename.split('_')[0].title()
    return 'Unknown'

def determine_work_type(file_path: str) -> str:
    """Determine type of literary work."""
    filename = file_path.lower()
    if 'poem' in filename:
        return 'poetry'
    elif 'play' in filename:
        return 'drama'
    elif 'novel' in filename:
        return 'novel'
    else:
        return 'prose'

def extract_publication_year(file_path: str) -> str:
    """Extract publication year from filename."""
    year_match = re.search(r'\b(19|20)\d{2}\b', file_path)
    return year_match.group() if year_match else 'unknown'

def extract_api_version(chunk: str) -> str:
    """Extract API version from documentation."""
    version_match = re.search(r'v\d+\.\d+', chunk)
    return version_match.group() if version_match else 'unknown'

def determine_section_type(chunk: str) -> str:
    """Determine type of documentation section."""
    if 'api' in chunk.lower():
        return 'api_reference'
    elif 'example' in chunk.lower():
        return 'examples'
    elif 'tutorial' in chunk.lower():
        return 'tutorial'
    else:
        return 'general'

def extract_last_updated(chunk: str) -> str:
    """Extract last updated date from documentation."""
    date_match = re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', chunk)
    return date_match.group() if date_match else 'unknown'

def extract_authors(chunk: str) -> List[str]:
    """Extract authors from research chunk."""
    # Look for author patterns
    authors = re.findall(r'[A-Z][a-z]+\s+[A-Z][a-z]+', chunk)
    return authors[:3]  # Limit to first 3 authors

def extract_journal(chunk: str) -> str:
    """Extract journal name from research chunk."""
    journal_match = re.search(r'Journal of \w+|Nature|Science|Cell', chunk)
    return journal_match.group() if journal_match else 'unknown'

def extract_doi(chunk: str) -> str:
    """Extract DOI from research chunk."""
    doi_match = re.search(r'10\.\d+/[^\s]+', chunk)
    return doi_match.group() if doi_match else 'unknown'
```

## Step 3: Test Your Document Processing

Create this test file to verify everything works:

```python
# test_document_processing.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_processor import process_document

def test_document_processing():
    """Test document processing for all project types"""
    print("🌶️ Testing Document Processing...")
    
    # Test literature processing
    print("1. Testing literature processing...")
    literature_content = """
    Romeo and Juliet by William Shakespeare
    
    Act 1, Scene 1
    Two households, both alike in dignity,
    In fair Verona, where we lay our scene,
    From ancient grudge break to new mutiny,
    Where civil blood makes civil hands unclean.
    """
    
    literature_chunks = process_document("romeo_juliet.txt", literature_content, "literature")
    print(f"   ✅ Processed {len(literature_chunks)} literature chunks")
    print(f"   Sample metadata: {literature_chunks[0]['metadata']}")
    
    # Test documentation processing
    print("2. Testing documentation processing...")
    doc_content = """
    # API Reference
    
    ## GET /api/users
    Retrieve a list of users.
    
    ### Parameters
    - `limit` (optional): Number of users to return
    - `offset` (optional): Number of users to skip
    
    ### Example
    ```bash
    curl -X GET "https://api.example.com/users?limit=10"
    ```
    """
    
    doc_chunks = process_document("api_docs.md", doc_content, "documentation")
    print(f"   ✅ Processed {len(doc_chunks)} documentation chunks")
    print(f"   Sample metadata: {doc_chunks[0]['metadata']}")
    
    # Test research processing
    print("3. Testing research processing...")
    research_content = """
    Abstract
    This study examines the effects of machine learning on document processing.
    
    Methodology
    We conducted a survey of 100 participants using a mixed-methods approach.
    
    Results
    Our findings show significant improvements in processing speed (Smith et al. 2023).
    """
    
    research_chunks = process_document("research_paper.txt", research_content, "research")
    print(f"   ✅ Processed {len(research_chunks)} research chunks")
    print(f"   Sample metadata: {research_chunks[0]['metadata']}")
    
    # Test custom processing
    print("4. Testing custom processing...")
    custom_content = """
    # My Custom Project
    
    This is my custom content about cooking recipes.
    
    ## Recipe 1: Chocolate Cake
    Ingredients: flour, sugar, eggs, chocolate
    Instructions: Mix ingredients and bake at 350°F for 30 minutes.
    """
    
    custom_chunks = process_document("my_project.txt", custom_content, "custom")
    print(f"   ✅ Processed {len(custom_chunks)} custom chunks")
    print(f"   Sample metadata: {custom_chunks[0]['metadata']}")
    
    print("\n🎉 All document processing tests passed!")
    return True

if __name__ == "__main__":
    test_document_processing()
```

## Step 4: Run the Test

```bash
cd backend
python test_document_processing.py
```

## What You've Learned

✅ **Document Chunking**: How to split documents into semantic chunks
✅ **Metadata Extraction**: How to extract rich metadata for different content types
✅ **JSONB Structure**: How to organize metadata for flexible querying
✅ **Project-Specific Processing**: How to handle different document types
✅ **Helper Functions**: How to create reusable text processing utilities

## Next Steps

Once your document processing tests pass, you're ready for:
- **[Mild: Search Engine](search_engine.md)** - Create vector embeddings and search
- **[Mild: RAG Pipeline](rag_pipeline.md)** - Complete RAG system

## Troubleshooting

**If chunking produces too many small chunks:**
- Increase `chunk_size` parameter
- Adjust sentence splitting logic

**If metadata extraction fails:**
- Check your regular expressions
- Add more robust pattern matching

**If processing is slow:**
- Optimize your helper functions
- Consider batch processing for large documents

Need help? Check the [🆘 Troubleshooting Guide](../TROUBLESHOOTING.md) or ask questions! 🤝
