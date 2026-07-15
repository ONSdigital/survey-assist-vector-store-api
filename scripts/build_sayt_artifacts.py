"""Build persisted SAYT artifacts for API deployments."""

import sys

from survey_assist_embed_core.sayt import SAYTBuilder
from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.sayt_api.deps.settings import (
    BuildSaytArtifactsSettings,
)

logger = get_logger(__name__)


def main() -> int:
    """Build SAYT artifacts from CLI arguments or environment values."""
    config = BuildSaytArtifactsSettings()
    source_file = config.sayt_source_file
    if source_file is None:
        raise SystemExit(
            "Provide --sayt-source-file or set the SAYT_SOURCE_FILE "
            "environment variable."
        )

    logger.info(
        "Building SAYT artifacts",
        source_file=source_file,
        artifact_dir=config.sayt_artifact_dir,
    )

    builder = SAYTBuilder.from_csv(
        source_file,
        search_text_col=config.search_text_col,
        display_text_col=config.display_text_col,
        min_chars=config.min_chars,
        max_suggestions=config.max_suggestions,
    )
    builder.build_artifact(
        config.sayt_artifact_dir,
        overwrite=config.overwrite,
    )

    logger.info(
        "SAYT artifacts built successfully",
        artifact_dir=config.sayt_artifact_dir,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
