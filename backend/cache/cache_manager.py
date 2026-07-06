import time
from typing import Any, Dict

class CacheManager:
    """
    Intelligent caching to avoid duplicate API calls and respect expiration times.
    Includes Smart cache expiration, Automatic refresh (simulated), Partial invalidation,
    and Cache statistics.
    """
    def __init__(self):
        self.cache: Dict[str, dict] = {}
        self.hits = 0
        self.misses = 0

    def get(self, cache_key: str) -> Any:
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() < entry["expires_at"]:
                self.hits += 1
                return entry["data"]
            else:
                # Expired
                del self.cache[cache_key]
        self.misses += 1
        return None

    def set(self, cache_key: str, data: Any, ttl_seconds: int = 300):
        self.cache[cache_key] = {
            "data": data,
            "expires_at": time.time() + ttl_seconds
        }

    def invalidate(self, cache_key: str):
        if cache_key in self.cache:
            del self.cache[cache_key]

    def invalidate_prefix(self, prefix: str):
        """Partial invalidation based on a prefix string (e.g. tool name)."""
        keys_to_delete = [k for k in self.cache.keys() if k.startswith(prefix)]
        for k in keys_to_delete:
            del self.cache[k]

    def get_stats(self) -> dict:
        total = self.hits + self.misses
        hit_ratio = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio_percent": round(hit_ratio, 2),
            "total_cached_items": len(self.cache)
        }

cache_manager = CacheManager()
