"""Tests for application metadata helpers."""

from types import SimpleNamespace

import pytest

from survey_assist_vector_store_api.api import app_metadata


@pytest.mark.api
def test_resolve_app_metadata_returns_explicit_overrides() -> None:
    """Verify that explicit metadata overrides are returned unchanged."""
    resolved_metadata = app_metadata.resolve_app_metadata(
        title="Custom API",
        description="Custom description",
        root_message="Custom API is running",
    )

    assert resolved_metadata == (
        "Custom API",
        "Custom description",
        "Custom API is running",
    )


@pytest.mark.api
def test_resolve_app_metadata_fills_missing_values_from_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that missing metadata fields are derived from the knowledgebase."""
    monkeypatch.setattr(
        app_metadata,
        "get_settings",
        lambda: SimpleNamespace(knowledgebase_name="SIC"),
    )

    resolved_metadata = app_metadata.resolve_app_metadata(
        title=None,
        description="Custom description",
        root_message=None,
    )

    assert resolved_metadata == (
        "SIC Vector Store API",
        "Custom description",
        "SIC Vector Store API is running",
    )


@pytest.mark.api
def test_resolve_default_version_uses_installed_package_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that package metadata is used when available."""
    monkeypatch.setattr(app_metadata, "version", lambda _name: "1.2.3")

    assert app_metadata.resolve_default_version() == "1.2.3"


@pytest.mark.api
def test_resolve_default_version_falls_back_when_package_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that missing package metadata falls back to a safe version."""

    def _raise_package_not_found(_name: str) -> str:
        raise app_metadata.PackageNotFoundError

    monkeypatch.setattr(
        app_metadata,
        "version",
        _raise_package_not_found,
    )

    assert app_metadata.resolve_default_version() == "0.0.0"
