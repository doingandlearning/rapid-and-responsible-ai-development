# Section 8: Production Deployment

**Scaling, Monitoring, and Securing Vector Search Systems**

---

## Section Overview

**Time:** 90 minutes  
**Format:** 45 min presentation + 45 min hands-on lab

**Learning Goals:**
- Deploy production-ready vector search systems at university scale
- Implement comprehensive monitoring and alerting strategies
- Master security, performance, and reliability best practices
- Design scalable architecture for Edinburgh's institutional needs

---

## Why Production Deployment Matters

### Beyond Development Systems

**Development environment:**
- Single user, controlled data, forgiving performance
- Simple setup, basic monitoring, manual intervention

**Production environment:**
- Hundreds of concurrent users, real institutional data
- High availability requirements, automated recovery
- Security compliance, audit trails, performance SLAs

---

## Edinburgh University Production Requirements

### Scale and Performance

**User Load:**
- 15,000+ students across 4 campuses
- 5,000+ staff members in 50+ departments
- Peak usage: 500+ concurrent queries
- 24/7 availability requirement

**Data Volume:**
- 100,000+ document chunks with embeddings
- 50GB+ vector data storage
- 10,000+ new documents monthly
- Multi-language content support

---

## Production Architecture Overview

### High-Level System Design

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│  Application    │────│   PostgreSQL    │
│   (nginx/haproxy)│    │   Servers       │    │   + pgvector    │
└─────────────────┘    │  (Docker/K8s)   │    │    Cluster     │
                       └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Embedding     │    │   Monitoring    │
                       │   Service       │    │   & Alerting    │
                       │   (Ollama)      │    │ (Prometheus/    │
                       └─────────────────┘    │  Grafana)       │
                                              └─────────────────┘
```

---

## Infrastructure Components

### Database Layer - PostgreSQL + pgvector

**Configuration for Production:**
- **Primary/Replica setup** - Read scaling and failover
- **Connection pooling** - PgBouncer for connection management  
- **Backup strategy** - Continuous WAL archiving + daily dumps
- **Monitoring** - Query performance, connection usage, disk space

**Hardware specifications:**
- **CPU:** 16+ cores for vector operations
- **RAM:** 64GB+ for index caching
- **Storage:** NVMe SSD for vector indexes
- **Network:** 10Gbps for data transfer

---

## Database Production Configuration

### PostgreSQL Tuning for Vectors

```sql
-- postgresql.conf optimizations
shared_buffers = '16GB'                    -- 25% of RAM
effective_cache_size = '48GB'              -- 75% of RAM  
work_mem = '256MB'                         -- Per-query memory
maintenance_work_mem = '2GB'               -- Index maintenance
max_connections = 200                      -- With connection pooling
checkpoint_timeout = '15min'               -- Reduce checkpoint frequency

-- pgvector specific settings
max_parallel_workers_per_gather = 4       -- Parallel query execution
jit = off                                  -- Disable JIT for vector ops
```

### Connection Pooling with PgBouncer

```ini
# pgbouncer.ini
[databases]
pgvector = host=localhost port=5432 dbname=pgvector

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 10
```

---

## Application Layer Architecture

### Container Strategy with Docker

```dockerfile
# Production Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

---

## Load Balancing Strategy

### nginx Configuration

```nginx
upstream vector_search_app {
    least_conn;
    server app1:8000 max_fails=3 fail_timeout=30s;
    server app2:8000 max_fails=3 fail_timeout=30s; 
    server app3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name search.ed.ac.uk;
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/edinburgh.pem;
    ssl_certificate_key /etc/ssl/private/edinburgh.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=search:10m rate=10r/s;
    
    location /api/ {
        limit_req zone=search burst=20 nodelay;
        proxy_pass http://vector_search_app;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts for vector operations
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 60s;
    }
}
```

---

## Embedding Service Scaling

### Ollama Production Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  ollama-primary:
    image: ollama/ollama
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4
      - OLLAMA_MAX_LOADED_MODELS=2
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'

  ollama-secondary:
    image: ollama/ollama  
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4
      - OLLAMA_MAX_LOADED_MODELS=2

  ollama-loadbalancer:
    image: nginx:alpine
    ports:
      - "11434:80"
    volumes:
      - ./ollama-nginx.conf:/etc/nginx/nginx.conf
