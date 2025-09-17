"""
Sample Code: Document Extraction
===============================

This example demonstrates text extraction from various document formats
as described in the slides. Shows PDF, HTML, and text file processing.
"""

import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExtractedDocument:
    """Represents an extracted document with metadata."""
    filename: str
    file_type: str
    title: str
    text: str
    pages: List[tuple]  # (page_number, text)
    metadata: Dict[str, Any]
    extraction_errors: List[str]
    created_at: datetime

def extract_text_from_pdf(file_path: str) -> tuple[str, List[str]]:
    """
    Extract text from PDF files.
    
    This implements PDF text extraction as shown in the slides.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Tuple of (full_text, list_of_errors)
    """
    try:
        import PyPDF2
        
        text = ""
        errors = []
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += page_text + "\n"
                    else:
                        errors.append(f"Page {page_num}: No text extracted")
                except Exception as e:
                    errors.append(f"Page {page_num}: {str(e)}")
        
        return text, errors
        
    except ImportError:
        return "", ["PyPDF2 not installed. Install with: pip install PyPDF2"]
    except Exception as e:
        return "", [f"PDF extraction failed: {str(e)}"]

def extract_text_from_html(file_path: str) -> tuple[str, List[str]]:
    """
    Extract text from HTML files.
    
    This implements HTML text extraction as shown in the slides.
    
    Args:
        file_path: Path to HTML file
        
    Returns:
        Tuple of (full_text, list_of_errors)
    """
    try:
        from bs4 import BeautifulSoup
        
        text = ""
        errors = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Handle ordered lists to preserve section numbers
            for ol in soup.find_all('ol'):
                counter = 1
                if ol.get('start'):
                    counter = int(ol.get('start'))
                for li in ol.find_all('li'):
                    li_text = li.get_text().strip()
                    if li_text and not li_text.startswith(str(counter) + '.'):
                        li.string = f"{counter}. {li_text}"
                    counter += 1
            
            # Handle headings to preserve structure
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading_text = heading.get_text().strip()
                if heading_text and not heading_text.startswith('#'):
                    level = int(heading.name[1])
                    heading.string = f"{'#' * level} {heading_text}"
            
            text = soup.get_text()
        
        return text, errors
        
    except ImportError:
        return "", ["BeautifulSoup not installed. Install with: pip install beautifulsoup4"]
    except Exception as e:
        return "", [f"HTML extraction failed: {str(e)}"]

def extract_text_from_txt(file_path: str) -> tuple[str, List[str]]:
    """
    Extract text from plain text files.
    
    Args:
        file_path: Path to text file
        
    Returns:
        Tuple of (full_text, list_of_errors)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text, []
    except Exception as e:
        return "", [f"Text extraction failed: {str(e)}"]

def extract_text_from_markdown(file_path: str) -> tuple[str, List[str]]:
    """
    Extract text from Markdown files.
    
    Args:
        file_path: Path to Markdown file
        
    Returns:
        Tuple of (full_text, list_of_errors)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text, []
    except Exception as e:
        return "", [f"Markdown extraction failed: {str(e)}"]

