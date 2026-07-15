"""Shared HTTP helpers for service entrypoints."""

import traceback
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse

from survey_assist_vector_store_api.shared.types import StructuredLogger


def build_generic_error_response(
    logger: StructuredLogger,
    exc: Exception,
) -> JSONResponse:
    """Log an unexpected exception and return a generic 500 response."""
    logger.error(
        "Unexpected error",
        error=str(exc),
        error_type=type(exc).__name__,
        traceback="".join(traceback.format_exception(exc)),
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )


def build_generic_error_handler(
    logger: StructuredLogger,
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    """Return a FastAPI-compatible exception handler bound to a logger."""

    async def generic_error_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return build_generic_error_response(logger, exc)

    return generic_error_handler