```

---

## Monitoring and Observability

### Application Performance Monitoring

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import logging

# Metrics collection
QUERY_TOTAL = Counter('vector_search_queries_total', 'Total queries', ['endpoint', 'status'])
QUERY_DURATION = Histogram('vector_search_duration_seconds', 'Query duration', ['query_type'])
ACTIVE_CONNECTIONS = Gauge('db_connections_active', 'Active DB connections')
EMBEDDING_QUEUE_SIZE = Gauge('embedding_queue_size', 'Embedding requests in queue')

class ProductionSearchMonitoring:
    def __init__(self):
        self.logger = self.setup_structured_logging()
        
    def setup_structured_logging(self):
        """Configure structured logging for production."""
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger('vector_search')
        
        # Add structured logging handler
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"component": "%(name)s", "message": "%(message)s"}'
        ))
        logger.addHandler(handler)
        
        return logger

    @QUERY_DURATION.time()  
    def monitor_search_query(self, query_func):
        """Monitor search query performance."""
        
        start_time = time.time()
        
        try:
            result = query_func()
            QUERY_TOTAL.labels(endpoint='search', status='success').inc()
            
            self.logger.info(
                f"Search query completed successfully",
                extra={
                    'query_duration': time.time() - start_time,
                    'results_count': len(result),
                    'success': True
                }
            )
            
            return result
            
        except Exception as e:
            QUERY_TOTAL.labels(endpoint='search', status='error').inc()
            
            self.logger.error(
                f"Search query failed: {str(e)}",
                extra={
                    'query_duration': time.time() - start_time,
                    'error': str(e),
                    'success': False
                }
            )
            raise
```

---

## Database Monitoring

### PostgreSQL Performance Metrics

```sql
-- Key production monitoring queries

-- 1. Connection usage
SELECT 
    state,
    COUNT(*) as connections
FROM pg_stat_activity 
GROUP BY state;

-- 2. Long-running queries
SELECT 
    now() - query_start as duration,
    query,
    state
FROM pg_stat_activity 
WHERE query_start < now() - interval '30 seconds'
ORDER BY duration DESC;

-- 3. Index usage for vectors
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename = 'document_chunks'
ORDER BY idx_scan DESC;

-- 4. Vector query performance
SELECT 
    calls,
    total_time,
    mean_time,
    query
FROM pg_stat_statements 
WHERE query LIKE '%<=>%'
ORDER BY total_time DESC
LIMIT 10;
```

---

## Health Check Implementation

### Comprehensive Health Monitoring

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
import psycopg
import requests
import redis

@dataclass
class HealthCheckResult:
    component: str
    healthy: bool
    response_time: float
    details: Dict[str, Any]
    error: Optional[str] = None

