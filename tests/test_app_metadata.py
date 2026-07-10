"""Tests for application metadata helpers."""

import pytest

from survey_assist_vector_store_api.api import app_metadata


@pytest.mark.api
def test_resolve_app_metadata_returns_explicit_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that explicit metadata overrides are returned unchanged."""
    monkeypatch.setattr(
        app_metadata,
        "resolve_installed_version",
        lambda _package_distribution_name: pytest.fail(
            "resolve_installed_version should not be used for explicit overrides"
        ),
    )

    resolved_metadata = app_metadata.resolve_app_metadata(
        title="Custom API",
        description="Custom description",
        root_message="Custom API is running",
        version="9.9.9",
    )

    assert resolved_metadata == (
        "Custom API",
        "Custom description",
        "Custom API is running",
        "9.9.9",
    )


@pytest.mark.api
def test_build_default_app_description_includes_package_versions() -> None:
    """Verify that the default docs description includes both package versions."""
    description = app_metadata.build_default_app_description(
        api_version="1.2.3",
        embed_core_version="4.5.6",
    )

    assert description == (
        "API for interacting with the vector store\n\n"
        "Package versions:\n"
        "- survey-assist-vector-store-api: 1.2.3\n"
        "- survey-assist-embed-core: 4.5.6"
    )


@pytest.mark.api
def test_resolve_app_metadata_uses_versioned_default_description() -> None:
    """Verify that missing metadata fields fall back to versioned defaults."""
    versions = {
        app_metadata.PACKAGE_DISTRIBUTION_NAME: "1.2.3",
        app_metadata.EMBED_CORE_PACKAGE_DISTRIBUTION_NAME: "4.5.6",
    }

    def _resolve_installed_version(package_distribution_name: str) -> str:
        return versions[package_distribution_name]

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        app_metadata,
        "resolve_installed_version",
        _resolve_installed_version,
    )

    resolved_metadata = app_metadata.resolve_app_metadata(
        title=None,
        description=None,
        root_message=None,
        version=None,
    )

    monkeypatch.undo()

    assert resolved_metadata == (
        app_metadata.DEFAULT_APP_TITLE,
        app_metadata.build_default_app_description(
            api_version="1.2.3",
            embed_core_version="4.5.6",
        ),
        app_metadata.DEFAULT_ROOT_MESSAGE,
        "1.2.3",
    )


@pytest.mark.api
def test_resolve_installed_version_uses_package_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that installed package metadata is used when available."""
    monkeypatch.setattr(app_metadata, "version", lambda _name: "1.2.3")

    assert app_metadata.resolve_installed_version("any-package") == "1.2.3"


@pytest.mark.api
def test_resolve_installed_version_falls_back_when_package_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that missing package metadata falls back to unknown."""

    def _raise_package_not_found(_name: str) -> str:
        raise app_metadata.PackageNotFoundError

    monkeypatch.setattr(
        app_metadata,
        "version",
        _raise_package_not_found,
    )

    assert app_metadata.resolve_installed_version("any-package") == "unknown"
