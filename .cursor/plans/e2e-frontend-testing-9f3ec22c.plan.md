<!-- 9f3ec22c-8edc-45ac-9c94-ce3742417b56 5180a236-c628-40e2-935b-183369dda8c0 -->
# E2E Frontend Testing Implementation

## Overview

Add Playwright-based e2e tests to verify frontend functionality, focusing on the complex Policies/Rulesets UI with nested sidebars, AJAX forms, and state management.

## Implementation Steps

### 1. Install Playwright Dependencies

**Update `src/requirements-dev.txt`:**

```python
pytest>=7.4.0
pytest-django>=4.5.0
pytest-playwright>=0.4.0
playwright>=1.40.0
pytest-cov>=4.1.0
coverage>=7.3.0
factory-boy>=3.3.0
```

**Update `Dockerfile.test`:**

Add Playwright browser installation after pip install:

```dockerfile
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN playwright install --with-deps chromium
```

### 2. Configure Pytest for E2E Tests

**Update `pytest.ini`:**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = compleasy.settings
python_files = tests.py test_*.py *_tests.py tests_*.py
python_classes = Test*
python_functions = test_*
addopts = --reuse-db --cov=api --cov=frontend --cov-report=html --cov-report=term-missing
markers =
    integration: marks tests as integration tests
    security: Security-focused tests
    e2e: End-to-end tests using Playwright
```

### 3. Create E2E Test Fixtures

**Create `src/frontend/conftest_e2e.py`:**

- `live_server` fixture for Django test server
- `authenticated_browser` fixture that logs in a test user
- `test_policy_data` fixture that creates sample rulesets and rules
- Helper function `wait_for_sidebar_animation` for consistent waits

### 4. Create E2E Test Suite

**Create `src/frontend/tests_e2e.py`:**

Test coverage for critical paths:

#### Ruleset Tests

- `test_create_ruleset_basic` - Create ruleset without rules
- `test_create_ruleset_with_rules` - Full flow: create → select rules → save
- `test_edit_ruleset_details` - Edit name and description
- `test_delete_ruleset_with_confirmation` - Delete with dialog confirmation

#### Rule Tests

- `test_create_rule` - Create new rule
- `test_edit_rule` - Edit existing rule
- `test_delete_rule_with_confirmation` - Delete with dialog confirmation

#### Device Detail Tests

- `test_device_select_rulesets` - Open ruleset selection sidebar
- `test_device_create_ruleset_from_detail` - Create ruleset from device view
- `test_device_nested_sidebar_state` - Verify edit sidebar hides/shows selection sidebar

#### Sidebar State Tests

- `test_sidebar_cancel_closes_panel` - Cancel button works
- `test_sidebar_x_button_closes_panel` - X button works
- `test_nested_sidebar_returns_to_parent` - Rule selection → back to ruleset edit

### 5. Update Docker Compose for E2E Tests

**Update `docker-compose.dev.yml`:**

Add e2e test service:

```yaml
test-e2e:
  build:
    context: .
    dockerfile: Dockerfile.test
  container_name: compleasy-test-e2e
  volumes:
    - ./src:/app
    - ./pytest.ini:/app/pytest.ini
  environment:
    - SECRET_KEY=${SECRET_KEY:-test-secret-key-for-testing}
    - DJANGO_ENV=testing
    - DJANGO_DEBUG=False
    - DJANGO_ALLOWED_HOSTS=*
    - PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
  working_dir: /app
  command: ["pytest", "-v", "-m", "e2e"]
  profiles:
    - test
  depends_on:
    - compleasy
```

### 6. Update CI/CD Pipeline

**Update `.github/workflows/test.yml`:**

Add new job after integration tests:

```yaml
e2e-tests:
  name: E2E Tests
  runs-on: ubuntu-latest
  needs: unit-tests
  
  steps:
  - uses: actions/checkout@v4
  
  - name: Set up Docker Buildx
    uses: docker/setup-buildx-action@v3
  
  - name: Build test image with Playwright
    run: |
      docker compose -f docker-compose.dev.yml --profile test build test-e2e
  
  - name: Start Compleasy service
    run: |
      docker compose -f docker-compose.dev.yml up -d compleasy
    env:
      SECRET_KEY: ${{ secrets.SECRET_KEY || 'test-secret' }}
  
  - name: Wait for service to be ready
    run: |
      docker compose -f docker-compose.dev.yml exec -T compleasy /bin/bash -c \
        "until curl -sf http://localhost:8000/health/; do sleep 2; done"
  
  - name: Run E2E tests
    run: |
      docker compose -f docker-compose.dev.yml --profile test run --rm test-e2e \
        pytest -v -m e2e --html=e2e-report.html --self-contained-html
  
  - name: Upload test report
    if: always()
    uses: actions/upload-artifact@v3
    with:
      name: e2e-test-report
      path: src/e2e-report.html
```

### 7. Documentation

**Create `docs/development/e2e-testing.md`:**

- How to run e2e tests locally
- How to debug failing tests
- How to add new test cases
- Common patterns and best practices
- Troubleshooting guide

**Update `README.md`:**

Add section on e2e testing:

````markdown
#### E2E Tests (Playwright)

Run end-to-end tests in headless browser:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test-e2e
````

Run specific e2e test:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test-e2e \
  pytest frontend/tests_e2e.py::test_create_ruleset_with_rules -v
```
```

### 8. Test Maintenance Guidelines

**Create `AGENTS.md` section:**

Add guidelines for AI agents working on frontend:

- Run e2e tests after any frontend changes
- Update selectors if UI structure changes
- Add new e2e test for new user-facing features
- Keep tests focused on user interactions, not implementation details

## Success Criteria

- All 12+ e2e tests pass locally and in CI/CD
- Tests run in under 3 minutes total
- Clear documentation for running and debugging tests
- CI/CD fails if e2e tests fail
- Tests are maintainable and don't require frequent updates for minor UI changes

### To-dos

- [ ] Add Playwright dependencies to requirements-dev.txt and Dockerfile.test
- [ ] Update pytest.ini with e2e marker
- [ ] Create conftest_e2e.py with authentication and test data fixtures
- [ ] Write e2e tests for ruleset CRUD operations (create, edit, delete)
- [ ] Write e2e tests for rule CRUD operations (create, edit, delete)
- [ ] Write e2e tests for device detail interactions
- [ ] Write e2e tests for sidebar state management
- [ ] Add test-e2e service to docker-compose.dev.yml
- [ ] Add e2e-tests job to GitHub Actions workflow
- [ ] Create e2e-testing.md documentation and update README.md
- [ ] Update AGENTS.md with e2e testing guidelines