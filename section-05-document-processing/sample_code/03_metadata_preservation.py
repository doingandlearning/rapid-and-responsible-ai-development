"""
Sample Code: Metadata Preservation
=================================

This example demonstrates metadata preservation as described in the slides.
Shows how to maintain document context, page references, and section identification.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
import json

@dataclass
class DocumentChunk:
    """Enhanced DocumentChunk with comprehensive metadata."""
    id: str
    document_id: str
    document_title: str
    text: str
    page_number: int
    section_title: Optional[str]
    subsection_title: Optional[str]
    chunk_index: int
    word_count: int
    character_count: int
    document_type: str
    document_version: str
    created_at: datetime
    last_modified: Optional[datetime] = None
    source_file: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_modified is None:
            self.last_modified = self.created_at
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['created_at'] = self.created_at.isoformat()
        data['last_modified'] = self.last_modified.isoformat() if self.last_modified else None
        return data
    
    def get_citation(self) -> str:
        """Generate a citation string for this chunk."""
        citation_parts = [self.document_title]
        
        if self.section_title:
            citation_parts.append(f"Section: {self.section_title}")
        
        if self.page_number:
            citation_parts.append(f"Page {self.page_number}")
        
        if self.document_version:
            citation_parts.append(f"Version {self.document_version}")
        
        return " | ".join(citation_parts)
    
    def get_search_context(self) -> str:
        """Generate search context metadata."""
        context_parts = []
        
        if self.section_title:
            context_parts.append(f"Section: {self.section_title}")
        
        if self.subsection_title:
            context_parts.append(f"Subsection: {self.subsection_title}")
        
        if self.tags:
            context_parts.append(f"Tags: {', '.join(self.tags)}")
        
        if self.document_type:
            context_parts.append(f"Type: {self.document_type}")
        
        return " | ".join(context_parts)

def extract_document_metadata(text: str, filename: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from document text.
    
    This implements the metadata extraction logic from the slides.
    
    Args:
        text: Document text
        filename: Original filename
        
    Returns:
        Dictionary with extracted metadata
    """
    # Basic document info
    metadata = {
        'filename': filename,
        'character_count': len(text),
        'word_count': len(text.split()),
        'line_count': len(text.split('\n')),
        'document_type': 'unknown',
        'version': '1.0',
        'author': 'University of Edinburgh',
        'created_date': datetime.now().isoformat()
    }
    
    # Detect document type based on content patterns
    if 'policy' in text.lower() or 'policy' in filename.lower():
        metadata['document_type'] = 'policy'
        metadata['tags'] = ['policy', 'compliance', 'governance']
    elif 'handbook' in text.lower() or 'handbook' in filename.lower():
        metadata['document_type'] = 'handbook'
        metadata['tags'] = ['handbook', 'student', 'guide']
    elif 'manual' in text.lower() or 'manual' in filename.lower():
        metadata['document_type'] = 'manual'
        metadata['tags'] = ['manual', 'technical', 'procedures']
    elif 'research' in text.lower() or 'paper' in text.lower():
        metadata['document_type'] = 'research'
        metadata['tags'] = ['research', 'academic', 'paper']
    
    # Extract version information
    version_patterns = [
        r'version\s+(\d+\.?\d*)',
        r'v(\d+\.?\d*)',
        r'(\d{4})',  # Year as version
    ]
    
    for pattern in version_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['version'] = match.group(1)
            break
    
    # Extract author information
    author_patterns = [
        r'author[s]?:\s*([^\n]+)',
        r'by\s+([^\n]+)',
        r'prepared by\s+([^\n]+)',
    ]
    
    for pattern in author_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['author'] = match.group(1).strip()
            break
    
    # Detect sections and structure
    section_patterns = [
        r'^\d+\.\s+',  # "1. Section Title"
        r'^\d+\.\d+\s+',  # "1.1 Section Title"
        r'^#{1,6}\s+',  # Markdown headers "# Section Title"
        r'^[A-Z][A-Z\s]+$',  # ALL CAPS headers
        r'^[A-Z][a-z\s]+:$',  # "Section Title:"
    ]
    
    has_sections = any(re.search(pattern, text, re.MULTILINE) for pattern in section_patterns)
    metadata['has_sections'] = has_sections
    
    # Count sections
    section_count = 0
    for pattern in section_patterns:
        section_count += len(re.findall(pattern, text, re.MULTILINE))
    metadata['section_count'] = section_count
    
    # Detect document structure elements
    metadata['has_bullet_points'] = bool(re.search(r'^[-*•]\s+', text, re.MULTILINE))
    metadata['has_numbered_lists'] = bool(re.search(r'^\d+\.\s+', text, re.MULTILINE))
    metadata['has_tables'] = bool(re.search(r'\|.*\|', text))  # Simple table detection
    metadata['has_code_blocks'] = bool(re.search(r'```', text))
    
    # Extract title (first meaningful line)
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if (len(line) > 10 and len(line) < 100 and 
            not line.startswith(('1.', '2.', '3.', '4.', '5.')) and
            not line.startswith('#') and
            not line.startswith('-') and
            not line.startswith('*')):
            metadata['extracted_title'] = line
            break
    
    return metadata

