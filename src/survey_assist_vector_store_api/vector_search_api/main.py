"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.shared.app_metadata import (
    API_PACKAGE_VERSION,
    build_default_app_description,
)
from survey_assist_vector_store_api.shared.http import build_generic_error_response
from survey_assist_vector_store_api.vector_search_api.lifespan import (
    vector_store_lifespan,
)
from survey_assist_vector_store_api.vector_search_api.routes.runtime_config import (
    router as runtime_config_router,
)
from survey_assist_vector_store_api.vector_search_api.routes.search_index import (
    router as search_index_router,
)

DEFAULT_API_PREFIX = "/v1"
DEFAULT_APP_TITLE = "Vector Store API"
DEFAULT_APP_DESCRIPTION = "API for interacting with the vector store"
DEFAULT_ROOT_MESSAGE = "Vector Store API is running"
logger = get_logger(__name__)


async def generic_error_handler(
    _request: Request,
    exc: Exception,
) -> object:
    """Handle unhandled exceptions with a generic error response.

    Args:
        _request: The HTTP request that triggered the exception (unused).
        exc: The exception instance that was raised.

    Returns:
        JSON response with status code 500 and an error detail message.
    """
    return build_generic_error_response(logger, exc)


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
    resolved_title = title or DEFAULT_APP_TITLE
    resolved_description = description or build_default_app_description(
        description=DEFAULT_APP_DESCRIPTION,
    )
    resolved_root_message = root_message or DEFAULT_ROOT_MESSAGE
    resolved_version = version or API_PACKAGE_VERSION

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
    application.include_router(runtime_config_router, prefix=api_prefix)
    application.include_router(search_index_router, prefix=api_prefix)

    return application


app = create_app()
