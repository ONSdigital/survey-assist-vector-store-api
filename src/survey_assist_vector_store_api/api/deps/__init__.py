"""Dependency helpers for the vector-store API."""

from survey_assist_vector_store_api.api.deps.settings import (
    VectorStoreApiSettings,
    get_settings,
)
from survey_assist_vector_store_api.api.deps.vector_store import (
    build_embedding_handler,
    get_embedding_handler,
)

__all__ = [
    "VectorStoreApiSettings",
    "build_embedding_handler",
    "get_embedding_handler",
    "get_settings",
]
