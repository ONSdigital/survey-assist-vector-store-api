"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.api.app_metadata import (
    resolve_app_metadata,
    resolve_default_version,
)
from survey_assist_vector_store_api.api.lifespan import vector_store_lifespan
from survey_assist_vector_store_api.api.routes.search_index import (
    router as search_index_router,
)

DEFAULT_API_PREFIX = "/v1"
logger = get_logger(__name__)


async def generic_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unhandled exceptions with a generic error response.

    Args:
        _request: The HTTP request that triggered the exception (unused).
        exc: The exception instance that was raised.

    Returns:
        JSON response with status code 500 and an error detail message.
    """
    logger.info(
        "Unexpected error",
        error=str(exc),
        error_type=type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )


def create_app(
    *,
    title: str | None = None,
    description: str | None = None,
    version: str | None = None,
    root_message: str | None = None,
    api_prefix: str = DEFAULT_API_PREFIX,
) -> FastAPI:
    """Create the vector-store API application.

    Args:
        title: Application title for API documentation. When omitted, a
            generic API default is used.
        description: Application description for API documentation. When
            omitted, a generic API default is used.
        version: Application version for API documentation. When omitted, the
            installed package version is used.
        root_message: Message returned by the root endpoint. When omitted, a
            generic API default is used.
        api_prefix: URL prefix for included API routers.

    Returns:
        FastAPI application configured with routes, exception handling, and a
        startup-loaded embedding handler.
    """
    resolved_title, resolved_description, resolved_root_message = resolve_app_metadata(
        title=title,
        description=description,
        root_message=root_message,
    )
    resolved_version = version or resolve_default_version()

    def read_root() -> dict[str, str]:
        """Retrieve the root endpoint status message."""
        return {"message": resolved_root_message}

    application = FastAPI(
        title=resolved_title,
        description=resolved_description,
        version=resolved_version,
        lifespan=vector_store_lifespan,
    )

    application.add_exception_handler(Exception, generic_error_handler)
    application.add_api_route("/", read_root, methods=["GET"])
    application.include_router(search_index_router, prefix=api_prefix)

    return application


app = create_app()
