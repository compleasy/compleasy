<!-- 680da20b-4c8a-412d-80c2-9a943e4f2778 f6275b7f-86ae-44ca-9a3b-bd3aef9a2ab4 -->
# Phase 0 - Test Infrastructure Setup

## Overview

Establish a robust testing foundation with pytest-django, real Lynis integration testing via Docker, and automated CI/CD pipeline. This ensures all future security fixes can be validated without breaking Lynis compatibility.

## Implementation Steps

### 1. Testing Dependencies

**Create `src/requirements-dev.txt`:**

- `pytest>=7.4.0` - Modern testing framework
- `pytest-django>=4.5.0` - Django integration for pytest
- `pytest-cov>=4.1.0` - Coverage reporting
- `coverage>=7.3.0` - Code coverage analysis
- `factory-boy>=3.3.0` - Test data factories

**Update `.gitignore`:**

- Add `.pytest_cache/`, `.coverage`, `htmlcov/`, `*.pyc`, `__pycache__/`

### 2. Pytest Configuration

**Create `pytest.ini`:**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = compleasy.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = --reuse-db --cov=api --cov=frontend --cov-report=html --cov-report=term-missing
```

**Create `src/conftest.py`:**

- Shared fixtures for LicenseKey, Device, test data
- Mock Lynis report data fixture
- Database setup helpers

### 3. Critical API Endpoint Tests

**Update `src/api/tests.py`:**

Test coverage for:

- `upload_report()` - Valid license, new device, report parsing, diff generation
- `upload_report()` - Invalid license (401), missing hostid (400), malformed data (400)
- `upload_report()` - Existing device update flow
- `upload_report()` - GET/PUT/DELETE methods (405)
- `check_license()` - Valid license returns "Response 100"
- `check_license()` - Invalid license returns 401 with "Response 500"
- `check_license()` - Missing parameters (400)
- `check_license()` - GET method (405)

Critical: Verify response format matches Lynis expectations exactly.

### 4. Docker Development Environment

**Create `docker-compose.dev.yml`:**

Services:

- `compleasy-dev` - Django app with volume mounts for live code reload
- `lynis-client` - Alpine-based container with:
  - Lynis installation
  - Compleasy plugin (`compleasy-lynis-plugin/plugin_compleasy_phase1`)
  - Test script to run Lynis and upload reports
  - Network access to `compleasy-dev`

Environment variables:

- `COMPLEASY_SERVER_URL=http://compleasy-dev:8000`
- `COMPLEASY_LICENSE_KEY` (generated on first run)

**Create `tests/docker/Dockerfile.lynis-client`:**

```dockerfile
FROM alpine:latest
RUN apk add --no-cache lynis curl bash
# Copy plugin and test scripts
# Configure Lynis to use compleasy plugin
```

**Create `tests/docker/run-lynis-test.sh`:**

- Check license validity
- Run Lynis scan with compleasy plugin
- Verify upload success
- Run second scan to test diff generation

### 5. Integration Test Suite

**Create `src/api/tests_integration.py`:**

- Test end-to-end Lynis workflow (requires Docker setup)
- Validate actual Lynis report parsing
- Verify plugin data collection
- Test multi-report diff generation

### 6. GitHub Actions CI/CD

**Create `.github/workflows/test.yml`:**

Workflow triggers:

- Push to main/develop branches
- Pull requests

Jobs:

1. **Unit Tests:**

   - Python 3.11 (current target)
   - Install dependencies from requirements.txt + requirements-dev.txt
   - Run migrations
   - Execute pytest with coverage
   - Upload coverage report

2. **Integration Tests:**

   - Build docker-compose.dev.yml services
   - Wait for Django service health
   - Run Lynis client test script
   - Verify report upload and parsing
   - Check logs for errors

3. **Linting (optional but recommended):**

   - flake8 or ruff for code quality

### 7. Test Data Fixtures

**Create `src/api/fixtures/test_data.json`:**

- Sample LicenseKey objects
- Sample Device objects
- Sample PolicyRule/PolicyRuleset for compliance testing

**Create `src/api/fixtures/sample_lynis_report.dat`:**

- Valid Lynis report data for testing parsing logic
- Include common fields: hostname, os, warnings, suggestions, etc.

### 8. Documentation

**Update `README.md` - Add "Development & Testing" section:**

````markdown
## Development & Testing

### Running Tests Locally
```bash
# Install dev dependencies
pip install -r src/requirements-dev.txt

# Run unit tests
cd src && pytest

# Run with coverage
pytest --cov=api --cov=frontend --cov-report=html

# Integration tests with Docker
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec lynis-client /test/run-lynis-test.sh
````

### Test Structure

- `src/api/tests.py` - Unit tests for API endpoints
- `src/api/tests_integration.py` - Integration tests
- `src/conftest.py` - Shared fixtures

```

## Critical Success Criteria

1. All tests pass with current codebase (no code changes yet)
2. Lynis client successfully:

   - Validates license via `/api/lynis/license/`
   - Uploads report via `/api/lynis/upload/`
   - Generates diff on second upload

3. GitHub Actions pipeline runs green
4. Test coverage for Lynis API endpoints >= 80%

## Files to Create

- `src/requirements-dev.txt`
- `pytest.ini`
- `src/conftest.py`
- `docker-compose.dev.yml`
- `tests/docker/Dockerfile.lynis-client`
- `tests/docker/run-lynis-test.sh`
- `src/api/tests_integration.py`
- `src/api/fixtures/test_data.json`
- `src/api/fixtures/sample_lynis_report.dat`
- `.github/workflows/test.yml`

## Files to Modify

- `src/api/tests.py` (add comprehensive tests)
- `.gitignore` (add test artifacts)
- `README.md` (add testing documentation)

## Non-Goals for Phase 0

- No code refactoring or security fixes (Phase 1+)
- No changes to production docker-compose.yml
- No changes to API endpoints or models
- Tests should validate **current** behavior, not ideal behavior

### To-dos

- [ ] Create requirements-dev.txt with pytest, pytest-django, pytest-cov, coverage, factory-boy
- [ ] Create pytest.ini with Django settings and coverage configuration
- [ ] Create conftest.py with shared fixtures for LicenseKey, Device, and mock Lynis report data
- [ ] Write comprehensive tests in src/api/tests.py for upload_report and check_license endpoints
- [ ] Create Dockerfile.lynis-client with Alpine, Lynis installation, and plugin configuration
- [ ] Create run-lynis-test.sh script to automate Lynis scan and report upload
- [ ] Create docker-compose.dev.yml with compleasy-dev and lynis-client services
- [ ] Create tests_integration.py for end-to-end Lynis workflow testing
- [ ] Create .github/workflows/test.yml with unit and integration test jobs
- [ ] Update .gitignore to exclude pytest cache, coverage reports, and Python artifacts
- [ ] Add Development & Testing section to README.md with instructions
- [ ] Run all tests locally and ensure they pass with current codebase