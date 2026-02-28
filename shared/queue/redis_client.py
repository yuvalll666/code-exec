import redis
from shared.core.config import settings

r = redis.Redis.from_url(
    settings.REDIS_URL, 
    decode_responses=True
)

def check_redis():
    """A simple helper to verify the connection is alive."""
    try:
        return r.ping()
    except redis.ConnectionError as e:
        print(f"❌ Redis Connection Error: {e}")
        return False