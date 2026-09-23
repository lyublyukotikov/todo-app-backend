from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    redis_url: str
    cache_ttl_seconds: int
    cache_tasks_key: str
    cache_categories_key: str
    cors_allow_origins: list[str]


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def get_settings() -> Settings:
    cors_origins = require_env("CORS_ALLOW_ORIGINS")

    return Settings(
        DATABASE_URL=require_env("DATABASE_URL"),
        redis_url=require_env("REDIS_URL"),
        cors_allow_origins=[
            origin.strip()
            for origin in cors_origins.split(",")
            if origin.strip()
        ],
        cache_tasks_key="cache:tasks_list",
        cache_categories_key="cache:categories_list",
        cache_ttl_seconds=3600,
    )
