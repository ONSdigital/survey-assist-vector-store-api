"""Request and response models for SAYT suggestions endpoints."""

from pydantic import BaseModel, Field
from survey_assist_embed_core.sayt import Suggestion


class SuggestionsRequest(BaseModel):
    """Payload for the SAYT suggestions route."""

    query: str | None = Field(
        default=None,
        description="Raw query text used to retrieve suggestions.",
    )
    num_suggestions: int | None = Field(
        default=None,
        description=(
            "Optional per-request suggestion limit. When omitted, the loaded "
            "SAYT artifact's built-in default is used, which comes from "
            "MAX_SUGGESTIONS at artifact build time."
        ),
    )


class SuggestionsResponse(BaseModel):
    """Response payload for the SAYT suggestions route."""

    suggestions: list[str]


class ScoredSuggestionsResponse(BaseModel):
    """Response payload for the SAYT scored-suggestions route."""

    suggestions: list[Suggestion]
