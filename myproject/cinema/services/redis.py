import redis
from django.conf import settings
import threading

class RedisClient:
    _instance = None
    _client = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._client = None
        return cls._instance

    def get_client(self):
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._client = redis.Redis.from_url(
                        settings.REDIS_URL,
                        decode_responses=True,
                    )
        return self._client

    def availabel(self) -> bool:
        try:
            return bool(self.get_client().ping())
        except redis.RedisError:
            return False

def get_redis() -> RedisClient:
    return RedisClient()

def get_client():
    return get_redis().get_client()

def redis_available() -> bool:
    return get_redis().availabel()
