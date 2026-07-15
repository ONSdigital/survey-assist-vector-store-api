"""Request models for vector-store search endpoints."""

from pydantic import BaseModel


class SearchIndexRequest(BaseModel):
    """Payload for the search-index route.

    Attributes:
        query: Ordered query fragments combined into cumulative searches.
    """

    query: list[str]
