# E2E Testing with Playwright

This document describes how to run and maintain end-to-end (E2E) tests for the TrikuSec frontend using Playwright.

## Overview

E2E tests verify the complete user experience by testing the frontend in a real browser environment. The tests cover:

- Ruleset CRUD operations (create, edit, delete)
- Rule CRUD operations (create, edit, delete)
- Device detail page interactions
- Sidebar state management and nested sidebar behavior
- AJAX form submissions
- Dialog confirmations

## Running E2E Tests

### Prerequisites

- Docker and Docker Compose installed
- TrikuSec service running (for E2E tests that need the live server)

### Running All E2E Tests

Run all E2E tests in headless mode:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test-e2e
```

### Running Specific Tests

Run a specific test file:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test-e2e \
  pytest frontend/tests_e2e.py -v
```

Run a specific test:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test-e2e \
  pytest frontend/tests_e2e.py::TestRulesetCRUD::test_create_ruleset_basic -v
```

### Running Tests with HTML Report

Generate an HTML report:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test-e2e \
  pytest -v -m e2e --html=e2e-report.html --self-contained-html
```

The report will be saved in `src/e2e-report.html`.

### Running Tests in Headed Mode (for Debugging)

To see the browser while tests run, you'll need to modify the test container to run in non-headless mode. This requires changes to the test configuration or running tests locally.

## Test Structure

### Test Files

- **`src/frontend/tests_e2e.py`**: Main E2E test suite
- **`src/frontend/conftest_e2e.py`**: E2E-specific fixtures

### Test Classes

- **`TestRulesetCRUD`**: Tests for ruleset create, edit, delete operations
- **`TestRuleCRUD`**: Tests for rule create, edit, delete operations
- **`TestDeviceDetailInteractions`**: Tests for device detail page interactions
- **`TestSidebarStateManagement`**: Tests for sidebar state and nested sidebar behavior

### Fixtures

- **`authenticated_browser`**: Provides a logged-in browser session
- **`test_policy_data`**: Creates sample rules and rulesets for testing
- **`test_device_with_rulesets`**: Creates a device with assigned rulesets
- **`live_server_url`**: Provides the URL of the Django test server

## Writing New E2E Tests

### Basic Test Structure

```python
@pytest.mark.e2e
def test_my_feature(authenticated_browser, live_server_url):
    """Test description."""
    page = authenticated_browser
    
    # Navigate to page
    page.goto(f"{live_server_url}/policies/")
    page.wait_for_load_state("networkidle")
    
    # Interact with page
    page.click('button:has-text("New Ruleset")')
    
    # Assert results
    assert page.locator('text=Expected Text').is_visible()
```

### Best Practices

1. **Use descriptive test names**: Test names should clearly describe what they test
2. **Wait for elements**: Always wait for elements to be visible/ready before interacting
3. **Use data-testid attributes**: When possible, use stable selectors (consider adding `data-testid` to HTML)
4. **Test user flows**: Focus on complete user workflows, not implementation details
5. **Keep tests independent**: Each test should be able to run in isolation
6. **Use fixtures**: Leverage fixtures for common setup (authentication, test data)

### Common Patterns

#### Waiting for Sidebars

```python
sidebar = page.locator('#ruleset-edit-panel')
sidebar.wait_for(state="visible", timeout=5000)
```

#### Filling Forms

```python
page.fill('#ruleset_name', 'Test Ruleset')
page.fill('#ruleset_description', 'Test description')
```

#### Handling Dialogs

```python
page.once("dialog", lambda dialog: dialog.accept())
page.click('button:has-text("Delete")')
```

#### Checking Visibility

```python
assert page.locator('text=Expected Text').is_visible()
assert page.locator('text=Should Not Exist').is_hidden()
```

## Debugging Failing Tests

### View Test Output

E2E tests provide detailed output. Look for:

- Element not found errors
- Timeout errors
- Network errors
- JavaScript console errors

### Common Issues

1. **Element not found**: The selector might be incorrect or the element might not be loaded yet
   - Solution: Add explicit waits or check if the element exists before interacting

2. **Timeout errors**: The page might be loading slowly or an action might be taking too long
   - Solution: Increase timeout or add explicit waits

3. **Dialog not handled**: If a test expects a dialog but it doesn't appear
   - Solution: Check if the dialog handler is set up before clicking the button

4. **Sidebar state issues**: Sidebars might not be in the expected state
   - Solution: Wait for sidebar animations to complete before interacting

### Running Tests Locally (Advanced)

For advanced debugging, you can run tests locally:

1. Install dependencies:
   ```bash
   pip install -r src/requirements-dev.txt
   playwright install chromium
   ```

2. Set up environment:
   ```bash
   export SECRET_KEY=test-secret-key
   export DJANGO_ENV=testing
   ```

3. Run tests:
   ```bash
   cd src
   pytest frontend/tests_e2e.py -v
   ```

## CI/CD Integration

E2E tests run automatically in GitHub Actions after integration tests pass. The workflow:

1. Builds the test image with Playwright
2. Starts the TrikuSec service
3. Waits for the service to be ready
4. Runs E2E tests
5. Uploads HTML test report as an artifact
6. Fails the build if tests fail

## Maintenance Guidelines

### When to Update Tests

- **UI changes**: If you change UI structure (HTML, CSS classes, IDs), update selectors
- **New features**: Add E2E tests for new user-facing features
- **Bug fixes**: Add regression tests for fixed bugs

### Selector Strategy

- **Prefer stable selectors**: Use IDs, data attributes, or text content
- **Avoid CSS classes**: CSS classes may change for styling reasons
- **Use semantic selectors**: Prefer `button:has-text("Save")` over `button.btn-primary`

### Test Data

- Use fixtures to create test data
- Clean up test data in fixtures (Django's test database is reset between tests)
- Use descriptive names for test data (e.g., "Test Ruleset E2E")

## Troubleshooting

### Tests Fail Intermittently

- **Timing issues**: Add explicit waits for async operations
- **Race conditions**: Ensure proper sequencing of actions
- **Browser state**: Check if previous tests are affecting current test

### Browser Not Found

If you see "Browser not found" errors:

```bash
# Rebuild the test image
docker compose -f docker-compose.dev.yml --profile test build test-e2e
```

### Service Not Ready

If tests fail because the service isn't ready:

- Check service logs: `docker compose -f docker-compose.dev.yml logs trikusec`
- Increase wait timeout in CI/CD workflow
- Check health endpoint: `curl http://localhost:8000/health/`

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest-playwright Documentation](https://pytest-playwright.readthedocs.io/)
- [Django Live Server Testing](https://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.LiveServerTestCase)

