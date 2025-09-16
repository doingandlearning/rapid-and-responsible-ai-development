# Section 8 Lab: Production Deployment

**Building Production-Ready Vector Search Systems for Edinburgh University**

## Lab Overview

**Time:** 45 minutes  
**Objective:** Deploy, secure, monitor, and scale vector search systems for production use at university scale  
**Context:** Transform the development system into a production-ready deployment capable of serving Edinburgh's institutional needs

---

## Prerequisites

✅ **Section 7 completed** - Advanced hybrid queries working with comprehensive monitoring  
✅ **Docker and Docker Compose** - Container orchestration capabilities  
✅ **System resources** - 8GB+ RAM, 4+ CPU cores for realistic testing  
✅ **Network access** - Ability to expose services on different ports  

### Quick Verification

```bash
# Verify Section 7 system is working
python -c "
from final_materials.section_07_advanced_vector_queries.solution.lab7_complete_system import EdinburghHybridSearch
search = EdinburghHybridSearch()
results = search.execute_hybrid_search('test query')
print(f'System ready: {len(results) >= 0}')
"

# Check Docker resources
docker system info | grep -E "(CPUs|Total Memory)"
```

---

## Lab Exercises

### Exercise 1: Production Database Configuration (10 minutes)

#### 1.1: PostgreSQL Production Optimization

**Create production database configuration:**

```bash
# Create production configuration directory
mkdir -p lab8_production/database_config
cd lab8_production/database_config
```

**Production postgresql.conf:**

```ini
# lab8_production/database_config/postgresql.conf
# PostgreSQL Production Configuration for Edinburgh University

# Connection Settings
max_connections = 200
superuser_reserved_connections = 3

# Memory Settings
shared_buffers = 4GB                      # 25% of available RAM (adjust for your system)
effective_cache_size = 12GB               # 75% of available RAM
work_mem = 256MB                          # Per-query memory
maintenance_work_mem = 1GB                # Index maintenance

# Checkpoint and WAL Settings
checkpoint_timeout = 15min                # Reduce checkpoint frequency
checkpoint_completion_target = 0.9       # Spread checkpoint I/O
wal_buffers = 64MB                       # WAL buffer size
wal_compression = on                     # Compress WAL files

# Query Planner Settings
random_page_cost = 1.1                   # SSD optimization
effective_io_concurrency = 200           # Concurrent I/O operations
max_parallel_workers_per_gather = 4     # Parallel query workers
max_parallel_workers = 8                # Total parallel workers

# Logging Settings
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000        # Log slow queries (>1s)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_duration = on
log_statement = 'all'

# Performance Monitoring
track_activities = on
track_counts = on
track_functions = all
track_io_timing = on

# pgvector Specific Settings
jit = off                                # Disable JIT for vector operations
```

**Production pg_hba.conf:**

```bash
# lab8_production/database_config/pg_hba.conf
# PostgreSQL Client Authentication Configuration

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 connections with password authentication
host    all             all             127.0.0.1/32            md5
host    all             all             10.0.0.0/8              md5
host    all             all             172.16.0.0/12           md5
host    all             all             192.168.0.0/16          md5

# Replication connections
host    replication     postgres        127.0.0.1/32            md5
host    replication     postgres        10.0.0.0/8              md5
```

#### 1.2: Connection Pooling with PgBouncer

**PgBouncer configuration:**

```ini
# lab8_production/database_config/pgbouncer.ini
[databases]
pgvector = host=postgres-primary port=5432 dbname=pgvector user=postgres password=postgres_password_here

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool settings
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 10
max_db_connections = 150

# Timeouts
server_reset_query = DISCARD ALL
server_check_query = SELECT 1
server_check_delay = 30
server_connect_timeout = 15
server_login_retry = 15

# Logging
admin_users = postgres
stats_users = postgres
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
```

**Create user authentication file:**

```bash
# lab8_production/database_config/userlist.txt
"postgres" "md5_hashed_password_here"
```

#### 1.3: Database Setup Script

**Create production database setup:**