def create_chunks_with_comprehensive_metadata(text: str,
                                            document_metadata: Dict[str, Any],
                                            page_number: int = 1,
                                            chunk_size: int = 300,
                                            overlap: int = 50) -> List[DocumentChunk]:
    """
    Create DocumentChunk objects with comprehensive metadata.
    
    This demonstrates the metadata preservation approach from the slides.
    
    Args:
        text: Input text to chunk
        document_metadata: Metadata extracted from document
        page_number: Page number this text came from
        chunk_size: Words per chunk
        overlap: Overlap between chunks
        
    Returns:
        List of DocumentChunk objects with rich metadata
    """
    chunks = []
    chunk_index = 0
    
    # Split text into chunks (using simple fixed-size for this example)
    words = text.split()
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        # Detect section title for this chunk
        section_title = detect_section_title(chunk_text)
        subsection_title = detect_subsection_title(chunk_text)
        
        # Generate tags based on content
        tags = generate_content_tags(chunk_text, document_metadata.get('tags', []))
        
        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document_metadata['filename'].lower().replace(' ', '-'),
            document_title=document_metadata.get('extracted_title', document_metadata['filename']),
            text=chunk_text,
            page_number=page_number,
            section_title=section_title,
            subsection_title=subsection_title,
            chunk_index=chunk_index,
            word_count=len(chunk_words),
            character_count=len(chunk_text),
            document_type=document_metadata.get('document_type', 'unknown'),
            document_version=document_metadata.get('version', '1.0'),
            source_file=document_metadata['filename'],
            author=document_metadata.get('author', 'University of Edinburgh'),
            tags=tags
        )
        chunks.append(chunk)
        chunk_index += 1
    
    return chunks

def detect_section_title(text: str) -> Optional[str]:
    """Detect section titles in chunk text."""
    lines = text.split('\n')
    
    for line in lines[:3]:  # Check first few lines
        line = line.strip()
        if not line:
            continue
        
        # Look for numbered sections
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return line
        
        # Look for markdown headers
        if re.match(r'^#{1,6}\s+', line):
            return line.replace('#', '').strip()
        
        # Look for all-caps titles
        if line.isupper() and 5 <= len(line) <= 50:
            return line
    
    return None

def detect_subsection_title(text: str) -> Optional[str]:
    """Detect subsection titles in chunk text."""
    lines = text.split('\n')
    
    for line in lines[:5]:  # Check first few lines
        line = line.strip()
        if not line:
            continue
        
        # Look for numbered subsections
        if re.match(r'^\d+\.\d+\s+[A-Z]', line):
            return line
        
        # Look for indented titles
        if line.startswith('  ') and line[2:3].isupper():
            return line.strip()
    
    return None

