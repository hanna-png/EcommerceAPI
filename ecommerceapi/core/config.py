import os
from dataclasses import dataclass


# frozen=True means object is immutable
@dataclass(frozen=True)
class Settings:
    """
    Container for storing configuration settings loaded from .env file.
    """

    database_url: str


def get_settings() -> Settings:
    """
    Loads settings from environment variables into a Settings object and returns it.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return Settings(database_url=database_url)


settings = get_settings()
