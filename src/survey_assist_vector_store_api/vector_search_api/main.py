"""FastAPI application entry point."""  # pylint: disable=duplicate-code

from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.shared.app_metadata import (
    API_PACKAGE_VERSION,
    build_default_app_description,
)
from survey_assist_vector_store_api.shared.fastapi_app import AppMetadata, create_app
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
    lifespan=vector_store_lifespan,
    routers=(runtime_config_router, search_index_router),
    logger=logger,
)
