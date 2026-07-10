"""Helpers for application metadata and version resolution."""

from importlib.metadata import PackageNotFoundError, version

PACKAGE_DISTRIBUTION_NAME = "survey-assist-vector-store-api"
EMBED_CORE_PACKAGE_DISTRIBUTION_NAME = "survey-assist-embed-core"
UNKNOWN_PACKAGE_VERSION = "unknown"
DEFAULT_APP_TITLE = "Vector Store API"
DEFAULT_APP_DESCRIPTION = "API for interacting with the vector store"
DEFAULT_ROOT_MESSAGE = "Vector Store API is running"


def resolve_app_metadata(
    *,
    title: str | None,
    description: str | None,
    root_message: str | None,
    version: str | None,
) -> tuple[str, str, str, str]:
    """Resolve application metadata and version.

    Returns the resolved title, description, root message, and API version.
    When metadata values are omitted, generic defaults are used and the docs
    description is enriched with installed package versions.
    """
    resolved_version = version or resolve_installed_version(PACKAGE_DISTRIBUTION_NAME)

    resolved_title = title or DEFAULT_APP_TITLE
    if description is None:
        resolved_embed_core_version = resolve_installed_version(
            EMBED_CORE_PACKAGE_DISTRIBUTION_NAME
        )
        resolved_description = build_default_app_description(
            api_version=resolved_version,
            embed_core_version=resolved_embed_core_version,
        )
    else:
        resolved_description = description
    resolved_root_message = root_message or DEFAULT_ROOT_MESSAGE
    return (
        resolved_title,
        resolved_description,
        resolved_root_message,
        resolved_version,
    )


def resolve_installed_version(package_distribution_name: str) -> str:
    """Resolve an installed package version from distribution metadata."""
    try:
        return version(package_distribution_name)
    except PackageNotFoundError:
        return UNKNOWN_PACKAGE_VERSION


def build_default_app_description(*, api_version: str, embed_core_version: str) -> str:
    """Build the default API-docs description including package versions."""
    return (
        f"{DEFAULT_APP_DESCRIPTION}\n\n"
        "### Package versions:\n"
        f"- {PACKAGE_DISTRIBUTION_NAME}: `{api_version}`\n"
        f"- {EMBED_CORE_PACKAGE_DISTRIBUTION_NAME}: `{embed_core_version}`"
    )
