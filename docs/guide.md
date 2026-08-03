# Survey Assist Vector Store API Guide

## Overview

This repository hosts two related FastAPI services:

- the vector-store API, which loads persisted embedding artifacts and serves ranked search results
- the SAYT API, which loads persisted SAYT artifacts and serves plain and scored search-as-you-type suggestions

Both services share the same codebase, validation workflow, and local `.env` file, but they run as separate processes and expose separate OpenAPI docs.

## Architecture

The repository is organised around two service entrypoints plus shared helpers:

- `survey_assist_vector_store_api.vector_store_api.main:app` runs the vector-store API on port `8088`
- `survey_assist_vector_store_api.sayt_api.main:app` runs the SAYT API on port `8089`
- `scripts/build_vector_store_artifacts.py` builds embedding artifacts used by the vector-store API
- `scripts/build_sayt_artifacts.py` builds SAYT artifacts used by the SAYT API

Shared modules under `src/survey_assist_vector_store_api/shared/` provide common FastAPI wiring, app metadata, and error handling.

## API Endpoints

The main local endpoints are:

- Vector-store docs: `http://localhost:8088/docs`
- SAYT docs: `http://localhost:8089/docs`
- Vector-store search: `POST /v1/search-index`
- Vector-store configuration: `GET /v1/configuration`
- SAYT suggestions: `POST /v1/suggestions`
- SAYT configuration: `GET /v1/configuration`

The vector-store search endpoint accepts a `query` list of cumulative fragments.
The SAYT suggestions endpoint accepts `query` plus optional positive `limit` and returns a JSON object whose `suggestions` field contains scored suggestion objects.
For the SAYT suggestions endpoint, `limit` overrides the default for that request only. If it is omitted, the API uses the default suggestion count baked into the loaded SAYT artifact when it was built, configured via `DEFAULT_NUM_SUGGESTIONS`.

## Integration with Survey Assist API

These services integrate with the Survey Assist API to provide:

- Embedding-based similarity search for SIC code classification
- Embedding-based similarity search for SOC code classification
- Search-as-you-type suggestions for supported classification flows
- Configuration inspection for both services
- Efficient artifact-backed retrieval

## Documentation

### Interactive Documentation

Each service provides two types of interactive documentation:

1. **Swagger UI** (`/docs`)
   - Interactive API testing
   - Request/response schemas
   - Example values
   - Try-it-out functionality

2. **ReDoc** (`/redoc`)
   - Alternative documentation view
   - Clean, readable format
   - Schema visualisation

You can access these interfaces by running the relevant service locally and opening its `/docs` or `/redoc` URL in a browser.

## Development

### Prerequisites

- Python 3.12
- Poetry for dependency management
- Access to data files
- Sufficient memory for vector storage

### Setup

Install dependencies:

```bash
poetry install
```

Install local git hooks:

```bash
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push
```

Copy `.env.example` to `.env` and adjust the values for the service or build step you want to run.

Build local artifacts as needed:

```bash
make build-vector-store
make build-sayt
```

Run the services locally:

```bash
make run-vector-store-api
make run-sayt-api
```

#### Container prerequisites
Before using Docker or Podman Compose, build the artifacts you want the containers to
load and point `VECTOR_STORE_DIR` and `SAYT_ARTIFACT_DIR` in `.env` at those
local directories. The exact Compose service names are `vector-store-api` and
`sayt-api`, while the exposed APIs remain the vector-store API on port `8088`
and the SAYT API on port `8089`. Override those host ports with
`VECTOR_STORE_PORT` and `SAYT_PORT` in `.env` if needed.

#### Run the services with Docker Compose

```bash
make docker-build
make docker-up
```

You can also target a single Compose service:

```bash
make docker-build service=vector-store-api
make docker-build service=sayt-api
make docker-up service=vector-store-api
make docker-up service=sayt-api
```

Stop the containers again with:

```bash
make docker-down
```

#### Run the services with Podman

##### Podman resource requirements

Loading the SAYT semantic model and persisted indexes may exceed the default
Podman machine memory allocation. For representative datasets, allocate at
least 8 GiB memory and enable swap:

```shell
podman machine init \
  --disk-size 100 \
  --cpus 7 \
  --memory 8192 \
  --swap 2048
```

Build and run both services:

```bash
make podman-up
```

Build and run sayt service:

```bash
podman compose up --build sayt-api
```

