"""Request and response models for SAYT suggestion endpoints."""

from pydantic import BaseModel


class SuggestRequest(BaseModel):
    """Payload for the SAYT suggest route."""

    query: str | None = None
    num_suggestions: int | None = None


class SuggestItem(BaseModel):
    """Single SAYT suggestion with its combined score."""

    display_text: str
    score: float


class SuggestResponse(BaseModel):
    """Response model for the SAYT suggest route."""

    suggestions: list[SuggestItem]
