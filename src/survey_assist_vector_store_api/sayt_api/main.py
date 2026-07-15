"""FastAPI application entry point for the SAYT API."""

from fastapi import FastAPI, Request
from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.sayt_api.lifespan import sayt_lifespan
from survey_assist_vector_store_api.sayt_api.routes.suggest import (
    router as suggest_router,
)
from survey_assist_vector_store_api.shared.app_metadata import (
    API_PACKAGE_VERSION,
    build_default_app_description,
)
from survey_assist_vector_store_api.shared.http import build_generic_error_response

DEFAULT_API_PREFIX = "/v1"
DEFAULT_APP_TITLE = "SAYT API"
DEFAULT_APP_DESCRIPTION = "API for interacting with the SAYT suggester"
DEFAULT_ROOT_MESSAGE = "SAYT API is running"
logger = get_logger(__name__)


async def generic_error_handler(
    _request: Request,
    exc: Exception,
) -> object:
    """Handle unhandled exceptions with a generic error response."""
    return build_generic_error_response(logger, exc)


def create_app(
    *,
    title: str | None = None,
    description: str | None = None,
    version: str | None = None,
    root_message: str | None = None,
    api_prefix: str = DEFAULT_API_PREFIX,
) -> FastAPI:
    """Create the SAYT API application."""
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
        lifespan=sayt_lifespan,
    )

    application.add_exception_handler(Exception, generic_error_handler)
    application.add_api_route("/", read_root, methods=["GET"])
    application.include_router(suggest_router, prefix=api_prefix)

    return application


app = create_app()
