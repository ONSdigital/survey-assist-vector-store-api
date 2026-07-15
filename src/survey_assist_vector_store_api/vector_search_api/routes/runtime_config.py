"""Routes for runtime embedding configuration."""

from typing import Annotated

from fastapi import APIRouter, Depends
from survey_assist_embed_core import EmbeddingHandler
from survey_assist_embed_core.models import EmbeddingStatus

from survey_assist_vector_store_api.vector_search_api.deps.vector_store import (
    get_embedding_handler,
)

router = APIRouter(tags=["runtime"])


@router.get("/runtime-config", response_model=EmbeddingStatus)
def runtime_config(
    handler: Annotated[EmbeddingHandler, Depends(get_embedding_handler)],
) -> EmbeddingStatus:
    """Return the effective configuration of the loaded embedding handler."""
    return handler.get_embed_config()
