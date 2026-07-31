"""Tests for the vector-store artifact build script."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from survey_assist_embed_core.adapters.classifai.vector_backend import (
    DEFAULT_CLASSIFAI_EMBEDDING_MODEL_NAME,
)

from tests.helpers import load_script_module, run_script_as_main, set_script_argv

SCRIPT_ENV_VARS = (
    "INDEX_SOURCE_FILE",
    "index_source_file",
    "SOURCE",
    "source",
    "SRC",
    "src",
    "VECTOR_STORE_DIR",
    "vector_store_dir",
    "STORE",
    "store",
    "DB_DIR",
    "db_dir",
    "OUTPUT_DIR",
    "output_dir",
    "EMBEDDING_MODEL_NAME",
    "embedding_model_name",
    "MODEL",
    "model",
)


def _clear_script_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove script-related environment variables for isolated test runs."""
    for env_var in SCRIPT_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)


def _load_script_module():
    """Load the build script directly from the repository scripts directory."""
    return load_script_module(
        script_name="build_vector_store_artifacts.py",
        module_name="build_vector_store_artifacts_script",
    )


@pytest.fixture(name="script")
def script_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Provide the build script module loaded from the scripts directory."""
    monkeypatch.chdir(tmp_path)
    _clear_script_env_vars(monkeypatch)
    return _load_script_module()


def _set_script_argv(
    monkeypatch: pytest.MonkeyPatch,
    *args: str,
) -> None:
    """Set sys.argv to mimic invoking the build script from the shell."""
    set_script_argv(monkeypatch, "build_vector_store_artifacts.py", *args)


@pytest.mark.utils
def test_script_runs_main_when_executed_as_main_module(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that the __main__ entrypoint delegates to main and exits cleanly."""
    calls: list[dict[str, str]] = []

    def fake_info(*_args, **_kwargs) -> None:
        """Ignore info logs during the test."""

    def fake_get_logger(_name: str) -> SimpleNamespace:
        """Return a minimal logger-like object for the script under test."""
        return SimpleNamespace(info=fake_info)

    def fake_build_embedding_index(**kwargs: str) -> None:
        calls.append(kwargs)

    monkeypatch.chdir(tmp_path)
    _clear_script_env_vars(monkeypatch)
    monkeypatch.setenv("INDEX_SOURCE_FILE", "data/source.csv")
    _set_script_argv(monkeypatch)
    monkeypatch.setattr(
        "survey_assist_embed_core.build_embedding_index",
        fake_build_embedding_index,
    )
    monkeypatch.setattr(
        "survey_assist_utils.logging.get_logger",
        fake_get_logger,
    )

    assert run_script_as_main("build_vector_store_artifacts.py") == 0
    assert calls == [
        {
            "index_source_file": "data/source.csv",
            "output_dir": "vector_store",
            "embedding_model_name": DEFAULT_CLASSIFAI_EMBEDDING_MODEL_NAME,
        }
    ]


@pytest.mark.utils
def test_main_uses_cli_arguments(
    script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that explicit CLI arguments are passed to embed-core."""
    calls: list[dict[str, str]] = []

    def fake_build_embedding_index(**kwargs: str) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(script, "build_embedding_index", fake_build_embedding_index)
    _set_script_argv(
        monkeypatch,
        "--index-source-file",
        "gs://bucket/input.csv",
        "--vector-store-dir",
        "build/output",
        "--embedding-model-name",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    exit_code = script.main()

    assert exit_code == 0
    assert calls == [
        {
            "index_source_file": "gs://bucket/input.csv",
            "output_dir": "build/output",
            "embedding_model_name": "sentence-transformers/all-MiniLM-L6-v2",
        }
    ]


@pytest.mark.utils
def test_main_uses_cli_aliases(
    script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the shorter CLI alias flags are accepted."""
    calls: list[dict[str, str]] = []

    def fake_build_embedding_index(**kwargs: str) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(script, "build_embedding_index", fake_build_embedding_index)
    _set_script_argv(
        monkeypatch,
        "--src",
        "gs://bucket/alias-input.csv",
        "--store",
        "alias-output",
        "--model",
        "sentence-transformers/paraphrase-MiniLM-L3-v2",
    )

    exit_code = script.main()

    assert exit_code == 0
    assert calls == [
        {
            "index_source_file": "gs://bucket/alias-input.csv",
            "output_dir": "alias-output",
            "embedding_model_name": "sentence-transformers/paraphrase-MiniLM-L3-v2",
        }
    ]


@pytest.mark.utils
def test_main_uses_environment_defaults(
    script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that environment variables can fully configure the build."""
    calls: list[dict[str, str]] = []

    def fake_build_embedding_index(**kwargs: str) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(script, "build_embedding_index", fake_build_embedding_index)
    monkeypatch.setenv("INDEX_SOURCE_FILE", "data/source.csv")
    monkeypatch.setenv("VECTOR_STORE_DIR", "artifacts/vector-store")
    monkeypatch.setenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/paraphrase-MiniLM-L3-v2",
    )
    _set_script_argv(monkeypatch)

    exit_code = script.main()

    assert exit_code == 0
    assert calls == [
        {
            "index_source_file": "data/source.csv",
            "output_dir": "artifacts/vector-store",
            "embedding_model_name": ("sentence-transformers/paraphrase-MiniLM-L3-v2"),
        }
    ]


@pytest.mark.utils
def test_main_ignores_output_dir_env_when_vector_store_dir_env_is_set(
    script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that OUTPUT_DIR is ignored in favour of VECTOR_STORE_DIR."""
    calls: list[dict[str, str]] = []

    def fake_build_embedding_index(**kwargs: str) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(script, "build_embedding_index", fake_build_embedding_index)
    monkeypatch.setenv("INDEX_SOURCE_FILE", "data/source.csv")
    monkeypatch.setenv("VECTOR_STORE_DIR", "artifacts/vector-store")
    monkeypatch.setenv("OUTPUT_DIR", "artifacts/output-dir")
    _set_script_argv(monkeypatch)

    exit_code = script.main()

    assert exit_code == 0
    assert calls[0]["output_dir"] == "artifacts/vector-store"


@pytest.mark.utils
def test_main_rejects_removed_output_dir_flag(
    script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the removed output-dir CLI flag is no longer accepted."""
    _set_script_argv(
        monkeypatch,
        "--index-source-file",
        "gs://bucket/input.csv",
        "--output-dir",
        "build/output",
    )

    with pytest.raises(SystemExit):
        script.main()


@pytest.mark.utils
def test_main_requires_index_source_file(
    script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the script fails fast when no source file is configured."""
    _set_script_argv(monkeypatch)

    with pytest.raises(SystemExit):
        script.main()
