# Lab: Document Processing for RAG Systems

## Learning Objectives

- ✅ Understand why document chunking is essential for RAG systems
- ✅ Implement different chunking strategies (fixed-size, semantic, structure-aware)
- ✅ Extract and process text from various document formats
- ✅ Optimize chunk size and overlap for embedding quality
- ✅ Handle metadata preservation and document structure
- ✅ Build a production-ready document processing pipeline

---

## Scenario

You're working with Edinburgh University's IT Services team to process their documentation for an AI-powered support system. You have three types of documents to process:

1. **IT Support Handbook** - Structured technical procedures
2. **Student WiFi Guide** - Step-by-step instructions with troubleshooting  
3. **VPN Policy Document** - Formal policy with legal language

Your goal is to chunk these documents effectively so students and staff can get accurate, attributable answers to their IT questions.

---

## Lab Structure

This lab is broken into 6 parts, each building on the previous:

### **Part 1: Document Text Extraction** (15 minutes)
**Goal:** Extract text from different document formats

**What you need to do:**
- Use files from the `input/` folder or add your own
- Implement text extraction for PDF, HTML, and plain text
- Handle different page structures and formatting
- Clean and normalize extracted text

**Key considerations:**
- What libraries will you use for PDF extraction?
- How will you handle empty or malformed pages?
- What text cleaning is necessary?

**Success criteria:**
- Successfully extract text from files in the input folder
- Text is clean and properly formatted
- Page numbers and structure are preserved

---

### **Part 2: Fixed-Size Chunking** (15 minutes)
**Goal:** Implement basic chunking with word count limits

**What you need to do:**
- Create a function that splits text into fixed-size chunks
- Implement overlap between chunks to preserve context
- Handle edge cases (very short/long text)
- Track chunk metadata (position, word count, etc.)

**Key considerations:**
- What's a good chunk size for your documents?
- How much overlap prevents context loss?
- How will you handle chunks that are too short?

**Success criteria:**
- Chunks are consistently sized with proper overlap
- No text is lost or duplicated
- Metadata is preserved for each chunk

---

### **Part 3: Content-Aware Chunking** (15 minutes)
**Goal:** Implement smarter chunking that respects document structure

**What you need to do:**
- Split text by paragraphs and sections, not just word count
- Detect section headers and titles
- Respect natural content boundaries
- Fall back to fixed-size chunking for very long paragraphs

**Key considerations:**
- How can you identify section boundaries?
- What patterns indicate important structural elements?
- How do you handle mixed content types?

**Success criteria:**
- Chunks respect document structure
- Section titles are detected and preserved
- Chunks are semantically coherent

---

### **Part 4: Quality Assessment** (10 minutes)
**Goal:** Evaluate and compare different chunking strategies

**What you need to do:**
- Create metrics to assess chunk quality
- Compare different chunking strategies
- Identify optimal parameters for each document type
- Detect and fix common chunking problems

**Key considerations:**
- What makes a "good" chunk?
- How do you measure chunk quality objectively?
- What are the trade-offs between different strategies?

**Success criteria:**
- Quality metrics are implemented and working
- Best strategy is identified for each document type
- Chunking parameters are optimized

---

### **Part 5: Database Integration** (15 minutes)
**Goal:** Store chunks with embeddings in a vector database

**What you need to do:**
- Design a database schema for document chunks
- Generate embeddings for each chunk
- Store chunks with metadata in PostgreSQL + pgvector
- Handle batch processing and error recovery

**Key considerations:**
- What metadata should be stored with each chunk?
- How will you handle embedding generation failures?
- What indexes are needed for efficient retrieval?

**Success criteria:**
- Chunks are stored with correct embeddings
- Database schema supports efficient queries
- Error handling prevents data loss

---

### **Part 6: Verification & Testing** (10 minutes)
**Goal:** Verify the complete pipeline works correctly

**What you need to do:**
- Query the database to verify chunk storage
- Test embedding generation and storage
- Verify metadata preservation
- Run end-to-end tests

**Key considerations:**
- How do you verify embeddings are correct?
- What queries will test your system thoroughly?
- How do you measure overall pipeline success?

**Success criteria:**
- All chunks are stored with correct embeddings
- Metadata is preserved and queryable
- Pipeline handles errors gracefully

---

## Getting Started

1. **Set up your environment:**
   ```bash
   cd environment && docker compose up -d
   source .venv/bin/activate
   ```

2. **Check the input folder:**
   ```bash
   ls input/
   ```
   The `input/` folder contains sample documents. You can add your own `.txt`, `.pdf`, or `.html` files here.

3. **Test the setup:**
   ```bash
   python test_input_processing.py
   ```
   This will verify that all parts work with the input files.

4. **Create your lab file:**
   ```bash
   touch lab5_document_processing.py
   ```

5. **Start with Part 1** and work through each section

6. **Use the solution files** for hints and guidance when needed

---

## Success Criteria

You've completed this lab when you have:

- [ ] Successfully extracted text from all three document types
- [ ] Implemented both fixed-size and content-aware chunking
- [ ] Quality assessment shows 80%+ quality score for best strategy
- [ ] Stored chunks with embeddings in database
- [ ] Database verification shows chunks stored with correct embeddings
- [ ] Metadata is preserved (page numbers, sections, etc.)

---

## Reflection & Discussion

**With your partner, discuss:**

1. **Strategy Trade-offs**: Which chunking strategy worked best for which document type? Why?

2. **Quality vs. Quantity**: How did chunk size affect both quality scores and search relevance?

3. **Metadata Value**: How important was preserving page numbers and section titles for user experience?

4. **Real-World Scaling**: How would you optimize this for processing 1,000 Edinburgh documents?

---

## Need Help?

- **Hints and guidance:** Check the `solution/` folder for step-by-step guidance
- **Code examples:** Each part has a solution file with implementation examples
- **Troubleshooting:** Common issues and solutions are documented
- **Best practices:** Learn from production-ready patterns

**Remember:** Focus on understanding the concepts and trade-offs. There are many valid approaches!
