<!-- 65f41ad7-e915-4955-ab6a-86acba28349b c42858ad-9684-44b9-8e07-0d154981ae61 -->
# Phase 2: Code Structure & Best Practices Implementation

## Overview

Implement all Phase 2 structural improvements (Issues 11-17) to enhance code organization, maintainability, and follow Django best practices. All changes will maintain backward compatibility with Lynis API endpoints.

## Prerequisites

- Phase 0 (Test Infrastructure): ✅ Complete
- Phase 1 (Security Fixes): ✅ Complete
- All tests must pass: `docker compose -f docker-compose.dev.yml --profile test run --rm test`
- Lynis integration must remain functional

## Implementation Order

### 2. Add Input Validation to ReportUploadForm (Issue #17)

**File**: `src/api/forms.py`

**Current state**: Basic form with no validators (lines 5-9)

**Changes**:

```python
import re
from django.core.validators import MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError

class ReportUploadForm(forms.Form):
    licensekey = forms.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='License key must contain only alphanumeric characters, hyphens, and underscores'
            )
        ],
        error_messages={
            'required': 'License key is required',
            'max_length': 'License key too long'
        }
    )
    
    hostid = forms.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Host ID must contain only alphanumeric characters, hyphens, and underscores'
            )
        ],
        error_messages={'required': 'Host ID is required'}
    )
    
    hostid2 = forms.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Host ID2 must contain only alphanumeric characters, hyphens, and underscores'
            )
        ],
        error_messages={'required': 'Host ID2 is required'}
    )
    
    data = forms.CharField(
        widget=forms.Textarea,
        error_messages={'required': 'Report data is required'}
    )
    
    def clean_data(self):
        data = self.cleaned_data.get('data', '')
        
        # Reasonable size limit: 10MB
        max_size = 10 * 1024 * 1024
        if len(data.encode('utf-8')) > max_size:
            raise ValidationError('Report data too large (max 10MB)')
        
        # Basic format validation: should contain Lynis report structure
        if 'report_version_major=' not in data:
            raise ValidationError('Invalid Lynis report format')
        
        return data
```

**Testing**: Verify existing tests still pass, especially `test_upload_report_malformed_data`

### 3. Move Utils to Proper Django App Structure (Issue #11)

**Current location**: `src/utils/` (2 files: `compliance.py`, `lynis_report.py`)

**Target location**: `src/api/utils/` (already exists!)

**Strategy**: `src/api/utils/` already exists and has `policy_query.py`. We need to move the root-level utils files there.

**Steps**:

1. Move files:

   - `src/utils/compliance.py` → `src/api/utils/compliance.py`
   - `src/utils/lynis_report.py` → `src/api/utils/lynis_report.py`

2. Update imports throughout codebase:

   - Search for `from utils.compliance import` → `from api.utils.compliance import`
   - Search for `from utils.lynis_report import` → `from api.utils.lynis_report import`
   - Likely locations: `src/api/views.py`, `src/frontend/views.py`

3. Delete empty `src/utils/` directory

4. Run tests to verify no import errors

**Critical**: Update all imports to use new path

### 4. Add STATIC_ROOT Configuration (Issue #13)

**File**: `src/compleasy/settings.py`

**Current state**: Only `STATIC_URL` and `STATICFILES_DIRS` configured (lines 186, 212-214)

**Changes**: Add after line 186:

```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# STATIC_ROOT: Directory where collectstatic will collect static files for production
# This is required for production deployments with a separate web server (Nginx, Apache)
STATIC_ROOT = os.environ.get('STATIC_ROOT', str(BASE_DIR / 'staticfiles'))
```

**Documentation**: Update README.md with production deployment section:

````markdown
### Collecting Static Files for Production

Before deploying, run:
```bash
docker compose -f docker-compose.yml run --rm compleasy python manage.py collectstatic --no-input
````

This collects all static files into `STATIC_ROOT` for serving by Nginx/Apache.

````

**Testing**: Verify `collectstatic` command works without errors

### 5. Move Report Cleanup Logic to Signals (Issue #14)

**Current location**: `src/api/models.py` lines 34-41 (inside `FullReport.save()`)

**Target**: `src/api/signals.py` (already exists)

**Changes**:

1. Remove cleanup logic from `FullReport.save()`:

```python
# models.py - REMOVE lines 34-41
def save(self, *args, **kwargs):
    super(FullReport, self).save(*args, **kwargs)
    # DELETE THIS LOGIC - moving to signal handler
