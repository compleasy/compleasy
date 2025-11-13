# Testing Guide

Complete guide to testing in Compleasy.

## Test Structure

All tests use pytest (not Django's unittest):

- `src/api/tests.py` - Unit tests for API endpoints
- `src/api/tests_integration.py` - Integration tests
- `src/api/tests_middleware.py` - Middleware tests
- `src/api/tests_policy_security.py` - Policy security tests
- `src/conftest.py` - Shared pytest fixtures

## Running Tests

### All Tests

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test
```

### Unit Tests Only

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest -m "not integration" -v
```

### Integration Tests Only

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest -m integration -v
```

### Specific Test File

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests.py -v
```

### Specific Test

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests.py::TestUploadReport::test_upload_report_valid_license_new_device -v
```

### With Coverage

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest --cov=api --cov=frontend --cov-report=html --cov-report=term-missing
```

## Test Types

### Unit Tests

Test individual components in isolation:

- API endpoints
- Models
- Forms
- Utilities

### Integration Tests

Test end-to-end workflows:

- Lynis report upload
- License validation
- Policy compliance

### Middleware Tests

Test custom middleware:

- Rate limiting
- Security headers
- Error handling

## Test Fixtures

Fixtures are defined in `src/conftest.py`:

- `license_key` - Sample license key
- `device` - Sample device
- `lynis_report` - Mock Lynis report data

## Writing Tests

### Example Unit Test

```python
import pytest
from api.views import upload_report

def test_upload_report_valid_license(client, license_key):
    response = client.post('/api/lynis/upload/', {
        'licensekey': license_key.licensekey,
        'hostid': 'test-host',
        'data': 'base64-encoded-data'
    })
    assert response.status_code == 200
```

### Example Integration Test

```python
@pytest.mark.integration
def test_lynis_workflow(client, license_key):
    # Upload report
    response = client.post('/api/lynis/upload/', {...})
    assert response.status_code == 200
    
    # Check device created
    device = Device.objects.get(hostid='test-host')
    assert device is not None
```

## Test Database

The test container automatically:
- Runs migrations before tests
- Uses a separate test database
- Cleans up after tests

## Continuous Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests

See `.github/workflows/test.yml` for CI configuration.

## Best Practices

- **Isolation** - Each test should be independent
- **Fixtures** - Use fixtures for common test data
- **Naming** - Use descriptive test names
- **Coverage** - Aim for high test coverage
- **Speed** - Keep tests fast

## Next Steps

- [Development Setup](setup.md) - Development environment
- [Contributing](contributing.md) - Contribution guidelines

