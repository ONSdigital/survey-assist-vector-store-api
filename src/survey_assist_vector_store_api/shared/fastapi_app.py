"""Shared helpers for constructing FastAPI applications."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, FastAPI
from starlette.types import Lifespan

from survey_assist_vector_store_api.shared.http import build_generic_error_handler
from survey_assist_vector_store_api.shared.types import StructuredLogger


@dataclass(frozen=True)
class AppMetadata:
    """Resolved application metadata used to construct a FastAPI app."""

    title: str
    description: str
    version: str
    root_message: str


def create_app(
    *,
    metadata: AppMetadata,
    api_prefix: str,
    lifespan: Lifespan[Any],
    routers: Sequence[APIRouter],
    logger: StructuredLogger,
) -> FastAPI:
    """Create a FastAPI app with shared metadata, error handling, and root route."""

    def read_root() -> dict[str, str]:
        """Retrieve the root endpoint status message."""
        return {"message": metadata.root_message}

    application = FastAPI(
        title=metadata.title,
        description=metadata.description,
        version=metadata.version,
        lifespan=lifespan,
    )

    application.add_exception_handler(
        Exception,
        build_generic_error_handler(logger),
    )
    application.add_api_route("/", read_root, methods=["GET"])

    for router in routers:
        application.include_router(router, prefix=api_prefix)

    return application