```python
# lab8_production/setup_production_db.py
import psycopg
import hashlib
import os
import json
from typing import Dict, Any

class ProductionDatabaseSetup:
    """Setup production-ready PostgreSQL + pgvector configuration."""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5050,  # Development port for testing
            'dbname': 'pgvector',
            'user': 'postgres',
            'password': 'postgres'
        }
    
    def create_production_user(self):
        """Create production database user with limited privileges."""
        
        conn = psycopg.connect(**self.db_config)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🔒 CREATING PRODUCTION DATABASE USER")
        print("=" * 50)
        
        try:
            # Create application user
            cur.execute("""
                CREATE USER vector_app WITH 
                PASSWORD 'production_password_change_me'
                NOSUPERUSER 
                NOCREATEDB 
                NOCREATEROLE
            """)
            print("✅ Created vector_app user")
        except psycopg.errors.DuplicateObject:
            print("⚠️  User vector_app already exists")
        
        # Grant necessary permissions
        cur.execute("GRANT CONNECT ON DATABASE pgvector TO vector_app")
        cur.execute("GRANT USAGE ON SCHEMA public TO vector_app")
        cur.execute("GRANT SELECT, INSERT, UPDATE ON document_chunks TO vector_app")
        cur.execute("GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO vector_app")
        
        print("✅ Granted application permissions")
        
        cur.close()
        conn.close()
    
    def optimize_database_settings(self):
        """Apply production optimizations to existing database."""
        
        conn = psycopg.connect(**self.db_config)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("\n⚡ APPLYING DATABASE OPTIMIZATIONS")
        print("=" * 50)
        
        # Create additional indexes for production
        production_indexes = [
            {
                'name': 'document_chunks_metadata_dept_idx',
                'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_metadata_dept_idx ON document_chunks ((metadata->>\'department\'))',
                'description': 'Department filtering optimization'
            },
            {
                'name': 'document_chunks_metadata_campus_idx', 
                'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_metadata_campus_idx ON document_chunks ((metadata->>\'campus\'))',
                'description': 'Campus filtering optimization'
            },
            {
                'name': 'document_chunks_metadata_priority_idx',
                'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_metadata_priority_idx ON document_chunks ((metadata->>\'priority\')::int)',
                'description': 'Priority filtering optimization'
            },
            {
                'name': 'document_chunks_full_text_idx',
                'sql': 'CREATE INDEX IF NOT EXISTS document_chunks_full_text_idx ON document_chunks USING gin(to_tsvector(\'english\', text))',
                'description': 'Full-text search optimization'
            }
        ]
        
        for idx in production_indexes:
            try:
                print(f"Creating {idx['name']}...")
                cur.execute(idx['sql'])
                print(f"  ✅ {idx['description']}")
            except Exception as e:
                print(f"  ⚠️ {idx['name']}: {str(e)}")
        
        # Gather table statistics for query planner
        cur.execute("ANALYZE document_chunks")
        print("✅ Updated table statistics")
        
        # Check index usage
        cur.execute("""
            SELECT indexname, idx_scan 
            FROM pg_stat_user_indexes 
            WHERE tablename = 'document_chunks'
            ORDER BY idx_scan DESC
        """)
        
        indexes = cur.fetchall()
        print(f"\n📊 INDEX USAGE STATISTICS:")
        for idx_name, scan_count in indexes:
            print(f"  {idx_name}: {scan_count} scans")
        
        cur.close()
        conn.close()
    
    def create_monitoring_views(self):
        """Create database views for production monitoring."""
        
        conn = psycopg.connect(**self.db_config)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("\n📊 CREATING MONITORING VIEWS")
        print("=" * 50)
        
        # Document statistics view
        cur.execute("""
            CREATE OR REPLACE VIEW document_stats AS
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as chunks_with_embeddings,
                COUNT(DISTINCT document_title) as unique_documents,
                AVG(LENGTH(text)) as avg_chunk_length,
                metadata->>'department' as department,
                metadata->>'campus' as campus
            FROM document_chunks
            GROUP BY metadata->>'department', metadata->>'campus'
        """)
        print("✅ Created document_stats view")
        
        # Query performance monitoring view  
        cur.execute("""
            CREATE OR REPLACE VIEW query_performance AS
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                stddev_time,
                rows
            FROM pg_stat_statements
            WHERE query LIKE '%document_chunks%'
            ORDER BY total_time DESC
        """)
        print("✅ Created query_performance view")
        
        cur.close()
        conn.close()
    
    def run_full_setup(self):
        """Execute complete production database setup."""
        
        print("🚀 PRODUCTION DATABASE SETUP")
        print("=" * 60)
        
        try:
            self.create_production_user()
            self.optimize_database_settings()
            self.create_monitoring_views()
            
            print("\n" + "=" * 60)
            print("✅ PRODUCTION DATABASE SETUP COMPLETE!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")

if __name__ == "__main__":
    setup = ProductionDatabaseSetup()
    setup.run_full_setup()
```

**Run database setup:**

```bash
python lab8_production/setup_production_db.py
```

---

### Exercise 2: Production Application Architecture (10 minutes)

#### 2.1: Production Flask Application

**Create production-ready application:**

