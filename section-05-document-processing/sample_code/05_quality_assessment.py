"""
Sample Code: Quality Assessment & Testing
=========================================

This example demonstrates quality assessment and testing as described in the slides.
Shows how to evaluate chunking quality and optimize performance.
"""

import statistics
import re
from typing import List, Dict, Any, Tuple
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
    section_title: str = None
    chunk_index: int = 0
    word_count: int = 0
    character_count: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.word_count == 0:
            self.word_count = len(self.text.split())
        if self.character_count == 0:
            self.character_count = len(self.text)

class ChunkQualityAnalyzer:
    """
    Analyzes the quality of document chunks.
    
    This implements the quality assessment metrics from the slides.
    """
    
    def __init__(self):
        self.optimal_chunk_size_range = (200, 500)  # Optimal word count range
        self.min_chunk_size = 50
        self.max_chunk_size = 1000
    
    def analyze_chunk_quality(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Comprehensive quality analysis of chunks.
        
        This implements the quality assessment function from the slides.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Dictionary with quality metrics
        """
        if not chunks:
            return {"error": "No chunks to analyze"}
        
        # Basic statistics
        word_counts = [c.word_count for c in chunks]
        char_counts = [c.character_count for c in chunks]
        
        # Size analysis
        size_metrics = self._analyze_size_distribution(word_counts)
        
        # Coherence analysis
        coherence_metrics = self._analyze_coherence(chunks)
        
        # Boundary quality analysis
        boundary_metrics = self._analyze_boundary_quality(chunks)
        
        # Metadata completeness
        metadata_metrics = self._analyze_metadata_completeness(chunks)
        
        # Overall quality score
        quality_score = self._calculate_overall_quality_score(
            size_metrics, coherence_metrics, boundary_metrics, metadata_metrics
        )
        
        return {
            "total_chunks": len(chunks),
            "quality_score": quality_score,
            "size_distribution": size_metrics,
            "coherence": coherence_metrics,
            "boundary_quality": boundary_metrics,
            "metadata_completeness": metadata_metrics,
            "recommendations": self._generate_recommendations(
                size_metrics, coherence_metrics, boundary_metrics, metadata_metrics
            )
        }
    
    def _analyze_size_distribution(self, word_counts: List[int]) -> Dict[str, Any]:
        """Analyze chunk size distribution."""
        if not word_counts:
            return {}
        
        avg_words = statistics.mean(word_counts)
        median_words = statistics.median(word_counts)
        std_words = statistics.stdev(word_counts) if len(word_counts) > 1 else 0
        
        # Count chunks in different size categories
        very_short = sum(1 for wc in word_counts if wc < self.min_chunk_size)
        short = sum(1 for wc in word_counts if self.min_chunk_size <= wc < self.optimal_chunk_size_range[0])
        optimal = sum(1 for wc in word_counts if self.optimal_chunk_size_range[0] <= wc <= self.optimal_chunk_size_range[1])
        long = sum(1 for wc in word_counts if self.optimal_chunk_size_range[1] < wc <= self.max_chunk_size)
        very_long = sum(1 for wc in word_counts if wc > self.max_chunk_size)
        
        # Calculate size consistency score
        size_consistency = 100 - (std_words / avg_words * 100) if avg_words > 0 else 0
        
        return {
            "avg_words": round(avg_words, 1),
            "median_words": round(median_words, 1),
            "std_deviation": round(std_words, 1),
            "min_words": min(word_counts),
            "max_words": max(word_counts),
            "very_short_chunks": very_short,
            "short_chunks": short,
            "optimal_chunks": optimal,
            "long_chunks": long,
            "very_long_chunks": very_long,
            "size_consistency_score": max(0, round(size_consistency, 1))
        }
    
    def _analyze_coherence(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Analyze semantic coherence of chunks."""
        broken_sentences = 0
        incomplete_paragraphs = 0
        topic_consistency_score = 0
        
        for chunk in chunks:
            text = chunk.text.strip()
            
            # Check for broken sentences (chunks ending mid-sentence)
            if text and not text.endswith(('.', '!', '?', ':', ';')):
                broken_sentences += 1
            
            # Check for incomplete paragraphs (chunks starting mid-paragraph)
            if text and not text[0].isupper():
                incomplete_paragraphs += 1
            
            # Simple topic consistency check (look for topic words)
            topic_words = self._extract_topic_words(text)
            if len(topic_words) > 0:
                topic_consistency_score += 1
        
        total_chunks = len(chunks)
        coherence_score = 100
        coherence_score -= (broken_sentences / total_chunks) * 40  # Penalty for broken sentences
        coherence_score -= (incomplete_paragraphs / total_chunks) * 30  # Penalty for incomplete paragraphs
        coherence_score += (topic_consistency_score / total_chunks) * 20  # Bonus for topic consistency
        
        return {
            "broken_sentences": broken_sentences,
            "incomplete_paragraphs": incomplete_paragraphs,
            "topic_consistency_chunks": topic_consistency_score,
            "coherence_score": max(0, round(coherence_score, 1))
        }
    
    def _analyze_boundary_quality(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Analyze quality of chunk boundaries."""
        good_boundaries = 0
        section_boundaries = 0
        paragraph_boundaries = 0
        
        for chunk in chunks:
            text = chunk.text.strip()
            
            # Check if chunk starts with section header
            if self._starts_with_section_header(text):
                section_boundaries += 1
                good_boundaries += 1
            
            # Check if chunk starts with paragraph
            elif self._starts_with_paragraph(text):
                paragraph_boundaries += 1
                good_boundaries += 1
            
            # Check if chunk ends properly
            if self._ends_properly(text):
                good_boundaries += 1
        
        total_chunks = len(chunks)
        boundary_score = (good_boundaries / (total_chunks * 2)) * 100  # 2 checks per chunk
        
        return {
            "good_boundaries": good_boundaries,
            "section_boundaries": section_boundaries,
            "paragraph_boundaries": paragraph_boundaries,
            "boundary_score": round(boundary_score, 1)
        }
    
    def _analyze_metadata_completeness(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Analyze completeness of chunk metadata."""
        total_chunks = len(chunks)
        
        chunks_with_sections = sum(1 for c in chunks if c.section_title)
        chunks_with_pages = sum(1 for c in chunks if c.page_number)
        chunks_with_word_counts = sum(1 for c in chunks if c.word_count > 0)
        
        section_coverage = (chunks_with_sections / total_chunks) * 100
        page_coverage = (chunks_with_pages / total_chunks) * 100
        word_count_coverage = (chunks_with_word_counts / total_chunks) * 100
        
        overall_metadata_score = (section_coverage + page_coverage + word_count_coverage) / 3
        
        return {
            "section_coverage": round(section_coverage, 1),
            "page_coverage": round(page_coverage, 1),
            "word_count_coverage": round(word_count_coverage, 1),
            "overall_metadata_score": round(overall_metadata_score, 1)
        }
    
    def _calculate_overall_quality_score(self, size_metrics: Dict, coherence_metrics: Dict, 
                                       boundary_metrics: Dict, metadata_metrics: Dict) -> float:
        """Calculate overall quality score."""
        # Weighted combination of different quality aspects
        size_score = size_metrics.get("size_consistency_score", 0)
        coherence_score = coherence_metrics.get("coherence_score", 0)
        boundary_score = boundary_metrics.get("boundary_score", 0)
        metadata_score = metadata_metrics.get("overall_metadata_score", 0)
        
        # Weighted average
        overall_score = (
            size_score * 0.25 +
            coherence_score * 0.35 +
            boundary_score * 0.25 +
            metadata_score * 0.15
        )
        
        return round(overall_score, 1)
    
    def _generate_recommendations(self, size_metrics: Dict, coherence_metrics: Dict,
                                boundary_metrics: Dict, metadata_metrics: Dict) -> List[str]:
        """Generate recommendations for improving chunk quality."""
        recommendations = []
        
        # Size recommendations
        if size_metrics.get("very_short_chunks", 0) > 0:
            recommendations.append("Consider increasing chunk size to avoid very short chunks")
        
        if size_metrics.get("very_long_chunks", 0) > 0:
            recommendations.append("Consider decreasing chunk size to avoid very long chunks")
        
        if size_metrics.get("size_consistency_score", 0) < 70:
            recommendations.append("Chunk sizes are inconsistent - consider using fixed-size chunking")
        
        # Coherence recommendations
        if coherence_metrics.get("broken_sentences", 0) > 0:
            recommendations.append("Some chunks break sentences - consider sentence-aware chunking")
        
        if coherence_metrics.get("coherence_score", 0) < 70:
            recommendations.append("Chunk coherence is low - consider content-aware chunking")
        
        # Boundary recommendations
        if boundary_metrics.get("boundary_score", 0) < 60:
            recommendations.append("Chunk boundaries need improvement - consider structure-aware chunking")
        
        # Metadata recommendations
        if metadata_metrics.get("section_coverage", 0) < 50:
            recommendations.append("Many chunks lack section information - improve section detection")
        
        if metadata_metrics.get("overall_metadata_score", 0) < 80:
            recommendations.append("Metadata completeness could be improved")
        
        return recommendations
    
    def _extract_topic_words(self, text: str) -> List[str]:
        """Extract topic-related words from text."""
        # Simple topic word extraction
        topic_words = []
        words = text.lower().split()
        
        # Look for common topic indicators
        topic_indicators = ['policy', 'procedure', 'requirement', 'guideline', 'regulation',
                          'academic', 'student', 'university', 'library', 'it', 'security']
        
        for word in words:
            if any(indicator in word for indicator in topic_indicators):
                topic_words.append(word)
        
        return topic_words
    
    def _starts_with_section_header(self, text: str) -> bool:
        """Check if text starts with a section header."""
        lines = text.split('\n')
        if not lines:
            return False
        
        first_line = lines[0].strip()
        return (re.match(r'^\d+\.\s+', first_line) or
                re.match(r'^#{1,6}\s+', first_line) or
                first_line.isupper())
    
    def _starts_with_paragraph(self, text: str) -> bool:
        """Check if text starts with a proper paragraph."""
        return text and text[0].isupper()
    
    def _ends_properly(self, text: str) -> bool:
        """Check if text ends properly."""
        return text and text.endswith(('.', '!', '?', ':', ';'))

def create_sample_chunks() -> List[DocumentChunk]:
    """Create sample chunks for testing."""
    chunks = []
    
    # Good quality chunk
    chunks.append(DocumentChunk(
        id="1",
        document_id="test-doc",
        document_title="Test Document",
        text="1. Password Requirements\n\nAll passwords must be at least 12 characters long and contain a combination of uppercase letters, lowercase letters, numbers, and special characters. This ensures strong security for university accounts.",
        page_number=1,
        section_title="Password Requirements",
        chunk_index=0,
        word_count=35
    ))
    
    # Chunk with broken sentence
    chunks.append(DocumentChunk(
        id="2",
        document_id="test-doc",
        document_title="Test Document",
        text="Passwords must be changed every 90 days and cannot be reused for the previous 12 password changes. Users who fail to",
        page_number=1,
        section_title="Password Requirements",
        chunk_index=1,
        word_count=25
    ))
    
    # Very short chunk
    chunks.append(DocumentChunk(
        id="3",
        document_id="test-doc",
        document_title="Test Document",
        text="comply will face disciplinary action.",
        page_number=1,
        section_title="Password Requirements",
        chunk_index=2,
        word_count=5
    ))
    
    # Good quality chunk
    chunks.append(DocumentChunk(
        id="4",
        document_id="test-doc",
        document_title="Test Document",
        text="2. Network Security\n\nAll devices connecting to the university network must have up-to-date antivirus software installed and enabled. Personal devices must be registered with IT Services before accessing the network.",
        page_number=1,
        section_title="Network Security",
        chunk_index=3,
        word_count=32
    ))
    
    return chunks

def demonstrate_quality_assessment():
    """
    Demonstrate quality assessment and testing.
    
    This shows the quality assessment approach from the slides.
    """
    print("🔍 QUALITY ASSESSMENT DEMONSTRATION")
    print("=" * 50)
    
    # Create sample chunks
    print("\n📝 Creating sample chunks for analysis...")
    chunks = create_sample_chunks()
    
    print(f"   Created {len(chunks)} sample chunks")
    
    # Analyze quality
    print("\n🔍 Analyzing chunk quality...")
    analyzer = ChunkQualityAnalyzer()
    quality_report = analyzer.analyze_chunk_quality(chunks)
    
    # Display results
    print(f"\n📊 QUALITY ANALYSIS RESULTS:")
    print(f"   Overall Quality Score: {quality_report['quality_score']}/100")
    print(f"   Total Chunks: {quality_report['total_chunks']}")
    
    # Size distribution
    size_metrics = quality_report['size_distribution']
    print(f"\n📏 SIZE DISTRIBUTION:")
    print(f"   Average words per chunk: {size_metrics['avg_words']}")
    print(f"   Size consistency score: {size_metrics['size_consistency_score']}/100")
    print(f"   Very short chunks: {size_metrics['very_short_chunks']}")
    print(f"   Optimal chunks: {size_metrics['optimal_chunks']}")
    print(f"   Very long chunks: {size_metrics['very_long_chunks']}")
    
    # Coherence analysis
    coherence_metrics = quality_report['coherence']
    print(f"\n🧠 COHERENCE ANALYSIS:")
    print(f"   Coherence score: {coherence_metrics['coherence_score']}/100")
    print(f"   Broken sentences: {coherence_metrics['broken_sentences']}")
    print(f"   Incomplete paragraphs: {coherence_metrics['incomplete_paragraphs']}")
    print(f"   Topic consistency chunks: {coherence_metrics['topic_consistency_chunks']}")
    
    # Boundary quality
    boundary_metrics = quality_report['boundary_quality']
    print(f"\n🔗 BOUNDARY QUALITY:")
    print(f"   Boundary score: {boundary_metrics['boundary_score']}/100")
    print(f"   Good boundaries: {boundary_metrics['good_boundaries']}")
    print(f"   Section boundaries: {boundary_metrics['section_boundaries']}")
    print(f"   Paragraph boundaries: {boundary_metrics['paragraph_boundaries']}")
    
    # Metadata completeness
    metadata_metrics = quality_report['metadata_completeness']
    print(f"\n🏷️ METADATA COMPLETENESS:")
    print(f"   Overall metadata score: {metadata_metrics['overall_metadata_score']}/100")
    print(f"   Section coverage: {metadata_metrics['section_coverage']}%")
    print(f"   Page coverage: {metadata_metrics['page_coverage']}%")
    print(f"   Word count coverage: {metadata_metrics['word_count_coverage']}%")
    
    # Recommendations
    recommendations = quality_report['recommendations']
    print(f"\n💡 RECOMMENDATIONS:")
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("   No specific recommendations - quality looks good!")
    
    print(f"\n✅ QUALITY ASSESSMENT BENEFITS:")
    print(f"   • Identifies chunking problems early")
    print(f"   • Provides actionable recommendations")
    print(f"   • Enables optimization of chunking strategies")
    print(f"   • Ensures consistent quality across documents")
    print(f"   • Supports continuous improvement")

if __name__ == "__main__":
    demonstrate_quality_assessment()
