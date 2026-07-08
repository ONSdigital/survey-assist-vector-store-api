"""Tests for the vector-store artifact build script."""

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_script_module():
    """Load the build script directly from the repository scripts directory."""
    script_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "build_vector_store_artifacts.py"
    )
    spec = importlib.util.spec_from_file_location(
        "build_vector_store_artifacts_script",
        script_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_vector_store_artifacts.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def script(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Provide the build script module loaded from the scripts directory."""
    monkeypatch.chdir(tmp_path)
    return _load_script_module()


def _set_script_argv(
    monkeypatch: pytest.MonkeyPatch,
    *args: str,
) -> None:
    """Set sys.argv to mimic invoking the build script from the shell."""
    monkeypatch.setattr(sys, "argv", ["build_vector_store_artifacts.py", *args])


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
