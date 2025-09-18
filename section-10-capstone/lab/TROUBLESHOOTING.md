# 🆘 Troubleshooting Guide - All Spice Levels

Having trouble? Don't worry - we've got you covered! This guide helps you solve common issues regardless of your spice level.

## 🌶️ Database Issues

### Connection Problems

**Problem**: `psycopg.OperationalError: connection to server at "localhost" (127.0.0.1), port 5050 failed`

**Solutions**:
1. **Check if PostgreSQL is running**:
   ```bash
   docker ps | grep postgres
   ```
   If not running, start it:
   ```bash
   docker-compose up -d postgres
   ```

2. **Check port availability**:
   ```bash
   lsof -i :5050
   ```
   If port is busy, change it in `docker-compose.yml`

3. **Verify database credentials**:
   Check your `DB_CONFIG` matches the docker-compose settings

**Problem**: `psycopg.OperationalError: FATAL: database "pgvector" does not exist`

**Solutions**:
1. **Create the database**:
   ```sql
   CREATE DATABASE pgvector;
   ```

2. **Check if you're connecting to the right database**:
   Verify the `dbname` in your `DB_CONFIG`

### Table Creation Issues

**Problem**: `ERROR: extension "vector" does not exist`

**Solutions**:
1. **Install pgvector extension**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Check if pgvector is available**:
   ```sql
   SELECT * FROM pg_available_extensions WHERE name = 'vector';
   ```

**Problem**: `ERROR: relation "document_chunks" already exists`

**Solutions**:
1. **Drop and recreate** (if you want to start fresh):
   ```sql
   DROP TABLE IF EXISTS document_chunks CASCADE;
   ```

2. **Use IF NOT EXISTS** (recommended):
   ```sql
   CREATE TABLE IF NOT EXISTS document_chunks (...);
   ```

### Search Issues

**Problem**: No search results returned

**Solutions**:
1. **Check if you have data**:
   ```sql
   SELECT COUNT(*) FROM document_chunks;
   ```

2. **Check embedding dimensions**:
   ```sql
   SELECT array_length(embedding, 1) FROM document_chunks LIMIT 1;
   ```
   Should be 1024 for BGE-M3 model

3. **Lower similarity threshold**:
   Try `similarity_threshold=0.1` instead of `0.4`

4. **Check embedding quality**:
   Make sure your embeddings are not all zeros

**Problem**: `ERROR: operator does not exist: vector <=> vector`

**Solutions**:
1. **Check pgvector extension**:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

2. **Recreate extension**:
   ```sql
   DROP EXTENSION IF EXISTS vector;
   CREATE EXTENSION vector;
   ```

## 🌶️🌶️ Embedding Issues

### Ollama Connection Problems

**Problem**: `requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=11434)`

**Solutions**:
1. **Check if Ollama is running**:
   ```bash
   docker ps | grep ollama
   ```

2. **Start Ollama**:
   ```bash
   docker-compose up -d ollama
   ```

3. **Wait for Ollama to start**:
   ```bash
   docker logs ollama
   ```
   Wait for "Ollama is running" message

4. **Test Ollama API**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Embedding Generation Issues

**Problem**: `KeyError: 'embedding'` in response

**Solutions**:
1. **Check model name**:
   Make sure you're using `bge-m3` (not `bge-m3:latest`)

2. **Check request format**:
   ```python
   response = requests.post(
       "http://localhost:11434/api/embed",
       json={"model": "bge-m3", "prompt": "your text"}
   )
   ```

3. **Check response format**:
   ```python
   print(response.json())  # Debug the response
   ```

**Problem**: Embeddings are all zeros or very similar

**Solutions**:
1. **Check input text**:
   Make sure it's not empty or too short

2. **Check model loading**:
   ```bash
   curl -X POST http://localhost:11434/api/generate -d '{"model": "bge-m3", "prompt": "test"}'
   ```

3. **Try different text**:
   Test with longer, more diverse text

## 🌶️🌶️🌶️ Frontend Issues

### Vite Development Server

