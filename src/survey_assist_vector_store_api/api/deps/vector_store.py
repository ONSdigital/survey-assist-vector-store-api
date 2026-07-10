"""Dependency helpers for loading and accessing the embedding handler."""

from typing import cast

from fastapi import Request
from survey_assist_embed_core import ClassifaiVectorBackend, EmbeddingHandler

from survey_assist_vector_store_api.api.deps.settings import RuntimeVectorStoreSettings


def load_embedding_handler(settings: RuntimeVectorStoreSettings) -> EmbeddingHandler:
    """Construct the startup-loaded embedding handler from application settings.

    Args:
        settings: Runtime settings supplying the vector-store location and
            search behaviour.

    Returns:
        Configured embedding handler ready to serve search requests.
    """
    return EmbeddingHandler(
        db_dir=settings.vector_store_dir,
        k_matches=settings.vector_store_k_matches,
        backend=ClassifaiVectorBackend(),
    )


def get_embedding_handler(request: Request) -> EmbeddingHandler:
    """Return the embedding handler attached to application state.

    Args:
        request: Current request whose state carries the shared handler.

    Returns:
        Startup-loaded embedding handler.

    Raises:
        RuntimeError: If the application lifespan did not attach a handler.
    """
    handler = getattr(request.state, "embedding_handler", None)
    if handler is None:
        raise RuntimeError("Embedding handler is not configured in application state.")

    return cast(EmbeddingHandler, handler)