def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    This implements text cleaning as shown in the slides.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text ready for chunking
    """
    # Remove page markers (if any)
    text = re.sub(r'--- Page \d+ ---', '', text)
    
    # Normalize multiple spaces to single spaces (but preserve line breaks)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Normalize multiple line breaks to single line breaks
    text = re.sub(r'\n+', '\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_document_title(text: str, filename: str) -> str:
    """
    Extract document title from text or filename.
    
    Args:
        text: Document text
        filename: Original filename
        
    Returns:
        Extracted or derived title
    """
    # Try to extract title from text
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if (len(line) > 10 and len(line) < 100 and 
            not line.startswith(('1.', '2.', '3.', '4.', '5.')) and
            not line.startswith('#') and
            not line.startswith('-') and
            not line.startswith('*')):
            return line
    
    # Fallback to filename
    return Path(filename).stem.replace('_', ' ').replace('-', ' ').title()

def split_text_into_pages(text: str, words_per_page: int = 500) -> List[tuple]:
    """
    Split text into pages for processing.
    
    Args:
        text: Full document text
        words_per_page: Approximate words per page
        
    Returns:
        List of (page_number, page_text) tuples
    """
    words = text.split()
    pages = []
    
    for i in range(0, len(words), words_per_page):
        page_words = words[i:i + words_per_page]
        page_text = " ".join(page_words)
        page_number = (i // words_per_page) + 1
        pages.append((page_number, page_text))
    
    return pages

def process_document(file_path: str) -> ExtractedDocument:
    """
    Process a single document and extract text.
    
    This implements the document processing pipeline from the slides.
    
    Args:
        file_path: Path to document file
        
    Returns:
        ExtractedDocument object
    """
    file_path = Path(file_path)
    file_type = file_path.suffix.lower()
    
    # Extract text based on file type
    if file_type == '.pdf':
        text, errors = extract_text_from_pdf(str(file_path))
    elif file_type in ['.html', '.htm']:
        text, errors = extract_text_from_html(str(file_path))
    elif file_type == '.txt':
        text, errors = extract_text_from_txt(str(file_path))
    elif file_type in ['.md', '.markdown']:
        text, errors = extract_text_from_markdown(str(file_path))
    else:
        text, errors = "", [f"Unsupported file type: {file_type}"]
    
    # Clean the extracted text
    if text:
        text = clean_extracted_text(text)
    
    # Extract title
    title = extract_document_title(text, file_path.name)
    
    # Split into pages
    pages = split_text_into_pages(text) if text else []
    
    # Create metadata
    metadata = {
        'file_size': file_path.stat().st_size if file_path.exists() else 0,
        'file_type': file_type,
        'word_count': len(text.split()) if text else 0,
        'character_count': len(text) if text else 0,
        'page_count': len(pages),
        'extraction_success': len(errors) == 0
    }
    
    return ExtractedDocument(
        filename=file_path.name,
        file_type=file_type,
        title=title,
        text=text,
        pages=pages,
        metadata=metadata,
        extraction_errors=errors,
        created_at=datetime.now()
    )

def process_directory(directory_path: str) -> List[ExtractedDocument]:
    """
    Process all supported documents in a directory.
    
    This demonstrates batch document processing from the slides.
    
    Args:
        directory_path: Path to directory containing documents
        
    Returns:
        List of ExtractedDocument objects
    """
    directory = Path(directory_path)
    documents = []
    
    # Supported file extensions
    supported_extensions = {'.pdf', '.html', '.htm', '.txt', '.md', '.markdown'}
    
    print(f"🔍 Scanning directory: {directory}")
    
    # Find all supported files
    files = [f for f in directory.iterdir() 
             if f.is_file() and f.suffix.lower() in supported_extensions]
    
    print(f"📁 Found {len(files)} files to process")
    
    # Process each file
    for file_path in files:
        print(f"📖 Processing: {file_path.name}")
        document = process_document(str(file_path))
        documents.append(document)
        
        if document.extraction_errors:
            print(f"   ⚠️  Errors: {len(document.extraction_errors)}")
        else:
            print(f"   ✅ Success: {document.metadata['word_count']} words, {document.metadata['page_count']} pages")
    
    return documents

def demonstrate_document_extraction():
    """
    Demonstrate document extraction with sample files.
    
    This shows the document processing capabilities from the slides.
    """
    print("📄 DOCUMENT EXTRACTION DEMONSTRATION")
    print("=" * 50)
    
    # Create sample files for demonstration
    sample_dir = Path("sample_documents")
    sample_dir.mkdir(exist_ok=True)
    
    # Create sample text file
    sample_text_file = sample_dir / "it_policy.txt"
    sample_text_file.write_text("""
    University of Edinburgh IT Policy
    
    1. Password Requirements
    All passwords must be at least 12 characters long and contain a combination of uppercase letters, lowercase letters, numbers, and special characters.
    
    2. Network Security
    All devices connecting to the university network must have up-to-date antivirus software installed and enabled.
    
    3. Data Protection
    All university data must be handled in accordance with GDPR regulations.
    """)
    
    # Create sample HTML file
    sample_html_file = sample_dir / "student_guide.html"
    sample_html_file.write_text("""
    <!DOCTYPE html>
    <html>
    <head><title>Student Guide</title></head>
    <body>
        <h1>Edinburgh Student Guide 2024</h1>
        <h2>Academic Calendar</h2>
        <p>The academic year runs from September to June.</p>
        <h2>Library Services</h2>
        <p>The university library provides access to millions of resources.</p>
        <ol>
            <li>24/7 access to main library</li>
            <li>Study spaces and group rooms</li>
            <li>Research support and training</li>
        </ol>
    </body>
    </html>
    """)
    
    # Create sample Markdown file
    sample_md_file = sample_dir / "research_guide.md"
    sample_md_file.write_text("""
    # Research Guide
    
    ## Getting Started
    
    This guide will help you navigate the research process at Edinburgh.
    
    ### Finding Resources
    
    1. Use the library catalog
    2. Search academic databases
    3. Consult with librarians
    
    ## Writing Your Paper
    
    Follow these steps for academic writing:
    - Choose your topic carefully
    - Conduct thorough research
    - Organize your arguments
    - Cite sources properly
    """)
    
    print(f"\n📊 Processing sample documents:")
    
    # Process the directory
    documents = process_directory(str(sample_dir))
    
    # Display results
    print(f"\n📋 EXTRACTION RESULTS:")
    print(f"   Total documents processed: {len(documents)}")
    
    successful = sum(1 for doc in documents if doc.metadata['extraction_success'])
    print(f"   Successfully extracted: {successful}")
    print(f"   Failed extractions: {len(documents) - successful}")
    
    # Show details for each document
    for i, doc in enumerate(documents, 1):
        print(f"\n   Document {i}: {doc.filename}")
        print(f"     Type: {doc.file_type}")
        print(f"     Title: {doc.title}")
        print(f"     Words: {doc.metadata['word_count']}")
        print(f"     Pages: {doc.metadata['page_count']}")
        print(f"     Success: {doc.metadata['extraction_success']}")
        
        if doc.extraction_errors:
            print(f"     Errors: {', '.join(doc.extraction_errors)}")
        
        # Show sample text
        if doc.text:
            print(f"     Sample text: {doc.text[:100]}...")
    
    print(f"\n✅ EXTRACTION CAPABILITIES:")
    print(f"   • PDF text extraction with PyPDF2")
    print(f"   • HTML parsing with BeautifulSoup")
    print(f"   • Plain text and Markdown support")
    print(f"   • Error handling and reporting")
    print(f"   • Text cleaning and normalization")
    print(f"   • Metadata extraction")
    print(f"   • Batch processing")
    
    # Clean up sample files
    import shutil
    shutil.rmtree(sample_dir)
    print(f"\n🧹 Cleaned up sample files")

if __name__ == "__main__":
    demonstrate_document_extraction()
