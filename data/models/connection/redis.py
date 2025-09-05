"""Redis connection module for network simulation"""
import os
from redis.client import Redis
from redis_om import get_redis_connection

from config.config import get_config

# Global Redis connection
_redis_connection = None
_redis_failed = False  # Cache failed state to avoid repeated warnings

def get_redis_conn() -> Redis:
    """Get or create Redis connection (singleton pattern)"""
    global _redis_connection, _redis_failed
    
    # Check if Redis is disabled
    if os.getenv("USE_REDIS", "1") == "0":
        return None
    
    # If we already failed, don't try again
    if _redis_failed:
        return None
    try:
        # Try to ping the existing connection
        if _redis_connection is not None:
            _redis_connection.ping()
            return _redis_connection
    except Exception:
        # If ping fails, close the old connection if it exists
        if _redis_connection is not None:
            try:
                _redis_connection.close()
            except:
                pass
            _redis_connection = None

    # Create new connection
    config = get_config()
    redis_config = config.redis

    # Debug: Print Redis configuration
    print(f"Redis config - Host: {redis_config.host}, Port: {redis_config.port}, DB: {redis_config.db}, SSL: {redis_config.ssl}")

    # Configure redis-om URL first
    scheme = "rediss" if redis_config.ssl else "redis"
    redis_url = f"{scheme}://{redis_config.username}:{redis_config.password.get_secret_value()}@{redis_config.host}:{redis_config.port}/{redis_config.db}"
    os.environ["REDIS_OM_URL"] = redis_url
    print(f"Redis URL: {redis_url}")

    # Create new connection with connection pooling settings
    _redis_connection = Redis(
        host=redis_config.host,
        port=redis_config.port,
        username=redis_config.username,
        password=redis_config.password.get_secret_value(),
        db=redis_config.db,
        decode_responses=True,
        ssl=redis_config.ssl,
        max_connections=2,  # Limit concurrent connections
        socket_timeout=5,   # Add timeout
        retry_on_timeout=True
    )
    
    try:
        _redis_connection.ping()
    except Exception as e:
        if _redis_connection is not None:
            _redis_connection.close()
        print(f"Warning: Redis connection failed: {str(e)}")
        print("Backend will run without Redis functionality")
        _redis_connection = None
        _redis_failed = True  # Mark as failed to avoid repeated attempts
    return _redis_connection