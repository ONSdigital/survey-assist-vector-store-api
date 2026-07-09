"""Build persisted vector-store artifacts for API deployments."""

import sys

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from survey_assist_embed_core import build_embedding_index
from survey_assist_embed_core.adapters.classifai.vector_backend import (
    DEFAULT_CLASSIFAI_EMBEDDING_MODEL_NAME,
)
from survey_assist_utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_VECTOR_STORE_DIR = "vector_store"


class BuildVectorStoreSettings(BaseSettings):
    """Settings for building persisted vector-store artifacts."""

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_kebab_case=True,
        cli_show_env_vars=True,
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


def main() -> int:
    """Build vector-store artifacts from CLI arguments or environment values."""
    config = BuildVectorStoreSettings()
    index_source_file = config.index_source_file
    if index_source_file is None:
        raise SystemExit(
            "Provide --index-source-file or set the INDEX_SOURCE_FILE "
            "environment variable."
        )
    logger.info(
        "Building vector-store artifacts",
        index_source_file=index_source_file,
        vector_store_dir=config.vector_store_dir,
    )

    build_embedding_index(
        index_source_file=index_source_file,
        output_dir=config.vector_store_dir,
        embedding_model_name=config.embedding_model_name,
    )

    logger.info(
        "Vector-store artifacts built successfully",
        vector_store_dir=config.vector_store_dir,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
