"""Helpers for application metadata and version resolution."""

from importlib.metadata import PackageNotFoundError, version

PACKAGE_DISTRIBUTION_NAME = "survey-assist-vector-store-api"
DEFAULT_APP_TITLE = "Vector Store API"
DEFAULT_APP_DESCRIPTION = "API for interacting with the vector store"
DEFAULT_ROOT_MESSAGE = "Vector Store API is running"


def resolve_app_metadata(
    *,
    title: str | None,
    description: str | None,
    root_message: str | None,
) -> tuple[str, str, str]:
    """Resolve application metadata.

    Returns explicit overrides when provided. Otherwise uses generic metadata
    for the API documentation and root endpoint.
    """
    if title is not None and description is not None and root_message is not None:
        return title, description, root_message

    resolved_title = title or DEFAULT_APP_TITLE
    resolved_description = description or DEFAULT_APP_DESCRIPTION
    resolved_root_message = root_message or DEFAULT_ROOT_MESSAGE
    return resolved_title, resolved_description, resolved_root_message


def resolve_default_version() -> str:
    """Resolve the application version from installed package metadata."""
    try:
        return version(PACKAGE_DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return "0.0.0"
