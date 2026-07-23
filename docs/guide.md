# Survey Assist Vector Store API Guide

## Overview

This repository hosts two related FastAPI services:

- the vector-store API, which loads persisted embedding artifacts and serves ranked search results
- the SAYT API, which loads persisted SAYT artifacts and serves scored typeahead suggestions

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
The SAYT suggestions endpoint accepts `query` plus optional `num_suggestions` and returns a JSON object whose `suggestions` field contains scored suggestions.

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
