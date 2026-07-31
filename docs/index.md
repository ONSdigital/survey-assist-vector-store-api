# Survey Assist Vector Store API

This repository provides two FastAPI services used by Survey Assist:

- a vector-store API backed by persisted embedding artifacts for SIC and SOC search
- a search-as-you-type (SAYT) API backed by persisted SAYT artifacts

Both services are intended to be deployed as private backend services behind the main Survey Assist API.

## Key Features

- **Vector-store Retrieval**: Similarity-based SIC and SOC retrieval from built embedding artifacts
- **SAYT Suggestions**: Low-latency search-as-you-type suggestions from built SAYT artifacts
- **Configuration Endpoints**: Service-level config visibility for local debugging and operations
- **Artifact Build Scripts**: Local commands for creating vector-store and SAYT artifacts
- **Interactive Documentation**: Built-in Swagger UI and ReDoc for each service

## API Documentation

When running locally, each service exposes its own interactive documentation:

- Vector-store Swagger UI: `http://localhost:8088/docs`
- Vector-store ReDoc: `http://localhost:8088/redoc`
- SAYT Swagger UI: `http://localhost:8089/docs`
- SAYT ReDoc: `http://localhost:8089/redoc`

## Getting Started

For setup, configuration, and local development commands, see the [Guide](guide.md).

## Development

The project includes comprehensive test coverage and follows strict code quality standards:

- Static type checking
- Code linting and formatting
- Security analysis
- Documentation generation

All development tools and processes are documented in the [Guide](guide.md).
