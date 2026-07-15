"""Tests for the SAYT artifact build script."""

import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT_ENV_VARS = (
    "SAYT_SOURCE_FILE",
    "sayt_source_file",
    "SOURCE",
    "source",
    "SRC",
    "src",
    "SAYT_ARTIFACT_DIR",
    "sayt_artifact_dir",
    "ARTIFACT",
    "artifact",
    "ARTIFACT_DIR",
    "artifact_dir",
    "SEARCH_TEXT_COL",
    "search_text_col",
    "DISPLAY_TEXT_COL",
    "display_text_col",
    "MIN_CHARS",
    "min_chars",
    "MAX_SUGGESTIONS",
    "max_suggestions",
    "OVERWRITE",
    "overwrite",
)


def _clear_script_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove script-related environment variables for isolated test runs."""
    for env_var in SCRIPT_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)


def _load_script_module():
    """Load the SAYT build script directly from the repository scripts directory."""
    script_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "build_sayt_artifacts.py"
    )
    spec = importlib.util.spec_from_file_location(
        "build_sayt_artifacts_script",
        script_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_sayt_artifacts.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="sayt_script")
def sayt_script_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Provide the SAYT build script module loaded from the scripts directory."""
    monkeypatch.chdir(tmp_path)
    _clear_script_env_vars(monkeypatch)
    return _load_script_module()


def _set_script_argv(
    monkeypatch: pytest.MonkeyPatch,
    *args: str,
) -> None:
    """Set sys.argv to mimic invoking the SAYT build script from the shell."""
    monkeypatch.setattr(sys, "argv", ["build_sayt_artifacts.py", *args])


@pytest.mark.utils
def test_script_runs_main_when_executed_as_main_module(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that the __main__ entrypoint delegates to main and exits cleanly."""
    builder_calls: list[dict[str, object]] = []
    build_calls: list[tuple[str, bool]] = []
    script_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "build_sayt_artifacts.py"
    )

    def fake_info(*_args, **_kwargs) -> None:
        """Ignore info logs during the test."""

    def fake_get_logger(_name: str) -> SimpleNamespace:
        """Return a minimal logger-like object for the script under test."""
        return SimpleNamespace(info=fake_info)

    class FakeBuilder:  # pylint: disable=too-few-public-methods
        """Minimal fake builder for the script under test."""

        def build_artifact(self, output_dir: str, *, overwrite: bool = False) -> None:
            build_calls.append((output_dir, overwrite))

    class FakeBuilderFactory:  # pylint: disable=too-few-public-methods
        """Class double providing the from_csv entrypoint."""

        @classmethod
        def from_csv(cls, file_path: str, **kwargs: object) -> FakeBuilder:
            builder_calls.append({"file_path": file_path, **kwargs})
            return FakeBuilder()

    monkeypatch.chdir(tmp_path)
    _clear_script_env_vars(monkeypatch)
    monkeypatch.setenv("SAYT_SOURCE_FILE", "data/sayt.csv")
    _set_script_argv(monkeypatch)
    monkeypatch.setattr(
        "survey_assist_embed_core.sayt.SAYTBuilder",
        FakeBuilderFactory,
    )
    monkeypatch.setattr(
        "survey_assist_utils.logging.get_logger",
        fake_get_logger,
    )

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(script_path), run_name="__main__")

    assert exc_info.value.code == 0
    assert builder_calls == [
        {
            "file_path": "data/sayt.csv",
            "search_text_col": "title",
            "display_text_col": None,
            "min_chars": 4,
            "max_suggestions": 10,
        }
    ]
    assert build_calls == [("sayt_artifact", False)]


@pytest.mark.utils
def test_main_uses_cli_arguments(
    sayt_script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that explicit CLI arguments are passed to the SAYT builder."""
    builder_calls: list[dict[str, object]] = []
    build_calls: list[tuple[str, bool]] = []

    class FakeBuilder:  # pylint: disable=too-few-public-methods
        """Minimal fake builder for the script under test."""

        def build_artifact(self, output_dir: str, *, overwrite: bool = False) -> None:
            build_calls.append((output_dir, overwrite))

    class FakeBuilderFactory:  # pylint: disable=too-few-public-methods
        """Class double providing the from_csv entrypoint."""

        @classmethod
        def from_csv(cls, file_path: str, **kwargs: object) -> FakeBuilder:
            builder_calls.append({"file_path": file_path, **kwargs})
            return FakeBuilder()

    monkeypatch.setattr(sayt_script, "SAYTBuilder", FakeBuilderFactory)
    _set_script_argv(
        monkeypatch,
        "--sayt-source-file",
        "gs://bucket/sayt.csv",
        "--sayt-artifact-dir",
        "build/sayt",
        "--search-text-col",
        "search_title",
        "--display-text-col",
        "display_title",
        "--min-chars",
        "2",
        "--max-suggestions",
        "7",
        "--overwrite",
        "true",
    )

    exit_code = sayt_script.main()

    assert exit_code == 0
    assert builder_calls == [
        {
            "file_path": "gs://bucket/sayt.csv",
            "search_text_col": "search_title",
            "display_text_col": "display_title",
            "min_chars": 2,
            "max_suggestions": 7,
        }
    ]
    assert build_calls == [("build/sayt", True)]


@pytest.mark.utils
def test_main_uses_environment_defaults(
    sayt_script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that environment variables can fully configure the SAYT build."""
    builder_calls: list[dict[str, object]] = []
    build_calls: list[tuple[str, bool]] = []

    class FakeBuilder:  # pylint: disable=too-few-public-methods
        """Minimal fake builder for the script under test."""

        def build_artifact(self, output_dir: str, *, overwrite: bool = False) -> None:
            build_calls.append((output_dir, overwrite))

    class FakeBuilderFactory:  # pylint: disable=too-few-public-methods
        """Class double providing the from_csv entrypoint."""

        @classmethod
        def from_csv(cls, file_path: str, **kwargs: object) -> FakeBuilder:
            builder_calls.append({"file_path": file_path, **kwargs})
            return FakeBuilder()

    monkeypatch.setattr(sayt_script, "SAYTBuilder", FakeBuilderFactory)
    monkeypatch.setenv("SAYT_SOURCE_FILE", "data/sayt.csv")
    monkeypatch.setenv("SAYT_ARTIFACT_DIR", "artifacts/sayt")
    monkeypatch.setenv("SEARCH_TEXT_COL", "search_text")
    monkeypatch.setenv("DISPLAY_TEXT_COL", "display_text")
    monkeypatch.setenv("MIN_CHARS", "3")
    monkeypatch.setenv("MAX_SUGGESTIONS", "8")
    monkeypatch.setenv("OVERWRITE", "true")
    _set_script_argv(monkeypatch)

    exit_code = sayt_script.main()

    assert exit_code == 0
    assert builder_calls == [
        {
            "file_path": "data/sayt.csv",
            "search_text_col": "search_text",
            "display_text_col": "display_text",
            "min_chars": 3,
            "max_suggestions": 8,
        }
    ]
    assert build_calls == [("artifacts/sayt", True)]


@pytest.mark.utils
def test_main_requires_sayt_source_file(
    sayt_script,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the script fails fast when no source file is configured."""
    _set_script_argv(monkeypatch)

    with pytest.raises(SystemExit):
        sayt_script.main()
