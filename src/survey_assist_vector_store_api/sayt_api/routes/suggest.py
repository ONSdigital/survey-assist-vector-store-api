"""Routes for SAYT suggestion endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from survey_assist_embed_core.sayt import SAYTSuggester, Suggestion

from survey_assist_vector_store_api.sayt_api.deps.suggester import get_suggester
from survey_assist_vector_store_api.sayt_api.models.suggest import SuggestRequest

router = APIRouter(tags=["sayt"])


@router.post("/suggest", response_model=list[Suggestion])
def suggest(
    payload: SuggestRequest,
    suggester: Annotated[SAYTSuggester, Depends(get_suggester)],
) -> list[Suggestion]:
    """Return ranked SAYT suggestions with scores."""
    return suggester.suggest_with_scores(
        payload.query,
        num_suggestions=payload.num_suggestions,
    )
