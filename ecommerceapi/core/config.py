import os
from dataclasses import dataclass


# frozen=True means object is immutable
@dataclass(frozen=True)
class Settings:
    """
    Container for storing configuration settings loaded from .env file.
    """

    database_url: str
    jwt_secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


def get_settings() -> Settings:
    """
    Loads settings from environment variables into a Settings object and returns it.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is not set")

    access_m = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    refresh_d = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    return Settings(
        database_url=database_url,
        jwt_secret_key=secret,
        access_token_expire_minutes=access_m,
        refresh_token_expire_days=refresh_d,
    )


settings = get_settings()
