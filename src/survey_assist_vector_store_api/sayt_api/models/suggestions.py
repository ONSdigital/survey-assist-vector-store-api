"""Request and response models for SAYT suggestions endpoints."""

from pydantic import AliasChoices, BaseModel, Field
from survey_assist_embed_core.sayt import Suggestion


class SuggestionsRequest(BaseModel):
    """Payload for the SAYT suggestions route."""

    query: str = Field(
        ...,
        description="Raw query text used to retrieve suggestions.",
    )
    limit: int | None = Field(
        default=None,
        gt=0,
        validation_alias=AliasChoices("limit", "num_suggestions"),
        description=(
            "Optional positive per-request suggestion limit. When omitted, "
            "the loaded SAYT artifact's built-in default is used, which is "
            "configured at artifact build time."
        ),
    )


class SuggestionsResponse(BaseModel):
    """Response payload for the SAYT suggestions route."""

    suggestions: list[Suggestion]