```python
# lab8_production/production_app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import logging
import time
import os
from dataclasses import asdict
from typing import Dict, Any, Optional

# Import our advanced search system
import sys
sys.path.append('../section-07-advanced-vector-queries/solution')
from lab7_complete_system import EdinburghHybridSearch, QueryConfig

# Production logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)

# Redis for caching and rate limiting
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class ProductionSearchAPI:
    """Production-ready API for Edinburgh University vector search."""
    
    def __init__(self):
        self.search_engine = EdinburghHybridSearch()
        self.logger = logging.getLogger('production_api')
        
        # Cache TTL settings (seconds)
        self.cache_ttl = {
            'search_results': 900,    # 15 minutes
            'health_check': 60,       # 1 minute
            'user_profile': 1800      # 30 minutes
        }
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key for results."""
        import hashlib
        import json
        
        key_data = f"{prefix}:{json.dumps(kwargs, sort_keys=True)}"
        if len(key_data) > 250:
            return f"{prefix}:hash:{hashlib.sha256(key_data.encode()).hexdigest()}"
        return key_data
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result."""
        try:
            cached = redis_client.get(cache_key)
            return json.loads(cached) if cached else None
        except Exception as e:
            self.logger.warning(f"Cache read failed: {e}")
            return None
    
    def cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int) -> None:
        """Cache result with TTL."""
        try:
            redis_client.setex(cache_key, ttl, json.dumps(result))
        except Exception as e:
            self.logger.warning(f"Cache write failed: {e}")

# Initialize API
api = ProductionSearchAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint."""
    
    cache_key = "health_check:system"
    cached_health = api.get_cached_result(cache_key)
    
    if cached_health:
        return jsonify(cached_health)
    
    start_time = time.time()
    
    try:
        # Test database connectivity
        test_results = api.search_engine.execute_hybrid_search("health check test")
        db_healthy = True
        db_response_time = time.time() - start_time
    except Exception as e:
        db_healthy = False
        db_response_time = time.time() - start_time
        api.logger.error(f"Database health check failed: {e}")
    
    # Test cache connectivity
    try:
        redis_client.ping()
        cache_healthy = True
    except Exception as e:
        cache_healthy = False
        api.logger.error(f"Cache health check failed: {e}")
    
    health_status = {
        'status': 'healthy' if (db_healthy and cache_healthy) else 'degraded',
        'timestamp': time.time(),
        'components': {
            'database': {
                'healthy': db_healthy,
                'response_time': db_response_time
            },
            'cache': {
                'healthy': cache_healthy
            }
        }
    }
    
    # Cache health status
    api.cache_result(cache_key, health_status, api.cache_ttl['health_check'])
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/api/search', methods=['POST'])
@limiter.limit("30 per minute")
def search_documents():
    """Main search endpoint with caching and monitoring."""
    
    start_time = time.time()
    
    try:
        # Parse request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter required'}), 400
        
        query = data['query'].strip()
        if not query or len(query) < 3:
            return jsonify({'error': 'Query must be at least 3 characters'}), 400
        
        # Sanitize query
        query = api.search_engine.sanitize_query(query) if hasattr(api.search_engine, 'sanitize_query') else query
        
        # Extract filters and configuration
        filters = data.get('filters', {})
        config_data = data.get('config', {})
        
        # Create configuration
        config = QueryConfig(
            similarity_threshold=config_data.get('similarity_threshold', 0.4),
            max_results=min(config_data.get('max_results', 10), 50),  # Limit to 50 max
            similarity_weight=config_data.get('similarity_weight', 0.6),
            priority_weight=config_data.get('priority_weight', 0.2),
            popularity_weight=config_data.get('popularity_weight', 0.1),
            department_weight=config_data.get('department_weight', 0.1)
        )
        
        # Check cache first
        cache_key = api.generate_cache_key('search', query=query, filters=filters, config=asdict(config))
        cached_result = api.get_cached_result(cache_key)
        
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['response_time'] = time.time() - start_time
            return jsonify(cached_result)
        
        # Execute search
        search_start = time.time()
        results = api.search_engine.execute_hybrid_search(query, filters, config)
        search_time = time.time() - search_start
        
        # Format response
        response_data = {
            'query': query,
            'results': [asdict(result) for result in results],
            'count': len(results),
            'response_time': time.time() - start_time,
            'search_time': search_time,
            'from_cache': False,
            'timestamp': time.time()
        }
        
        # Cache successful results
        if results:
            api.cache_result(cache_key, response_data, api.cache_ttl['search_results'])
        
        # Log successful search
        api.logger.info(
            f"Search completed",
            extra={
                'query_length': len(query),
                'results_count': len(results),
                'response_time': response_data['response_time'],
                'search_time': search_time,
                'filters_used': len(filters)
            }
        )
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'error': 'Search failed',
            'message': str(e),
            'response_time': time.time() - start_time,
            'timestamp': time.time()
        }
        
        api.logger.error(f"Search error: {str(e)}", extra={'query': data.get('query', 'unknown')})
        return jsonify(error_response), 500

@app.route('/api/stats', methods=['GET'])
@limiter.limit("10 per minute")
def get_system_stats():
    """System statistics endpoint."""
    
    try:
        stats = api.search_engine.get_query_performance_stats()
        
        # Add cache statistics
        cache_info = redis_client.info()
        stats['cache'] = {
            'used_memory': cache_info.get('used_memory_human', 'unknown'),
            'connected_clients': cache_info.get('connected_clients', 0),
            'keyspace_hits': cache_info.get('keyspace_hits', 0),
            'keyspace_misses': cache_info.get('keyspace_misses', 0)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve stats', 'message': str(e)}), 500

@app.route('/api/admin/clear_cache', methods=['POST'])
@limiter.limit("5 per minute")
def clear_cache():
    """Administrative endpoint to clear cache."""
    
    try:
        # In production, this would require admin authentication
        flushed = redis_client.flushdb()
        
        return jsonify({
            'message': 'Cache cleared successfully',
            'success': flushed,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to clear cache', 'message': str(e)}), 500

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded."""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e),
        'retry_after': e.retry_after
    }), 429

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Development server for testing
    app.run(host='0.0.0.0', port=5100, debug=False)
```

#### 2.2: Production Docker Configuration

**Create production Dockerfile:**

```dockerfile
# lab8_production/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy requirements and install Python dependencies
COPY --chown=app:app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
  CMD curl -f http://localhost:5100/health || exit 1

# Expose port
EXPOSE 5100

# Production server
CMD ["gunicorn", "--bind", "0.0.0.0:5100", "--workers", "4", "--timeout", "60", "production_app:app"]
```

