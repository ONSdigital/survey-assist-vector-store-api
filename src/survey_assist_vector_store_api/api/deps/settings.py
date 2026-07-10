"""Application settings for the vector-store API."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from survey_assist_embed_core.adapters.classifai.vector_backend import (
    DEFAULT_CLASSIFAI_EMBEDDING_MODEL_NAME,
)

DEFAULT_VECTOR_STORE_DIR = "vector_store"


class BuildVectorStoreSettings(BaseSettings):
    """Settings for building persisted vector-store artifacts."""

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_kebab_case=True,
        extra="ignore",
        populate_by_name=True,
        env_file=".env",
    )

    index_source_file: str | None = Field(
        default=None,
        description=(
            "Local path or GCS URI for the source data. Falls back to the "
            "INDEX_SOURCE_FILE environment variable."
        ),
        validation_alias=AliasChoices("source", "src"),
    )
    vector_store_dir: str = Field(
        default=DEFAULT_VECTOR_STORE_DIR,
        description=(
            "Directory where persisted artifacts should be written. Falls back "
            f"to VECTOR_STORE_DIR, then {DEFAULT_VECTOR_STORE_DIR}."
        ),
        validation_alias=AliasChoices("store", "db_dir"),
    )
    embedding_model_name: str = Field(
        default=DEFAULT_CLASSIFAI_EMBEDDING_MODEL_NAME,
        description=(
            "Embedding model name used during vectorisation. Falls back to the "
            "EMBEDDING_MODEL_NAME environment variable, then the "
            "embed-core default model."
        ),
        validation_alias=AliasChoices("model"),
    )


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

    vector_store_dir: str = DEFAULT_VECTOR_STORE_DIR
    vector_store_k_matches: int = 20


@lru_cache(maxsize=1)
def get_settings() -> RuntimeVectorStoreSettings:
    """Return cached application settings loaded from environment variables."""
    return RuntimeVectorStoreSettings()