**Problem**: `Loading failed for the module with source "http://localhost:3000/src/index.css"`

**Solutions**:
1. **Clear Vite cache**:
   ```bash
   rm -rf .vite node_modules/.vite
   ```

2. **Reinstall dependencies**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Check CSS imports**:
   Make sure you're importing `index.css` not `App.css`

**Problem**: `Module not found: Can't resolve 'lucide-react'`

**Solutions**:
1. **Install missing dependencies**:
   ```bash
   npm install lucide-react
   ```

2. **Check package.json**:
   Make sure all dependencies are listed

### API Connection Issues

**Problem**: `Failed to fetch` or CORS errors

**Solutions**:
1. **Check backend is running**:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Check CORS configuration**:
   Make sure Flask has CORS enabled

3. **Check proxy configuration**:
   Verify Vite proxy settings in `vite.config.js`

**Problem**: `404 Not Found` for API endpoints

**Solutions**:
1. **Check API routes**:
   Make sure Flask routes are defined

2. **Check URL paths**:
   Verify frontend is calling correct endpoints

3. **Check Flask app**:
   Make sure Flask app is running on correct port

## 🌶️🌶️🌶️🌶️ Performance Issues

### Slow Search Queries

**Problem**: Search takes too long

**Solutions**:
1. **Add indexes**:
   ```sql
   CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
   ```

2. **Optimize similarity threshold**:
   Higher threshold = faster queries

3. **Limit results**:
   Use smaller `limit` parameter

4. **Check database performance**:
   ```sql
   EXPLAIN ANALYZE SELECT ... FROM document_chunks ...;
   ```

### Memory Issues

**Problem**: Out of memory errors

**Solutions**:
1. **Process documents in batches**:
   Don't load all documents at once

2. **Use generators**:
   Process data lazily

3. **Optimize embeddings**:
   Use smaller embedding dimensions if possible

4. **Monitor memory usage**:
   ```python
   import psutil
   print(f"Memory usage: {psutil.virtual_memory().percent}%")
   ```

## 🌶️🌶️🌶️🌶️🌶️ Advanced Issues

### Production Deployment

**Problem**: System works locally but not in production

**Solutions**:
1. **Check environment variables**:
   Make sure all config is set correctly

2. **Check database permissions**:
   Ensure production database allows your operations

3. **Check network connectivity**:
   Verify all services can communicate

4. **Check logs**:
   Look at application and database logs

### Scaling Issues

**Problem**: System slows down with more data

**Solutions**:
1. **Implement connection pooling**:
   Reuse database connections

2. **Add caching**:
   Cache frequent queries

3. **Optimize queries**:
   Use query analysis tools

4. **Consider sharding**:
   Split data across multiple databases

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Look at error messages carefully**
3. **Check logs for more details**
4. **Try the solutions above**
5. **Test with minimal examples**

### When Asking for Help

Include:
- **Your spice level** (Mild/Medium/Spicy)
- **Error message** (exact text)
- **What you were trying to do**
- **What you've already tried**
- **Your system details** (OS, Python version, etc.)

### Where to Get Help

- **Discussion forum**: Ask questions and share solutions
- **Office hours**: Get one-on-one help
- **Peer support**: Help each other out
- **Documentation**: Check official docs

## 🎉 Success Stories

### Common Solutions That Worked

**"I was getting connection errors until I realized I needed to wait for Docker to fully start"**
- Solution: Add `sleep 10` after starting Docker services

**"My search wasn't working because my embeddings were all zeros"**
- Solution: Check that Ollama is properly loaded and responding

**"The frontend couldn't connect to the backend because of CORS"**
- Solution: Add `CORS(app)` to Flask application

**"My database was slow because I forgot to create indexes"**
- Solution: Add proper indexes for vector operations

## 🚀 Pro Tips

1. **Start simple**: Get basic functionality working first
2. **Test incrementally**: Test each component separately
3. **Use logging**: Add print statements to debug
4. **Check data**: Verify your data looks correct
5. **Be patient**: Some operations take time to complete

Remember: Every problem has a solution, and every solution teaches you something new! 🤝
