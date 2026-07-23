"""FastAPI application entry point for the SAYT API."""  # pylint: disable=duplicate-code

from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.sayt_api.lifespan import sayt_lifespan
from survey_assist_vector_store_api.sayt_api.routes.configuration import (
    router as configuration_router,
)
from survey_assist_vector_store_api.sayt_api.routes.suggestions import (
    router as suggestions_router,
)
from survey_assist_vector_store_api.shared.app_metadata import (
    API_PACKAGE_VERSION,
    build_default_app_description,
)
from survey_assist_vector_store_api.shared.fastapi_app import AppMetadata, create_app

DEFAULT_API_PREFIX = "/v1"
DEFAULT_APP_TITLE = "SAYT API"
DEFAULT_APP_DESCRIPTION = "API for interacting with the SAYT suggester"
DEFAULT_ROOT_MESSAGE = "SAYT API is running"
DEFAULT_APP_METADATA = AppMetadata(
    title=DEFAULT_APP_TITLE,
    description=build_default_app_description(description=DEFAULT_APP_DESCRIPTION),
    version=API_PACKAGE_VERSION,
    root_message=DEFAULT_ROOT_MESSAGE,
)

logger = get_logger(__name__)


app = create_app(
    metadata=DEFAULT_APP_METADATA,
    api_prefix=DEFAULT_API_PREFIX,
    lifespan=sayt_lifespan,
    routers=(configuration_router, suggestions_router),
    logger=logger,
)
