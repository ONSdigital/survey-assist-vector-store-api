"""Tests for the SAYT suggestions route."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from survey_assist_embed_core.sayt import Suggestion

from survey_assist_vector_store_api.sayt_api import lifespan as lifespan_module
from survey_assist_vector_store_api.sayt_api import main as main_module
from tests.helpers import create_test_app


class FakeSuggester:  # pylint: disable=too-few-public-methods
    """Simple test double for the embed-core SAYT suggester."""

    def __init__(self) -> None:
        self.suggest_calls: list[tuple[str | None, int | None]] = []
        self.suggest_with_scores_calls: list[tuple[str | None, int | None]] = []

    def suggest(
        self,
        query: str | None,
        num_suggestions: int | None = None,
    ) -> list[str]:
        """Record inputs and return deterministic suggestion text."""
        self.suggest_calls.append((query, num_suggestions))
        return [
            "Software developer",
            "Software engineer",
        ]

    def suggest_with_scores(
        self,
        query: str | None,
        num_suggestions: int | None = None,
    ) -> list[Suggestion]:
        """Record inputs and return a deterministic set of suggestions."""
        self.suggest_with_scores_calls.append((query, num_suggestions))
        return [
            Suggestion(display_text="Software developer", score=0.95),
            Suggestion(display_text="Software engineer", score=0.91),
        ]


@pytest.mark.api
def test_suggestions_route_uses_suggester_from_request_state(
    create_sayt_app_with_suggester,
) -> None:
    """Verify that the route reads the startup-loaded suggester from request state."""
    fake_suggester = FakeSuggester()
    app = create_sayt_app_with_suggester(fake_suggester)

    with TestClient(app) as client:
        response = client.post(
            "/v1/suggestions",
            json={"query": "soft", "num_suggestions": 2},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "suggestions": [
            "Software developer",
            "Software engineer",
        ]
    }
    assert fake_suggester.suggest_calls == [("soft", 2)]
    assert not fake_suggester.suggest_with_scores_calls


@pytest.mark.api
def test_scored_suggestions_route_uses_suggester_from_request_state(
    create_sayt_app_with_suggester,
) -> None:
    """Verify that the scored route returns suggestions with scores."""
    fake_suggester = FakeSuggester()
    app = create_sayt_app_with_suggester(fake_suggester)

    with TestClient(app) as client:
        response = client.post(
            "/v1/scored-suggestions",
            json={"query": "soft", "num_suggestions": 2},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "suggestions": [
            {"display_text": "Software developer", "score": 0.95},
            {"display_text": "Software engineer", "score": 0.91},
        ]
    }
    assert not fake_suggester.suggest_calls
    assert fake_suggester.suggest_with_scores_calls == [("soft", 2)]


@pytest.mark.api
def test_suggestions_route_accepts_null_query(
    create_sayt_app_with_suggester,
) -> None:
    """Verify that the route passes null queries through to the suggester."""
    fake_suggester = FakeSuggester()
    app = create_sayt_app_with_suggester(fake_suggester)

    with TestClient(app) as client:
        response = client.post("/v1/suggestions", json={"query": None})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "suggestions": [
            "Software developer",
            "Software engineer",
        ]
    }
    assert fake_suggester.suggest_calls == [(None, None)]
    assert not fake_suggester.suggest_with_scores_calls


@pytest.mark.api
def test_create_app_loads_suggester_on_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the concrete app constructs the suggester during startup."""
    fake_suggester = FakeSuggester()
    settings_marker = object()
    seen_settings: list[object] = []

    def fake_get_settings() -> object:
        return settings_marker

    def fake_load_suggester(settings: object) -> FakeSuggester:
        seen_settings.append(settings)
        return fake_suggester

    monkeypatch.setattr(lifespan_module, "get_settings", fake_get_settings)
    monkeypatch.setattr(lifespan_module, "load_suggester", fake_load_suggester)

    app = create_test_app(
        main_module,
        lifespan=main_module.sayt_lifespan,
    )

    with TestClient(app) as client:
        response = client.post("/v1/suggestions", json={"query": "soft"})

    assert response.status_code == status.HTTP_200_OK
    assert seen_settings == [settings_marker]
    assert fake_suggester.suggest_calls == [("soft", None)]
    assert not fake_suggester.suggest_with_scores_calls
