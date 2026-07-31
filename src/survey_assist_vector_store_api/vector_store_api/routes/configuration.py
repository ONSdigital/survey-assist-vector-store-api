"""Routes for vector-store configuration."""

from typing import Annotated

from fastapi import APIRouter, Depends
from survey_assist_embed_core import EmbeddingHandler
from survey_assist_embed_core.models import EmbeddingStatus

from survey_assist_vector_store_api.vector_store_api.deps.vector_store import (
    get_embedding_handler,
)

router = APIRouter(tags=["configuration"])


@router.get("/configuration", response_model=EmbeddingStatus)
def configuration(
    handler: Annotated[EmbeddingHandler, Depends(get_embedding_handler)],
) -> EmbeddingStatus:
    """Return the effective configuration of the loaded embedding handler."""
    return handler.get_embed_config()
