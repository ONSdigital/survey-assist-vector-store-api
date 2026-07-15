"""Routes for SAYT suggestion endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from survey_assist_embed_core.sayt import SAYTSuggester

from survey_assist_vector_store_api.sayt_api.deps.suggester import get_suggester
from survey_assist_vector_store_api.sayt_api.models.suggest import (
    SuggestItem,
    SuggestRequest,
    SuggestResponse,
)

router = APIRouter(tags=["sayt"])


@router.post("/suggest", response_model=SuggestResponse)
def suggest(
    payload: SuggestRequest,
    suggester: Annotated[SAYTSuggester, Depends(get_suggester)],
) -> SuggestResponse:
    """Return ranked SAYT suggestions with scores."""
    suggestions = suggester.suggest_with_scores(
        payload.query,
        num_suggestions=payload.num_suggestions,
    )
    return SuggestResponse(
        suggestions=[
            SuggestItem(display_text=item.display_text, score=item.score)
            for item in suggestions
        ]
    )
