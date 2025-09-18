# Capstone Lab: Advanced RAG Systems - Choose Your Adventure

**Objective**: Build a complete, production-ready RAG system showcasing all course concepts

## 🎯 Project Options

Choose one of these exciting projects that demonstrate different aspects of RAG systems:

### Option 1: Documentation Chat Assistant
**Perfect for**: Technical teams, API documentation, developer tools
- **Data Source**: API documentation, technical guides, code examples
- **Challenge**: Handle complex technical queries with code snippets
- **JSON/JSONB Usage**: Store API schemas, code examples, and metadata

### Option 2: Literary Analysis System  
**Perfect for**: Literature students, researchers, digital humanities
- **Data Source**: Complete works of Shakespeare, Dickens, Pratchett
- **Challenge**: Semantic search across literary works with character/theme analysis
- **JSON/JSONB Usage**: Store character relationships, themes, and literary metadata

### Option 3: Research Paper Interaction System
**Perfect for**: Academic researchers, students, knowledge workers
- **Data Source**: Academic papers, research abstracts, citations
- **Challenge**: Complex academic queries with citation tracking
- **JSON/JSONB Usage**: Store paper metadata, citation networks, and research relationships


### Option 4: Whatever You Fancy 🎨
**Perfect for**: Creative minds, unique use cases, personal projects
- **Data Source**: Your choice - anything that interests you!
- **Challenge**: Define your own problems and create custom solutions
- **JSON/JSONB Usage**: Store whatever metadata makes sense for your domain 
---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    REACT FRONTEND                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Chat UI   │  │  Analytics  │  │  Settings   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/JSON
┌─────────────────────▼───────────────────────────────────┐
│                  FLASK BACKEND                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   API       │  │  Document   │  │    RAG      │     │
│  │  Routes     │  │ Processing  │  │  Pipeline   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                POSTGRESQL + PGVECTOR                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Vectors    │  │   JSONB     │  │  Metadata   │     │
│  │  (1024d)    │  │  Documents  │  │   Tables    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema with JSONB

### Core Tables
```sql
-- Document chunks with rich JSONB metadata
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(50) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1024),
    
    -- JSONB for flexible metadata storage
    metadata JSONB NOT NULL DEFAULT '{}',
    document_info JSONB NOT NULL DEFAULT '{}',
    processing_info JSONB NOT NULL DEFAULT '{}',
    
    -- Extracted fields for performance
    document_type VARCHAR(50),
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query analytics with JSONB for flexible tracking
CREATE TABLE query_analytics (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_metadata JSONB DEFAULT '{}',
    response_metadata JSONB DEFAULT '{}',
    user_session JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document relationships (for literature/research projects)
CREATE TABLE document_relationships (
    id SERIAL PRIMARY KEY,
    source_doc_id VARCHAR(50),
    target_doc_id VARCHAR(50),
    relationship_type VARCHAR(50),
    relationship_data JSONB DEFAULT '{}',
    confidence_score FLOAT
);

-- Create indexes for JSONB fields
CREATE INDEX idx_chunks_metadata ON document_chunks USING gin(metadata);
CREATE INDEX idx_chunks_document_info ON document_chunks USING gin(document_info);
CREATE INDEX idx_analytics_query_metadata ON query_analytics USING gin(query_metadata);
```

### JSONB Usage Examples

**Document Metadata (Literature Project):**
```json
{
  "title": "Hamlet",
  "author": "William Shakespeare",
  "genre": "tragedy",
  "year": 1603,
  "characters": ["Hamlet", "Ophelia", "Claudius", "Gertrude"],
  "themes": ["revenge", "madness", "death", "corruption"],
  "act": 1,
  "scene": 1,
  "line_range": [1, 50],
  "literary_devices": ["metaphor", "soliloquy"],
  "difficulty_level": "advanced"
}
```

**API Documentation Metadata:**
```json
{
  "endpoint": "/api/users",
  "method": "GET",
  "parameters": [
    {"name": "limit", "type": "integer", "required": false},
    {"name": "offset", "type": "integer", "required": false}
  ],
  "response_schema": {
    "type": "object",
    "properties": {
      "users": {"type": "array"},
      "total": {"type": "integer"}
    }
  },
  "examples": [
    {"input": "?limit=10", "output": "{\"users\": [...]}"}
  ],
  "version": "v1.2.0"
}
```

