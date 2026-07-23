"""Routes for SAYT suggestions endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from survey_assist_embed_core.sayt import SAYTSuggester

from survey_assist_vector_store_api.sayt_api.deps.suggester import get_suggester
from survey_assist_vector_store_api.sayt_api.models.suggestions import (
    ScoredSuggestionsResponse,
    SuggestionsRequest,
    SuggestionsResponse,
)

router = APIRouter(tags=["sayt"])


@router.post("/suggestions", response_model=SuggestionsResponse)
def suggest(
    payload: SuggestionsRequest,
    suggester: Annotated[SAYTSuggester, Depends(get_suggester)],
) -> SuggestionsResponse:
    """Return ranked SAYT suggestions without scores."""
    return SuggestionsResponse(
        suggestions=suggester.suggest(
            payload.query,
            num_suggestions=payload.num_suggestions,
        )
    )


@router.post("/scored-suggestions", response_model=ScoredSuggestionsResponse)
def scored_suggestions(
    payload: SuggestionsRequest,
    suggester: Annotated[SAYTSuggester, Depends(get_suggester)],
) -> ScoredSuggestionsResponse:
    """Return ranked SAYT suggestions with scores."""
    return ScoredSuggestionsResponse(
        suggestions=suggester.suggest_with_scores(
            payload.query,
            num_suggestions=payload.num_suggestions,
        )
    )
