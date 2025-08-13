from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
  """Configuration for connecting to a Redis instance.

  Values are populated from environment variables and can be overridden
  by explicitly instantiating the class with keyword arguments.
  """

  host: str = Field(
    default="localhost", alias="REDIS_HOST", description="Hostname of the Redis server"
  )
  port: int = Field(
    default=6379, alias="REDIS_PORT", description="Port on which Redis is listening"
  )
  username: Optional[str] = Field(
    default=None,
    alias="REDIS_USERNAME",
    description="Username for Redis authentication, if set",
  )
  password: Optional[str] = Field(
    default=None,
    alias="REDIS_PASSWORD",
    description="Password for Redis authentication, if set",
  )
  db: int = Field(
    default=0, alias="REDIS_DB", description="Redis database number to use"
  )

  ssl: bool = Field(
      default=False,
      alias="REDIS_SSL",
      description="Whether to use SSL for Redis connection"
  )
  ssl_cert_reqs: Optional[str] = Field(
      default=None,
      alias="REDIS_SSL_CERT_REQS",
      description="SSL certificate requirements ('none', 'optional', or 'required')"
  )

  # Pydantic v2 configuration
  model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

