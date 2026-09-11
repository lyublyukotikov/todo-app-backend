from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    cors_allow_origins: list[str]


def get_settings() -> Settings:
    return Settings(
        DATABASE_URL="postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres",
        cors_allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
    )
