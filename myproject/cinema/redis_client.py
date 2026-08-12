import redis
from django.conf import settings

_client = None

def get_client():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _client

def redis_available():
    try:
        return get_client().ping()
    except redis.RedisError:
        return False