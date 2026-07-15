"""Shared helpers for multiple service entrypoints."""

from survey_assist_vector_store_api.shared.app_metadata import (
    API_PACKAGE_VERSION,
    EMBED_CORE_PACKAGE_VERSION,
    UNKNOWN_PACKAGE_VERSION,
    build_default_app_description,
)
from survey_assist_vector_store_api.shared.build_settings import BaseBuildSettings
from survey_assist_vector_store_api.shared.http import (
    build_generic_error_handler,
    build_generic_error_response,
)

__all__ = [
    "API_PACKAGE_VERSION",
    "EMBED_CORE_PACKAGE_VERSION",
    "UNKNOWN_PACKAGE_VERSION",
    "BaseBuildSettings",
    "build_default_app_description",
    "build_generic_error_handler",
    "build_generic_error_response",
]
