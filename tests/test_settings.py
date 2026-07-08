"""Tests for vector-store API settings."""

import pytest

from survey_assist_vector_store_api.api.deps.settings import VectorStoreApiSettings


@pytest.mark.api
def test_settings_validate_field_names_and_uppercase_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Verify that settings accept snake_case kwargs and uppercase env vars."""
    by_name_matches = 10
    by_env_matches = 15

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("KNOWLEDGEBASE_NAME", "SOC")
    monkeypatch.setenv("VECTOR_STORE_DIR", "soc-store")
    monkeypatch.setenv("VECTOR_STORE_K_MATCHES", str(by_env_matches))

    settings_by_name = VectorStoreApiSettings(
        knowledgebase_name="SIC",
        vector_store_dir="sic-store",
        vector_store_k_matches=by_name_matches,
    )
    settings_by_env = VectorStoreApiSettings()

    assert settings_by_name.knowledgebase_name == "SIC"
    assert settings_by_name.vector_store_dir == "sic-store"
    assert settings_by_name.vector_store_k_matches == by_name_matches

    assert settings_by_env.knowledgebase_name == "SOC"
    assert settings_by_env.vector_store_dir == "soc-store"
    assert settings_by_env.vector_store_k_matches == by_env_matches
