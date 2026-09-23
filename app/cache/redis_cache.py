from typing import Any
import json

from redis import Redis


class RedisCacheBackend:
    def __init__(
        self,
        redis_url: str,
        cache_ttl_seconds: int | None = None,
    ):
        self.redis = Redis.from_url(
            redis_url,
            decode_responses=True,
        )
        self.cache_ttl_seconds = cache_ttl_seconds

    def set(self, key: str, value: Any) -> None:
        self.redis.set(
            name=key,
            value=json.dumps(value),
            ex=self.cache_ttl_seconds,
        )

    def get(self, key: str) -> Any | None:
        value = self.redis.get(name=key)

        if value is None:
            return None

        return json.loads(value)

    def delete(self, key: str) -> None:
        self.redis.delete(key)
