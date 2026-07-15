"""Shared helpers for application metadata and version resolution."""

from importlib import metadata

_PACKAGE_DISTRIBUTION_NAME = "survey-assist-vector-store-api"
_EMBED_CORE_PACKAGE_DISTRIBUTION_NAME = "survey-assist-embed-core"
UNKNOWN_PACKAGE_VERSION = "unknown"


def _resolve_package_version(package_distribution_name: str) -> str:
    """Resolve an installed package version from distribution metadata."""
    try:
        return metadata.version(package_distribution_name)
    except metadata.PackageNotFoundError:
        return UNKNOWN_PACKAGE_VERSION


API_PACKAGE_VERSION = _resolve_package_version(_PACKAGE_DISTRIBUTION_NAME)
EMBED_CORE_PACKAGE_VERSION = _resolve_package_version(
    _EMBED_CORE_PACKAGE_DISTRIBUTION_NAME
)


def build_default_app_description(
    *,
    description: str,
) -> str:
    """Build the default API-docs description including package versions."""
    return (
        f"{description}\n\n"
        "### Package versions:\n"
        f"- {_PACKAGE_DISTRIBUTION_NAME}: `{API_PACKAGE_VERSION}`\n"
        f"- {_EMBED_CORE_PACKAGE_DISTRIBUTION_NAME}: `{EMBED_CORE_PACKAGE_VERSION}`"
    )
