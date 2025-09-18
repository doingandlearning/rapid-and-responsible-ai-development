# Web Interface Guide

## Quick Start

### Start the Web Interface
```bash
# Easiest way - standalone script
python start_web_interface.py

# Or use command line arguments
python lab6_rag_pipeline.py --web

# Custom port
python lab6_rag_pipeline.py --web --port 8080
```

### Access the Interface
1. Open your web browser
2. Go to: `http://localhost:5100`
3. Start asking questions!

## Features

### What You'll See
- **Clean interface** with Edinburgh University branding
- **Chat-style Q&A** for testing the RAG system
- **Real-time responses** with source citations
- **Confidence indicators** showing answer quality
- **Response time display** for performance monitoring

### Example Questions to Try
- "How do I reset my password?"
- "I can't connect to WiFi on campus"
- "What are the VPN requirements?"
- "How do I configure student email?"
- "What's the two-factor authentication process?"

## Troubleshooting

### Web Interface Won't Start

**Error: "Port already in use"**
```bash
# Try a different port
python lab6_rag_pipeline.py --web --port 8080

# Or find what's using port 5100
lsof -i :5100
```

**Error: "System validation failed"**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check if Section 5 data is available
python -c "
import psycopg
conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL')
print(f'Available chunks: {cur.fetchone()[0]}')
"
```

**Error: "Module not found"**
```bash
# Install required dependencies
pip install psycopg requests flask

# Make sure you're in the right directory
cd section-06-rag-pipeline/solution
```

### Web Interface Starts But No Responses

**Check API Key**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key
python test_direct_api.py
```

**Check Database Connection**
```bash
# Test database connection
python -c "
import psycopg
try:
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
    print('✅ Database connected')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

**Check Ollama Service**
```bash
# Test embedding service
curl http://localhost:11434/api/embed -X POST -H "Content-Type: application/json" -d '{"model":"bge-m3","input":"test"}'
```

### Performance Issues

**Slow Responses**
- Check if PostgreSQL has proper indexes
- Verify Ollama is running and responsive
- Check network connectivity to OpenAI API

**Memory Issues**
- Reduce the number of chunks retrieved
- Lower the similarity threshold
- Use a smaller model for testing

## Advanced Usage

### Custom Configuration
```python
# Modify the web interface
from lab6_rag_pipeline import create_rag_web_interface

app = create_rag_web_interface()

# Add custom routes
@app.route('/custom')
def custom_endpoint():
    return "Custom endpoint"

# Start with custom settings
app.run(host='0.0.0.0', port=5100, debug=True)
```

### Production Deployment
```bash
# Disable debug mode
python lab6_rag_pipeline.py --web --no-debug

# Use a production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5100 lab6_rag_pipeline:create_rag_web_interface()
```

### API Testing
```bash
# Test the API directly
curl -X POST http://localhost:5100/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'

# Health check
curl http://localhost:5100/health
```

## Security Notes

- The web interface is designed for **testing and demonstration**
- For production use, add proper authentication and security measures
- Consider rate limiting for API endpoints
- Validate and sanitize all user inputs
- Use HTTPS in production environments

## Support

If you encounter issues:
1. Check the troubleshooting steps above
2. Verify all services are running (PostgreSQL, Ollama)
3. Check the console output for error messages
4. Ensure all dependencies are installed
5. Verify your API key is valid and has credits