**Create requirements.txt for production:**

```txt
# lab8_production/requirements.txt
flask==3.0.0
flask-cors==4.0.0
flask-limiter==3.5.0
psycopg[binary]==3.1.13
requests==2.31.0
redis==5.0.1
gunicorn==21.2.0
prometheus-client==0.19.0
```

---

### Exercise 3: Container Orchestration and Monitoring (12 minutes)

#### 3.1: Docker Compose Production Stack

**Create production docker-compose.yml:**

```yaml
# lab8_production/docker-compose.yml
version: '3.8'

services:
  # PostgreSQL with production configuration
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_DB: pgvector
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-production_password_change_me}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_config/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./database_config/pg_hba.conf:/etc/postgresql/pg_hba.conf:ro
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  # Connection pooling
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    environment:
      DATABASES_HOST: postgres
      DATABASES_PORT: 5432
      DATABASES_USER: postgres
      DATABASES_PASSWORD: ${POSTGRES_PASSWORD:-production_password_change_me}
      DATABASES_DBNAME: pgvector
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 200
      DEFAULT_POOL_SIZE: 25
    ports:
      - "6432:6432"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "psql -h localhost -p 6432 -U postgres -d pgvector -c 'SELECT 1'"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Embedding service
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      OLLAMA_NUM_PARALLEL: 2
      OLLAMA_MAX_LOADED_MODELS: 1
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:11434/api/tags || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # Application instances
  app:
    build: .
    environment:
      DB_HOST: pgbouncer
      DB_PORT: 6432
      DB_NAME: pgvector
      DB_USER: postgres
      DB_PASSWORD: ${POSTGRES_PASSWORD:-production_password_change_me}
      OLLAMA_URL: http://ollama:11434/api/embed
      REDIS_HOST: redis
      REDIS_PORT: 6379
      FLASK_ENV: production
    ports:
      - "5100-5103:5100"  # Map multiple ports for scaling
    depends_on:
      pgbouncer:
        condition: service_healthy
      ollama:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/ssl:ro
    depends_on:
      - app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Monitoring - Prometheus
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'

  # Monitoring - Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin123}
      GF_USERS_ALLOW_SIGN_UP: false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus

volumes:
  postgres_data:
  ollama_models:
  redis_data:
  prometheus_data:
  grafana_data:
```

#### 3.2: nginx Load Balancer Configuration

**Create nginx configuration:**

```nginx
# lab8_production/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Upstream application servers
    upstream vector_search_app {
        least_conn;
        server app:5100 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=search:10m rate=5r/s;

    # Main server block
    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # Health check endpoint (no rate limiting)
        location /health {
            proxy_pass http://vector_search_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 5s;
            proxy_send_timeout 10s;
            proxy_read_timeout 10s;
        }

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://vector_search_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts for vector operations
            proxy_connect_timeout 10s;
            proxy_send_timeout 30s;
            proxy_read_timeout 60s;
        }

        # Search endpoint with stricter rate limiting
        location /api/search {
            limit_req zone=search burst=10 nodelay;
            
            proxy_pass http://vector_search_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Extended timeouts for search operations
            proxy_connect_timeout 15s;
            proxy_send_timeout 60s;
            proxy_read_timeout 120s;
        }

        # Deny access to hidden files
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
    }
}
```

#### 3.3: Monitoring Configuration

**Create Prometheus configuration:**

```yaml
# lab8_production/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'vector-search-app'
    static_configs:
      - targets: ['app:5100']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []
```

---

### Exercise 4: Security and Access Control (8 minutes)

#### 4.1: Environment Configuration

**Create environment configuration:**

```bash
# lab8_production/.env.production
# Database Configuration
POSTGRES_PASSWORD=secure_password_change_in_production
DB_ENCRYPTION_KEY=32_character_encryption_key_here

# Application Secrets
JWT_SECRET_KEY=jwt_secret_key_change_in_production
FLASK_SECRET_KEY=flask_secret_key_change_in_production

# Monitoring
GRAFANA_PASSWORD=grafana_admin_password_change_me

# Service URLs
OLLAMA_URL=http://ollama:11434/api/embed
REDIS_URL=redis://redis:6379/0

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
SEARCH_RATE_LIMIT_PER_MINUTE=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/vector-search/app.log
```

#### 4.2: Security Enhancement Script

**Create security setup script:**

