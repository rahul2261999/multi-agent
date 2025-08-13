from __future__ import annotations

from typing import Dict, Optional

import redis.asyncio as redis
from dotenv import load_dotenv
from langgraph.checkpoint.redis import AsyncRedisSaver

from src.libs.logger.manager import get_logger
from src.libs.redis.redis_setting import RedisSettings


load_dotenv()
logger = get_logger(__name__)

# Singleton instances
_redis_client: Optional[redis.Redis] = None
_checkpoint_savers: Dict[int, AsyncRedisSaver] = {}

# Lazily load settings to avoid unnecessary environment parsing at import time
_settings: Optional[RedisSettings] = None


def _get_settings() -> RedisSettings:
  """Return cached `RedisSettings` instance."""
  global _settings
  if _settings is None:
    _settings = RedisSettings()  # type: ignore[call-arg]
    logger.debug(
      f"Loaded Redis settings: {_settings.model_dump(exclude={'password'})}"
    )
  return _settings


def get_redis_client() -> redis.Redis:
  """Return a singleton instance of the asyncio Redis client.

  The connection parameters are loaded from environment variables via
  `RedisSettings`. Subsequent calls return the same client instance to
  avoid creating multiple connection pools.
  """
  global _redis_client

  if _redis_client is None:
    settings = _get_settings()

    _redis_client = redis.Redis(
      host=settings.host,
      port=settings.port,
      username=settings.username,
      password=settings.password,
      db=settings.db,
      decode_responses=True,
      ssl=settings.ssl,
      ssl_cert_reqs=settings.ssl_cert_reqs or "none",  # For Azure Redis Cache, often "none" is sufficient
      socket_timeout=30,  # 30 seconds timeout for socket operations
      socket_connect_timeout=30,  # 30 seconds timeout for connection establishment
      retry_on_timeout=True,  # Retry on timeout
      health_check_interval=30  # Health check every 30 seconds
    )

    logger.info(
      f"Initialized Redis client (host={settings.host}, port={settings.port}, db={settings.db}, ssl={settings.ssl})",
    )
  return _redis_client


async def init_checkpoint_saver(ttl: int = 15) -> AsyncRedisSaver:
  """Return a singleton `AsyncRedisSaver` instance for the given TTL (in minutes).

  A distinct saver is created per TTL value and cached for subsequent calls.
  """
  if ttl not in _checkpoint_savers:
    redis_client = get_redis_client()
    
    saver = AsyncRedisSaver(redis_client=redis_client, ttl={"default_ttl": ttl})
    await saver.asetup()

    _checkpoint_savers[ttl] = saver

    logger.info(f"Redis checkpoint saver initialized (TTL={ttl} minutes)")
    

  return _checkpoint_savers[ttl]

def get_checkpoint_saver(ttl: int = 15) -> AsyncRedisSaver:
  """Return a singleton `AsyncRedisSaver` instance for the given TTL (in minutes).
  """
  if ttl not in _checkpoint_savers:
    raise ValueError(f"Checkpoint saver for TTL {ttl} not initialized")
  
  return _checkpoint_savers[ttl]




__all__ = [
  "RedisSettings",
  "get_redis_client",
  "get_checkpoint_saver",
]
