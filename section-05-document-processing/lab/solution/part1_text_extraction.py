"""
Part 1: Document Text Extraction - Solution
==========================================

This solution shows how to extract text from different document formats
and prepare it for chunking.
"""

import os
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path

def get_input_files(input_dir: str = "input") -> List[str]:
    """
    Get all supported files from the input directory.
    
    Args:
        input_dir: Path to input directory
        
    Returns:
        List of file paths
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"⚠️  Input directory '{input_dir}' not found. Creating it...")
        input_path.mkdir(exist_ok=True)
        return []
    
    supported_extensions = {'.txt', '.pdf', '.html', '.htm', '.md'}
    files = []
    
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files.append(str(file_path))
    
    return sorted(files)

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text content
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    try:
        if extension == '.txt' or extension == '.md':
            return extract_text_from_txt(file_path)
        elif extension == '.pdf':
            return extract_text_from_pdf(file_path)
        elif extension in ['.html', '.htm']:
            return extract_text_from_html(file_path)
        else:
            print(f"⚠️  Unsupported file type: {extension}")
            return ""
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {e}")
        return ""

def extract_text_from_txt(file_path: Path) -> str:
    """Extract text from plain text files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF files."""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n\n--- Page {page_num} ---\n\n"
                    text += page_text
        return text
    except ImportError:
        print("⚠️  PyPDF2 not installed. Install with: pip install PyPDF2")
        return f"[PDF content from {file_path.name} - PyPDF2 required]"
    except Exception as e:
        print(f"❌ Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_html(file_path: Path) -> str:
    """Extract text from HTML files."""
    try:
        from bs4 import BeautifulSoup
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
                    # Add the number back to the list item
                    li_text = li.get_text().strip()
                    if li_text and not li_text.startswith(str(counter) + '.'):
                        li.string = f"{counter}. {li_text}"
                    counter += 1
            
            # Handle headings to preserve structure
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading_text = heading.get_text().strip()
                if heading_text and not heading_text.startswith('#'):
                    # Add markdown-style heading markers
                    level = int(heading.name[1])
                    heading.string = f"{'#' * level} {heading_text}"
            
            return soup.get_text()
    except ImportError:
        print("⚠️  BeautifulSoup not installed. Install with: pip install beautifulsoup4")
        return f"[HTML content from {file_path.name} - BeautifulSoup required]"
    except Exception as e:
        print(f"❌ Error reading HTML {file_path}: {e}")
        return ""

def split_text_into_pages(text: str, max_chars_per_page: int = 2000) -> List[Tuple[int, str]]:
    """
    Split text into pages for processing.
    
    Args:
        text: Full text content
        max_chars_per_page: Maximum characters per page
        
    Returns:
        List of (page_number, page_text) tuples
    """
    if len(text) <= max_chars_per_page:
        return [(1, text)]
    
    pages = []
    lines = text.split('\n')
    current_page = ""
    page_num = 1
    
    for line in lines:
        if len(current_page) + len(line) + 1 > max_chars_per_page and current_page:
            pages.append((page_num, current_page.strip()))
            current_page = line
            page_num += 1
        else:
            if current_page:
                current_page += "\n" + line
            else:
                current_page = line
    
    # Add the last page
    if current_page.strip():
        pages.append((page_num, current_page.strip()))
    
    return pages

def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
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

def extract_document_metadata(text: str, filename: str) -> Dict[str, Any]:
    """
    Extract metadata from document text.
    
    Args:
        text: Document text
        filename: Original filename
        
    Returns:
        Dictionary with extracted metadata
    """
    # More comprehensive section detection patterns
    section_patterns = [
        r'^\d+\.\s+',  # "1. Section Title"
        r'^\d+\.\d+\s+',  # "1.1 Section Title"
        r'^#{1,6}\s+',  # Markdown headers "# Section Title"
        r'^[A-Z][A-Z\s]+$',  # ALL CAPS headers
        r'^[A-Z][a-z\s]+:$',  # "Section Title:"
        r'^[A-Z][a-z\s]+$',  # Title case headers
        r'^\d+\.\s+[A-Z]',  # "1. Section Title" (more flexible)
        r'^[A-Z][a-z\s]+$',  # Title case headers (standalone)
    ]
    
    has_sections = any(re.search(pattern, text, re.MULTILINE) for pattern in section_patterns)
    
    # Count actual sections found
    section_count = 0
    for pattern in section_patterns:
        section_count += len(re.findall(pattern, text, re.MULTILINE))
    
    metadata = {
        'filename': filename,
        'character_count': len(text),
        'word_count': len(text.split()),
        'line_count': len(text.split('\n')),
        'has_sections': has_sections,
        'section_count': section_count,
        'has_bullet_points': bool(re.search(r'^[-*•]\s+', text, re.MULTILINE)),
        'has_numbered_lists': bool(re.search(r'^\d+\.\s+', text, re.MULTILINE)),
        'estimated_pages': max(1, len(text) // 2000)  # Rough estimate
    }
    
    # Try to extract title (first line that looks like a title)
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if (len(line) > 10 and len(line) < 100 and 
            not line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) and
            not line.startswith('#') and
            not line.startswith('-') and
            not line.startswith('*') and
            not line.startswith('IT Support') and  # Skip common prefixes
            not line.startswith('Student') and
            not line.startswith('University')):
            metadata['extracted_title'] = line
            break
    
    return metadata

def process_document_file(file_path: str) -> Dict[str, Any]:
    """
    Complete document processing pipeline.
    
    Args:
        file_path: Path to document file
        
    Returns:
        Dictionary with processed document data
    """
    file_path = Path(file_path)
    print(f"📖 Processing: {file_path.name}")
    
    # Extract text
    raw_text = extract_text_from_file(str(file_path))
    if not raw_text:
        return {'error': 'Failed to extract text'}
    
    # Clean text
    cleaned_text = clean_extracted_text(raw_text)
    
    # Extract metadata
    metadata = extract_document_metadata(cleaned_text, file_path.name)
    
    # Split into pages
    pages = split_text_into_pages(cleaned_text)
    
    return {
        'filename': file_path.name,
        'filepath': str(file_path),
        'title': metadata.get('extracted_title', file_path.stem),
        'text': cleaned_text,
        'pages': pages,
        'metadata': metadata
    }

def process_all_input_files(input_dir: str = "../input") -> Dict[str, Dict[str, Any]]:
    """
    Process all files in the input directory.
    
    Args:
        input_dir: Path to input directory
        
    Returns:
        Dictionary mapping filenames to processed document data
    """
    print(f"🔍 Scanning input directory: {input_dir}")
    
    files = get_input_files(input_dir)
    if not files:
        print(f"⚠️  No supported files found in {input_dir}")
        print(f"   Supported formats: .txt, .pdf, .html, .htm, .md")
        return {}
    
    print(f"📁 Found {len(files)} files to process")
    
    processed_documents = {}
    
    for file_path in files:
        result = process_document_file(file_path)
        if 'error' not in result:
            processed_documents[result['filename']] = result
        else:
            print(f"❌ Failed to process {file_path}: {result['error']}")
    
    return processed_documents

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Document Text Extraction")
    print("=" * 50)
    
    # Process all files in input directory
    processed_documents = process_all_input_files("input")
    
    if not processed_documents:
        print("\n💡 To test this solution:")
        print("   1. Add some .txt, .pdf, or .html files to the 'input' folder")
        print("   2. Run this script again")
        print("   3. The script will automatically process all supported files")
        exit(0)
    
    print(f"\n📊 Processing Summary:")
    print(f"   Files processed: {len(processed_documents)}")
    
    for filename, doc_data in processed_documents.items():
        print(f"\n📄 {filename}")
        print(f"   Title: {doc_data['title']}")
        print(f"   Pages: {len(doc_data['pages'])}")
        print(f"   Words: {doc_data['metadata']['word_count']}")
        print(f"   Characters: {doc_data['metadata']['character_count']}")
        print(f"   Has sections: {doc_data['metadata']['has_sections']}")
        print(f"   File type: {Path(doc_data['filepath']).suffix}")
        
        # Show sample text
        if doc_data['pages']:
            sample_text = doc_data['pages'][0][1][:100]
            print(f"   Sample: {sample_text}...")
    
    print(f"\n🎉 Text extraction complete!")
    print(f"Next step: Implement chunking strategies in Part 2")
    print(f"\n💡 Add more files to the 'input' folder to test with different document types!")
