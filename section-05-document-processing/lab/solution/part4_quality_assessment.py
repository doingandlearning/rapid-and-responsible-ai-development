"""
Part 4: Quality Assessment - Solution
====================================

This solution shows how to assess and compare chunk quality
across different chunking strategies.
"""

import statistics
from collections import Counter
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

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
    section_title: str = None
    created_at: str = None

def assess_chunk_quality(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """
    Comprehensive quality assessment of document chunks.
    
    Args:
        chunks: List of DocumentChunk objects to assess
        
    Returns:
        Dictionary with quality metrics
    """
    if not chunks:
        return {"error": "No chunks to assess"}
    
    # Basic statistics
    word_counts = [c.word_count for c in chunks]
    char_counts = [c.character_count for c in chunks]
    
    # Check for broken sentences (chunks ending mid-sentence)
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text[-1] in '.!?':
            broken_sentences += 1
    
    # Check for very short chunks (likely poor splits)
    very_short = sum(1 for wc in word_counts if wc < 20)
    
    # Check for very long chunks (might need better splitting)
    very_long = sum(1 for wc in word_counts if wc > 800)
    
    # Duplicate detection (similar chunks)
    chunk_texts = [c.text.lower().strip() for c in chunks]
    duplicates = len(chunk_texts) - len(set(chunk_texts))
    
    # Section coverage (how many chunks have section titles)
    with_sections = sum(1 for c in chunks if c.section_title)
    
    # Calculate quality metrics
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
    
    # Overall quality score (0-100)
    quality_score = 100
    quality_score -= (broken_sentences / len(chunks)) * 20  # Penalty for broken sentences
    quality_score -= (very_short / len(chunks)) * 15        # Penalty for very short chunks
    quality_score -= (very_long / len(chunks)) * 10         # Penalty for very long chunks
    quality_score -= (duplicates / len(chunks)) * 25        # Penalty for duplicates
    quality_score = max(0, quality_score)
    
    quality_report['overall_quality_score'] = quality_score
    
    return quality_report

def compare_chunking_strategies(document_data: Dict[str, Any]) -> Tuple[str, List[DocumentChunk], Dict[str, Any]]:
    """
    Compare different chunking strategies on the same document.
    
    Args:
        document_data: Document to test with
        
    Returns:
        Tuple of (best_strategy_name, best_chunks, best_quality)
    """
    print(f"📊 CHUNKING STRATEGY COMPARISON")
    print(f"Document: {document_data['title']}")
    print("=" * 70)
    
    # Import chunking functions (in practice, these would be from your modules)
    from part2_fixed_chunking import create_chunks_from_document
    from part3_content_aware_chunking import create_content_aware_chunks
    
    strategies = [
        ("Fixed-Size (200w, 40w overlap)", 
         lambda d: create_chunks_from_document(d, "fixed", 200, 40)),
        ("Fixed-Size (300w, 50w overlap)", 
         lambda d: create_chunks_from_document(d, "fixed", 300, 50)),
        ("Content-Aware (300w max)", 
         lambda d: create_content_aware_chunks(d, 300)),
        ("Content-Aware (400w max)", 
         lambda d: create_content_aware_chunks(d, 400)),
    ]
    
    results = []
    
    for strategy_name, strategy_func in strategies:
        print(f"\n🔧 Testing: {strategy_name}")
        chunks = strategy_func(document_data)
        quality = assess_chunk_quality(chunks)
        
        results.append((strategy_name, chunks, quality))
        
        print(f"   Chunks created: {quality['total_chunks']}")
        print(f"   Avg words/chunk: {quality['word_count_stats']['mean']:.1f}")
        print(f"   Quality score: {quality['overall_quality_score']:.1f}/100")
        print(f"   Issues: {quality['quality_issues']['broken_sentences']} broken sentences, "
              f"{quality['quality_issues']['duplicate_chunks']} duplicates")
    
    # Find best strategy
    best_strategy = max(results, key=lambda x: x[2]['overall_quality_score'])
    print(f"\n🏆 Best Strategy: {best_strategy[0]}")
    print(f"   Quality Score: {best_strategy[2]['overall_quality_score']:.1f}/100")
    
    return best_strategy

def analyze_document_type_requirements(document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze what chunking approach works best for different document types.
    
    Args:
        document_data: Document to analyze
        
    Returns:
        Dictionary with document type analysis
    """
    title = document_data['title'].lower()
    
    # Determine document type based on title and content
    if 'policy' in title or 'policy' in document_data.get('text', '').lower():
        doc_type = 'policy'
        recommended_chunk_size = 400
        recommended_overlap = 80
    elif 'guide' in title or 'guide' in document_data.get('text', '').lower():
        doc_type = 'guide'
        recommended_chunk_size = 250
        recommended_overlap = 50
    elif 'handbook' in title or 'handbook' in document_data.get('text', '').lower():
        doc_type = 'handbook'
        recommended_chunk_size = 300
        recommended_overlap = 60
    else:
        doc_type = 'general'
        recommended_chunk_size = 300
        recommended_overlap = 50
    
    return {
        'document_type': doc_type,
        'recommended_chunk_size': recommended_chunk_size,
        'recommended_overlap': recommended_overlap,
        'reasoning': f"Document type '{doc_type}' typically works best with {recommended_chunk_size} word chunks and {recommended_overlap} word overlap"
    }

def generate_quality_report(chunks: List[DocumentChunk], strategy_name: str) -> None:
    """
    Generate a detailed quality report for chunks.
    
    Args:
        chunks: List of DocumentChunk objects
        strategy_name: Name of the chunking strategy used
    """
    quality = assess_chunk_quality(chunks)
    
    print(f"\n📋 DETAILED QUALITY REPORT")
    print(f"Strategy: {strategy_name}")
    print("=" * 50)
    
    print(f"Overall Quality Score: {quality['overall_quality_score']:.1f}/100")
    print(f"Total Chunks: {quality['total_chunks']}")
    
    print(f"\nWord Count Distribution:")
    stats = quality['word_count_stats']
    print(f"  Mean: {stats['mean']:.1f}")
    print(f"  Median: {stats['median']:.1f}")
    print(f"  Std Dev: {stats['std_dev']:.1f}")
    print(f"  Range: {stats['min']} - {stats['max']}")
    
    print(f"\nQuality Issues:")
    issues = quality['quality_issues']
    print(f"  Broken sentences: {issues['broken_sentences']}")
    print(f"  Very short chunks (<20 words): {issues['very_short_chunks']}")
    print(f"  Very long chunks (>800 words): {issues['very_long_chunks']}")
    print(f"  Duplicate chunks: {issues['duplicate_chunks']}")
    
    print(f"\nMetadata Coverage:")
    coverage = quality['metadata_coverage']
    print(f"  Chunks with sections: {coverage['chunks_with_sections']}")
    print(f"  Section coverage: {coverage['section_coverage_pct']:.1f}%")
    
    # Quality recommendations
    print(f"\n💡 Recommendations:")
    if issues['broken_sentences'] > quality['total_chunks'] * 0.1:
        print(f"  - Consider adjusting chunk boundaries to avoid breaking sentences")
    if issues['very_short_chunks'] > quality['total_chunks'] * 0.05:
        print(f"  - Increase minimum chunk size or improve splitting logic")
    if issues['very_long_chunks'] > quality['total_chunks'] * 0.05:
        print(f"  - Decrease maximum chunk size or improve content-aware splitting")
    if coverage['section_coverage_pct'] < 50:
        print(f"  - Improve section title detection for better metadata coverage")

def optimize_chunking_parameters(document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find optimal chunking parameters for a document.
    
    Args:
        document_data: Document to optimize for
        
    Returns:
        Dictionary with optimal parameters
    """
    print(f"\n🔧 OPTIMIZING CHUNKING PARAMETERS")
    print(f"Document: {document_data['title']}")
    print("=" * 50)
    
    # Test different parameter combinations
    test_params = [
        (200, 40, "Small chunks, moderate overlap"),
        (250, 50, "Medium-small chunks, good overlap"),
        (300, 50, "Medium chunks, good overlap"),
        (350, 60, "Medium-large chunks, high overlap"),
        (400, 80, "Large chunks, very high overlap"),
    ]
    
    best_score = 0
    best_params = None
    best_chunks = None
    
    for chunk_size, overlap, description in test_params:
        print(f"\nTesting: {description}")
        
        # Test fixed-size chunking
        from part2_fixed_chunking import create_chunks_from_document
        chunks = create_chunks_from_document(
            document_data, 
            chunk_strategy="fixed", 
            chunk_size=chunk_size, 
            overlap=overlap
        )
        
        quality = assess_chunk_quality(chunks)
        score = quality['overall_quality_score']
        
        print(f"  Quality score: {score:.1f}/100")
        
        if score > best_score:
            best_score = score
            best_params = (chunk_size, overlap, description)
            best_chunks = chunks
    
    print(f"\n🏆 Optimal Parameters: {best_params[2]}")
    print(f"   Chunk size: {best_params[0]} words")
    print(f"   Overlap: {best_params[1]} words")
    print(f"   Quality score: {best_score:.1f}/100")
    
    return {
        'optimal_chunk_size': best_params[0],
        'optimal_overlap': best_params[1],
        'quality_score': best_score,
        'chunks': best_chunks
    }

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Quality Assessment")
    print("=" * 50)
    
    # Create sample document
    sample_document = {
        'title': 'VPN Policy Document',
        'text': 'Sample policy text...',
        'pages': [
            (1, """University VPN Policy

The University of Edinburgh provides Virtual Private Network (VPN) services to enable secure remote access to university resources. This policy outlines the acceptable use and security requirements for VPN services.

1. Purpose and Scope
   The VPN service allows authorized users to securely access university systems and data from off-campus locations. This policy applies to all users of university VPN services.

2. Eligibility
   VPN access is available to:
   - Current students enrolled in degree programs
   - Active staff members
   - Authorized contractors with valid agreements
   - Visiting researchers with appropriate permissions"""),
            
            (2, """3. Security Requirements
   All VPN users must comply with the following security requirements:
   - Use strong authentication methods
   - Keep VPN client software updated
   - Report security incidents immediately
   - Follow data handling procedures

4. User Responsibilities
   Users of university VPN services must:
   - Use VPN only for authorized university activities
   - Maintain confidentiality of VPN credentials
   - Report suspected security incidents immediately
   - Comply with all university IT policies and procedures""")
        ]
    }
    
    # Compare strategies
    best_strategy_name, best_chunks, best_quality = compare_chunking_strategies(sample_document)
    
    # Generate detailed report
    generate_quality_report(best_chunks, best_strategy_name)
    
    # Analyze document type requirements
    doc_analysis = analyze_document_type_requirements(sample_document)
    print(f"\n📄 Document Type Analysis:")
    print(f"   Type: {doc_analysis['document_type']}")
    print(f"   Recommended chunk size: {doc_analysis['recommended_chunk_size']} words")
    print(f"   Recommended overlap: {doc_analysis['recommended_overlap']} words")
    print(f"   Reasoning: {doc_analysis['reasoning']}")
    
    # Optimize parameters
    optimization_result = optimize_chunking_parameters(sample_document)
    
    print(f"\n🎉 Quality assessment complete!")
    print(f"Next step: Implement database integration in Part 5")
