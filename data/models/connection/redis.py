"""Redis connection module for network simulation"""
import os
from redis.client import Redis
from redis_om import get_redis_connection

from config.config import get_config

# Global Redis connection
_redis_connection = None

def get_redis_conn() -> Redis:
    """Get or create Redis connection (singleton pattern)"""
    global _redis_connection
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

    # Configure redis-om URL first
    scheme = "rediss" if redis_config.ssl else "redis"
    redis_url = f"{scheme}://{redis_config.username}:{redis_config.password.get_secret_value()}@{redis_config.host}:{redis_config.port}/{redis_config.db}"
    os.environ["REDIS_OM_URL"] = redis_url

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
        raise Exception(f"Failed to connect to Redis: {str(e)}")
    return _redis_connection