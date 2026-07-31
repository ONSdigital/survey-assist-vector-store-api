"""Application settings for the SAYT API and SAYT artifact builder."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from survey_assist_vector_store_api.shared.build_settings import BaseBuildSettings

DEFAULT_SAYT_ARTIFACT_DIR = "sayt_artifact"


class BuildSaytArtifactsSettings(BaseBuildSettings):
    """Settings for building persisted SAYT artifacts."""

    sayt_source_file: str | None = Field(
        default=None,
        description=(
            "Local path or GCS URI for the SAYT source CSV. Falls back to the "
            "SAYT_SOURCE_FILE environment variable."
        ),
        validation_alias=AliasChoices("source", "src"),
    )
    sayt_artifact_dir: str = Field(
        default=DEFAULT_SAYT_ARTIFACT_DIR,
        description=(
            "Directory where persisted SAYT artifacts should be written. Falls "
            f"back to SAYT_ARTIFACT_DIR, then {DEFAULT_SAYT_ARTIFACT_DIR}."
        ),
        validation_alias=AliasChoices("artifact", "artifact_dir"),
    )
    search_text_col: str = Field(
        default="search_text",
        description="CSV column used as the SAYT search text.",
        validation_alias=AliasChoices("search-col"),
    )
    display_text_col: str = Field(
        default="display_text",
        description="CSV column used as the SAYT display text.",
        validation_alias=AliasChoices("display-col"),
    )
    min_chars: int = Field(
        default=3,
        ge=3,
        description="Minimum query length baked into the built SAYT artifact.",
        validation_alias=AliasChoices("min"),
    )
    default_num_suggestions: int = Field(
        default=10,
        gt=0,
        le=100,
        description=(
            "Default suggestion count baked into the built SAYT artifact and "
            "used when requests omit limit."
        ),
        validation_alias=AliasChoices(
            "default_suggestions",
            "max_suggestions",
        ),
    )


class RuntimeSaytSettings(BaseSettings):
    """Runtime configuration for the SAYT API."""

    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
        env_file=".env",
    )

    sayt_artifact_dir: str = DEFAULT_SAYT_ARTIFACT_DIR


@lru_cache(maxsize=1)
def get_settings() -> RuntimeSaytSettings:
    """Return cached runtime settings loaded from environment variables."""
    return RuntimeSaytSettings()
