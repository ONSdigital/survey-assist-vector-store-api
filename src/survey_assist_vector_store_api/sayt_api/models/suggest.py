"""Request and response models for SAYT suggestion endpoints."""

from pydantic import BaseModel


class SuggestRequest(BaseModel):
    """Payload for the SAYT suggest route."""

    query: str | None = None
    num_suggestions: int | None = None
