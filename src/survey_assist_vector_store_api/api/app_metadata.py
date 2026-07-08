"""Helpers for application metadata and version resolution."""

from importlib.metadata import PackageNotFoundError, version

from survey_assist_vector_store_api.api.deps.settings import get_settings

PACKAGE_DISTRIBUTION_NAME = "survey-assist-vector-store-api"


def resolve_app_metadata(
    *,
    title: str | None,
    description: str | None,
    root_message: str | None,
) -> tuple[str, str, str]:
    """Resolve deployment-specific app metadata.

    Returns explicit overrides when provided. Otherwise derives metadata from
    the configured knowledgebase name so separate deployments can identify the
    underlying vector store they serve.
    """
    if title is not None and description is not None and root_message is not None:
        return title, description, root_message

    knowledgebase_name = get_settings().knowledgebase_name

    resolved_title = title or f"{knowledgebase_name} Vector Store API"
    resolved_description = (
        description or f"API for interacting with the {knowledgebase_name} vector store"
    )
    resolved_root_message = (
        root_message or f"{knowledgebase_name} Vector Store API is running"
    )
    return resolved_title, resolved_description, resolved_root_message


def resolve_default_version() -> str:
    """Resolve the application version from installed package metadata."""
    try:
        return version(PACKAGE_DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return "0.0.0"