**Research Paper Metadata:**
```json
{
  "title": "Attention Is All You Need",
  "authors": ["Vaswani", "Shazeer", "Parmar"],
  "year": 2017,
  "venue": "NIPS",
  "citations": 50000,
  "keywords": ["transformer", "attention", "neural networks"],
  "abstract": "We propose a new simple network architecture...",
  "sections": ["introduction", "method", "experiments", "conclusion"],
  "figures": 3,
  "tables": 2,
  "references": 60
}
```

---

## 🎯 Implementation Tasks

### Phase 1: Foundation

#### Task 1.1: Choose Your Project
- [ ] Select project type (literature/documentation/research)
- [ ] Download sample data for your chosen project
- [ ] Set up development environment

#### Task 1.2: Database Setup
- [ ] Create PostgreSQL schema with JSONB support
- [ ] Implement DatabaseManager class
- [ ] Test JSONB queries and indexing

#### Task 1.3: Document Processing
- [ ] Implement DocumentProcessor for your project type
- [ ] Create chunking strategy appropriate for your content
- [ ] Design JSONB metadata schema
- [ ] Process sample documents and store in database

### Phase 2: Core Development

#### Task 2.1: Search Engine 
- [ ] Implement vector similarity search
- [ ] Add JSONB filtering capabilities
- [ ] Create hybrid search (vector + text)
- [ ] Add result ranking and scoring

#### Task 2.2: LLM Integration
- [ ] Set up LLM service (OpenAI/Ollama)
- [ ] Create context assembly from search results
- [ ] Implement response generation with source citation
- [ ] Add confidence scoring

#### Task 2.3: API Development
- [ ] Create Flask API endpoints
- [ ] Implement query processing pipeline
- [ ] Add error handling and validation
- [ ] Create analytics endpoints

### Phase 3: Frontend & Integration 

#### Task 3.1: React Frontend
- [ ] Create chat interface component
- [ ] Implement message display with sources
- [ ] Add analytics dashboard
- [ ] Style with modern CSS framework

#### Task 3.2: System Integration
- [ ] Connect frontend to backend API
- [ ] Test end-to-end functionality
- [ ] Add loading states and error handling
- [ ] Implement real-time updates

### Phase 4: Advanced Features

#### Task 4.1: Analytics & Monitoring
- [ ] Implement query analytics
- [ ] Add performance monitoring
- [ ] Create usage dashboards
- [ ] Set up logging

#### Task 4.2: Optimization & Testing
- [ ] Optimize database queries
- [ ] Add comprehensive testing
- [ ] Performance tuning
- [ ] Documentation

---

## 🏆 Success Criteria

### Technical Requirements
- [ ] **Working RAG System**: Complete query-to-response pipeline
- [ ] **JSONB Integration**: Rich metadata storage and querying
- [ ] **Vector Search**: Semantic similarity search with pgvector
- [ ] **Source Citation**: All responses include verifiable sources
- [ ] **Performance**: < 3 second response times
- [ ] **Frontend**: Clean, responsive React interface

### Project-Specific Requirements

#### Literature Project
- [ ] Character relationship analysis
- [ ] Theme extraction and search
- [ ] Literary device identification
- [ ] Cross-work comparisons

#### Documentation Project
- [ ] API endpoint discovery
- [ ] Code example extraction
- [ ] Schema-based filtering
- [ ] Version management

#### Research Project
- [ ] Citation network analysis
- [ ] Methodology extraction
- [ ] Abstract summarization
- [ ] Reference tracking

### Quality Standards
- [ ] **Code Quality**: Clean, documented, testable code
- [ ] **Error Handling**: Graceful failure modes
- [ ] **User Experience**: Intuitive, responsive interface
- [ ] **Documentation**: Clear setup and usage instructions

---

## 🚀 Getting Started

1. **Choose your project type** from the options
2. **Set up the development environment** using the provided scripts
3. **Start with the database schema** and JSONB design
4. **Implement document processing** for your chosen content type
5. **Build the search and RAG pipeline** with vector similarity
6. **Create the React frontend** with a modern chat interface
7. **Add analytics and monitoring** for system insights
8. **Test, optimize, and present** your completed system

Remember: This capstone showcases everything you've learned about RAG systems, vector databases, document processing, and modern web development. Make it something you're proud to demonstrate!

---

## 📚 Additional Resources

- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [React Documentation](https://reactjs.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

Good luck building something amazing! 🎉
