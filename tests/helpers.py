"""Shared helpers for reducing duplication in tests."""

import asyncio
import importlib.util
import runpy
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from survey_assist_vector_store_api.shared.fastapi_app import AppMetadata, create_app


def assert_registered_generic_error_handler(
    monkeypatch: pytest.MonkeyPatch,
    *,
    app: FastAPI,
    logger: Any,
) -> None:
    """Assert that an app-level generic exception handler logs and returns a 500."""
    logged_messages: list[tuple[str, dict[str, str]]] = []
    request = Request({"type": "http", "headers": []})

    def fake_error(message: str, **kwargs: str) -> None:
        logged_messages.append((message, kwargs))

    monkeypatch.setattr(logger, "error", fake_error)

    response: JSONResponse = asyncio.run(
        cast(Any, app.exception_handlers[Exception])(request, RuntimeError("boom"))
    )

    assert len(logged_messages) == 1
    message, kwargs = logged_messages[0]
    assert message == "Unexpected error"
    assert kwargs["error"] == "boom"
    assert kwargs["error_type"] == "RuntimeError"
    assert "RuntimeError: boom" in kwargs["traceback"]
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.body == b'{"detail":"An unexpected error occurred"}'


def create_test_app(
    main_module: Any,
    *,
    metadata: AppMetadata | None = None,
    lifespan: Any | None = None,
) -> FastAPI:
    """Create a service app for tests with optional metadata or lifespan overrides."""
    routers: tuple[Any, ...]
    if hasattr(main_module, "search_index_router"):
        routers = (main_module.runtime_config_router, main_module.search_index_router)
    elif hasattr(main_module, "suggest_router") and hasattr(
        main_module,
        "runtime_config_router",
    ):
        routers = (main_module.runtime_config_router, main_module.suggest_router)
    else:
        routers = (main_module.suggest_router,)

    return create_app(
        metadata=metadata or main_module.DEFAULT_APP_METADATA,
        api_prefix=main_module.DEFAULT_API_PREFIX,
        lifespan=(
            lifespan or main_module.vector_store_lifespan
            if hasattr(main_module, "vector_store_lifespan")
            else lifespan or main_module.sayt_lifespan
        ),
        routers=routers,
        logger=main_module.logger,
    )


def load_script_module(*, script_name: str, module_name: str) -> ModuleType:
    """Load a script from the repository scripts directory as an importable module."""
    script_path = Path(__file__).resolve().parents[1] / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def set_script_argv(
    monkeypatch: pytest.MonkeyPatch,
    script_name: str,
    *args: str,
) -> None:
    """Set sys.argv to mimic invoking a repository script from the shell."""
    monkeypatch.setattr(sys, "argv", [script_name, *args])


def run_script_as_main(script_name: str) -> int:
    """Execute a repository script as __main__ and return its exit code."""
    script_path = Path(__file__).resolve().parents[1] / "scripts" / script_name

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(script_path), run_name="__main__")

    return cast(int, exc_info.value.code)