````

2. Add signal handler in `src/api/signals.py`:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import FullReport

@receiver(post_save, sender=FullReport)
def cleanup_old_reports(sender, instance, created, **kwargs):
    """
    Keep only the latest 2 reports for each device.
    This signal fires after a FullReport is saved.
    """
    if created:  # Only run for new reports
        reports = FullReport.objects.filter(device=instance.device).order_by('-created_at')
        if reports.count() > 2:
            # Delete older reports except the latest 2
            for report in reports[2:]:
                report.delete()
```

3. Ensure signal is connected: Verify `src/api/apps.py` has proper `ready()` method:
```python
from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import api.signals  # noqa
```


**Why this is better**: Separates business logic from model persistence, easier to test, can be disabled if needed, follows Single Responsibility Principle.

**Testing**: Verify report cleanup still works by uploading multiple reports

### 6. Implement API Versioning with Backward Compatibility (Issue #15)

**Current URLs**: `/api/lynis/upload/`, `/api/lynis/license/`

**Target**: Add `/api/v1/lynis/upload/` while keeping old endpoints for Lynis compatibility

**Critical**: MUST maintain `/api/lynis/*` endpoints - they are used by external Lynis clients

**Changes**:

1. Update `src/compleasy/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    
    # API v1 (versioned endpoints)
    path('api/v1/', include('api.urls', namespace='api_v1')),
    
    # Legacy API (backward compatibility for Lynis)
    # These endpoints must remain for external Lynis clients
    path('api/', include('api.urls_legacy')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

2. Create `src/api/urls_legacy.py` (backward compatibility):
```python
"""
Legacy API URLs for backward compatibility with Lynis clients.
DO NOT REMOVE - These endpoints are used by external Lynis installations.
"""
from django.urls import path
from . import views

# No app_name here - legacy endpoints have no namespace
urlpatterns = [
    path('', views.index, name='api_index_legacy'),
    path('lynis/upload/', views.upload_report, name='upload_report'),
    path('lynis/license/', views.check_license, name='check_license'),
]
```

3. Update `src/api/urls.py` (versioned):
```python
"""API v1 URLs - versioned API endpoints"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.index, name='index'),
    path('lynis/upload/', views.upload_report, name='upload_report'),
    path('lynis/license/', views.check_license, name='check_license'),
]
```

4. Update tests to use reverse with namespace where appropriate

**Result**: Both `/api/lynis/upload/` (legacy) and `/api/v1/lynis/upload/` (versioned) will work

**Testing**:

- Verify Lynis integration test still works (uses legacy URLs)
- Verify both URL patterns route to same views
- Update any internal links to use versioned URLs

### 7. Split Settings into Environment-Specific Files (Issue #12)

**Current**: Single `src/compleasy/settings.py` (238 lines)

**Target**: Settings package with base/development/production split

**Strategy**: Create settings package while maintaining backward compatibility

**Steps**:

1. Create `src/compleasy/settings/` directory

2. Create `src/compleasy/settings/__init__.py`:
```python
"""
Settings module for Compleasy.
Loads appropriate settings based on DJANGO_ENV environment variable.
"""
import os

# Determine which settings to use
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *  # noqa
elif env == 'testing':
    from .testing import *  # noqa
else:
    from .development import *  # noqa
```

3. Move current settings to `src/compleasy/settings/base.py`:

   - Keep all common settings
   - Remove environment-specific overrides
   - Use placeholder values that will be overridden

4. Create `src/compleasy/settings/development.py`:
```python
from .base import *  # noqa

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Less strict security for local development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Verbose logging for debugging
LOGGING['root']['level'] = 'DEBUG'

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

5. Create `src/compleasy/settings/production.py`:
```python
from .base import *  # noqa

# Production-specific settings
DEBUG = False

# Require explicit ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError('DJANGO_ALLOWED_HOSTS must be set in production')

# Strict security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Production logging (INFO level)
LOGGING['root']['level'] = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')

# Require PostgreSQL in production
if not os.environ.get('DATABASE_URL'):
    raise ValueError('DATABASE_URL must be set in production')
```

6. Create `src/compleasy/settings/testing.py`:
```python
from .development import *  # noqa

# Testing-specific settings
# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable rate limiting in tests
RATELIMIT_ENABLE = False

# Simpler password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
```

7. Update all references:

   - `docker-compose.yml`: Add `DJANGO_ENV=production`
   - `docker-compose.dev.yml`: Add `DJANGO_ENV=development`
   - `pytest.ini`: Update to `DJANGO_SETTINGS_MODULE = compleasy.settings`
   - `manage.py`: Already uses `DJANGO_SETTINGS_MODULE`
   - `wsgi.py`: Already uses `DJANGO_SETTINGS_MODULE`

8. Update `.env.example`: Add `DJANGO_ENV=development`

**Benefits**:

- Clear separation of concerns
- Environment-specific optimizations
- Easier to understand what changes between environments
- Safer defaults for production

**Testing**: Run tests in all three environments to verify settings load correctly

## Testing Strategy

After each change:

1. Run unit tests: `docker compose -f docker-compose.dev.yml --profile test run --rm test`
2. Run integration tests: `docker compose -f docker-compose.dev.yml up --abort-on-container-exit lynis-client`
3. Verify Lynis endpoints work with both legacy and versioned URLs
4. Check for import errors and linter warnings
5. Test static file collection: `docker compose -f docker-compose.dev.yml run --rm compleasy python manage.py collectstatic --no-input`

## Files Changed

**Created**:

- `src/api/urls_legacy.py` (backward compatibility)
- `src/compleasy/settings/__init__.py`
- `src/compleasy/settings/base.py`
- `src/compleasy/settings/development.py`
- `src/compleasy/settings/production.py`
- `src/compleasy/settings/testing.py`

**Modified**:

- `src/api/forms.py` (add validators)
- `src/api/models.py` (remove cleanup logic)
- `src/api/signals.py` (add cleanup signal)
- `src/api/apps.py` (ensure signals are loaded)
- `src/api/urls.py` (add namespace)
- `src/compleasy/urls.py` (add versioning)
- `src/compleasy/settings.py` (will be deleted after split)
- `docker-compose.yml` (add DJANGO_ENV)
- `docker-compose.dev.yml` (add DJANGO_ENV)
- `README.md` (document static files, settings structure)
- Any files importing from `utils.*` (update imports)

**Moved**:

- `src/utils/compliance.py` → `src/api/utils/compliance.py`
- `src/utils/lynis_report.py` → `src/api/utils/lynis_report.py`

**Deleted**:

- `src/utils/` directory
- `src/compleasy/settings.py` (replaced by settings package)

## Rollback Plan

Each change is independent and can be reverted:

- Git commit after each successful step
- Tag working states
- Keep backward compatibility at all times
- Lynis API endpoints must never break

## Success Criteria

- ✅ All 17 unit tests pass
- ✅ Lynis integration test passes
- ✅ No import errors
- ✅ Static files can be collected successfully
- ✅ Report cleanup works via signals
- ✅ Both `/api/lynis/upload/` and `/api/v1/lynis/upload/` work
- ✅ Form validation rejects invalid input
- ✅ Settings load correctly in all three environments
- ✅ No `src/utils/` at project root
- ✅ STATIC_ROOT configured and documented

## Notes

- **Issue #16 (Empty Test Files)**: Already completed in Phase 0 with 17 passing tests
- **Critical**: Never break Lynis API compatibility (`/api/lynis/*` endpoints)
- All tests run in Docker containers
- Use `docker compose` (not `docker-compose`)

### To-dos

- [ ] Add validators to ReportUploadForm for license key, hostid, and data fields
- [ ] Move src/utils/*.py files to src/api/utils/ and update all imports
- [ ] Add STATIC_ROOT configuration to settings and document collectstatic
- [ ] Move report cleanup logic from FullReport.save() to signal handler
- [ ] Add API versioning (/api/v1/) while maintaining backward compatibility
- [ ] Split settings.py into settings package (base/development/production/testing)
- [ ] Update README.md with new structure documentation
- [ ] Run complete test suite and verify Lynis integration works