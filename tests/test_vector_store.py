"""Tests for vector-store dependency helpers."""

from types import SimpleNamespace

import pytest

from survey_assist_vector_store_api.api.deps import vector_store as vector_store_module
from survey_assist_vector_store_api.api.deps.settings import RuntimeVectorStoreSettings


class FakeEmbeddingHandler:  # pylint: disable=too-few-public-methods
    """Constructor double for the concrete embedding handler."""

    def __init__(self, *, db_dir: str, k_matches: int, backend: object):
        """Record the constructor arguments for assertion."""
        self.db_dir = db_dir
        self.k_matches = k_matches
        self.backend = backend


@pytest.mark.api
def test_build_embedding_handler_uses_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the concrete builder wires settings into the handler."""
    backend_marker = object()
    expected_k_matches = 12
    settings = RuntimeVectorStoreSettings(
        vector_store_dir="sic-store",
        vector_store_k_matches=expected_k_matches,
    )

    monkeypatch.setattr(
        vector_store_module,
        "ClassifaiVectorBackend",
        lambda: backend_marker,
    )
    monkeypatch.setattr(
        vector_store_module,
        "EmbeddingHandler",
        FakeEmbeddingHandler,
    )

    handler = vector_store_module.load_embedding_handler(settings)

    assert isinstance(handler, FakeEmbeddingHandler)
    assert vars(handler) == {
        "db_dir": "sic-store",
        "k_matches": expected_k_matches,
        "backend": backend_marker,
    }


@pytest.mark.api
def test_get_embedding_handler_returns_state_handler() -> None:
    """Verify that the request-state handler is returned unchanged."""
    handler = object()
    request = SimpleNamespace(state=SimpleNamespace(embedding_handler=handler))

    assert vector_store_module.get_embedding_handler(request) is handler


@pytest.mark.api
def test_get_embedding_handler_raises_when_handler_missing() -> None:
    """Verify that a missing request-state handler raises a clear error."""
    request = SimpleNamespace(state=SimpleNamespace())

    with pytest.raises(
        RuntimeError,
        match=r"Embedding handler is not configured in application state\.",
    ):
        vector_store_module.get_embedding_handler(request)