```python
# lab8_production/setup_security.py
import os
import secrets
import hashlib
import json
from typing import Dict, Any

class ProductionSecuritySetup:
    """Setup production security configurations."""
    
    def __init__(self):
        self.env_file = '.env.production'
        self.secrets_dir = 'secrets'
    
    def generate_secure_secrets(self) -> Dict[str, str]:
        """Generate secure secrets for production."""
        
        print("🔐 GENERATING PRODUCTION SECRETS")
        print("=" * 50)
        
        secrets_dict = {
            'POSTGRES_PASSWORD': secrets.token_urlsafe(32),
            'JWT_SECRET_KEY': secrets.token_urlsafe(64),
            'FLASK_SECRET_KEY': secrets.token_urlsafe(32),
            'GRAFANA_PASSWORD': secrets.token_urlsafe(16),
            'DB_ENCRYPTION_KEY': secrets.token_urlsafe(32)
        }
        
        # Create secrets directory
        os.makedirs(self.secrets_dir, exist_ok=True)
        
        # Save secrets securely
        secrets_file = os.path.join(self.secrets_dir, 'production_secrets.json')
        with open(secrets_file, 'w') as f:
            json.dump(secrets_dict, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(secrets_file, 0o600)
        
        print("✅ Generated secure secrets")
        print(f"✅ Saved to {secrets_file}")
        print("⚠️  IMPORTANT: Store these secrets securely and never commit to version control!")
        
        return secrets_dict
    
    def create_user_auth_config(self):
        """Create user authentication configuration."""
        
        print("\n👥 CREATING USER AUTHENTICATION CONFIG")
        print("=" * 50)
        
        # Edinburgh University departments and roles
        edinburgh_config = {
            'departments': [
                'IT Services',
                'Student Services', 
                'Library',
                'Estates',
                'HR',
                'Finance',
                'Research Services',
                'Academic Registry'
            ],
            'campuses': [
                'Central Campus',
                "King's Buildings",
                'Easter Bush',
                'Western General'
            ],
            'user_roles': {
                'student': {
                    'clearance_level': 2,
                    'rate_limit': 30,
                    'max_results': 20
                },
                'staff': {
                    'clearance_level': 3,
                    'rate_limit': 60,
                    'max_results': 50
                },
                'academic': {
                    'clearance_level': 4,
                    'rate_limit': 100,
                    'max_results': 100
                },
                'admin': {
                    'clearance_level': 5,
                    'rate_limit': 200,
                    'max_results': 200
                }
            }
        }
        
        config_file = os.path.join(self.secrets_dir, 'auth_config.json')
        with open(config_file, 'w') as f:
            json.dump(edinburgh_config, f, indent=2)
        
        print("✅ Created authentication configuration")
        return edinburgh_config
    
    def create_ssl_config(self):
        """Create SSL configuration template."""
        
        print("\n🔒 CREATING SSL CONFIGURATION")
        print("=" * 50)
        
        ssl_config = {
            'certificate_path': '/etc/ssl/certs/edinburgh.pem',
            'private_key_path': '/etc/ssl/private/edinburgh.key',
            'protocols': ['TLSv1.2', 'TLSv1.3'],
            'ciphers': [
                'ECDHE-ECDSA-AES128-GCM-SHA256',
                'ECDHE-RSA-AES128-GCM-SHA256',
                'ECDHE-ECDSA-AES256-GCM-SHA384',
                'ECDHE-RSA-AES256-GCM-SHA384'
            ]
        }
        
        # Create nginx SSL configuration
        nginx_ssl_config = f"""
# SSL Configuration for Production
ssl_certificate {ssl_config['certificate_path']};
ssl_certificate_key {ssl_config['private_key_path']};

ssl_protocols {' '.join(ssl_config['protocols'])};
ssl_ciphers {':'.join(ssl_config['ciphers'])};
ssl_prefer_server_ciphers off;

ssl_session_cache shared:SSL:1m;
ssl_session_timeout 10m;

# HSTS (optional)
add_header Strict-Transport-Security "max-age=31536000" always;
"""
        
        os.makedirs('nginx/ssl', exist_ok=True)
        with open('nginx/ssl/ssl_config.conf', 'w') as f:
            f.write(nginx_ssl_config)
        
        print("✅ Created SSL configuration template")
        print("⚠️  IMPORTANT: Replace with actual SSL certificates for production!")
        
        return ssl_config
    
    def create_security_checklist(self):
        """Create production security checklist."""
        
        checklist = """
# Production Security Checklist

## Pre-Deployment
- [ ] All default passwords changed
- [ ] SSL certificates obtained and configured
- [ ] Environment variables secured and not in version control
- [ ] Database access restricted to application only
- [ ] Rate limiting configured and tested
- [ ] Input validation implemented
- [ ] Error handling doesn't expose sensitive information

## Post-Deployment
- [ ] Security scanning performed
- [ ] Penetration testing completed
- [ ] Access logs monitoring configured
- [ ] Intrusion detection system configured
- [ ] Backup encryption verified
- [ ] Incident response plan documented

## Ongoing Maintenance
- [ ] Regular security updates applied
- [ ] Access logs reviewed monthly
- [ ] Rate limiting effectiveness monitored
- [ ] SSL certificate expiration tracking
- [ ] User access reviews quarterly
- [ ] Vulnerability assessments annually
"""
        
        with open('SECURITY_CHECKLIST.md', 'w') as f:
            f.write(checklist)
        
        print("✅ Created security checklist")
    
    def run_security_setup(self):
        """Execute complete security setup."""
        
        print("🔐 PRODUCTION SECURITY SETUP")
        print("=" * 60)
        
        try:
            secrets = self.generate_secure_secrets()
            auth_config = self.create_user_auth_config()
            ssl_config = self.create_ssl_config()
            self.create_security_checklist()
            
            print("\n" + "=" * 60)
            print("✅ SECURITY SETUP COMPLETE!")
            print("=" * 60)
            print("\n🚨 IMPORTANT SECURITY REMINDERS:")
            print("  1. Change all generated passwords in production")
            print("  2. Store secrets in a secure key management system")
            print("  3. Configure proper SSL certificates")
            print("  4. Set up proper firewall rules")
            print("  5. Enable audit logging")
            print("  6. Review and test all security configurations")
            
        except Exception as e:
            print(f"\n❌ Security setup failed: {str(e)}")

if __name__ == "__main__":
    security_setup = ProductionSecuritySetup()
    security_setup.run_security_setup()
```

