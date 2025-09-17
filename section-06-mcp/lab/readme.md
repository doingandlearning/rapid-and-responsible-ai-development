# Lab: Building an MCP Document Server
## Extending LLMs with Structured Tools

---

## **Objective**
Build a complete Model Context Protocol (MCP) server that provides document querying tools for LLMs. Transform the starting code into a production-ready MCP server with semantic search, document retrieval, and analysis capabilities.

---

## **What You'll Build**

### **Core MCP Tools:**
- `search_documents(query, filters)` - Semantic search with metadata filtering
- `get_document(id)` - Retrieve specific documents by ID or title
- `summarize_document(id)` - Generate document summaries
- `analyze_document_similarity(doc1, doc2)` - Compare document similarity

### **Advanced Features:**
- Input validation and error handling
- Connection pooling and caching
- Rate limiting and security
- Comprehensive logging and monitoring

---

## **Prerequisites**

- PostgreSQL + pgvector database running (from Section 4)
- Ollama service running with BGE-M3 model
- Python 3.13 with required dependencies
- Basic understanding of MCP concepts

---

## **Lab Structure**

### **Step 1: MCP Server Setup (15 minutes)**
- Install MCP SDK and dependencies
- Create basic server structure
- Implement database connection

### **Step 2: Document Search Tools (30 minutes)**
- Build semantic search tool
- Add metadata filtering capabilities
- Implement hybrid search functionality

### **Step 3: Document Retrieval Tools (25 minutes)**
- Create document retrieval tool
- Add document summarization
- Implement chunk-based retrieval

### **Step 4: Integration & Testing (20 minutes)**
- Test tools with sample queries
- Add error handling and validation
- Performance optimization

---

## **Expected Outcome**

Participants will have built a complete MCP server that:
- Provides standardized document querying tools for LLMs
- Integrates seamlessly with existing pgvector database
- Includes production-ready error handling and security
- Demonstrates modern AI tool integration patterns

---

## **Getting Started**

1. **Navigate to the lab directory:**
   ```bash
   cd section-06-mcp/lab
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start with the provided code:**
   ```bash
   python start/mcp_server.py
   ```

4. **Follow the step-by-step instructions in the code comments**

---

## **Success Criteria**

### **Technical Requirements:**
- ✅ All MCP tools work without errors
- ✅ Proper input validation and error handling
- ✅ Integration with pgvector database
- ✅ Search results returned in < 2 seconds

### **Code Quality:**
- ✅ Clean, readable, well-documented code
- ✅ Proper error handling and logging
- ✅ Unit tests for core functions
- ✅ Production-ready security measures

---

## **Bonus Challenges**

1. **Add Caching:** Implement Redis caching for search results
2. **Streaming Support:** Add real-time document updates
3. **Multi-Modal:** Support image and document analysis
4. **Workflow Tools:** Create document approval processes
5. **Analytics:** Add usage tracking and performance metrics

---

## **Support & Resources**

- **MCP Documentation:** [Model Context Protocol](https://modelcontextprotocol.io)
- **pgvector Docs:** [PostgreSQL Vector Extension](https://github.com/pgvector/pgvector)
- **Ollama API:** [Local LLM Server](https://ollama.ai)

**Need Help?** Ask questions, collaborate with peers, and experiment with different approaches!
