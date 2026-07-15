"""Tests for SAYT dependency helpers."""

from types import SimpleNamespace

import pytest

from survey_assist_vector_store_api.sayt_api.deps import suggester as suggester_module
from survey_assist_vector_store_api.sayt_api.deps.settings import RuntimeSaytSettings


@pytest.mark.api
def test_load_suggester_uses_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that the concrete loader wires settings into SAYTSuggester."""
    settings = RuntimeSaytSettings(sayt_artifact_dir="artifacts/sayt")
    loaded_paths: list[str] = []
    expected_suggester = object()

    class FakeSuggester:  # pylint: disable=too-few-public-methods
        """Constructor double for the concrete suggester."""

        @classmethod
        def from_artifact(cls, artifact_dir: str) -> object:
            loaded_paths.append(artifact_dir)
            return expected_suggester

    monkeypatch.setattr(suggester_module, "SAYTSuggester", FakeSuggester)

    suggester = suggester_module.load_suggester(settings)

    assert suggester is expected_suggester
    assert loaded_paths == ["artifacts/sayt"]


@pytest.mark.api
def test_get_suggester_returns_state_suggester() -> None:
    """Verify that the request-state suggester is returned unchanged."""
    suggester = object()
    request = SimpleNamespace(state=SimpleNamespace(suggester=suggester))

    assert suggester_module.get_suggester(request) is suggester


@pytest.mark.api
def test_get_suggester_raises_when_suggester_missing() -> None:
    """Verify that a missing request-state suggester raises a clear error."""
    request = SimpleNamespace(state=SimpleNamespace())

    with pytest.raises(
        RuntimeError,
        match=r"SAYT suggester is not configured in application state\.",
    ):
        suggester_module.get_suggester(request)
