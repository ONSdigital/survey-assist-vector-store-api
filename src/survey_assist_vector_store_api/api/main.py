"""FastAPI application entry point."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

StartupHook = Callable[[FastAPI], None]
ShutdownHook = Callable[[FastAPI], None]


def create_app(  # pylint: disable=too-many-arguments # noqa: PLR0913
    *,
    title: str = "API",
    description: str = "FastAPI service",
    version: str = "0.1.0",
    root_message: str = "API is running",
    api_prefix: str = "/v1",
    routers: list[APIRouter] | None = None,
    startup_hook: StartupHook | None = None,
    shutdown_hook: ShutdownHook | None = None,
) -> FastAPI:
    """Initialise and configure a FastAPI application.

    Creates a FastAPI application with customisable settings, optional routers,
    and lifecycle hooks for startup and shutdown operations. The application
    includes a generic exception handler to manage unhandled errors.

    Args:
        title: Application title for API documentation. Defaults to "API".
        description: Application description for API documentation.
            Defaults to "FastAPI service".
        version: Application version for API documentation.
            Defaults to "0.1.0".
        root_message: Message returned by the root endpoint.
            Defaults to "API is running".
        api_prefix: URL prefix for all included routers.
            Defaults to "/v1".
        routers: List of APIRouter instances to include in the application.
            If None, no routers are included. Defaults to None.
        startup_hook: Optional callable invoked during application startup.
            Receives the FastAPI app instance as parameter. Defaults to None.
        shutdown_hook: Optional callable invoked during application shutdown.
            Receives the FastAPI app instance as parameter. Defaults to None.

    Returns:
        Configured FastAPI application instance ready for use.
    """

    @asynccontextmanager
    async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
        """Manage application lifecycle with optional startup and shutdown hooks.

        This context manager handles the lifespan of the FastAPI application,
        executing startup operations before the application begins handling
        requests and shutdown operations when the application terminates.

        Args:
            app_instance: The FastAPI application instance.

        Yields:
            None. The function yields control to the application during its
            operational lifespan.
        """
        if startup_hook:
            startup_hook(app_instance)

        yield

        if shutdown_hook:
            shutdown_hook(app_instance)

    application = FastAPI(
        title=title,
        description=description,
        version=version,
        lifespan=lifespan,
    )

    @application.exception_handler(Exception)
    async def generic_error_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unhandled exceptions with a generic error response.

        This exception handler catches all unhandled exceptions and returns
        a standardised JSON response with a 500 status code. Exception details
        are logged for debugging purposes.

        Args:
            _request: The HTTP request that triggered the exception (unused).
            exc: The exception instance that was raised.

        Returns:
            JSON response with status code 500 and an error detail message.
        """
        # Replace with your project logger if required.
        print(f"Unexpected error: {exc}")

        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )

    @application.get("/")
    def read_root() -> dict[str, str]:
        """Retrieve the root endpoint status message.

        Returns a simple JSON response containing the configured root message,
        indicating that the API is operational.

        Returns:
            Dictionary containing a single "message" key with the root message
            value as a string.
        """
        return {"message": root_message}

    for router in routers or []:
        application.include_router(router, prefix=api_prefix)

    return application


app = create_app(
    title="Example Vector Store API",
    description="API for interacting with Vector Store",
    version="0.1.0",
    root_message="Example Vector Store API is running",
)
