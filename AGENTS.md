# Agent Guidelines for Compleasy

This document contains critical guidelines and hints for AI agents working on the Compleasy project.

## Critical Commands

### Docker Compose Syntax

**ALWAYS use `docker compose` (with a space), NEVER `docker-compose` (with a hyphen).**

- ✅ Correct: `docker compose up`
- ✅ Correct: `docker compose -f docker-compose.dev.yml run --rm test`
- ❌ Wrong: `docker-compose up`
- ❌ Wrong: `docker-compose -f docker-compose.dev.yml run --rm test`

This is the modern Docker Compose V2 syntax. All commands, documentation, and scripts should use this format.

## Testing Infrastructure

### All Tests Run in Docker

**Never install dependencies locally. All tests must run inside Docker containers.**

- Tests are run using: `docker compose -f docker-compose.dev.yml --profile test run --rm test`
- The test container automatically runs migrations before executing tests
- Test container has all dependencies pre-installed (pytest, pytest-django, coverage, etc.)
- Source code is mounted as a volume for live testing

### Test Commands

```bash
# Run all unit tests
docker compose -f docker-compose.dev.yml --profile test run --rm test

# Run specific test file
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests.py -v

# Run with coverage
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest --cov=api --cov=frontend --cov-report=html --cov-report=term-missing

# Run specific test
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests.py::TestUploadReport::test_upload_report_valid_license_new_device -v

# Access test container shell
docker compose -f docker-compose.dev.yml --profile test run --rm test /bin/bash
```

## Critical API Endpoints (DO NOT BREAK)

The following Lynis API endpoints **MUST** remain unchanged to maintain compatibility:

### `/api/lynis/upload/`
- **Location**: `src/api/views.py` - `upload_report()` function
- **URL Pattern**: `/api/lynis/upload/`
- **Method**: POST only
- **Decorator**: `@csrf_exempt` (required for external API)
- **Request Format**: Form data with `licensekey`, `hostid`, `hostid2`, `data`
- **Response Format**: `'OK'` (200) or error messages
- **Critical**: Used by Lynis clients to upload audit reports

### `/api/lynis/license/`
- **Location**: `src/api/views.py` - `check_license()` function
- **URL Pattern**: `/api/lynis/license/`
- **Method**: POST only
- **Decorator**: `@csrf_exempt` (required for external API)
- **Request Format**: Form data with `licensekey`, `collector_version`
- **Response Format**: `'Response 100'` (200) for valid, `'Response 500'` (401) for invalid
- **Critical**: Used by Lynis clients to validate license keys

**When modifying these endpoints:**
- Never change the URL patterns
- Never remove `@csrf_exempt` decorator
- Never change request/response format
- Always test with actual Lynis client before committing changes

## Project Structure

### Key Directories

- `src/` - Main application source code
  - `src/api/` - API application (models, views, forms, tests)
  - `src/frontend/` - Frontend application (views, templates, static files)
  - `src/compleasy/` - Django project settings
  - `src/utils/` - Shared utilities (will be moved to proper app structure)
  - `src/conftest.py` - Pytest fixtures
- `lynis/` - Lynis integration files
  - `lynis/Dockerfile` - Docker image for Lynis client testing
  - `lynis/run-lynis-test.sh` - Integration test script
- `compleasy-lynis-plugin/` - Lynis custom plugin
- `.github/workflows/` - CI/CD workflows

### Key Files

- `docker-compose.yml` - Production Docker Compose configuration
- `docker-compose.dev.yml` - Development Docker Compose configuration (includes test service)
- `Dockerfile` - Production Docker image
- `Dockerfile.test` - Test Docker image
- `pytest.ini` - Pytest configuration
- `src/requirements.txt` - Production dependencies
- `src/requirements-dev.txt` - Development dependencies (pytest, coverage, etc.)

## Security Considerations

### Critical Security Issues (from plan)

1. **Open Redirect Vulnerability** - `src/frontend/views.py` lines 109, 300, 313
   - Never use `request.META.get('HTTP_REFERER')` directly in redirects
   - Always validate referer against safe URLs

