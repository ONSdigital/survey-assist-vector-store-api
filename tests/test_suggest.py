"""Tests for the SAYT suggest route."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from survey_assist_embed_core.sayt import Suggestion


class FakeSuggester:  # pylint: disable=too-few-public-methods
    """Simple test double for the embed-core SAYT suggester."""

    def __init__(self) -> None:
        self.calls: list[tuple[str | None, int | None]] = []

    def suggest_with_scores(
        self,
        query: str | None,
        num_suggestions: int | None = None,
    ) -> list[Suggestion]:
        """Record inputs and return a deterministic set of suggestions."""
        self.calls.append((query, num_suggestions))
        return [
            Suggestion(display_text="Software developer", score=0.95),
            Suggestion(display_text="Software engineer", score=0.91),
        ]


@pytest.mark.api
def test_suggest_route_uses_suggester_from_request_state(
    create_sayt_app_with_suggester,
) -> None:
    """Verify that the route reads the startup-loaded suggester from request state."""
    fake_suggester = FakeSuggester()
    app = create_sayt_app_with_suggester(fake_suggester)

    with TestClient(app) as client:
        response = client.post(
            "/v1/suggest",
            json={"query": "soft", "num_suggestions": 2},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"display_text": "Software developer", "score": 0.95},
        {"display_text": "Software engineer", "score": 0.91},
    ]
    assert fake_suggester.calls == [("soft", 2)]


@pytest.mark.api
def test_suggest_route_accepts_null_query(
    create_sayt_app_with_suggester,
) -> None:
    """Verify that the route passes null queries through to the suggester."""
    fake_suggester = FakeSuggester()
    app = create_sayt_app_with_suggester(fake_suggester)

    with TestClient(app) as client:
        response = client.post("/v1/suggest", json={"query": None})

    assert response.status_code == status.HTTP_200_OK
    assert fake_suggester.calls == [(None, None)]
