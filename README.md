# Survey Assist Vector Store API

[![CI](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/ci.yml/badge.svg?branch=main)]

<!-- These could be split out
![CI](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/ci.yml/badge.svg)
![Tests](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/tests.yml/badge.svg)
![Bandit](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/security.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/ONSdigital/survey-assist-vector-store-api)
-->

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/github/license/ONSdigital/survey-assist-vector-store-api)
![Release](https://img.shields.io/github/v/release/ONSdigital/survey-assist-vector-store-api)
![Status](https://img.shields.io/badge/code%20status-in%20development%20-red)

## Overview

This repository now hosts two related FastAPI services used by Survey Assist:

- a vector-search API backed by persisted embedding artifacts
- a search-as-you-type (SAYT) API backed by persisted SAYT artifacts

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Running Locally](#running-locally)
- [Configuration](#configuration)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Security](#security)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)
- [Maintainers](#maintainers)
- [Additional Documentation](#additional-documentation)

## Features

- FastAPI endpoints
- Industry (SIC) vector search
- Occupation (SOC) vector search
- Search-as-you-type suggestion serving
- Artifact build scripts for both service types
- API documentation

## Architecture

The services in this repository consist of:

- FastAPI endpoints
- ClassifAI used for vector-store retrieval artifacts
- SAYT retrieval components from `survey-assist-embed-core`
- all-MiniLM-L6-v2 used for embeddings where required
- Deployed as Google Cloud Run services

Depending on configuration and entrypoint, the code can deploy vector-search or SAYT serving workloads.

**Important** - In the deployed solution, this service is private to GCP services, it will only be called via the main Survey Assist API.

## Prerequisites

- Python 3.12
- Poetry 2.1.3 or later
- Git
- Make
- Docker / Colima (optional) / Podman
- Google Cloud SDK

## Local Development Setup

### Clone Repository

```shell
git clone https://github.com/ONSdigital/survey-assist-vector-store-api.git
```

### Install Dependencies

```shell
poetry install
```

### Install Git Hooks

This repository uses pre-commit hooks to perform code quality,
security, and secret-scanning checks before code is committed.

```shell
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## Running Locally

### Build Artifacts

Build the vector-search artifacts:

```shell
make build-vector-store
```

Build the SAYT artifacts:

```shell
make build-sayt
```

Rebuild SAYT artifacts and replace an existing local artifact directory:

```shell
make rebuild-sayt
```

You can also run the build scripts directly and inspect their supported CLI
flags with `--help`:

```shell
poetry run python scripts/build_vector_store_artifacts.py --help
poetry run python scripts/build_sayt_artifacts.py --help
```

### Start Applications

Run the vector-search API:

```shell
make run-vector-search-api
```

Run the SAYT API:

```shell
make run-sayt-api
```

### API Documentation

Vector-search docs: http://localhost:8088/docs

SAYT docs: http://localhost:8089/docs

The OpenAPI descriptions include the installed package versions for
`survey-assist-vector-store-api` and `survey-assist-embed-core`.

Key runtime endpoints:

- Vector-search runtime configuration: `GET /v1/runtime-config`
- SAYT runtime configuration: `GET /v1/runtime-config`
- SAYT suggestions: `POST /v1/suggest`, returning a JSON array of scored suggestions

## Configuration

Copy `.env.example` to `.env` and adjust values for your environment. The same
`.env` file is used by both API runtimes and both local artifact-build scripts.

| Variable               | Description                                                                    | Required            | Notes                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------ | ------------------- | --------------------------------------------------------------------------------------------- |
| VECTOR_STORE_DIR       | Directory or GCS URI for persisted vector-store artifacts                      | No                  | Defaults to `vector_store`; shared by the API and build script                                |
| VECTOR_STORE_K_MATCHES | Maximum number of ranked matches returned per search request                   | No                  | Defaults to `20`                                                                              |
| INDEX_SOURCE_FILE      | Local path or GCS URI for the source data used to build vector-store artifacts | Only for build step | Required by `make build-vector-store` / `scripts/build_vector_store_artifacts.py`             |
| EMBEDDING_MODEL_NAME   | Embedding model override for vector-store artifact generation                  | No                  | Defaults to the embed-core model if omitted                                                   |
| SAYT_ARTIFACT_DIR      | Directory or GCS URI for persisted SAYT artifacts                              | No                  | Defaults to `sayt_artifact`; used by the SAYT API and build script                            |
| SAYT_SOURCE_FILE       | Local path or GCS URI for the source CSV used to build SAYT artifacts          | Only for build step | Required by `make build-sayt` / `scripts/build_sayt_artifacts.py`                             |
| SEARCH_TEXT_COL        | CSV column used as SAYT search text                                            | No                  | Defaults to `title`                                                                           |
| DISPLAY_TEXT_COL       | Optional CSV column used as SAYT display text                                  | No                  | Defaults to the search-text column when omitted                                               |
| MIN_CHARS              | Minimum query length baked into built SAYT artifacts                           | No                  | Defaults to `4`                                                                               |
| MAX_SUGGESTIONS        | Default suggestion count baked into built SAYT artifacts                       | No                  | Defaults to `10`                                                                              |
| OVERWRITE              | Replace an existing SAYT artifact directory during local builds                | No                  | Defaults to `false`; can also be enabled explicitly with `make rebuild-sayt` or `--overwrite` |

## Repository Structure

Update as the repository evolves

```txt
survey-assist-vector-store-api/
|-- cicd/                           # GCP cloud build cicd pipelines
|-- docs/                           # mkdocs documentation
|-- scripts/                        # scripts not used inline in the application
|-- src/                            # main source
|-- tests/                          # pytest unit tests
|-- .github/                        # GitHub actions workflows
|-- README.md                       # This file
```

## Testing

Run all of the unit tests

```shell
make all-tests
```

Additional testing guidance is available in [CONTRIBUTING.md](CONTRIBUTING.md).

## Code Quality

Running validation checks:

```shell
make check-python-nofix
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards and validation requirements.

## Security

Security checks are performed using:

- Bandit
- GitHub Dependabot
- Secret scanning

Security vulnerabilities **must not** be disclosed publicly.

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Documentation

Documentation is maintained using MkDocs.

```shell
make run-docs
```

## Release Process

Release guidance is documented in [RELEASING.md](RELEASING.md).

## Contributing

Please read [the contribution guidelines](CONTRIBUTING.md) before creating a pull request.

## License

This project is licensed under the terms in [LICENSE](LICENSE).

## Maintainers

Repository ownership and review responsibility are listed in [CODEOWNERS](CODEOWNERS).

## Additional Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [RELEASING.md](RELEASING.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)
- [CODEOWNERS](CODEOWNERS)
