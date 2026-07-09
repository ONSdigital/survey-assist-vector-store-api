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

A generic vector store and api used by survey assist. This can deploy either an industry, occupation or search as you type vector store.

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

## Features

- FastAPI endpoints
- Industry (SIC) vector search
- Occupation (SOC) vector search
- Vector store integration
- API Documentation

## Architecture

The vector store API consists of:

- FastAPI endpoints
- ClassifAI used for vector store
- all-MiniLM-L6-v2 used for embeddings
- Deployed as a Google Cloud Run service

Depending upon configuration the code will deploy and industry, occupation or search as you type vector store.

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

### Start Application

make run-vector-store

### API Documentation

http://localhost:8080/docs

## Configuration

Copy `.env.example` to `.env` and adjust values for your environment. The same
`.env` file is used by the API runtime settings and the vector-store build
script.

| Variable               | Description                                                                    | Required            | Notes                                                                             |
| ---------------------- | ------------------------------------------------------------------------------ | ------------------- | --------------------------------------------------------------------------------- |
| KNOWLEDGEBASE_NAME     | Display name used in API metadata and the root status message                  | No                  | Usually `SIC` or `SOC`; defaults to `Example` if omitted                          |
| VECTOR_STORE_DIR       | Directory or GCS URI for persisted vector-store artifacts                      | No                  | Defaults to `vector_store`; shared by the API and build script                    |
| VECTOR_STORE_K_MATCHES | Maximum number of ranked matches returned per search request                   | No                  | Defaults to `20`                                                                  |
| INDEX_SOURCE_FILE      | Local path or GCS URI for the source data used to build vector-store artifacts | Only for build step | Required by `make build-vector-store` / `scripts/build_vector_store_artifacts.py` |
| EMBEDDING_MODEL_NAME   | Embedding model override for vector-store artifact generation                  | No                  | Defaults to the embed-core model if omitted                                       |

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

## Contributing

Please read [the contribution guidelines](CONTRIBUTING.md) before creating a pull request.

## Additional Documentation

[CONTRIBUTING.md](CONTRIBUTING.md)
[RELEASING.md](RELEASING.md)
[SECURITY.md](SECURITY.md)
[CHANGELOG.md](CHANGELOG.md)
[LICENSE.md](LICENSE.md)
[CODEOWNERS.md](CODEOWNERS.md)
