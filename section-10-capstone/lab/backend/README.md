# Backend - RAG System

This is the Flask backend for the RAG system capstone project.

## Architecture

The backend uses a modern functional approach with the following services:

- **database_manager.py**: PostgreSQL operations with psycopg3, context managers, and JSONB support
- **document_processor.py**: Document processing stubs for different project types
- **search_engine.py**: Vector similarity search with JSONB filtering
- **llm_integration.py**: LLM response generation
- **analytics.py**: Query analytics and system monitoring

## Key Features

- **Modern psycopg3**: Uses the latest PostgreSQL driver with context managers
- **Structured Data**: SearchResult dataclasses for type safety
- **RealDictCursor**: Named column access for better readability
- **JSONB Integration**: Rich metadata storage and querying
- **Error Handling**: Comprehensive error handling and validation

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start services:**
   ```bash
   docker-compose up -d postgres ollama
   ```

3. **Load sample data:**
   ```bash
   python load_sample_data.py --project-type literature
   ```

4. **Test the system:**
   ```bash
   python test_system.py
   ```

5. **Start the server:**
   ```bash
   python app.py
   ```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/query` - Main RAG query endpoint
- `GET /api/analytics` - System analytics
- `GET /api/documents/stats` - Document statistics
- `POST /api/documents/search` - Search documents

## Project Types

The system supports three project types:

1. **Literature**: Shakespeare, Dickens, Pratchett with character/theme analysis
2. **Documentation**: API docs with endpoint/parameter extraction
3. **Research**: Academic papers with citation analysis

## Implementation Notes

Most functions are stubs with TODO comments. Students should implement:

- Document processing logic for their chosen project type
- Advanced search and ranking algorithms
- LLM prompt engineering
- Analytics and monitoring features

## JSONB Usage

The system uses PostgreSQL JSONB for flexible metadata storage:

```sql
-- Example queries
SELECT * FROM document_chunks WHERE metadata->>'characters' ? 'Hamlet';
SELECT * FROM document_chunks WHERE document_info->>'author' = 'Shakespeare';
SELECT jsonb_array_elements(metadata->'themes') as theme FROM document_chunks;
```
