import os
from typing import Optional, Any
import logging
import secrets
import uuid
from datetime import datetime
import redis

logger = logging.getLogger(__name__)

class RedisDB:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "localhost")
        self.redis = redis.ConnectionPool().from_url(self.redis_url)
        self.conn = None
        
    def connect(self):
        try:
            self.conn = redis.Redis().from_pool(self.redis)
            # Test the connection
            logger.info(f"Redis connected successfully to {self.redis_url}")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def disconnect(self):
        if self.redis:
            self.redis.close()
            self.redis = None

    def set_key(self, key: str, value: Any, ttl: int = None):
        if not self.conn:
            self.connect()
        logger.info(f"Setting key: {key} with value: {value} and ttl: {ttl}")
        self.conn.set(key, value, ex=ttl)
    
    def get_key(self, key: str) -> Any:
        if not self.conn:
            self.connect()
        logger.info(f"Getting key: {key}")
        return self.conn.get(key)
