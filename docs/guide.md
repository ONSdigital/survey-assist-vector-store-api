# Survey Assist Vector Store API Guide

## Overview

This repository hosts two related FastAPI services:

- the vector-store API, which loads persisted embedding artifacts and serves ranked search results
- the SAYT API, which loads persisted SAYT artifacts and serves plain and scored search-as-you-type suggestions

Both services share the same codebase, validation workflow, and local `.env` file, but they run as separate processes and expose separate OpenAPI docs.

## Architecture

The repository is organised around two service entrypoints plus shared helpers:

- `survey_assist_vector_store_api.vector_store_api.main:app` runs the vector-store API on port `8088`
- `survey_assist_vector_store_api.sayt_api.main:app` runs the SAYT API on port `8090`
- `scripts/build_vector_store_artifacts.py` builds embedding artifacts used by the vector-store API
- `scripts/build_sayt_artifacts.py` builds SAYT artifacts used by the SAYT API

Shared modules under `src/survey_assist_vector_store_api/shared/` provide common FastAPI wiring, app metadata, and error handling.

## API Endpoints

The main local endpoints are:

- Vector-store docs: `http://localhost:8088/docs`
- SAYT docs: `http://localhost:8090/docs`
- Vector-store search: `POST /v1/search-index`
- Vector-store configuration: `GET /v1/configuration`
- SAYT suggestions: `POST /v1/suggestions`
- SAYT configuration: `GET /v1/configuration`

The vector-store search endpoint accepts a `query` list of cumulative fragments. The SAYT suggestions endpoint accepts `query` plus optional positive `limit` and returns a JSON object whose `suggestions` field contains scored suggestion objects. For the SAYT suggestions endpoint, `limit` overrides the default for that request only. If it is omitted, the API uses the default suggestion count baked into the loaded SAYT artifact when it was built, configured via `DEFAULT_NUM_SUGGESTIONS`.

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

To prepare separate local artifacts for different taxonomies or knowledgebase sources, run the same build targets with different source-file and output-directory overrides:

```bash
make build-vector-store INDEX_SOURCE_FILE=path/to/sic_source.csv VECTOR_STORE_DIR=vector_store_sic
make build-vector-store INDEX_SOURCE_FILE=path/to/soc_source.csv VECTOR_STORE_DIR=vector_store_soc
make build-sayt SAYT_SOURCE_FILE=path/to/sic_sayt_source.csv SAYT_ARTIFACT_DIR=sayt_artifact_sic
make build-sayt SAYT_SOURCE_FILE=path/to/soc_sayt_source.csv SAYT_ARTIFACT_DIR=sayt_artifact_soc
```

Run the services locally:

```bash
make run-vector-store-api
make run-sayt-api
```

Direct `make` runs can take these values from `.env`, exported shell variables, or `make VAR=value` overrides. When more than one source is set, shell variables and `make VAR=value` overrides take precedence. This keeps the workflow taxonomy-agnostic: the same targets can run SIC, SOC, or future knowledgebases by changing source-file, artifact-directory, and port variables. Docker and Podman Compose read the same values from `.env` or your shell environment:

```bash
make run-vector-store-api VECTOR_STORE_DIR=vector_store_sic VECTOR_STORE_PORT=8088
make run-vector-store-api VECTOR_STORE_DIR=vector_store_soc VECTOR_STORE_PORT=8089
make run-sayt-api SAYT_ARTIFACT_DIR=sayt_artifact_sic SAYT_PORT=8090
make run-sayt-api SAYT_ARTIFACT_DIR=sayt_artifact_soc SAYT_PORT=8091
```

#### Container prerequisites

Before using Docker or Podman Compose, build the artifacts you want the containers to load and point `VECTOR_STORE_DIR` and `SAYT_ARTIFACT_DIR` in `.env` or your shell environment at those local directories. The exact Compose service names are `vector-store-api` and `sayt-api`, while the exposed APIs remain the vector-store API on port `8088` and the SAYT API on port `8090`. Override those host ports with `VECTOR_STORE_PORT` and `SAYT_PORT` in `.env` or your shell environment if needed.

