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

## License Key Management System

### License Model Structure

The license system supports both **per-device licenses** and **shared licenses** with device limits:

#### Organization Model (Future Multi-Tenancy)
- **Location**: `src/api/models.py` - `Organization` class
- **Purpose**: Foundation for future multi-tenant support (currently single-tenant)
- **Key Fields**: `name`, `slug`, `is_active`
- **Note**: All licenses are currently linked to a default organization

#### LicenseKey Model
- **Location**: `src/api/models.py` - `LicenseKey` class
- **Key Fields**:
  - `licensekey`: Unique license key string (used by Lynis clients)
  - `name`: Human-readable name (e.g., "Production servers" or "web-01")
  - `organization`: ForeignKey to Organization (null allowed for backward compatibility)
  - `max_devices`: Integer or null (null = unlimited devices)
  - `expires_at`: DateTime or null (null = no expiration)
  - `is_active`: Boolean (inactive licenses cannot enroll new devices)
- **Methods**:
  - `device_count()`: Returns number of devices using this license
  - `has_capacity()`: Checks if license can accept more devices (considers active status, expiration, and device count)

#### Critical Constraints

1. **Lynis API Compatibility**: 
   - The `licensekey` field is the ONLY authentication mechanism
   - There is NO separate "device token" - license key = device authentication
   - Lynis clients send `licensekey` in POST data - this cannot be changed

2. **License Capacity Checks**:
   - New device enrollment checks license capacity before creating device
   - Existing devices can continue uploading reports even if license is at capacity
   - Capacity check considers: `is_active`, `expires_at`, and `device_count` vs `max_devices`

3. **License Validation**:
   - `validate_license()`: Checks if license exists, is active, and not expired
   - `check_license_capacity()`: Validates license AND checks if it has capacity
   - Both functions used in `upload_report()` endpoint

#### License Utilities

- **Location**: `src/api/utils/license_utils.py`
- **Functions**:
  - `generate_license_key()`: Generates unique license key in format `xxxxxxxx-xxxxxxxx-xxxxxxxx`
  - `validate_license(licensekey)`: Returns (is_valid: bool, error_message: str)
  - `check_license_capacity(licensekey)`: Returns (has_capacity: bool, error_message: str)

#### Migration Notes

- Migration `0010_add_organization_and_license_fields.py`:
  - Creates default organization
  - Sets existing licenses to `max_devices=null` (unlimited) to maintain current behavior
  - Adds new fields to LicenseKey model
  - Makes `licensekey` field unique

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

## UI/UX Architecture

### Collapsible Sidebar Pattern

Compleasy uses a **consistent UX pattern** for CRUD operations:

- **List views**: Full-window display (e.g., license list, device list)
- **Detail views**: Full-window with related data (e.g., license details with devices)
- **Create/Edit operations**: Collapsible right-side panel (sidebar)

#### Rationale

This pattern provides:
- **Context preservation**: Users see the list/details while editing
- **Reduced cognitive load**: No navigation interruption or page reloads
- **Quick operations**: Fast edits without losing place
- **Modern UX**: Follows patterns from popular apps (Gmail, Slack, Linear)

#### When to Use Collapsible Sidebar

✅ **Use sidebar for:**
- Simple forms (3-6 fields)
- Frequent edit operations
- Forms where seeing related data adds value
- Quick create/update workflows

❌ **Use full-page form for:**
- Complex forms (10+ fields) or multi-step wizards
- Critical operations requiring full attention
- Rich content editing (markdown, WYSIWYG)
- Heavy media uploads
- Mobile-first features where sidebars don't work well

#### Implementation Pattern

**Current implementations:**
- Rules: `src/frontend/templates/policy/rule_edit_sidebar.html` + `src/frontend/static/js/rules.js`
- Rulesets: `src/frontend/templates/policy/ruleset_selection_sidebar.html` + `src/frontend/static/js/rulesets.js`
- Licenses: `src/frontend/templates/license/license_edit_sidebar.html` + `src/frontend/static/js/licenses.js`

**Template structure:**
```html
<div id="item-edit-panel" class="hidden fixed right-0 top-0 h-full w-1/4 bg-white shadow-md z-50">
    <div class="flex justify-between items-center p-4 border-b bg-gray-200">
        <h2 class="text-xl font-bold" id="item-edit-title">Edit Item</h2>
        <button class="item-edit-panel-button"><!-- Close icon --></button>
    </div>
    <form id="item-edit-form" method="POST">
        {% csrf_token %}
        <!-- Form fields -->
        <div class="absolute flex space-x-2 w-full bottom-0 p-4 bg-gray-200">
            <button type="submit">Save</button>
            <button type="button" class="item-edit-panel-button">Cancel</button>
        </div>
    </form>
</div>
```

**JavaScript structure:**
```javascript
function toggleItemEditPanel(itemId) {
    const panel = document.getElementById('item-edit-panel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) {
        loadItemDetails(itemId);  // Populate form
    }
}

function submitItemForm() {
    // AJAX submission with X-Requested-With header
    // Handle success (close panel, reload) or errors (show in panel)
}
```

**Backend structure:**
```python
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'item_id': item.id})
            return redirect('item_detail', item_id=item.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return redirect('item_list')  # Fallback
```

**Key requirements:**
1. Sidebar template included in both list and detail pages
2. JavaScript file loaded with item data serialized to JSON
3. Views handle both AJAX (JSON response) and traditional (redirect) requests
4. Toggle button classes: `.item-edit-panel-button` for open/close
5. Form submission via AJAX with `X-Requested-With: XMLHttpRequest` header

#### Best Practices

- **Keyboard support**: Sidebar should close on `Esc` key (future enhancement)
- **Error handling**: Show validation errors inline without closing sidebar
- **Success feedback**: Currently reloads page; consider toast notifications
- **Mobile**: Consider full-screen modal for small screens
- **Consistency**: Follow existing patterns for new features

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