2. **Weak Default Credentials** - `docker-compose.yml` line 12
   - Never hardcode passwords in version control
   - Use environment variables with `.env.example` for defaults

3. **ALLOWED_HOSTS** - `src/compleasy/settings.py` line 54
   - Never use `ALLOWED_HOSTS = ['*']` in production
   - Require explicit configuration via environment variable

4. **DEBUG Logging** - `src/compleasy/settings.py` lines 17-29
   - Root logger set to `DEBUG` exposes sensitive information
   - Make logging level configurable via environment variable

5. **Missing Security Headers** - Add HSTS, X-Content-Type-Options, CSP headers

6. **Unvalidated Input** - `src/frontend/views.py` lines 141-151, 163-177
   - Always validate license keys from URL parameters

7. **No Rate Limiting** - API endpoints need rate limiting protection

## Code Conventions

### Django Best Practices

- Use Django's built-in features (forms, validators, middleware)
- Follow Django naming conventions
- Use `db_index=True` on frequently queried fields
- Move business logic out of views into models or utility functions

### Testing

- All tests use pytest (not Django's unittest)
- Tests are in `src/api/tests.py` (unit tests) and `src/api/tests_integration.py` (integration tests)
- Use fixtures from `src/conftest.py` for common test data
- Integration tests are marked with `@pytest.mark.integration`
- Always test critical Lynis API endpoints before committing

### Database

- Currently using SQLite (will be migrated to PostgreSQL for production)
- Migrations are automatically run in test container
- Never commit database files (`*.sqlite3`)

## Environment Variables

### Required

- `SECRET_KEY` - Django secret key (must be set, no default)
- `DJANGO_DEBUG` - Debug mode (default: `False` for security)

### Optional

- `DJANGO_ALLOWED_HOSTS` - Allowed hosts (default: `['*']` for development)
- `COMPLEASY_URL` - Compleasy server URL
- `COMPLEASY_ADMIN_USERNAME` - Admin username (default: `admin`)
- `COMPLEASY_ADMIN_PASSWORD` - Admin password (default: `compleasy`)

## Common Tasks

### Running Tests

```bash
# Unit tests only
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest -m "not integration" -v

# Integration tests only
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest -m integration -v

# All tests
docker compose -f docker-compose.dev.yml --profile test run --rm test
```

### Running Development Server

```bash
docker compose -f docker-compose.dev.yml up compleasy
```

### Running Integration Tests with Lynis

```bash
# Set environment variables
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
export COMPLEASY_LICENSE_KEY=test-license-key-$(date +%s)

# Start services
docker compose -f docker-compose.dev.yml up -d compleasy

# Wait for health check, then run Lynis client
docker compose -f docker-compose.dev.yml up --abort-on-container-exit lynis-client
```

## Important Notes

1. **Never break Lynis compatibility** - The API endpoints are used by external Lynis clients
2. **Always test in Docker** - Never assume local environment matches production
3. **Use Docker Compose V2 syntax** - Always `docker compose`, never `docker-compose`
4. **Security first** - Review security implications of all changes
5. **Test coverage** - Maintain test coverage for critical functionality
6. **Documentation** - Update README.md and this file when making significant changes

## File Naming Conventions

- Docker files: `Dockerfile`, `Dockerfile.test`, `docker-compose.yml`, `docker-compose.dev.yml`
- Test files: `tests.py`, `tests_integration.py`, `conftest.py`
- Configuration: `pytest.ini`, `settings.py`
- Scripts: `docker-entrypoint.sh`, `docker-entrypoint-test.sh`, `run-lynis-test.sh`

## When Making Changes

1. **Before making changes:**
   - Read this file completely
   - Understand the impact on Lynis API endpoints
   - Check if tests exist for the code you're modifying

2. **While making changes:**
   - Use `docker compose` syntax (not `docker-compose`)
   - Run tests in Docker containers
   - Test Lynis integration if modifying API endpoints

3. **After making changes:**
   - Run all tests: `docker compose -f docker-compose.dev.yml --profile test run --rm test`
   - Verify Lynis integration still works
   - Update documentation if needed
   - Update this file if you discover new important guidelines

