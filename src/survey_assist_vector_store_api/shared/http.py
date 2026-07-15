"""Shared HTTP helpers for service entrypoints."""

import traceback

from fastapi.responses import JSONResponse


def build_generic_error_response(logger, exc: Exception) -> JSONResponse:
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
