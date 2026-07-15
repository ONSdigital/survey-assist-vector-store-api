"""Tests for vector-store API settings."""

import pytest

from survey_assist_vector_store_api.vector_search_api.deps.settings import (
    RuntimeVectorStoreSettings,
    get_settings,
)


@pytest.mark.api
def test_settings_validate_field_names_and_uppercase_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify that settings accept snake_case kwargs and uppercase env vars."""
    by_name_matches = 10
    by_env_matches = 15

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VECTOR_STORE_DIR", "soc-store")
    monkeypatch.setenv("VECTOR_STORE_K_MATCHES", str(by_env_matches))

    settings_by_name = RuntimeVectorStoreSettings(
        vector_store_dir="sic-store",
        vector_store_k_matches=by_name_matches,
    )
    settings_by_env = RuntimeVectorStoreSettings()

    assert settings_by_name.vector_store_dir == "sic-store"
    assert settings_by_name.vector_store_k_matches == by_name_matches

    assert settings_by_env.vector_store_dir == "soc-store"
    assert settings_by_env.vector_store_k_matches == by_env_matches


@pytest.mark.api
def test_get_settings_reads_and_caches_runtime_settings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify that get_settings reads env vars once and returns a cached model."""
    expected_k_matches = 25

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VECTOR_STORE_DIR", "cached-store")
    monkeypatch.setenv("VECTOR_STORE_K_MATCHES", str(expected_k_matches))
    get_settings.cache_clear()

    settings = get_settings()
    cached_settings = get_settings()

    assert settings.vector_store_dir == "cached-store"
    assert settings.vector_store_k_matches == expected_k_matches
    assert cached_settings is settings

    get_settings.cache_clear()
