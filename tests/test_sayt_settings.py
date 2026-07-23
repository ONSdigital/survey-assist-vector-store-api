"""Tests for SAYT API settings."""

import pytest

from survey_assist_vector_store_api.sayt_api.deps.settings import (
    BuildSaytArtifactsSettings,
    RuntimeSaytSettings,
    get_settings,
)


@pytest.mark.api
def test_runtime_settings_validate_field_names_and_uppercase_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify that runtime settings accept kwargs and uppercase env vars."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SAYT_ARTIFACT_DIR", "sayt-cache")

    settings_by_name = RuntimeSaytSettings(sayt_artifact_dir="sayt-local")
    settings_by_env = RuntimeSaytSettings()

    assert settings_by_name.sayt_artifact_dir == "sayt-local"
    assert settings_by_env.sayt_artifact_dir == "sayt-cache"


@pytest.mark.api
def test_get_settings_reads_and_caches_runtime_settings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify that get_settings reads env vars once and returns a cached model."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SAYT_ARTIFACT_DIR", "cached-sayt")
    get_settings.cache_clear()

    settings = get_settings()
    cached_settings = get_settings()

    assert settings.sayt_artifact_dir == "cached-sayt"
    assert cached_settings is settings

    get_settings.cache_clear()


@pytest.mark.utils
def test_build_settings_accept_aliases_and_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify the SAYT build settings expose the expected CLI aliases."""
    expected_min_chars = 2
    expected_max_suggestions = 7

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_sayt_artifacts.py",
            "--src",
            "gs://bucket/sayt.csv",
            "--artifact",
            "artifacts/sayt",
            "--search-col",
            "search_title",
            "--display-col",
            "display_title",
            "--min",
            "2",
            "--max",
            "7",
        ],
    )

    settings = BuildSaytArtifactsSettings()

    assert settings.sayt_source_file == "gs://bucket/sayt.csv"
    assert settings.sayt_artifact_dir == "artifacts/sayt"
    assert settings.search_text_col == "search_title"
    assert settings.display_text_col == "display_title"
    assert settings.min_chars == expected_min_chars
    assert settings.max_suggestions == expected_max_suggestions