def generate_content_tags(text: str, base_tags: List[str]) -> List[str]:
    """Generate content-based tags for a chunk."""
    tags = base_tags.copy()
    
    # Add content-specific tags
    if 'password' in text.lower():
        tags.append('authentication')
    if 'policy' in text.lower():
        tags.append('governance')
    if 'library' in text.lower():
        tags.append('services')
    if 'academic' in text.lower():
        tags.append('academic')
    if 'it' in text.lower() or 'computer' in text.lower():
        tags.append('technology')
    if 'registration' in text.lower():
        tags.append('procedures')
    
    return list(set(tags))  # Remove duplicates

def demonstrate_metadata_preservation():
    """
    Demonstrate comprehensive metadata preservation.
    
    This shows the metadata importance mentioned in the slides.
    """
    print("🏷️ METADATA PRESERVATION DEMONSTRATION")
    print("=" * 50)
    
    # Sample Edinburgh IT policy with rich structure
    sample_text = """
    University of Edinburgh IT Security Policy
    Version 2.1
    Author: IT Security Team
    Last Updated: September 2024
    
    1. Introduction and Scope
    
    This policy outlines the information security requirements for all users of University of Edinburgh IT systems and networks. The policy applies to students, staff, contractors, and visitors.
    
    1.1 Policy Objectives
    
    The primary objectives of this policy are to:
    - Protect university information assets
    - Ensure compliance with data protection regulations
    - Maintain the integrity of IT systems
    - Prevent unauthorized access to sensitive data
    
    2. Password Requirements
    
    All users must comply with the following password requirements:
    - Minimum 12 characters in length
    - Must contain uppercase and lowercase letters
    - Must include numbers and special characters
    - Cannot reuse previous 12 passwords
    - Must be changed every 90 days
    
    2.1 Password Storage
    
    Passwords must be stored securely using approved password managers. Writing down passwords is strictly prohibited.
    
    3. Network Security
    
    All devices connecting to the university network must:
    - Have up-to-date antivirus software
    - Be registered with IT Services
    - Use approved security configurations
    - Comply with network access policies
    
    4. Data Protection and Privacy
    
    All university data must be handled in accordance with GDPR regulations. Personal data must be encrypted when stored or transmitted.
    
    4.1 Data Classification
    
    Data is classified into three categories:
    - Public: Can be freely shared
    - Internal: For university use only
    - Confidential: Restricted access required
    """
    
    # Extract document metadata
    print("\n📊 Extracting document metadata:")
    metadata = extract_document_metadata(sample_text, "it-security-policy-v2.1.pdf")
    
    print(f"   Document Type: {metadata['document_type']}")
    print(f"   Version: {metadata['version']}")
    print(f"   Author: {metadata['author']}")
    print(f"   Word Count: {metadata['word_count']}")
    print(f"   Sections Detected: {metadata['section_count']}")
    print(f"   Tags: {', '.join(metadata['tags'])}")
    
    # Create chunks with comprehensive metadata
    print(f"\n📝 Creating chunks with metadata:")
    chunks = create_chunks_with_comprehensive_metadata(
        sample_text,
        metadata,
        page_number=1,
        chunk_size=200,
        overlap=30
    )
    
    print(f"   Created {len(chunks)} chunks with rich metadata")
    
    # Demonstrate metadata usage
    print(f"\n🔍 Metadata Usage Examples:")
    
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n   Chunk {i}:")
        print(f"     Citation: {chunk.get_citation()}")
        print(f"     Search Context: {chunk.get_search_context()}")
        print(f"     Tags: {', '.join(chunk.tags)}")
        print(f"     Text Preview: {chunk.text[:100]}...")
    
    # Show metadata export
    print(f"\n📤 Metadata Export (JSON):")
    sample_chunk = chunks[0]
    metadata_json = json.dumps(sample_chunk.to_dict(), indent=2)
    print(metadata_json[:300] + "...")
    
    print(f"\n✅ METADATA BENEFITS:")
    print(f"   • Source attribution for AI responses")
    print(f"   • Document context and versioning")
    print(f"   • Page references and section identification")
    print(f"   • Search and filtering capabilities")
    print(f"   • Compliance and audit trails")
    print(f"   • User experience enhancement")

if __name__ == "__main__":
    demonstrate_metadata_preservation()