The provided Compose file defines one vector-store service and one SAYT service per Compose project. If you want to run SIC and SOC side by side with Docker or Podman, use the same artifact-directory and port overrides as direct terminal runs, and give each stack its own `COMPOSE_PROJECT_NAME` so the containers, network, and host-port bindings stay separate.

#### Run the services with Docker Compose

```bash
make docker-build
make docker-up
```

To run SIC and SOC side by side with Docker Compose, start two separate Compose projects:

Start the SIC stack:

```bash
make docker-up \
   COMPOSE_PROJECT_NAME=sic-demo \
   VECTOR_STORE_DIR=data/output/vector_store_sic_demo \
   SAYT_ARTIFACT_DIR=data/output/sayt_artifact_sic_demo \
   VECTOR_STORE_PORT=8088 \
   SAYT_PORT=8090
```

Start the SOC stack:

```bash
make docker-up \
   COMPOSE_PROJECT_NAME=soc-demo \
   VECTOR_STORE_DIR=data/output/vector_store_soc_demo \
   SAYT_ARTIFACT_DIR=data/output/sayt_artifact_soc_demo \
   VECTOR_STORE_PORT=8089 \
   SAYT_PORT=8091
```

This mirrors the direct terminal workflow: the same artifact directories and ports are used for each taxonomy, and `COMPOSE_PROJECT_NAME` is the extra value that keeps the two container stacks separate.

`COMPOSE_PROJECT_NAME` is a built-in Docker Compose variable that names the stack and its resources.

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

For side-by-side Docker runs, stop each stack with the same project name you used to start it:

```bash
make docker-down COMPOSE_PROJECT_NAME=sic-demo
make docker-down COMPOSE_PROJECT_NAME=soc-demo
```

#### Run the services with Podman

##### Podman resource requirements

Loading the SAYT semantic model and persisted indexes may exceed the default Podman machine memory allocation. For representative datasets, allocate at least 8 GiB memory and enable swap:

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

The same side-by-side pattern works with Podman:

Start the SIC stack:

```bash
make podman-up \
   COMPOSE_PROJECT_NAME=sic-demo \
   VECTOR_STORE_DIR=data/output/vector_store_sic_demo \
   SAYT_ARTIFACT_DIR=data/output/sayt_artifact_sic_demo \
   VECTOR_STORE_PORT=8088 \
   SAYT_PORT=8090
```

Start the SOC stack:

```bash
make podman-up \
   COMPOSE_PROJECT_NAME=soc-demo \
   VECTOR_STORE_DIR=data/output/vector_store_soc_demo \
   SAYT_ARTIFACT_DIR=data/output/sayt_artifact_soc_demo \
   VECTOR_STORE_PORT=8089 \
   SAYT_PORT=8091
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
make podman-down
```

For side-by-side Podman runs, stop each stack with:

```bash
make podman-down COMPOSE_PROJECT_NAME=sic-demo
make podman-down COMPOSE_PROJECT_NAME=soc-demo
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

Configuration is managed through environment variables. For convenient local defaults, put them in `.env`; for one-off runs, export them in your shell or pass `make VAR=value` overrides.

The same variables keep the workflow taxonomy-agnostic: point the build and runtime commands at different source files, artifact directories, and ports for SIC, SOC, or other knowledgebases.

The main settings include:

- Embedding model selection
- Vector-store artifact directory and result limits
- SAYT artifact directory and build inputs
- SAYT build parameters such as minimum characters and default suggestion limit

For day-to-day use, it helps to think of the variables in two groups: runtime variables used by the APIs when they start, and build variables used by the local artifact-generation scripts.

When using Docker Compose locally, `VECTOR_STORE_DIR` and `SAYT_ARTIFACT_DIR` should point to local artifact directories that can be bind-mounted into the containers. For direct `make` runs, the same variables determine which taxonomy's artifacts each API loads.

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
