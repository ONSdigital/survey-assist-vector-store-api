"""Request and response models for SAYT suggestions endpoints."""

from pydantic import BaseModel
from survey_assist_embed_core.sayt import Suggestion


class SuggestionsRequest(BaseModel):
    """Payload for the SAYT suggestions route."""

    query: str | None = None
    num_suggestions: int | None = None


class SuggestionsResponse(BaseModel):
    """Response payload for the SAYT suggestions route."""

    suggestions: list[str]


class ScoredSuggestionsResponse(BaseModel):
    """Response payload for the SAYT scored-suggestions route."""

    suggestions: list[Suggestion]
