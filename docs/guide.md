# Survey Assist Vector Store API Guide

## Overview

update when merged

## Architecture

update when merged

## API Endpoints

update when merged

## Integration with Survey Assist API

The Vector Store Service integrates with the Survey Assist API to provide:
- Embedding-based similarity search for SIC code classification
- Real-time status monitoring
- Efficient vector storage and retrieval
- Asynchronous communication

## Documentation

### Interactive Documentation
The service provides two types of interactive documentation:
1. **Swagger UI** (`/docs`)
   - Interactive API testing
   - Request/response schemas
   - Example values
   - Try-it-out functionality

2. **ReDoc** (`/redoc`)
   - Alternative documentation view
   - Clean, readable format
   - Schema visualisation

You can access these interactive documentation tools by ensuring the service is running and then navigating to the `/docs` or `/redoc` URL in a browser (e.g., http://127.0.0.1:8088/docs).

## Development

### Prerequisites
- Python 3.12
- Poetry for dependency management
- Access to data files
- Sufficient memory for vector storage

### Setup
update when merged

### Testing
The project includes comprehensive test coverage:
- API endpoint tests
- Vector store functionality tests
- Error handling tests
- Integration tests

Tests can be run using:
```bash
make unit-tests  # Run unit tests with coverage for utils module
make api-tests   # Run API tests with coverage for api module
make all-tests   # Run all tests with coverage for the entire project
```

The tests include coverage requirements:
- Minimum 80% coverage for each module
- Coverage reports showing missing lines
- Separate coverage for API and utility modules

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

The service provides a configuration system that includes:
- Embedding model selection
- Database directory configuration
- Index file paths
- Search parameters

Configuration is managed through environment variables and configuration files.

## Security

The service is designed to be deployed with:
- API Gateway integration
- Secure data storage
- Environment-specific configurations
- Rate limiting

## Contributing

Please refer to the project's [contribution guidelines](https://github.com/ONSdigital/survey-assist-vector-store-api/blob/main/CONTRIBUTING.md) for information on:
- Code style
- Testing requirements
- Documentation standards
- Pull request process
