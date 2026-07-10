"""Build persisted vector-store artifacts for API deployments."""

import sys

from survey_assist_embed_core import build_embedding_index
from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.api.deps.settings import BuildVectorStoreSettings

logger = get_logger(__name__)


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
