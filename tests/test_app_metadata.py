"""Tests for application metadata helpers."""

import importlib

import pytest

from survey_assist_vector_store_api.shared import app_metadata

DEFAULT_DESCRIPTION = "API for interacting with the vector store"


@pytest.mark.api
def test_build_default_app_description_includes_package_versions() -> None:
    """Verify that the default docs description includes both package versions."""
    description = app_metadata.build_default_app_description(
        description=DEFAULT_DESCRIPTION,
    )

    assert description == (
        "API for interacting with the vector store\n\n"
        "### Package versions:\n"
        f"- survey-assist-vector-store-api: `{app_metadata.API_PACKAGE_VERSION}`\n"
        f"- survey-assist-embed-core: `{app_metadata.EMBED_CORE_PACKAGE_VERSION}`"
    )


@pytest.mark.api
def test_module_resolves_package_versions_at_import_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that version constants are resolved when the module is imported."""
    seen_names: list[str] = []

    def fake_version(name: str) -> str:
        seen_names.append(name)
        return {
            "survey-assist-vector-store-api": "1.2.3",
            "survey-assist-embed-core": "4.5.6",
        }[name]

    monkeypatch.setattr(app_metadata.metadata, "version", fake_version)
    reloaded_module = importlib.reload(app_metadata)

    assert reloaded_module.API_PACKAGE_VERSION == "1.2.3"
    assert reloaded_module.EMBED_CORE_PACKAGE_VERSION == "4.5.6"
    assert seen_names == [
        "survey-assist-vector-store-api",
        "survey-assist-embed-core",
    ]


@pytest.mark.api
def test_module_falls_back_when_package_metadata_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that missing package metadata falls back to unknown."""

    def _raise_package_not_found(_name: str) -> str:
        raise app_metadata.metadata.PackageNotFoundError

    monkeypatch.setattr(app_metadata.metadata, "version", _raise_package_not_found)
    reloaded_module = importlib.reload(app_metadata)

    assert reloaded_module.API_PACKAGE_VERSION == "unknown"
    assert reloaded_module.EMBED_CORE_PACKAGE_VERSION == "unknown"
