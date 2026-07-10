"""Application settings for the vector-store API."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeVectorStoreSettings(BaseSettings):
    """Runtime configuration for the vector-store API.

    Attributes:
        vector_store_dir: Local directory or GCS URI for persisted vector-store
            artifacts.
        vector_store_k_matches: Maximum number of ranked matches returned for
            each search request.
    """

    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
        env_file=".env",
    )

    vector_store_dir: str = "vector_store"
    vector_store_k_matches: int = 20


@lru_cache(maxsize=1)
def get_settings() -> RuntimeVectorStoreSettings:
    """Return cached application settings loaded from environment variables."""
    return RuntimeVectorStoreSettings()
