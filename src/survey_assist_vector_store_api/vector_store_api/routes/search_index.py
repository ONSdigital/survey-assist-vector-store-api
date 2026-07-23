"""Routes for vector-store search endpoints."""

from typing import Annotated, cast

from fastapi import APIRouter, Depends
from survey_assist_embed_core import EmbeddingHandler
from survey_assist_embed_core.models import SearchIndexResponse

from survey_assist_vector_store_api.vector_store_api.deps.vector_store import (
    get_embedding_handler,
)
from survey_assist_vector_store_api.vector_store_api.models.search_index import (
    SearchIndexRequest,
)

router = APIRouter(tags=["search"])


@router.post("/search-index", response_model=SearchIndexResponse)
def search_index(
    payload: SearchIndexRequest,
    handler: Annotated[EmbeddingHandler, Depends(get_embedding_handler)],
) -> SearchIndexResponse:
    """Search the loaded vector store using cumulative query fragments.

    Args:
        payload: Query fragments submitted by the client.
        handler: Startup-loaded embedding handler injected from app state.

    Returns:
        Ranked, deduplicated search results.
    """
    return handler.search_index_multi(cast(list[str | None], payload.query))
