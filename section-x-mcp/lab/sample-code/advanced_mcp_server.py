"""
Advanced MCP Server with Caching and Security
=============================================

This example shows advanced MCP server patterns including:
- Redis caching for performance
- API key authentication
- Rate limiting
- Comprehensive logging
- Health checks
- Metrics collection
"""

import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import redis
from datetime import datetime, timedelta

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedDocumentMCPServer:
    """Production-ready MCP server with advanced features"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url)
        self.api_keys = self._load_api_keys()
        self.rate_limits = {}
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Health check endpoint
        self.health_status = "healthy"
        self.last_health_check = time.time()
    
    def _load_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys with metadata"""
        return {
            "demo-key-123": {
                "user": "demo-user",
                "permissions": ["read", "search"],
                "rate_limit": 100,
                "created_at": "2024-01-01T00:00:00Z"
            },
            "admin-key-456": {
                "user": "admin-user", 
                "permissions": ["read", "search", "write", "admin"],
                "rate_limit": 1000,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    
    def _validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info"""
        if api_key not in self.api_keys:
            return None
        return self.api_keys[api_key]
    
    def _check_rate_limit(self, api_key: str) -> bool:
        """Check if API key has exceeded rate limits"""
        user_info = self._validate_api_key(api_key)
        if not user_info:
            return False
        
        now = time.time()
        rate_limit = user_info["rate_limit"]
        
        # Get current request count for this hour
        hour_key = f"rate_limit:{api_key}:{int(now // 3600)}"
        current_count = self.redis_client.get(hour_key)
        
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)
        
        if current_count >= rate_limit:
            return False
        
        # Increment counter
        self.redis_client.incr(hour_key)
        self.redis_client.expire(hour_key, 3600)  # Expire after 1 hour
        
        return True
    
    def _get_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate cache key for operation"""
        # Create deterministic key from operation and parameters
        key_data = {"operation": operation, "params": sorted(params.items())}
        key_string = json.dumps(key_data, sort_keys=True)
        return f"mcp_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache"""
        try:
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                self.metrics["cache_hits"] += 1
                return json.loads(cached_result)
            else:
                self.metrics["cache_misses"] += 1
                return None
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None
    
    def _set_cache(self, cache_key: str, result: Dict[str, Any], ttl: int = 3600):
        """Set result in cache"""
        try:
            self.redis_client.setex(cache_key, ttl, json.dumps(result))
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def _log_request(self, operation: str, api_key: str, success: bool, 
                    execution_time: float, result_count: int = 0):
        """Log request details"""
        user_info = self._validate_api_key(api_key)
        user = user_info["user"] if user_info else "unknown"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "user": user,
            "success": success,
            "execution_time": execution_time,
            "result_count": result_count
        }
        
        logger.info(f"Request: {json.dumps(log_data)}")
        
        # Update metrics
        self.metrics["requests_total"] += 1
        if success:
            self.metrics["requests_successful"] += 1
        else:
            self.metrics["requests_failed"] += 1
    
    def search_documents(self, query: str, limit: int = 10, 
                        api_key: str = None, use_cache: bool = True) -> Dict[str, Any]:
        """Search documents with caching and rate limiting"""
        start_time = time.time()
        
        try:
            # Validate API key
            if api_key and not self._validate_api_key(api_key):
                return {"success": False, "error": "Invalid API key"}
            
            # Check rate limits
            if api_key and not self._check_rate_limit(api_key):
                return {"success": False, "error": "Rate limit exceeded"}
            
            # Check cache first
            cache_key = None
            if use_cache:
                cache_key = self._get_cache_key("search_documents", {
                    "query": query, "limit": limit
                })
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    self._log_request("search_documents", api_key or "anonymous", 
                                    True, time.time() - start_time, 
                                    cached_result.get("count", 0))
                    return cached_result
            
            # Perform search (placeholder - would integrate with actual search)
            results = self._perform_search(query, limit)
            
            # Prepare result
            result = {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "cached": False,
                "execution_time": time.time() - start_time
            }
            
            # Cache result
            if use_cache and cache_key:
                self._set_cache(cache_key, result, ttl=1800)  # 30 minutes
            
            # Log request
            self._log_request("search_documents", api_key or "anonymous", 
                            True, time.time() - start_time, len(results))
            
            return result
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            self._log_request("search_documents", api_key or "anonymous", 
                            False, time.time() - start_time)
            return {
                "success": False,
                "error": "Search failed",
                "details": str(e)
            }
    
    def _perform_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Perform actual search (placeholder implementation)"""
        # This would integrate with your actual search implementation
        return [
            {
                "id": f"doc-{i}",
                "title": f"Document {i}",
                "similarity_score": 0.9 - (i * 0.1),
                "content_preview": f"This is document {i} content..."
            }
            for i in range(min(limit, 5))
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get server health status"""
        now = time.time()
        
        # Check Redis connection
        redis_healthy = True
        try:
            self.redis_client.ping()
        except:
            redis_healthy = False
        
        # Check database connection (placeholder)
        db_healthy = True
        
        # Overall health
        overall_healthy = redis_healthy and db_healthy
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "redis": "healthy" if redis_healthy else "unhealthy",
                "database": "healthy" if db_healthy else "unhealthy"
            },
            "metrics": self.metrics,
            "uptime": now - self.last_health_check
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics"""
        return {
            "requests_total": self.metrics["requests_total"],
            "requests_successful": self.metrics["requests_successful"],
            "requests_failed": self.metrics["requests_failed"],
            "success_rate": (
                self.metrics["requests_successful"] / self.metrics["requests_total"]
                if self.metrics["requests_total"] > 0 else 0
            ),
            "cache_hit_rate": (
                self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
                if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_metrics(self):
        """Reset server metrics"""
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        logger.info("Metrics reset")

def main():
    """Example usage of advanced MCP server"""
    server = AdvancedDocumentMCPServer()
    
    # Test health check
    health = server.get_health_status()
    print(f"Server health: {health['status']}")
    
    # Test search with caching
    print("\n=== Testing Search with Caching ===")
    result1 = server.search_documents("test query", limit=5, api_key="demo-key-123")
    print(f"First search: {result1['success']}, cached: {result1.get('cached', False)}")
    
    result2 = server.search_documents("test query", limit=5, api_key="demo-key-123")
    print(f"Second search: {result2['success']}, cached: {result2.get('cached', False)}")
    
    # Test rate limiting
    print("\n=== Testing Rate Limiting ===")
    for i in range(5):
        result = server.search_documents(f"query {i}", api_key="demo-key-123")
        print(f"Request {i+1}: {result['success']}")
    
    # Show metrics
    print("\n=== Server Metrics ===")
    metrics = server.get_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
