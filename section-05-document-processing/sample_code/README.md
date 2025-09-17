# Sample Code: Document Processing & PDF Chunking

This folder contains comprehensive worked examples demonstrating all the key concepts from Section 5 of the course. Each example is designed to be run independently and shows practical implementations of the concepts discussed in the slides.

## 📁 Files Overview

### 01_fixed_size_chunking.py
**Demonstrates:** Fixed-size chunking strategy from the slides

**Key Concepts:**
- Basic chunking algorithm with word count limits
- Overlap handling between chunks
- Metadata preservation with DocumentChunk class
- Quality assessment metrics
- Advantages and disadvantages of fixed-size approach

**What You'll Learn:**
- How to implement simple, predictable chunking
- When fixed-size chunking works best
- How to handle chunk boundaries and overlaps
- Quality metrics for evaluating chunking results

**Run it:**
```bash
python 01_fixed_size_chunking.py
```

---

### 02_content_aware_chunking.py
**Demonstrates:** Content-aware chunking strategy from the slides

**Key Concepts:**
- Document structure preservation
- Section title detection using regex patterns
- Paragraph-based chunking with size limits
- Semantic coherence maintenance
- Advanced metadata extraction

**What You'll Learn:**
- How to respect document structure while chunking
- Section detection techniques for better organization
- When content-aware chunking provides better results
- How to balance structure preservation with size constraints

**Run it:**
```bash
python 02_content_aware_chunking.py
```

---

### 03_metadata_preservation.py
**Demonstrates:** Comprehensive metadata preservation from the slides

**Key Concepts:**
- Rich metadata structure with DocumentChunk class
- Document type detection and classification
- Version and author extraction
- Citation generation for AI responses
- Search context metadata
- JSON serialization for storage

**What You'll Learn:**
- Why metadata is crucial for RAG systems
- How to extract meaningful document information
- How to generate citations and search context
- Best practices for metadata design

**Run it:**
```bash
python 03_metadata_preservation.py
```

---

### 04_document_extraction.py
**Demonstrates:** Multi-format document extraction from the slides

**Key Concepts:**
- PDF text extraction with PyPDF2
- HTML parsing with BeautifulSoup
- Text and Markdown file handling
- Error handling and reporting
- Text cleaning and normalization
- Batch processing capabilities

**What You'll Learn:**
- How to handle different document formats
- Text extraction best practices
- Error handling for robust processing
- Text cleaning techniques for better chunking

**Run it:**
```bash
python 04_document_extraction.py
```

---

### 05_quality_assessment.py
**Demonstrates:** Quality assessment and testing from the slides

**Key Concepts:**
- Comprehensive quality metrics
- Size distribution analysis
- Coherence and boundary quality assessment
- Metadata completeness evaluation
- Automated recommendations generation
- Quality scoring algorithms

**What You'll Learn:**
- How to measure chunking quality objectively
- Key metrics for evaluating chunk performance
- How to identify and fix chunking problems
- Quality optimization strategies

**Run it:**
```bash
python 05_quality_assessment.py
```

---

### 06_production_pipeline.py
**Demonstrates:** Production-ready pipeline architecture from the slides

**Key Concepts:**
- End-to-end document processing pipeline
- Parallel processing with ThreadPoolExecutor
- Database integration with connection pooling
- Embedding generation with Ollama
- Error handling and logging
- Performance monitoring and statistics

**What You'll Learn:**
- How to build scalable document processing systems
- Production deployment considerations
- Performance optimization techniques
- Monitoring and error handling best practices

**Run it:**
```bash
python 06_production_pipeline.py
```

## 🚀 Getting Started

### Prerequisites
Make sure you have the required dependencies installed:

```bash
pip install PyPDF2 beautifulsoup4 psycopg requests
```

### Running the Examples

1. **Start with the basics:** Run `01_fixed_size_chunking.py` to understand fundamental chunking concepts
2. **Explore advanced strategies:** Try `02_content_aware_chunking.py` for structure-aware processing
3. **Understand metadata:** Run `03_metadata_preservation.py` to see why metadata matters
4. **Handle real documents:** Use `04_document_extraction.py` for multi-format processing
5. **Ensure quality:** Run `05_quality_assessment.py` to learn quality evaluation
6. **Scale up:** Try `06_production_pipeline.py` for production-ready systems

### Customizing the Examples

Each example is designed to be easily customizable:

- **Change chunk sizes:** Modify `chunk_size` and `overlap` parameters
- **Add new document types:** Extend the extraction functions
- **Customize quality metrics:** Adjust the quality assessment criteria
- **Integrate with your data:** Replace sample data with your documents

## 🎯 Learning Path

### For Beginners
1. Start with `01_fixed_size_chunking.py` to understand basic concepts
2. Move to `02_content_aware_chunking.py` for advanced techniques
3. Use `03_metadata_preservation.py` to understand metadata importance

### For Intermediate Users
1. Run `04_document_extraction.py` to handle real documents
2. Use `05_quality_assessment.py` to evaluate your chunking
3. Try `06_production_pipeline.py` for scalable solutions

### For Advanced Users
1. Modify the examples to fit your specific use case
2. Integrate with your existing document processing pipeline
3. Extend the quality metrics for your domain
4. Optimize performance for your scale requirements

## 🔧 Integration with Lab Solutions

These sample code examples complement the lab solutions in the `solution/` folder:

- **Sample code** shows concepts in isolation with clear explanations
- **Lab solutions** provide complete, integrated implementations
- **Use sample code** to understand individual concepts
- **Use lab solutions** to see how everything works together

## 📚 Additional Resources

- **Slides:** Refer to `slides.md` for the theoretical background
- **Lab README:** Check `README.md` for hands-on exercises
- **Solution files:** Use `solution/` folder for complete implementations

## 🤝 Contributing

Feel free to extend these examples with:
- New document formats
- Additional quality metrics
- Performance optimizations
- Integration patterns
- Error handling improvements

## 📝 Notes

- All examples use sample data and can be run without external dependencies (except for the production pipeline)
- The production pipeline example requires a running PostgreSQL database with pgvector
- Examples are designed to be educational and may need modification for production use
- Error handling is simplified for clarity - production code should be more robust