class SystemHealthMonitor:
    """Comprehensive health monitoring for production deployment."""
    
    def __init__(self, config):
        self.config = config
        self.redis_client = redis.Redis(host=config.redis_host)
        
    def check_database_health(self) -> HealthCheckResult:
        """Check PostgreSQL + pgvector health."""
        
        start_time = time.time()
        
        try:
            conn = psycopg.connect(
                host=self.config.db_host,
                port=self.config.db_port,
                dbname=self.config.db_name,
                user=self.config.db_user,
                password=self.config.db_password,
                connect_timeout=5
            )
            
            cur = conn.cursor()
            
            # Test basic connectivity
            cur.execute('SELECT 1')
            
            # Test vector operations
            cur.execute('SELECT vector_dims(\'[1,2,3]\'::vector)')
            
            # Check document availability
            cur.execute('SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL')
            chunk_count = cur.fetchone()[0]
            
            # Check connection pool status
            cur.execute('SELECT COUNT(*) FROM pg_stat_activity WHERE state = \'active\'')
            active_connections = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                component='database',
                healthy=chunk_count > 0,
                response_time=response_time,
                details={
                    'chunk_count': chunk_count,
                    'active_connections': active_connections,
                    'connectivity': True
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component='database',
                healthy=False,
                response_time=time.time() - start_time,
                details={'connectivity': False},
                error=str(e)
            )
    
    def check_embedding_service_health(self) -> HealthCheckResult:
        """Check Ollama embedding service health."""
        
        start_time = time.time()
        
        try:
            # Test model availability
            response = requests.get(
                f'{self.config.ollama_url.replace("/api/embed", "/api/tags")}',
                timeout=10
            )
            response.raise_for_status()
            
            models = response.json().get('models', [])
            bge_available = any('bge-m3' in model.get('name', '') for model in models)
            
            if bge_available:
                # Test embedding generation
                embed_response = requests.post(
                    self.config.ollama_url,
                    json={'model': 'bge-m3', 'input': 'health check'},
                    timeout=30
                )
                embed_response.raise_for_status()
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                component='embedding_service',
                healthy=bge_available,
                response_time=response_time,
                details={
                    'models_available': len(models),
                    'bge_m3_loaded': bge_available
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component='embedding_service',
                healthy=False,
                response_time=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def check_cache_health(self) -> HealthCheckResult:
        """Check Redis cache health."""
        
        start_time = time.time()
        
        try:
            # Test basic connectivity
            self.redis_client.ping()
            
            # Test read/write operations
            test_key = 'health_check_test'
            self.redis_client.set(test_key, 'test_value', ex=60)
            retrieved_value = self.redis_client.get(test_key)
            
            # Get cache statistics
            info = self.redis_client.info()
            memory_usage = info.get('used_memory_human', 'unknown')
            connected_clients = info.get('connected_clients', 0)
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                component='cache',
                healthy=retrieved_value == b'test_value',
                response_time=response_time,
                details={
                    'memory_usage': memory_usage,
                    'connected_clients': connected_clients
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                component='cache',
                healthy=False, 
                response_time=time.time() - start_time,
                details={},
                error=str(e)
            )
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        
        health_checks = [
            self.check_database_health(),
            self.check_embedding_service_health(),
            self.check_cache_health()
        ]
        
        overall_healthy = all(check.healthy for check in health_checks)
        
        return {
            'healthy': overall_healthy,
            'timestamp': datetime.now().isoformat(),
            'components': {check.component: {
                'healthy': check.healthy,
                'response_time': check.response_time,
                'details': check.details,
                'error': check.error
            } for check in health_checks}
        }
```

---

## Security Implementation

### Authentication and Authorization

```python
from functools import wraps
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
import bcrypt

class EdinburghSecurityManager:
    """Security management for Edinburgh University deployment."""
    
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.jwt = JWTManager(app)
        
        # JWT configuration
        app.config['JWT_SECRET_KEY'] = config.jwt_secret_key
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)  # Working day
        
    def require_authentication(self, f):
        """Require valid JWT token for access."""
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return f(*args, **kwargs)
            except Exception as e:
                return {'error': 'Authentication required', 'message': str(e)}, 401
                
        return decorated_function
    
    def require_role(self, required_roles):
        """Require specific role for access."""
        
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    verify_jwt_in_request()
                    user_info = get_jwt_identity()
                    user_role = user_info.get('role')
                    
                    if user_role not in required_roles:
                        return {
                            'error': 'Insufficient permissions',
                            'required': required_roles,
                            'current': user_role
                        }, 403
                    
                    return f(*args, **kwargs)
                    
                except Exception as e:
                    return {'error': 'Authorization failed', 'message': str(e)}, 401
                    
            return decorated_function
        return decorator
    
    def get_user_search_filters(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get search filters based on user role and department."""
        
        role = user_info.get('role', 'student')
        department = user_info.get('department')
        campus = user_info.get('campus')
        
        filters = {}
        
        # Role-based clearance levels
        clearance_levels = {
            'student': 2,
            'staff': 3,
            'academic': 4,
            'admin': 4
        }
        
        filters['max_clearance_level'] = clearance_levels.get(role, 1)
        
        # Department-based filtering
        if department:
            filters['user_department'] = department
            
        # Campus-based prioritization
        if campus:
            filters['preferred_campus'] = campus
        
        return filters

    def sanitize_query(self, query: str) -> str:
        """Sanitize user query input."""
        
        # Remove potentially dangerous characters
        query = re.sub(r'[<>"\']', '', query)
        
        # Limit query length
        query = query[:500]
        
        # Basic SQL injection prevention (though we use parameters)
        dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER']
        for pattern in dangerous_patterns:
            query = re.sub(f'\\b{pattern}\\b', '', query, flags=re.IGNORECASE)
        
        return query.strip()
```

---

## Caching Strategy

### Multi-Layer Caching

```python
import redis
from functools import wraps
import hashlib
import json
from typing import Any, Optional

class ProductionCacheManager:
    """Multi-layer caching for production performance."""
    
    def __init__(self, config):
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=0,
            decode_responses=True
        )
        
        # Cache TTL settings (seconds)
        self.ttl_settings = {
            'embedding': 3600,      # 1 hour - embeddings are expensive
            'search_results': 900,  # 15 minutes - balance freshness vs performance
            'user_profile': 1800,   # 30 minutes - user context
            'health_check': 60      # 1 minute - system health
        }
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate consistent cache key from parameters."""
        
        # Sort kwargs for consistent key generation
        sorted_items = sorted(kwargs.items())
        key_data = f"{prefix}:{json.dumps(sorted_items, sort_keys=True)}"
        
        # Use hash for long keys
        if len(key_data) > 250:
            key_hash = hashlib.sha256(key_data.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return key_data
    
    def cache_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache embedding results."""
        
        key = self.generate_cache_key('embedding', text=text)
        
        try:
            self.redis_client.setex(
                key, 
                self.ttl_settings['embedding'],
                json.dumps(embedding)
            )
        except Exception as e:
            # Don't fail if cache is unavailable
            logging.warning(f"Cache write failed: {e}")
    
    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Retrieve cached embedding."""
        
        key = self.generate_cache_key('embedding', text=text)
        
        try:
            cached = self.redis_client.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logging.warning(f"Cache read failed: {e}")
            return None
    
    def cache_search_results(self, query: str, filters: Dict[str, Any], results: List[Dict]) -> None:
        """Cache search results."""
        
        key = self.generate_cache_key('search', query=query, filters=filters)
        
        try:
            # Serialize results for caching
            cache_data = {
                'results': results,
                'timestamp': time.time(),
                'count': len(results)
            }
            
            self.redis_client.setex(
                key,
                self.ttl_settings['search_results'],
                json.dumps(cache_data)
            )
        except Exception as e:
            logging.warning(f"Search cache write failed: {e}")
    
    def get_cached_search_results(self, query: str, filters: Dict[str, Any]) -> Optional[List[Dict]]:
        """Retrieve cached search results."""
        
        key = self.generate_cache_key('search', query=query, filters=filters)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                cache_data = json.loads(cached)
                return cache_data['results']
            return None
        except Exception as e:
            logging.warning(f"Search cache read failed: {e}")
            return None
    
    def warm_cache(self, popular_queries: List[str]) -> None:
        """Pre-populate cache with popular queries."""
        
        for query in popular_queries:
            # Generate embeddings for popular queries
            try:
                # This would call your embedding service
                embedding = self.embedding_service.get_embedding(query)
                self.cache_embedding(query, embedding)
            except Exception as e:
                logging.warning(f"Cache warming failed for query '{query}': {e}")
    
    def cache_with_fallback(self, cache_key: str, fetch_func, ttl: int = 900):
        """Generic cache-with-fallback pattern."""
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Try cache first
                    cached = self.redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)
                except Exception:
                    pass  # Fall through to function call
                
                # Call original function
                result = func(*args, **kwargs)
                
                # Cache result
                try:
                    self.redis_client.setex(cache_key, ttl, json.dumps(result))
                except Exception:
                    pass  # Don't fail if cache write fails
                
                return result
            
            return wrapper
        return decorator
```

---

## Backup and Recovery

### Database Backup Strategy

```bash
#!/bin/bash
# production-backup.sh - PostgreSQL + pgvector backup script

set -e

# Configuration
DB_HOST="localhost"
DB_PORT="5432"  
DB_NAME="pgvector"
DB_USER="postgres"
BACKUP_DIR="/var/backups/pgvector"
RETENTION_DAYS=30
S3_BUCKET="edinburgh-vector-backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/pgvector_backup_$TIMESTAMP.sql"

echo "Starting backup at $(date)"

# Full database backup
pg_dump \
    --host=$DB_HOST \
    --port=$DB_PORT \
    --username=$DB_USER \
    --dbname=$DB_NAME \
    --verbose \
    --format=custom \
    --compress=9 \
    --file=$BACKUP_FILE

# Verify backup
pg_restore --list $BACKUP_FILE > /dev/null

if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    
    # Upload to S3 for offsite storage
    aws s3 cp $BACKUP_FILE s3://$S3_BUCKET/daily/
    
    # Compress for local storage
    gzip $BACKUP_FILE
    
    echo "Backup uploaded to S3 and compressed locally"
else
    echo "Backup verification failed!"
    exit 1
fi

# Cleanup old backups
find $BACKUP_DIR -name "pgvector_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# WAL archiving for continuous backup
if [ ! -d "/var/lib/postgresql/wal_archive" ]; then
    mkdir -p /var/lib/postgresql/wal_archive
fi

echo "Backup process completed at $(date)"
```

### Disaster Recovery Procedures

```yaml
# disaster-recovery.yml - Recovery procedures documentation
recovery_procedures:
  
  database_failure:
    detection:
      - Health check failures
      - Connection timeouts
      - Query execution errors
    
    response:
      1. "Switch to read replica if available"
      2. "Assess primary database status" 
      3. "If corrupted, restore from latest backup"
      4. "Replay WAL files for point-in-time recovery"
      5. "Update application configuration to new primary"
    
    commands:
      restore_from_backup: |
        pg_restore --host=new-primary --port=5432 --username=postgres 
                   --dbname=pgvector --clean --create backup_file.sql
      
      wal_replay: |
        pg_basebackup -h backup-server -D /var/lib/postgresql/data -U postgres -P -W
  
  application_failure:
    detection:
      - HTTP 5xx responses
      - Container crashes
      - Memory/CPU exhaustion
    
    response:
      1. "Check container logs for errors"
      2. "Restart failed containers"
      3. "Scale horizontally if needed"
      4. "Monitor system resources"
    
    commands:
      restart_containers: |
        docker-compose restart vector-search-app
      
      scale_up: |
        docker-compose up --scale vector-search-app=5
  
  embedding_service_failure:
    detection:
      - Ollama API timeouts
      - Model loading failures
      - Memory exhaustion
    
    response:
      1. "Restart Ollama service"
      2. "Check model availability"
      3. "Clear model cache if needed"
      4. "Switch to backup embedding service"
    
    commands:
      restart_ollama: |
        docker-compose restart ollama-service
      
      reload_models: |
        docker exec ollama-service ollama pull bge-m3
```

---

## Performance Optimization

### Database Performance Tuning

```sql
-- Advanced PostgreSQL configuration for production

-- Memory settings
shared_buffers = '16GB'                    -- 25% of total RAM
effective_cache_size = '48GB'              -- 75% of total RAM  
work_mem = '256MB'                         -- Per-query working memory
maintenance_work_mem = '2GB'               -- Index maintenance memory

-- Checkpoint and WAL settings  
checkpoint_timeout = '15min'               -- Reduce checkpoint frequency
checkpoint_completion_target = 0.9         -- Spread checkpoint I/O
wal_buffers = '64MB'                       -- WAL buffer size
wal_compression = on                       -- Compress WAL files

-- Query planner settings
random_page_cost = 1.1                     -- SSD optimization
effective_io_concurrency = 200             -- Concurrent I/O operations
max_parallel_workers_per_gather = 4       -- Parallel query workers
max_parallel_workers = 8                  -- Total parallel workers

-- Connection settings
max_connections = 200                      -- With connection pooling
superuser_reserved_connections = 3         -- Reserved for admin

-- Logging for monitoring
log_duration = on                          -- Log query duration
log_min_duration_statement = 1000          -- Log slow queries (>1s)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

-- Statistics collection
track_activities = on
track_counts = on
track_functions = all
track_io_timing = on
```

### Index Optimization for Production

```sql
-- Comprehensive indexing strategy for production scale

-- 1. HNSW vector index with optimal parameters
CREATE INDEX CONCURRENTLY document_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- 2. GIN index for JSONB metadata with optimal operator class
CREATE INDEX CONCURRENTLY document_chunks_metadata_gin 
ON document_chunks 
USING gin (metadata jsonb_path_ops);

-- 3. Partial indexes for common filters
CREATE INDEX CONCURRENTLY document_chunks_active_docs 
ON document_chunks (document_title, page_number) 
WHERE metadata->>'status' = 'active';

-- 4. Expression indexes for computed fields
CREATE INDEX CONCURRENTLY document_chunks_priority_expr 
ON document_chunks ((metadata->>'priority')::int) 
WHERE (metadata->>'priority')::int >= 3;

-- 5. Composite index for common query patterns
CREATE INDEX CONCURRENTLY document_chunks_dept_type_composite 
ON document_chunks (
    (metadata->>'department'), 
    (metadata->>'doc_type'),
    page_number
);

-- 6. Timestamp index for time-based queries
CREATE INDEX CONCURRENTLY document_chunks_last_reviewed 
ON document_chunks ((metadata->>'last_reviewed')::timestamp) 
WHERE metadata->>'last_reviewed' IS NOT NULL;

-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename = 'document_chunks'
ORDER BY idx_scan DESC;
```

---

## Scaling Strategies

### Horizontal Scaling Patterns

```python
class LoadBalancedSearchCluster:
    """Manage multiple search service instances for load distribution."""
    
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.current_node = 0
        self.node_health = {node: True for node in nodes}
        self.request_counts = {node: 0 for node in nodes}
    
    def get_healthy_node(self) -> Optional[str]:
        """Get next healthy node using round-robin."""
        
        healthy_nodes = [node for node in self.nodes if self.node_health[node]]
        
        if not healthy_nodes:
            return None
        
        # Round-robin among healthy nodes
        node = healthy_nodes[self.current_node % len(healthy_nodes)]
        self.current_node = (self.current_node + 1) % len(healthy_nodes)
        
        return node
    
    def execute_search_with_failover(self, query: str, filters: Dict = None) -> Dict:
        """Execute search with automatic failover."""
        
        attempts = 0
        max_attempts = len(self.nodes)
        
        while attempts < max_attempts:
            node = self.get_healthy_node()
            
            if not node:
                raise Exception("No healthy nodes available")
            
            try:
                # Execute search on selected node
                result = self.execute_search_on_node(node, query, filters)
                self.request_counts[node] += 1
                return result
                
            except Exception as e:
                # Mark node as unhealthy and try next
                self.node_health[node] = False
                attempts += 1
                logging.warning(f"Node {node} failed, trying next: {e}")
        
        raise Exception("All nodes failed to respond")
    
    def check_node_health(self, node: str) -> bool:
        """Check individual node health."""
        
        try:
            response = requests.get(f'http://{node}/health', timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def update_node_health(self):
        """Update health status for all nodes."""
        
        for node in self.nodes:
            self.node_health[node] = self.check_node_health(node)
```

### Database Read Scaling

```python
class DatabaseClusterManager:
    """Manage PostgreSQL primary/replica cluster for read scaling."""
    
    def __init__(self, primary_url: str, replica_urls: List[str]):
        self.primary_url = primary_url
        self.replica_urls = replica_urls
        self.replica_weights = [1.0 / len(replica_urls)] * len(replica_urls)
    
    def get_read_connection(self):
        """Get connection for read queries with replica load balancing."""
        
        # Select replica based on weights
        replica_url = random.choices(self.replica_urls, weights=self.replica_weights)[0]
        
        try:
            return psycopg.connect(replica_url)
        except Exception as e:
            logging.warning(f"Replica connection failed, using primary: {e}")
            return psycopg.connect(self.primary_url)
    
    def get_write_connection(self):
        """Get connection for write queries (always primary)."""
        return psycopg.connect(self.primary_url)
    
    def execute_search_query(self, query: str, params: List[Any]) -> List[Any]:
        """Execute read-only search query on replica."""
        
        with self.get_read_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()
    
    def execute_write_query(self, query: str, params: List[Any]) -> None:
        """Execute write query on primary."""
        
        with self.get_write_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
```

---

## Alerting and Incident Response

### Prometheus Alerting Rules

```yaml
# alerting-rules.yml
groups:
- name: vector-search-alerts
  rules:
  
  # High query latency alert
  - alert: HighQueryLatency
    expr: histogram_quantile(0.95, vector_search_duration_seconds) > 3
    for: 2m
    labels:
      severity: warning
      component: vector-search
    annotations:
      summary: "Vector search queries are running slowly"
      description: "95th percentile query latency is {{ $value }}s"
  
  # Error rate alert  
  - alert: HighErrorRate
    expr: rate(vector_search_queries_total{status="error"}[5m]) > 0.1
    for: 1m
    labels:
      severity: critical
      component: vector-search
    annotations:
      summary: "High error rate in vector search"
      description: "Error rate is {{ $value }} errors per second"
  
  # Database connection alert
  - alert: DatabaseConnectionsHigh
    expr: db_connections_active > 180
    for: 2m
    labels:
      severity: warning
      component: database
    annotations:
      summary: "Database connection pool nearly exhausted"
      description: "{{ $value }} active connections out of 200 limit"
  
  # Embedding service down alert
  - alert: EmbeddingServiceDown
    expr: up{job="ollama-service"} == 0
    for: 30s
    labels:
      severity: critical
      component: embeddings
    annotations:
      summary: "Embedding service is down"
      description: "Ollama embedding service is not responding"
  
  # Disk space alert
  - alert: LowDiskSpace
    expr: disk_free_percent < 10
    for: 1m
    labels:
      severity: critical
      component: infrastructure
    annotations:
      summary: "Low disk space on vector database server"
      description: "Only {{ $value }}% disk space remaining"
```

### Incident Response Playbook

```markdown
# Vector Search System - Incident Response Playbook

## Severity Levels

### P1 (Critical) - Service Down
- **Response time:** 15 minutes
- **Escalation:** Immediate to on-call engineer
- **Communication:** Status page update + stakeholder notification

### P2 (High) - Degraded Performance  
- **Response time:** 30 minutes
- **Escalation:** Primary on-call
- **Communication:** Internal notification

### P3 (Medium) - Minor Issues
- **Response time:** 2 hours
- **Escalation:** During business hours
- **Communication:** Bug tracking system

## Common Incidents

### 1. High Query Latency (P2)
**Symptoms:** Search queries taking >3 seconds
**Immediate actions:**
1. Check database connection pool status
2. Review slow query log for problematic queries
3. Check system resource utilization (CPU, memory, disk I/O)
4. Consider temporarily scaling application instances

**Investigation steps:**
1. Analyze query execution plans with EXPLAIN ANALYZE
2. Check for missing or degraded indexes
3. Review recent configuration changes
4. Monitor embedding service performance

### 2. Service Completely Down (P1)
**Symptoms:** All search requests returning 5xx errors
**Immediate actions:**
1. Check all service health endpoints
2. Review container/service logs for errors
3. Verify database connectivity
4. Check embedding service availability
5. Restart services if necessary

**Communication template:**
```
🚨 INCIDENT ALERT 🚨
Service: Vector Search System
Status: INVESTIGATING
Impact: Edinburgh University staff and students cannot access document search
ETA for resolution: [Time estimate]
Updates: [Communication channel]
```

### 3. Database Connection Exhaustion (P2)
**Symptoms:** Connection timeout errors, high active connection count
**Immediate actions:**
1. Check PgBouncer connection pool status
2. Identify and terminate long-running queries if safe
3. Scale application instances down temporarily to reduce load
4. Review connection pool configuration

### 4. Embedding Service Failure (P2)
**Symptoms:** Embedding generation timeouts, model loading errors
**Immediate actions:**
1. Restart Ollama service containers
2. Check GPU/CPU resource availability  
3. Verify model files are accessible
4. Clear embedding service cache if corrupted
```

---

## Compliance and Security

### Edinburgh University IT Policies

```python
class ComplianceManager:
    """Ensure compliance with Edinburgh University IT policies."""
    
    def __init__(self, config):
        self.config = config
        self.audit_logger = self.setup_audit_logging()
    
    def setup_audit_logging(self):
        """Setup audit trail logging for compliance."""
        
        audit_logger = logging.getLogger('audit')
        audit_handler = logging.FileHandler('/var/log/vector-search/audit.log')
        audit_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "user_id": "%(user_id)s", '
            '"query": "%(query)s", "results_count": %(results_count)d, '
            '"ip_address": "%(ip_address)s", "session_id": "%(session_id)s"}'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
        
        return audit_logger
    
    def log_search_query(self, user_id: str, query: str, results_count: int, 
                        ip_address: str, session_id: str):
        """Log search query for audit trail."""
        
        self.audit_logger.info(
            "Search query executed",
            extra={
                'user_id': user_id,
                'query': query,
                'results_count': results_count,
                'ip_address': ip_address,
                'session_id': session_id
            }
        )
    
    def check_data_retention_compliance(self):
        """Ensure compliance with data retention policies."""
        
        # Remove audit logs older than required retention period
        retention_days = self.config.audit_retention_days
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Implementation would depend on log storage system
        self.cleanup_old_audit_logs(cutoff_date)
    
    def validate_user_access(self, user_info: Dict, requested_clearance: int) -> bool:
        """Validate user access against university policies."""
        
        user_clearance = user_info.get('clearance_level', 1)
        user_department = user_info.get('department')
        user_role = user_info.get('role')
        
        # Basic clearance level check
        if user_clearance < requested_clearance:
            return False
        
        # Department-specific restrictions
        if requested_clearance >= 3:
            # Level 3+ requires departmental affiliation
            return user_department is not None
        
        return True
    
    def anonymize_sensitive_data(self, text: str) -> str:
        """Remove or mask sensitive information from text."""
        
        # Email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     '[EMAIL_REDACTED]', text)
        
        # Phone numbers (UK format)
        text = re.sub(r'\b(?:\+44|0)[1-9]\d{8,10}\b', '[PHONE_REDACTED]', text)
        
        # Student/Staff IDs (Edinburgh format: s1234567 or user123)
        text = re.sub(r'\b[s]\d{7}\b', '[STUDENT_ID_REDACTED]', text)
        text = re.sub(r'\b[user]\d{3,6}\b', '[STAFF_ID_REDACTED]', text)
        
        # Postcodes (UK format)
        text = re.sub(r'\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b', '[POSTCODE_REDACTED]', text)
        
        return text
```

---

## Deployment Automation

### Infrastructure as Code with Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  # Primary database
  postgres-primary:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_DB: pgvector
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--auth-method=md5"
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
      - ./pg_hba.conf:/etc/postgresql/pg_hba.conf
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8.0'
    
  # Database replica for read scaling
  postgres-replica:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_DB: pgvector
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGUSER: postgres
      POSTGRES_PRIMARY_HOST: postgres-primary
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
    depends_on:
      - postgres-primary
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '4.0'

  # Connection pooling
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    environment:
      DATABASES_HOST: postgres-primary
      DATABASES_PORT: 5432
      DATABASES_USER: postgres
      DATABASES_PASSWORD: ${POSTGRES_PASSWORD}
      DATABASES_DBNAME: pgvector
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 1000
      DEFAULT_POOL_SIZE: 25
    ports:
      - "6432:6432"
    depends_on:
      - postgres-primary

  # Embedding service cluster
  ollama-primary:
    image: ollama/ollama
    volumes:
      - ollama_models:/root/.ollama
    environment:
      OLLAMA_NUM_PARALLEL: 4
      OLLAMA_MAX_LOADED_MODELS: 2
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'

  ollama-secondary:
    image: ollama/ollama
    volumes:
      - ollama_models:/root/.ollama
    environment:
      OLLAMA_NUM_PARALLEL: 4
      OLLAMA_MAX_LOADED_MODELS: 2
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'

  # Embedding service load balancer
  ollama-lb:
    image: nginx:alpine
    ports:
      - "11434:80"
    volumes:
      - ./nginx/ollama-lb.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - ollama-primary
      - ollama-secondary

  # Application services
  vector-search-app:
    build: .
    environment:
      DB_HOST: pgbouncer
      DB_PORT: 6432
      OLLAMA_URL: http://ollama-lb/api/embed
      REDIS_HOST: redis
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - pgbouncer
      - ollama-lb
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  # Caching layer
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - vector-search-app

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus

volumes:
  postgres_primary_data:
  postgres_replica_data:
  ollama_models:
  redis_data:
  prometheus_data:
  grafana_data:
```

---

## Production Readiness Checklist

### Pre-Deployment Validation

**Infrastructure:**
- [ ] Database primary/replica setup tested
- [ ] Connection pooling configured and tested
- [ ] Load balancers configured with health checks
- [ ] SSL certificates installed and valid
- [ ] Backup and recovery procedures tested

**Security:**
- [ ] Authentication and authorization implemented
- [ ] Input sanitization and validation in place
- [ ] Audit logging configured
- [ ] Secrets management implemented
- [ ] Network security rules configured

**Performance:**
- [ ] Load testing completed at expected scale
- [ ] Database indexes optimized
- [ ] Caching strategy implemented and tested
- [ ] Query performance benchmarks met
- [ ] Resource utilization within acceptable limits

**Monitoring:**
- [ ] Health checks implemented for all services
- [ ] Metrics collection configured
- [ ] Alerting rules defined and tested
- [ ] Dashboards created for key metrics
- [ ] Log aggregation and analysis setup

---

## Going Live Strategy

### Phased Rollout Plan

**Phase 1: Limited Beta (Week 1-2)**
- Deploy to staging environment
- Test with 50 internal staff members
- Monitor performance and gather feedback
- Fix critical issues

**Phase 2: Departmental Rollout (Week 3-4)**  
- Roll out to IT Services and Library staff
- 500+ users, real workload testing
- Performance optimization based on usage patterns
- Train support staff

**Phase 3: University-Wide Launch (Week 5-6)**
- Full deployment to all staff and students
- Monitor system performance under full load
- Support ticket triage and resolution
- Continuous optimization

**Phase 4: Optimization and Enhancement (Ongoing)**
- Performance tuning based on usage analytics
- Feature enhancements based on user feedback
- Capacity planning and scaling
- Regular security and compliance reviews

---

## Success Metrics

### Key Performance Indicators

**Performance Metrics:**
- Query response time: p95 < 1 second
- System availability: >99.5% uptime
- Error rate: <0.5% of all queries
- Concurrent user capacity: 500+ users

**Business Metrics:**
- User adoption rate: >60% of target users
- Search success rate: >80% queries find relevant results
- Support ticket reduction: 30% decrease in routine inquiries
- User satisfaction score: >4.0/5.0

---

## Ready for Production!

### Section Completion

**You've mastered:**
🎯 **Production architecture** - Scalable, resilient system design  
🎯 **Security implementation** - Authentication, authorization, audit trails  
🎯 **Performance optimization** - Database tuning, caching, monitoring  
🎯 **Operational excellence** - Deployment, monitoring, incident response  
🎯 **Edinburgh integration** - University-specific requirements and compliance

**Next:** 45 minutes of hands-on production deployment! 🚀