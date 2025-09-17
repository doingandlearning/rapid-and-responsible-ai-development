# Section 6.5: Model Context Protocol (MCP)
## Extending LLMs with Structured Tools

---

## **Overview**

This section introduces the Model Context Protocol (MCP), a standardized way to give LLMs access to external tools and data sources. You'll learn how to build MCP servers with document querying tools and integrate them with your existing RAG pipeline.

---

## **Learning Objectives**

By the end of this section, you will be able to:

- **Understand MCP Fundamentals**: Explain what MCP is and why it matters for AI systems
- **Build Document Tools**: Create MCP tools for document search, retrieval, and analysis
- **Implement MCP Servers**: Set up production-ready MCP servers with proper error handling
- **Integrate with RAG**: Connect MCP tools to your existing vector database and RAG pipeline
- **Apply Production Patterns**: Implement security, caching, monitoring, and performance optimization

---

## **Section Contents**

### **Slides** (`slides.md`)
- MCP fundamentals and architecture
- Document tool design patterns
- MCP server implementation
- Integration with existing systems
- Production considerations

### **Lab** (`lab/`)
- **Start**: Basic MCP server structure to build upon
- **Solution**: Complete implementation with all features
- **Sample Code**: Additional examples and advanced patterns

### **Activities** (`activities/`)
- **MCP Tool Design Workshop**: Design tools for specific domains
- Hands-on exercises for tool development

### **Resources** (`resources/`)
- **Section Overview**: Comprehensive reference material
- Best practices and common pitfalls
- Further reading and tools

---

## **Prerequisites**

- Completed Section 4 (PostgreSQL + pgvector setup)
- Completed Section 6 (RAG Pipeline Integration)
- Basic understanding of Python and APIs
- Docker and Ollama running locally

---

## **Key Technologies**

- **MCP SDK**: Model Context Protocol implementation
- **PostgreSQL + pgvector**: Vector database for document storage
- **Ollama**: Local embedding generation
- **Python 3.13**: Development language
- **Redis**: Caching and session management

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

## **What You'll Build**

### **Core MCP Tools**
- `search_documents(query, filters)` - Semantic search with metadata filtering
- `get_document(id)` - Retrieve specific documents by ID or title
- `summarize_document(id)` - Generate document summaries
- `analyze_document_similarity(doc1, doc2)` - Compare document similarity

### **Advanced Features**
- Input validation and error handling
- Connection pooling and caching
- Rate limiting and security
- Comprehensive logging and monitoring

---

## **Success Criteria**

### **Technical Requirements**
- ✅ All MCP tools work without errors
- ✅ Proper input validation and error handling
- ✅ Integration with pgvector database
- ✅ Search results returned in < 2 seconds

### **Code Quality**
- ✅ Clean, readable, well-documented code
- ✅ Proper error handling and logging
- ✅ Unit tests for core functions
- ✅ Production-ready security measures

---

## **Getting Started**

1. **Navigate to the lab directory:**
   ```bash
   cd section-06-mcp/lab
   ```

2. **Install dependencies:**
   ```bash
   pip install -r sample-code/requirements.txt
   ```

3. **Start with the provided code:**
   ```bash
   python start/mcp_server.py
   ```

4. **Follow the step-by-step instructions in the code comments**

---

## **Sample Code**

The `sample-code/` directory includes:

- **`mcp_client_example.py`**: How to use MCP tools from a client
- **`advanced_mcp_server.py`**: Production patterns with caching and security
- **`test_mcp_server.py`**: Comprehensive test suite
- **`requirements.txt`**: All necessary dependencies

---

## **Next Steps**

After completing this section:

1. **Practice**: Build MCP tools for your specific domain
2. **Integrate**: Connect MCP tools to your existing systems
3. **Deploy**: Set up production MCP servers
4. **Monitor**: Implement monitoring and alerting
5. **Scale**: Optimize for performance and reliability

---

## **Resources**

- **MCP Documentation**: [Model Context Protocol](https://modelcontextprotocol.io)
- **pgvector Docs**: [PostgreSQL Vector Extension](https://github.com/pgvector/pgvector)
- **Ollama API**: [Local LLM Server](https://ollama.ai)

**Need Help?** Check the activities, resources, and sample code for additional guidance!
