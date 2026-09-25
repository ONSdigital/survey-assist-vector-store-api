"""Routes for SAYT suggestions endpoints."""

from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, Depends
from survey_assist_embed_core.sayt import SAYTSuggester
from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.sayt_api.deps.suggester import get_suggester
from survey_assist_vector_store_api.sayt_api.models.suggestions import (
    SuggestionsRequest,
    SuggestionsResponse,
)

router = APIRouter(tags=["sayt"])
logger = get_logger(__name__)


@router.post("/suggestions", response_model=SuggestionsResponse)
def suggest(
    payload: SuggestionsRequest,
    suggester: Annotated[SAYTSuggester, Depends(get_suggester)],
) -> SuggestionsResponse:
    """Return ranked SAYT suggestions with scores."""
    start_time = perf_counter()
    suggestions = suggester.suggest_with_scores(
        payload.query,
        num_suggestions=payload.limit,
    )
    elapsed_time_ms = round((perf_counter() - start_time) * 1000, 2)
    logger.info(
        "SAYT suggestion request completed",
        query=payload.query,
        num_suggestions=payload.limit,
        elapsed_time_ms=elapsed_time_ms,
        returned_suggestions=len(suggestions),
    )
    return SuggestionsResponse(suggestions=suggestions)