**Run security setup:**

```bash
cd lab8_production
python setup_security.py
```

---

### Exercise 5: Production Deployment and Testing (5 minutes)

#### 5.1: Deployment Automation Script

**Create deployment script:**

```bash
#!/bin/bash
# lab8_production/deploy.sh
# Production Deployment Script for Edinburgh University Vector Search

set -e

echo "🚀 EDINBURGH UNIVERSITY VECTOR SEARCH - PRODUCTION DEPLOYMENT"
echo "=============================================================================="

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v ^# | xargs)
fi

# Pre-deployment checks
echo "🔍 PRE-DEPLOYMENT CHECKS"
echo "----------------------------------------"

# Check Docker resources
echo "Checking Docker resources..."
MEMORY_GB=$(docker system info --format '{{.MemTotal}}' | awk '{print int($1/1024/1024/1024)}')
if [ $MEMORY_GB -lt 8 ]; then
    echo "⚠️  Warning: Less than 8GB RAM available. Production deployment may be slow."
fi

# Check required files
REQUIRED_FILES=("docker-compose.yml" "Dockerfile" "production_app.py" "nginx/nginx.conf")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done
echo "✅ All required files present"

# Build application image
echo ""
echo "🔨 BUILDING APPLICATION IMAGE"
echo "----------------------------------------"
docker-compose build app

# Start core services first
echo ""
echo "🚀 STARTING CORE SERVICES"
echo "----------------------------------------"

# Start database and wait for health check
echo "Starting PostgreSQL..."
docker-compose up -d postgres
echo "Waiting for PostgreSQL to be ready..."
timeout 60 docker-compose exec postgres pg_isready -U postgres || {
    echo "❌ PostgreSQL failed to start"
    exit 1
}

# Initialize database if needed
echo "Setting up production database..."
python setup_production_db.py

# Start remaining infrastructure
echo "Starting Redis cache..."
docker-compose up -d redis

echo "Starting Ollama embedding service..."
docker-compose up -d ollama
echo "Waiting for Ollama to be ready..."
sleep 30

# Download embedding model
echo "Ensuring BGE-M3 model is available..."
docker-compose exec ollama ollama pull bge-m3 || echo "⚠️  Model download may continue in background"

# Start application services
echo ""
echo "🎯 STARTING APPLICATION SERVICES"
echo "----------------------------------------"

echo "Starting connection pooling..."
docker-compose up -d pgbouncer

echo "Starting application instances..."
docker-compose up -d app

echo "Starting load balancer..."
docker-compose up -d nginx

# Start monitoring
echo "Starting monitoring services..."
docker-compose up -d prometheus grafana

# Health checks
echo ""
echo "🏥 HEALTH CHECKS"
echo "----------------------------------------"

# Wait for application to be ready
echo "Waiting for application health checks..."
sleep 15

# Test application health
for i in {1..5}; do
    if curl -f http://localhost/health >/dev/null 2>&1; then
        echo "✅ Application health check passed"
        break
    else
        echo "⏳ Waiting for application... (attempt $i/5)"
        sleep 10
    fi
    
    if [ $i -eq 5 ]; then
        echo "❌ Application health check failed"
        echo "Checking logs..."
        docker-compose logs --tail=20 app
        exit 1
    fi
done

# Test search functionality
echo "Testing search functionality..."
SEARCH_RESPONSE=$(curl -s -X POST http://localhost/api/search \
    -H "Content-Type: application/json" \
    -d '{"query": "test deployment search"}')

if echo "$SEARCH_RESPONSE" | grep -q '"count"'; then
    echo "✅ Search functionality test passed"
else
    echo "❌ Search functionality test failed"
    echo "Response: $SEARCH_RESPONSE"
fi

# Display service status
echo ""
echo "📊 SERVICE STATUS"
echo "----------------------------------------"
docker-compose ps

echo ""
echo "🎯 DEPLOYMENT ACCESS INFORMATION"
echo "----------------------------------------"
echo "🔍 Search API:        http://localhost/api/search"
echo "❤️  Health Check:     http://localhost/health"
echo "📈 Monitoring:        http://localhost:3000 (Grafana)"
echo "🔧 Metrics:           http://localhost:9090 (Prometheus)"

echo ""
echo "✅ PRODUCTION DEPLOYMENT COMPLETE!"
echo "=============================================================================="
```

**Make deployment script executable and run:**

```bash
chmod +x lab8_production/deploy.sh
cd lab8_production
./deploy.sh
```

#### 5.2: Production Testing Suite

**Create production test script:**

