"""Tests for SAYT API settings."""

import pytest
from pydantic import ValidationError

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
    expected_min_chars = 3
    expected_default_num_suggestions = 7

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
            "3",
            "--default-num-suggestions",
            "7",
        ],
    )

    settings = BuildSaytArtifactsSettings()

    assert settings.sayt_source_file == "gs://bucket/sayt.csv"
    assert settings.sayt_artifact_dir == "artifacts/sayt"
    assert settings.search_text_col == "search_title"
    assert settings.display_text_col == "display_title"
    assert settings.min_chars == expected_min_chars
    assert settings.default_num_suggestions == expected_default_num_suggestions


@pytest.mark.utils
def test_build_settings_default_display_text_column(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify the SAYT build settings default the display-text column."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_sayt_artifacts.py",
            "--src",
            "gs://bucket/sayt.csv",
        ],
    )

    settings = BuildSaytArtifactsSettings()

    assert settings.display_text_col == "display_text"


@pytest.mark.utils
def test_build_settings_accept_legacy_max_suggestions_alias(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify the legacy max_suggestions env var still maps to the new field."""
    expected_default_num_suggestions = 8

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["build_sayt_artifacts.py"])
    monkeypatch.setenv("MAX_SUGGESTIONS", "8")

    settings = BuildSaytArtifactsSettings()

    assert settings.default_num_suggestions == expected_default_num_suggestions


@pytest.mark.utils
def test_build_settings_accept_default_suggestions_alias(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify the convenience default_suggestions env var maps to the field."""
    expected_default_num_suggestions = 9

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["build_sayt_artifacts.py"])
    monkeypatch.setenv("DEFAULT_SUGGESTIONS", "9")

    settings = BuildSaytArtifactsSettings()

    assert settings.default_num_suggestions == expected_default_num_suggestions


@pytest.mark.utils
@pytest.mark.parametrize("value", [0, -1, 101])
def test_build_settings_validate_default_num_suggestions(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    value: int,
) -> None:
    """Verify the build-time default suggestion count stays in bounds."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["build_sayt_artifacts.py"])

    with pytest.raises(ValidationError, match="default_num_suggestions"):
        BuildSaytArtifactsSettings(default_num_suggestions=value)


@pytest.mark.utils
@pytest.mark.parametrize("value", [0, 2])
def test_build_settings_validate_min_chars(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    value: int,
) -> None:
    """Verify min_chars stays within the supported SAYT bounds."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["build_sayt_artifacts.py"])

    with pytest.raises(ValidationError, match="min_chars"):
        BuildSaytArtifactsSettings(min_chars=value)