Build and run the vector-store service:

```bash
podman compose up --build vector-store-api
```

Stop the containers with:

```bash
make docker-down
```

### Testing

The project includes comprehensive test coverage:

- API endpoint tests
- Vector-store functionality tests
- SAYT functionality tests
- Error handling tests

Tests can be run using:

```bash
make unit-tests
make api-tests
make all-tests
```

The tests include coverage requirements:

- Minimum 80% coverage for each module
- Coverage reports showing missing lines
- Separate coverage targets for unit-test and API-test commands

### Code Quality

Code quality is maintained through:

- Static type checking with mypy
- Linting with pylint and ruff
- Security checking with bandit
- Documentation with mkdocs

## Error Handling

The service implements robust error handling:

- Validation errors for invalid requests
- Service unavailability errors
- Detailed error messages for debugging
- Proper HTTP status codes for different error scenarios

## Configuration

Configuration is managed through environment variables loaded from `.env`.
The main settings include:

- Embedding model selection
- Vector-store artifact directory and result limits
- SAYT artifact directory and build inputs
- SAYT build parameters such as minimum characters and default suggestion limit

For day-to-day use, it helps to think of the variables in two groups: runtime
variables used by the APIs when they start, and build variables used by the
local artifact-generation scripts.

When using Docker Compose locally, `VECTOR_STORE_DIR` and `SAYT_ARTIFACT_DIR`
should point to local artifact directories that can be bind-mounted into the
containers.

### Runtime Variables

| Variable                 | Used by                                        | Required | Default         | Description                                                   |
| ------------------------ | ---------------------------------------------- | -------- | --------------- | ------------------------------------------------------------- |
| `VECTOR_STORE_DIR`       | Vector-store API and vector-store build script | No       | `vector_store`  | Directory or GCS URI for persisted vector-store artifacts.    |
| `VECTOR_STORE_K_MATCHES` | Vector-store API                               | No       | `20`            | Maximum number of ranked matches returned per search request. |
| `SAYT_ARTIFACT_DIR`      | SAYT API and SAYT build script                 | No       | `sayt_artifact` | Directory or GCS URI for persisted SAYT artifacts.            |

### Build Variables

| Variable                  | Used by                                                               | Required                    | Default                  | Description                                                                                                                         |
| ------------------------- | --------------------------------------------------------------------- | --------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `INDEX_SOURCE_FILE`       | `make build-vector-store` / `scripts/build_vector_store_artifacts.py` | Yes for vector-store builds | None                     | Local path or GCS URI for the source data used to build vector-store artifacts.                                                     |
| `EMBEDDING_MODEL_NAME`    | `make build-vector-store` / `scripts/build_vector_store_artifacts.py` | No                          | embed-core default model | Embedding model override used during vector-store artifact generation.                                                              |
| `SAYT_SOURCE_FILE`        | `make build-sayt` / `scripts/build_sayt_artifacts.py`                 | Yes for SAYT builds         | None                     | Local path or GCS URI for the source CSV used to build SAYT artifacts.                                                              |
| `SEARCH_TEXT_COL`         | `make build-sayt` / `scripts/build_sayt_artifacts.py`                 | No                          | `search_text`            | CSV column used as the SAYT search text.                                                                                            |
| `DISPLAY_TEXT_COL`        | `make build-sayt` / `scripts/build_sayt_artifacts.py`                 | No                          | `display_text`           | CSV column used as the SAYT display text.                                                                                           |
| `MIN_CHARS`               | `make build-sayt` / `scripts/build_sayt_artifacts.py`                 | No                          | `3`                      | Minimum query length baked into the built SAYT artifact. Must be at least `3`.                                                      |
| `DEFAULT_NUM_SUGGESTIONS` | `make build-sayt` / `scripts/build_sayt_artifacts.py`                 | No                          | `10`                     | Default suggestion count baked into the built SAYT artifact and used when API requests omit `limit`. Must be between `1` and `100`. |

The complete example file lives in the repository root as `.env.example`.

## Security

The services are designed to be deployed with:

- API Gateway integration
- Secure data storage
- Environment-specific configurations

## Contributing

Please refer to the project's [contribution guidelines](https://github.com/ONSdigital/survey-assist-vector-store-api/blob/main/CONTRIBUTING.md) for information on:

- Code style
- Testing requirements
- Documentation standards
- Pull request process