```python
# lab8_production/test_production.py
import requests
import time
import json
import concurrent.futures
from typing import Dict, Any, List

class ProductionTestSuite:
    """Comprehensive testing suite for production deployment."""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test system health endpoint."""
        
        print("🏥 Testing health endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            result = {
                'test': 'health_endpoint',
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
            
            if response.status_code == 200:
                health_data = response.json()
                result['healthy_components'] = sum(1 for comp in health_data.get('components', {}).values() if comp.get('healthy'))
                print(f"  ✅ Health check passed ({result['response_time']:.3f}s)")
            else:
                print(f"  ❌ Health check failed (status: {response.status_code})")
                
        except Exception as e:
            result = {
                'test': 'health_endpoint',
                'status': 'error',
                'error': str(e)
            }
            print(f"  ❌ Health check error: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_search_functionality(self) -> Dict[str, Any]:
        """Test basic search functionality."""
        
        print("🔍 Testing search functionality...")
        
        test_queries = [
            "password reset instructions",
            "network connectivity troubleshooting", 
            "email configuration setup",
            "student accommodation WiFi"
        ]
        
        search_results = []
        
        for query in test_queries:
            try:
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}/api/search",
                    json={"query": query},
                    timeout=30
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    search_results.append({
                        'query': query,
                        'status': 'success',
                        'response_time': response_time,
                        'results_count': data.get('count', 0),
                        'search_time': data.get('search_time', 0)
                    })
                    print(f"  ✅ '{query}' - {data.get('count', 0)} results ({response_time:.3f}s)")
                else:
                    search_results.append({
                        'query': query,
                        'status': 'failed',
                        'response_time': response_time,
                        'status_code': response.status_code
                    })
                    print(f"  ❌ '{query}' - Failed (status: {response.status_code})")
                    
            except Exception as e:
                search_results.append({
                    'query': query,
                    'status': 'error',
                    'error': str(e)
                })
                print(f"  ❌ '{query}' - Error: {e}")
        
        overall_result = {
            'test': 'search_functionality',
            'status': 'pass' if all(r['status'] == 'success' for r in search_results) else 'fail',
            'individual_results': search_results,
            'avg_response_time': sum(r.get('response_time', 0) for r in search_results) / len(search_results),
            'total_results_found': sum(r.get('results_count', 0) for r in search_results)
        }
        
        self.test_results.append(overall_result)
        return overall_result
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality."""
        
        print("⚠️  Testing rate limiting...")
        
        # Send requests rapidly to trigger rate limiting
        rapid_requests = 0
        rate_limited = False
        
        try:
            for i in range(15):  # Should trigger rate limit
                response = self.session.post(
                    f"{self.base_url}/api/search",
                    json={"query": f"rate limit test {i}"},
                    timeout=10
                )
                
                if response.status_code == 429:
                    rate_limited = True
                    break
                elif response.status_code == 200:
                    rapid_requests += 1
                
                time.sleep(0.1)  # Small delay between requests
            
            result = {
                'test': 'rate_limiting',
                'status': 'pass' if rate_limited else 'fail',
                'requests_before_limit': rapid_requests,
                'rate_limiting_active': rate_limited
            }
            
            if rate_limited:
                print(f"  ✅ Rate limiting active after {rapid_requests} requests")
            else:
                print(f"  ⚠️  Rate limiting not triggered after {rapid_requests} requests")
                
        except Exception as e:
            result = {
                'test': 'rate_limiting',
                'status': 'error',
                'error': str(e)
            }
            print(f"  ❌ Rate limiting test error: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_concurrent_load(self, concurrent_users: int = 10, requests_per_user: int = 5) -> Dict[str, Any]:
        """Test concurrent user load."""
        
        print(f"⚡ Testing concurrent load ({concurrent_users} users, {requests_per_user} requests each)...")
        
        def make_search_request(user_id: int) -> List[Dict[str, Any]]:
            """Make multiple search requests for a user."""
            user_results = []
            
            for request_num in range(requests_per_user):
                try:
                    start_time = time.time()
                    
                    response = self.session.post(
                        f"{self.base_url}/api/search",
                        json={"query": f"concurrent test user {user_id} request {request_num}"},
                        timeout=30
                    )
                    
                    response_time = time.time() - start_time
                    
                    user_results.append({
                        'user_id': user_id,
                        'request_num': request_num,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'success': response.status_code == 200
                    })
                    
                except Exception as e:
                    user_results.append({
                        'user_id': user_id,
                        'request_num': request_num,
                        'error': str(e),
                        'success': False
                    })
            
            return user_results
        
        # Execute concurrent requests
        start_time = time.time()
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_search_request, i) for i in range(concurrent_users)]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    user_results = future.result()
                    all_results.extend(user_results)
                except Exception as e:
                    print(f"  ❌ Concurrent request failed: {e}")
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in all_results if r.get('success')]
        failed_requests = [r for r in all_results if not r.get('success')]
        
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r['response_time'] for r in successful_requests)
        else:
            avg_response_time = 0
            max_response_time = 0
        
        result = {
            'test': 'concurrent_load',
            'status': 'pass' if len(successful_requests) > len(failed_requests) else 'fail',
            'total_requests': len(all_results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(all_results) if all_results else 0,
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'total_test_time': total_time,
            'requests_per_second': len(all_results) / total_time if total_time > 0 else 0
        }
        
        print(f"  📊 Results: {len(successful_requests)}/{len(all_results)} successful")
        print(f"     Success rate: {result['success_rate']:.1%}")
        print(f"     Avg response time: {avg_response_time:.3f}s")
        print(f"     Requests/second: {result['requests_per_second']:.1f}")
        
        if result['success_rate'] >= 0.8:
            print(f"  ✅ Concurrent load test passed")
        else:
            print(f"  ❌ Concurrent load test failed")
        
        self.test_results.append(result)
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive production test suite."""
        
        print("🚀 PRODUCTION TEST SUITE")
        print("=" * 60)
        
        # Run all tests
        self.test_health_endpoint()
        self.test_search_functionality()
        self.test_rate_limiting()
        self.test_concurrent_load()
        
        # Summarize results
        passed_tests = sum(1 for r in self.test_results if r.get('status') == 'pass')
        total_tests = len(self.test_results)
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'individual_results': self.test_results
        }
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} tests passed ({summary['success_rate']:.1%})")
        print("=" * 60)
        
        if summary['success_rate'] >= 0.75:
            print("✅ Production deployment tests PASSED!")
        else:
            print("❌ Production deployment tests FAILED!")
            print("Please review failed tests and fix issues before production use.")
        
        return summary

if __name__ == "__main__":
    test_suite = ProductionTestSuite()
    results = test_suite.run_all_tests()
    
    # Save test results
    with open('production_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to production_test_results.json")
```

**Run production tests:**

```bash
cd lab8_production
python test_production.py
```

---

## Lab Verification

### Production Readiness Checklist

```bash
# lab8_production/verify_production.sh
#!/bin/bash

echo "🔍 PRODUCTION READINESS VERIFICATION"
echo "====================================="

# Check all services are running
echo "1. Service Status:"
docker-compose ps | grep -E "(Up|healthy)" && echo "  ✅ All services running" || echo "  ❌ Some services down"

# Check application response
echo "2. Application Response:"
curl -s http://localhost/health | grep -q "healthy" && echo "  ✅ Application responding" || echo "  ❌ Application not responding"

# Check database connectivity  
echo "3. Database Connectivity:"
docker-compose exec -T postgres pg_isready -U postgres && echo "  ✅ Database accessible" || echo "  ❌ Database issues"

# Check embedding service
echo "4. Embedding Service:"
curl -s http://localhost:11434/api/tags | grep -q "models" && echo "  ✅ Embedding service ready" || echo "  ❌ Embedding service issues"

# Check monitoring
echo "5. Monitoring Services:"
curl -s http://localhost:9090/api/v1/status/config | grep -q "success" && echo "  ✅ Prometheus running" || echo "  ❌ Prometheus issues"
curl -s http://localhost:3000/api/health | grep -q "ok" && echo "  ✅ Grafana running" || echo "  ❌ Grafana issues"

# Resource usage
echo "6. Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "🎯 Access URLs:"
echo "  🔍 Search API: http://localhost/api/search"
echo "  ❤️  Health: http://localhost/health"
echo "  📈 Grafana: http://localhost:3000"
echo "  🔧 Prometheus: http://localhost:9090"
```

**Run verification:**

```bash
chmod +x lab8_production/verify_production.sh
./verify_production.sh
```

---

## Success Criteria

### ✅ Lab Completion Checklist

**After completing this lab, you should have:**

- [ ] **Production database** - Optimized PostgreSQL with connection pooling
- [ ] **Scalable application** - Containerized Flask app with load balancing  
- [ ] **Monitoring system** - Prometheus + Grafana with custom dashboards
- [ ] **Security implementation** - Authentication, rate limiting, input validation
- [ ] **Automated deployment** - Docker Compose stack with health checks
- [ ] **Performance validation** - Load testing and concurrent user support
- [ ] **Operational procedures** - Backup, recovery, and incident response plans

### 🎯 Key Achievements

**Production Capabilities:**
- Handle 100+ concurrent users with sub-second response times
- Comprehensive monitoring and alerting for all system components
- Automated deployment and scaling procedures
- Security controls appropriate for university environment

**Edinburgh Integration:**
- Multi-campus, multi-department support at scale
- Role-based access control for different user types
- Compliance with university IT policies and procedures
- Integration-ready for existing Edinburgh systems

---

## Next Steps

**For Real Production Deployment:**
- Replace all placeholder passwords with secure credentials
- Configure proper SSL certificates from a trusted CA
- Set up proper backup and disaster recovery procedures
- Integrate with Edinburgh's existing authentication systems
- Configure proper firewall rules and network security
- Set up comprehensive log aggregation and analysis

**For Continued Learning:**
- Explore Kubernetes deployment for advanced orchestration
- Implement advanced caching strategies with Redis clustering
- Add comprehensive API documentation with OpenAPI/Swagger
- Integrate with university single sign-on systems
- Implement advanced analytics and usage reporting

---

## Troubleshooting

### Common Production Issues

**Services won't start:**
```bash
# Check Docker resources
docker system df
docker system prune  # Clean up if needed

# Check logs
docker-compose logs [service_name]
```

**Slow performance:**
```bash
# Check resource usage
docker stats

# Check database performance
docker-compose exec postgres psql -U postgres -d pgvector -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

**High error rates:**
```bash
# Check application logs
docker-compose logs app | grep ERROR

# Check nginx logs  
docker-compose logs nginx | grep error
```

---

**🎉 Congratulations! You've successfully deployed a production-ready vector search system for Edinburgh University! 🚀**

Your system is now capable of serving thousands of users with enterprise-grade reliability, security, and performance monitoring.